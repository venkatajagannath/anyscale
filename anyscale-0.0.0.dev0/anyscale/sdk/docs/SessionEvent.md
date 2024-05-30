# SessionEvent

Model of a session event item from the session event log.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**event_type** | **str** | The category of session event. | 
**log_level** | [**LogLevelTypes**](LogLevelTypes.md) | The severity of the session event. | 
**timestamp** | **datetime** | The time at which the session event occurred. | 
**description** | **str** | A human readable description of the session event. | 
**cause** | [**SessionEventCause**](SessionEventCause.md) | The reason why the session event occurred. None indicates an unknown cause. | [optional] 
**id** | **str** | A unique identifier for the session event. | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


