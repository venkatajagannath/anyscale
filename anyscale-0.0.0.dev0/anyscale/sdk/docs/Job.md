# Job

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Server assigned unique identifier. | 
**ray_session_name** | **str** | Name of the Session provided from Ray | 
**ray_job_id** | **str** | ID of the Job provided from Ray | 
**name** | **str** | Name of this Job. | [optional] 
**status** | [**JobStatus**](JobStatus.md) | Status of this Job&#39;s execution. | 
**created_at** | **datetime** | Time at which this Job was created. | 
**finished_at** | **datetime** | Time at which this Job finished. If absent, this Job is still running. | [optional] 
**ray_job_submission_id** | **str** | ID of the submitted Ray Job that this Job corresponds to. | [optional] 
**cluster_id** | **str** | ID of the Anyscale Cluster this Job is on. | 
**namespace_id** | **str** | ID of the Anyscale Namespace this Job is using. | 
**runtime_environment_id** | **str** | ID of the Anyscale Runtime Environment this Job is using. | 
**project_id** | **str** | ID of the Project this Job belongs to. | [optional] 
**creator_id** | **str** | ID of the user who created this Job. | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


