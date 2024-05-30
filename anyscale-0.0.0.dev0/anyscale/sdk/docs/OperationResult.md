# OperationResult

The result of an Operation upon completion. Exactly one of `error` or `data` will be set.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | **object** | The response of this operation in case of success.        This is typically the resource that this operation acted on. | [optional] 
**error** | [**OperationError**](OperationError.md) | The response of this operation in case of failure | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


