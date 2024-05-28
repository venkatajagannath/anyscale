# MiniJobRun

The MiniJobRun fetches a BaseJob and decorates it with     - cluster  This is more performant than using DecoratedJob because it fetches much less additional information
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**ray_session_name** | **str** |  | 
**ray_job_id** | **str** |  | 
**name** | **str** |  | [optional] 
**status** | [**BaseJobStatus**](BaseJobStatus.md) |  | 
**created_at** | **datetime** |  | 
**finished_at** | **datetime** |  | [optional] 
**ha_job_id** | **str** |  | [optional] 
**ray_job_submission_id** | **str** |  | [optional] 
**cluster_id** | **str** |  | 
**namespace_id** | **str** |  | 
**environment_id** | **str** |  | 
**project_id** | **str** |  | [optional] 
**creator_id** | **str** |  | 
**cluster** | [**MiniCluster**](MiniCluster.md) |  | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


