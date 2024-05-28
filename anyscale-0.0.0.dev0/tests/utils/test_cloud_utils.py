from dataclasses import dataclass
from typing import Optional
from unittest.mock import call, Mock, patch

import pytest

from anyscale.cli_logger import CloudSetupLogger
from anyscale.client.openapi_client.models import (
    CloudAnalyticsEvent,
    CloudAnalyticsEventCloudProviderError,
    CloudAnalyticsEventError,
    CreateAnalyticsEvent,
)
from anyscale.utils.cloud_utils import (
    CloudEventProducer,
    extract_cloudformation_failure_reasons,
    get_errored_resources_and_reasons,
    unroll_pagination,
)


@pytest.mark.parametrize(
    ("internal_error", "cloud_provider_error"),
    [(True, False), (False, True), (False, False), (True, True)],
)
@pytest.mark.parametrize("exception", [True, False])
def test_cloud_event_producer_produce(internal_error, cloud_provider_error, exception):
    mock_api_client = Mock()
    mock_cli_version = "mock_version"
    mock_cloud_provider = Mock()
    mock_api_client.produce_analytics_event_api_v2_analytics_post = Mock()
    if exception:
        mock_api_client.produce_analytics_event_api_v2_analytics_post.side_effect = (
            Exception()
        )
    logger = CloudSetupLogger()
    mock_cloud_resource = Mock()
    if cloud_provider_error:
        logger.log_resource_error(mock_cloud_resource, "not_found", 404)
    mock_internal_error = "mock_internal_error" if internal_error else None
    expected_cloud_provider_error = (
        [
            CloudAnalyticsEventCloudProviderError(
                cloud_resource=mock_cloud_resource, error_code="not_found,404",
            )
        ]
        if cloud_provider_error
        else None
    )

    cloud_event_producer = CloudEventProducer(mock_cli_version, mock_api_client)
    cloud_event_producer.init_trace_context(Mock(), mock_cloud_provider, Mock())
    mock_event_name = Mock()
    succeeded = not (internal_error or cloud_provider_error)
    expected_error = None
    if internal_error or cloud_provider_error:
        expected_error = CloudAnalyticsEventError(
            internal_error=mock_internal_error,
            cloud_provider_error=expected_cloud_provider_error,
        )

    # shouldn't throw exceptions
    cloud_event_producer.produce(
        event_name=mock_event_name,
        succeeded=succeeded,
        logger=logger,
        internal_error=mock_internal_error,
    )

    mock_api_client.produce_analytics_event_api_v2_analytics_post.assert_called_once_with(
        CreateAnalyticsEvent(
            cloud_analytics_event=CloudAnalyticsEvent(
                cli_version=mock_cli_version,
                trace_id=cloud_event_producer.trace_id,
                cloud_id=cloud_event_producer.cloud_id,
                succeeded=succeeded,
                command_name=cloud_event_producer.command_name,
                raw_command_input=cloud_event_producer.raw_command_input,
                cloud_provider=mock_cloud_provider,
                event_name=mock_event_name,
                error=expected_error,
            )
        )
    )


@pytest.mark.parametrize("has_next_token", [True, False])
def test_get_errored_resources_and_reasons(has_next_token: bool):
    mock_reasons = Mock()
    mock_client = Mock()
    mock_client.describe_stack_events = Mock()
    if has_next_token:
        mock_client.describe_stack_events.side_effect = [
            {
                "StackEvents": [
                    {
                        "ResourceStatus": "CREATE_FAILED",
                        "ResourceType": "AWS::EC2::Instance",
                        "LogicalResourceId": "mock_resource_id",
                        "ResourceStatusReason": "mock_reason",
                    }
                ],
                "NextToken": "mock_token",
            },
            {
                "StackEvents": [
                    {
                        "ResourceStatus": "CREATE_FAILED",
                        "ResourceType": "AWS::EC2::Instance",
                        "LogicalResourceId": "mock_resource_id2",
                        "ResourceStatusReason": "mock_reason2",
                    }
                ],
            },
        ]
    else:
        mock_client.describe_stack_events.return_value = {
            "StackEvents": [
                {
                    "ResourceStatus": "CREATE_FAILED",
                    "ResourceType": "AWS::EC2::Instance",
                    "LogicalResourceId": "mock_resource_id",
                    "ResourceStatusReason": "mock_reason",
                }
            ]
        }

    mock_reasons = Mock(return_value={})
    with patch.multiple(
        "anyscale.utils.cloud_utils",
        extract_cloudformation_failure_reasons=mock_reasons,
    ):
        get_errored_resources_and_reasons(mock_client, Mock())
    if has_next_token:
        assert mock_client.describe_stack_events.call_count == 2
        assert mock_reasons.call_count == 2
    else:
        assert mock_client.describe_stack_events.call_count == 1
        assert mock_reasons.call_count == 1


def test_extract_cloudformation_failure_reasons():
    events = []

    # test empty events
    assert extract_cloudformation_failure_reasons(events) == {}

    # test single event
    events.append(
        {
            "ResourceStatus": "CREATE_FAILED",
            "ResourceType": "AWS::EC2::Instance",
            "LogicalResourceId": "mock_resource_id",
            "ResourceStatusReason": "mock_reason",
        }
    )
    expected = {"mock_resource_id": "mock_reason"}
    assert extract_cloudformation_failure_reasons(events) == expected

    # test resource status
    events.append(
        {
            "ResourceStatus": "CREATE_COMPLETE",
            "ResourceType": "AWS::EC2::Instance",
            "LogicalResourceId": "mock_resource_id2",
            "ResourceStatusReason": "mock_reason2",
        }
    )
    assert extract_cloudformation_failure_reasons(events) == expected

    # test unknown reason
    events.append(
        {
            "ResourceStatus": "CREATE_FAILED",
            "ResourceType": "AWS::EC2::Instance",
            "LogicalResourceId": "mock_resource_id3",
        }
    )
    expected["mock_resource_id3"] = "Unknown reason"
    assert extract_cloudformation_failure_reasons(events) == expected

    # test resource creation cancelled
    events.append(
        {
            "ResourceStatus": "CREATE_FAILED",
            "ResourceType": "AWS::EC2::Instance",
            "LogicalResourceId": "mock_resource_id4",
            "ResourceStatusReason": "Resource creation cancelled",
        }
    )
    assert extract_cloudformation_failure_reasons(events) == expected


def test_unroll_resources_for_aws_list_call():
    @dataclass
    class Response:
        next_token: Optional[str]

    num_pages = 5

    def paginated_method(next_token: Optional[str]) -> Response:
        if not next_token:
            return Response(next_token="1")

        next_token_i = int(next_token)
        return Response(
            next_token=str(next_token_i + 1) if next_token_i < num_pages else None,
        )

    paginated_method_mock = Mock(side_effect=paginated_method)

    responses = unroll_pagination(paginated_method_mock, lambda r: r.next_token)

    expected_responses = [
        Response(next_token=str(i)) for i in range(1, num_pages + 1)
    ] + [Response(next_token=None)]

    assert expected_responses == responses

    paginated_method_mock.assert_has_calls(
        calls=[call(None)] + [call(str(i)) for i in range(1, num_pages + 1)],
        any_order=False,
    )
