# JobsQuery

Query model used to filter Jobs.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**TextQuery**](TextQuery.md) | Filters Jobs by name. If this field is absent, no filtering is done. | [optional] 
**runtime_environment_id** | **str** | Filters Jobs by runtime enviornment id. If this field is absent, no filtering is done. | [optional] 
**cluster_id** | **str** | Filters Jobs by cluster id. If this field is absent, no filtering is done. | [optional] 
**creator_id** | **str** | Filters Jobs by creator_id. If this field is absent, no filtering is done. | [optional] 
**ray_job_id** | **str** | Filters Jobs by ray_job_id. If this field is absent, no filtering is done. Note: the ray_job_id is only unique for one cluster. | [optional] 
**project_id** | **str** | Filters Jobs by project_id. If this field is absent, no filtering is done. | [optional] 
**include_child_jobs** | **bool** | Include jobs that have parents | [optional] [default to False]
**ha_job_id** | **str** | Filter by the anyscale job | [optional] 
**show_ray_client_runs_only** | **bool** | DEPRECATED: use type_filter. Shows only ray client runs. Orthogonal to passing ha_job_id | [optional] [default to True]
**paging** | [**PageQuery**](PageQuery.md) | Pagination information. | [optional] 
**state_filter** | [**list[BaseJobStatus]**](BaseJobStatus.md) | Filter Jobs by Job Status. If this field is an empty set, no filtering is done. | [optional] [default to []]
**type_filter** | [**list[JobRunType]**](JobRunType.md) | Filter Jobs by their type. Their type is determined by their usage within the product e.g. Interactive sessions, job runs | [optional] [default to []]
**sort_by_clauses** | [**list[SortByClauseJobsSortField]**](SortByClauseJobsSortField.md) | The order used to specify results. The list will be used to construct ORDER BY database queries. If not specified, the fallback order by clauses are 1. Creation time (desc) 2. Name (ascending) and 3. ID (ascending) | [optional] [default to [{"sort_field":"CREATED_AT","sort_order":"DESC"},{"sort_field":"NAME","sort_order":"ASC"},{"sort_field":"ID","sort_order":"ASC"}]]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


