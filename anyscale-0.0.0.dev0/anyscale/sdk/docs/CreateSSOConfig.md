# CreateSSOConfig

Model used to create an SSOConfig. Must contain at least one of idp_metadata_url or static_config.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**idp_metadata_url** | **str** | Identity provider (IdP) metadata url. If given along with the other static identity provider fields, Anyscale will first attempt metadata exchange to get IdP attributes. If Anyscale can&#39;t reach the metadata endpoint or if the metadata url isn&#39;t given, Anyscale will use static_idp_config as a backup. Either idp_metadata_url or static_idp_config is required. | [optional] 
**static_idp_config** | [**StaticSSOConfig**](StaticSSOConfig.md) | Static identity provider configuration. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


