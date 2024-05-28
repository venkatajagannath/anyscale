# SessionsQuery

Query model used to filter Cluster. It is exposed in SDK.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**TextQuery**](TextQuery.md) | Filters Cluster by name. If this field is absent, no filtering is done. | [optional] 
**paging** | [**PageQuery**](PageQuery.md) | Pagination information. | [optional] 
**state_filter** | [**list[SessionState]**](SessionState.md) | Filter Cluster by Session State. If this field is an empty set, no filtering is done. | [optional] [default to []]
**creator_id** | **str** | Filters Jobs by creator_id. If this field is absent, no filtering is done. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


