from unittest.mock import Mock

from anyscale.utils.connect_helpers import search_entities


def test_search_entities():
    # 1. Test all records returned
    continued_response_of_size_two = Mock(
        results=[Mock(), Mock()], metadata=Mock(next_paging_token="token",),
    )
    mock_search_api = Mock(
        side_effect=[
            continued_response_of_size_two,
            Mock(results=[Mock()], metadata=Mock(next_paging_token=None,),),
        ]
    )
    assert len(search_entities(mock_search_api, query_obj=Mock())) == 3
    # 2. Test `max_to_return` reached
    mock_search_api = Mock(return_value=continued_response_of_size_two)
    assert len(search_entities(mock_search_api, query_obj=Mock(), max_to_return=1)) == 1
