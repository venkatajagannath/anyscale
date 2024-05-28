# ActorsQuery

Query model used to filter Actors.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**TextQuery**](TextQuery.md) | Filters Actors by name. If this field is absent, no filtering is done. | [optional] 
**runtime_environment_id** | **str** | Filters Actors by runtime environment id. If this field is absent, no filtering is done. | [optional] 
**job_id** | **str** | Filters Actors by job id. If this field is absent, no filtering is done. | [optional] 
**ray_job_submission_db_id** | **str** | Filters Actors by ray job submission db id. If this field is absent, no filtering is done. | [optional] 
**cluster_id** | **str** | Filters Actors by cluster_id. If this field is absent, no filtering is done. | [optional] 
**serve_deployment_id** | **str** | Filters Actors by serve_deployment_id. If this field is absent, no filtering is done. | [optional] 
**only_replicas** | **bool** | Filters for Actors that are replicas by filtering out ServeController / HTTPProxyActors. Must be used in conjunction with serve_deployment_id | [optional] 
**paging** | [**PageQuery**](PageQuery.md) | Pagination information. | [optional] 
**state_filter** | [**list[ActorStatus]**](ActorStatus.md) | Filter Actors by Actor Status. If this field is an empty set, no filtering is done. | [optional] [default to []]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


