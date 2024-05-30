# RuntimeEnvironment

Reusable runtime environment for Jobs and Actors running in Anyscale.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Server assigned unique Identifier | 
**ray_env_hash** | **str** | A hash of this Runtime Environment as provided by Ray | 
**name** | **str** | Name for this Runtime Environment. | [optional] 
**working_dir** | **str** | The working directory for this Runtime Environment. | [optional] 
**py_modules** | **list[str]** | Python modules included in this Runtime Environment. | [optional] 
**pip_packages** | **str** | Pip dependencies installed in this Runtime Environment. | [optional] 
**conda_env_name** | **str** | Name of the Conda environment this Runtime Environment is using. | [optional] 
**conda_values** | [**object**](.md) | Conda values for this Runtime Environment. | [optional] 
**env_variables** | **dict(str, str)** | Environment variables set for this Runtime Environment. | [optional] 
**created_at** | **datetime** | Time at which this Runtime Environment was created. | 
**creator_id** | **str** | ID of the User who created this Runtime Environment. | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


