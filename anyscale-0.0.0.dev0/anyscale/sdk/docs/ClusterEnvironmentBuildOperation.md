# ClusterEnvironmentBuildOperation

Describes a long running operation that will eventually complete. Consider this an abstract class. Specific kinds of operations should subclass this.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of this operation. | 
**completed** | **bool** | Boolean indicating if this operation is completed. | 
**progress** | [**OperationProgress**](OperationProgress.md) | Details about the progress of this operation at the time of the request.             This will be absent for completed operations. | [optional] 
**result** | [**OperationResult**](OperationResult.md) | The result of this operation after it has completed.             This is always provided when the operation is complete. | [optional] 
**cluster_environment_build_id** | **str** | ID of the Cluster Environment Build this operation is for. | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


