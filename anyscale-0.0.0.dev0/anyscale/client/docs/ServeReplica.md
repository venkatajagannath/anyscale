# ServeReplica

ServeReplica are actors created by the ServeController. They include additional metric defined in ServeReplicaMetric.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**ray_actor_id** | **str** |  | 
**ray_replica_id** | **str** |  | [optional] 
**replica_deployment_version** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**status** | [**ActorStatus**](ActorStatus.md) |  | 
**lifetime** | [**ActorLifetime**](ActorLifetime.md) |  | 
**class_name** | **str** |  | [optional] 
**task_name** | **str** |  | [optional] 
**job_id** | **str** |  | 
**created_at** | **datetime** |  | 
**finished_at** | **datetime** |  | [optional] 
**current_worker_id** | **str** |  | 
**ray_ip_address** | **str** |  | [optional] 
**ray_port** | **int** |  | [optional] 
**runtime_environment_id** | **str** |  | 
**serve_deployment_id** | **str** |  | [optional] 
**metrics** | [**ServeReplicaMetric**](ServeReplicaMetric.md) | The metrics for this replica | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


