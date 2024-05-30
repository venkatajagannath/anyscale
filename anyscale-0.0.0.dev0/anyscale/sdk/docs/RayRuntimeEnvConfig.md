# RayRuntimeEnvConfig

A runtime env config. Can be used to start a production job.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**working_dir** | **str** | The working directory that your code will run in. Must be a remote URI like an s3 or git path. | [optional] 
**py_modules** | **list[str]** | Python modules that will be installed along with your runtime env. These must be remote URIs. | [optional] 
**pip** | **list[str]** | A list of pip packages to install. | [optional] 
**conda** | **object** | [Union[Dict[str, Any], str]: Either the conda YAML config or the name of a local conda env (e.g., \&quot;pytorch_p36\&quot;),  | [optional] 
**env_vars** | **dict(str, str)** | Environment variables to set. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


