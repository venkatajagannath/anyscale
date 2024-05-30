# ClustersQuery

Query model used to filter Clusters.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_id** | **str** | Filters Clusters belonging to a Project. If this field is absent, no filtering is done. | [optional] 
**name** | [**TextQuery**](TextQuery.md) | Filters Clusters by name. If this field is absent, no filtering is done. | [optional] 
**paging** | [**PageQuery**](PageQuery.md) | Pagination information. | [optional] 
**state_filter** | [**list[ClusterState]**](ClusterState.md) | Filter Sessions by Session State. If this field is an empty set, no filtering is done. | [optional] [default to []]
**archive_status** | [**ArchiveStatus**](ArchiveStatus.md) | The archive status to filter by. Defaults to unarchived. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


