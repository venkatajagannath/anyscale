# DecoratedInteractiveSession

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
**project** | [**MiniProject**](MiniProject.md) |  | [optional] 
**cluster** | [**MiniCluster**](MiniCluster.md) |  | 
**creator** | [**MiniUser**](MiniUser.md) |  | 
**namespace** | [**MiniNamespace**](MiniNamespace.md) |  | 
**runtime_environment** | [**MiniRuntimeEnvironment**](MiniRuntimeEnvironment.md) |  | 
**cost_dollars** | **float** | The total cost, in dollars, of the job&#39;s cluster during the time the job was running | [optional] 
**is_colocated** | **bool** | Whether or not this job was colocated with another job on the same cluster at the same time | [optional] 
**access** | [**JobAccess**](JobAccess.md) | The varieity of users with access to this job. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


