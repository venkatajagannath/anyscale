# DecoratedCronJob

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the job | 
**description** | **str** | Description of the job | [optional] 
**project_id** | **str** | Id of the project this job will start clusters in | 
**config** | [**ProductionJobConfig**](ProductionJobConfig.md) | The config that was used to create this job | 
**cron_expression** | **str** | cron expression to define the frequency at which to run this cron job | [optional] 
**id** | **str** | The id of this job | 
**created_at** | **datetime** | The time this job was created | 
**updated_at** | **datetime** | The time this job was updated | 
**creator_id** | **str** | The id of the user who created this job | 
**project** | [**MiniProject**](MiniProject.md) | The project in which this production job lives | 
**creator** | [**MiniUser**](MiniUser.md) | The creator of this job | 
**last_executions** | [**list[MiniProductionJob]**](MiniProductionJob.md) |  | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


