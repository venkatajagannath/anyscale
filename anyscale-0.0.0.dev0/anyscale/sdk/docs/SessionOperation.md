# SessionOperation

Describes a long running session operation that will eventually complete.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of this operation. | 
**completed** | **bool** | Boolean indicating if this operation is completed. | 
**progress** | [**OperationProgress**](OperationProgress.md) | Details about the progress of this operation at the time of the request.             This will be absent for completed operations. | [optional] 
**result** | [**OperationResult**](OperationResult.md) | The result of this operation after it has completed.             This is always provided when the operation is complete. | [optional] 
**session_id** | **str** | ID of the Session that is being updated. | 
**session_operation_type** | [**SessionOperationType**](SessionOperationType.md) | The variety of operation being performed:             start sets the session&#39;s goal state to Running,             stop sets the session&#39;s goal state to Stopped,             terminate sets the session&#39;s goal state to Terminated | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


