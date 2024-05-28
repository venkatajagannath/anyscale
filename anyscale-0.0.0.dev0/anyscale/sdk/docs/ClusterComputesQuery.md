# ClusterComputesQuery

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_id** | **str** | Filters Cluster Computes by project. If this field is absent, no filtering is done. | [optional] 
**creator_id** | **str** | Filters Compute Computes by creator. If this field is absent, no filtering is done. | [optional] 
**name** | [**TextQuery**](TextQuery.md) | Filters ComputeTemplates by name. If this field is absent, no filtering is done. | [optional] 
**include_anonymous** | **bool** | Whether to include anonymous compute templates in the search. | [optional] [default to False]
**paging** | [**PageQuery**](PageQuery.md) | Pagination information. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


