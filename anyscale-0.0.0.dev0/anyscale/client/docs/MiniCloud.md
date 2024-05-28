# MiniCloud

The greatest common factor for cloud data across most endpoints of the API server
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The id of the cloud | 
**name** | **str** | The name of this cloud | 
**provider** | [**CloudProviders**](CloudProviders.md) | The cloud provider for this cloud | 
**is_k8s** | **bool** | Whether this cloud is managed via K8s | [optional] [default to False]
**is_aioa** | **bool** | Whether this cloud is an AIOA cloud. | [optional] [default to False]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


