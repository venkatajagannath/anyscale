# ProviderMetadata

Various information about the Cloud account fetched from the Cloud provider.  This object is primarily used for caching calls to the cloud provider. It is to be considered soft state, and each field is optional. If a field is present, it is also timestamped with when we got the data.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**timestamp** | **datetime** |  | 
**available_regions** | [**object**](.md) | The available regions for this Cloud. | [optional] 
**available_azs** | [**object**](.md) | The available AZs for this Cloud. | [optional] 
**available_instance_types** | [**object**](.md) | The instance types available for this Cloud. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


