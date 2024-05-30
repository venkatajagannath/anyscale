# ProductionJobConfig

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entrypoint** | **str** | A script that will be run to start your job. This command will be run in the root directory of the specified runtime env. Eg. &#39;python script.py&#39; | 
**runtime_env** | [**RayRuntimeEnvConfig**](RayRuntimeEnvConfig.md) | A ray runtime env json. Your entrypoint will be run in the environment specified by this runtime env. | [optional] 
**build_id** | **str** | The id of the cluster env build. This id will determine the docker image your job is run on. | 
**compute_config_id** | **str** | The id of the compute configuration that you want to use. This id will specify the resources required for your job | 
**compute_config** | [**ClusterComputeConfig**](ClusterComputeConfig.md) | One-off compute that the cluster will use. | [optional] 
**max_retries** | **int** | The number of retries this job will attempt on failure. Set to None to set infinite retries | [optional] [default to 5]
**runtime_env_config** | [**RayRuntimeEnvConfig**](RayRuntimeEnvConfig.md) | DEPRECATED: Use runtime_env | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


