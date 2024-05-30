# AppConfigConfigSchema

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**base_image** | [**BASEIMAGESENUM**](BASEIMAGESENUM.md) | The base image used in the app config. It needs to be one of the base images that we ever supported (BASE_IMAGES_HISTORY). | 
**env_vars** | [**object**](.md) | Environment varibles in the docker image that&#39;ll be used at runtime. | [optional] 
**debian_packages** | **list[str]** | List of debian packages that&#39;ll be included in the image. | [optional] 
**python** | [**PythonModules**](PythonModules.md) | Python related dependencies. | [optional] 
**post_build_cmds** | **list[str]** | List of post build commands that&#39;ll be included in the image. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


