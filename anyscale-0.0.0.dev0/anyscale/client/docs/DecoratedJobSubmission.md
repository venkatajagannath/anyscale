# DecoratedJobSubmission

A decorated job submission
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The id of this job submission | 
**status** | [**JobStatus**](JobStatus.md) | The current status of this job submission | 
**created_at** | **datetime** | The time this job submission was created | 
**finished_at** | **datetime** | The time this job submission was finished | [optional] 
**ha_job_id** | **str** | The anyscale job id of this job submission | [optional] 
**ray_job_submission_id** | **str** | The ray job submission id of this job submission | [optional] 
**ray_session_name** | **str** | The ray session name of this job submission | 
**cluster_id** | **str** | The id of the cluster associated with this job submission | 
**environment_id** | **str** | The id of the environment associated with this job submission | [optional] 
**creator_id** | **str** | The id of the user who created this job submission | [optional] 
**name** | **str** | Name of this Job Submission. | [optional] 
**cluster** | [**MiniCluster**](MiniCluster.md) | Cluster/Session of this Job Submission. | [optional] 
**creator** | [**MiniUser**](MiniUser.md) | Creator (User) of this Job Submission. | [optional] 
**runtime_environment** | [**MiniRuntimeEnvironment**](MiniRuntimeEnvironment.md) | Runtime Environment of this Job Submission. | [optional] 
**cost_dollars** | **float** | The total cost, in dollars, of the job&#39;s cluster during the time the job was running | [optional] 
**project** | [**MiniProject**](MiniProject.md) | The project in which this job submission lives | [optional] 
**access** | [**JobAccess**](JobAccess.md) | The varieity of users with access to this job. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


