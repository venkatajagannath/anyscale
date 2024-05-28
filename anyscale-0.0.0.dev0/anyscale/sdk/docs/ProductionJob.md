# ProductionJob

Model of a Production Job for use in the SDK.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The id of this job | 
**name** | **str** | Name of the job | 
**description** | **str** | Description of the job | [optional] 
**created_at** | **datetime** | The time this job was created | 
**creator_id** | **str** | The id of the user who created this job | 
**config** | [**ProductionJobConfig**](ProductionJobConfig.md) | The config that was used to create this job | 
**state** | [**ProductionJobStateTransition**](ProductionJobStateTransition.md) | The current state of this job | 
**project_id** | **str** | Id of the project this job will start clusters in | 
**last_job_run_id** | **str** | The id of the last job run | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


