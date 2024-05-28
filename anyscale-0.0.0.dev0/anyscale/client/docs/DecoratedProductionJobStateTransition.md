# DecoratedProductionJobStateTransition

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The id of this job state transition | 
**state_transitioned_at** | **datetime** | The last time the state of this job was updated. This includes updates to the state and to the goal state | 
**current_state** | [**HaJobStates**](HaJobStates.md) | The current state of the job | 
**goal_state** | [**HaJobGoalStates**](HaJobGoalStates.md) | The goal state of the job | [optional] 
**error** | **str** | An error message that occurred in this job state transition | [optional] 
**operation_message** | **str** | The logging message for this job state transition | [optional] 
**cluster_id** | **str** | The id of the cluster the job is running on | [optional] 
**cluster** | [**MiniCluster**](MiniCluster.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


