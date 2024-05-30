from dataclasses import dataclass
import inspect
from typing import Any, Callable, Dict, Generic, List, Optional, TYPE_CHECKING, TypeVar

from anyscale.anyscale_pydantic import BaseModel
from anyscale.client.openapi_client.models.session import Session
from anyscale.sdk.anyscale_client.models.cluster import Cluster


if TYPE_CHECKING:
    from anyscale.sdk.anyscale_client.sdk import AnyscaleSDK


try:
    from ray.client_builder import ClientContext
except ImportError:
    # Import error will be raised in `ClientBuilder.__init__`.
    # Not raising error here to allow `anyscale.connect required_ray_version`
    # to work.
    @dataclass
    class ClientContext:  # type: ignore
        pass


@dataclass
class AnyscaleClientConnectResponse:
    """
    Additional information returned about clusters that were connected from Anyscale.
    """

    cluster_id: str


class AnyscaleClientContext(ClientContext):  # type: ignore
    def __init__(
        self, anyscale_cluster_info: AnyscaleClientConnectResponse, **kwargs: Any,
    ) -> None:
        if _multiclient_supported() and "_context_to_restore" not in kwargs:
            # Set to None for now until multiclient is supported on connect
            kwargs["_context_to_restore"] = None
        super().__init__(**kwargs)
        self.anyscale_cluster_info = anyscale_cluster_info


def _multiclient_supported() -> bool:
    """True if ray version supports multiple clients, False otherwise"""
    _context_params = inspect.signature(ClientContext.__init__).parameters
    return "_context_to_restore" in _context_params


def find_project_id(sdk: "AnyscaleSDK", project_name: str) -> Optional[str]:
    """Return id if a project of a given name exists."""
    resp = sdk.search_projects({"name": {"equals": project_name}})
    if len(resp.results) > 0:
        return resp.results[0].id  # type: ignore
    else:
        return None


def get_cluster(
    sdk: "AnyscaleSDK", project_id: str, session_name: str
) -> Optional[Session]:
    """Query Anyscale for the given cluster's metadata."""
    clusters = sdk.search_clusters(
        {
            "project_id": project_id,
            "name": {"equals": session_name},
            "archive_status": "ALL",
        }
    ).results
    cluster_found: Optional[Cluster] = None
    for cluster in clusters:
        if cluster.name == session_name:
            cluster_found = cluster
            break

    # A separate call is needed because downstream clients expect "Session" type
    if cluster_found:
        return sdk.get_session(cluster_found.id).result
    return None


def list_entities(
    list_function: Callable[..., Any],
    container_id: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    max: Optional[int] = None,  # noqa: A002
) -> List[Any]:
    """Convenience function to automatically handle paging tokens.

    This function repeatedly calls `list_function`, which is a GET endpoint
    with `container_id` until all (potentially paged) results are received.
    """
    entities: List[Any] = []
    has_more = True
    paging_token = None
    filters = filters or {}
    while has_more and (not max or len(entities) < max):
        if container_id:
            resp = list_function(
                container_id, count=50, paging_token=paging_token, **filters
            )
        else:
            resp = list_function(count=50, paging_token=paging_token, **filters)
        entities.extend(resp.results)
        paging_token = resp.metadata.next_paging_token
        has_more = paging_token is not None
    return entities


T = TypeVar("T")


class ListResponseMetadata(BaseModel):
    total: Optional[int] = None
    next_paging_token: Optional[str] = None


class ListResponse(BaseModel, Generic[T]):
    results: List[T]
    metadata: ListResponseMetadata


# Must be the `<Entity>Query` Anyscale model. It cannot be a dict.
QueryObj = TypeVar("QueryObj", bound=object)


def search_entities(
    search_function: Callable[[QueryObj], ListResponse[T]],
    query_obj: QueryObj,
    max_to_return: int = 1000,
) -> List[T]:
    """Automatically paginate to retrieve all search results up to `max_to_return`
    (default = 1000).

    Works for POST endpoints where a single query object is passed
    (in the request body) to the endpoint.
    """
    entities: List[T] = []
    has_more = True
    count = 0

    while has_more and count < max_to_return:
        resp = search_function(query_obj)
        count += len(resp.results)
        entities += resp.results

        next_paging_token = resp.metadata.next_paging_token
        query_obj.paging.paging_token = next_paging_token  # type: ignore
        has_more = next_paging_token is not None
    if count > max_to_return:
        count = max_to_return
        entities = entities[:max_to_return]

    return entities
