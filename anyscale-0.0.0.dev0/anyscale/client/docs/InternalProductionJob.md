# InternalProductionJob

ProductionJob type that is exposed in create and terminate endpoints.
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
**is_service** | **bool** | Indicates if this job is runs with indefinitely with HA | 
**cost_dollars** | **float** | The total cost, in dollars, of the ha job. This is the sum of all job runs  | [optional] 
**url** | **str** | URL to access deployment running in service | [optional] 
**token** | **str** | Token used to authenticate user service if it is accessible to public internet. This field will beempty if user service is not publically accessible. | [optional] 
**access** | [**UserServiceAccessTypes**](UserServiceAccessTypes.md) | Whether service can be accessed by public internet traffic. | [optional] 
**healthcheck_url** | **str** | The healthcheck url. Anyscale will poll this url to determine whether the service is healthy or not. Only present for services | [optional] 
**archived_at** | **datetime** | The time in which this instance is archived. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


