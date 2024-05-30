# Resources

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cpu** | **int** | Number of CPUs in this node type. If left blank, Ray may automatically detect it for you; see https://docs.ray.io/en/master/cluster/config.html#cluster-configuration-resources-type for more. | [optional] 
**gpu** | **int** | Number of GPUs in this node type. If left blank, Ray may automatically detect it for you; see https://docs.ray.io/en/master/cluster/config.html#cluster-configuration-resources-type for more. | [optional] 
**memory** | **int** | Amount of memory to allocate to the Python worker. If left blank, Ray will choose an appropriate amount based on available resources; see https://docs.ray.io/en/master/cluster/config.html#cluster-configuration-resources-type for more. | [optional] 
**object_store_memory** | **int** | The amount of memory in bytes allocated for the Ray object store on this node. If left blank, Ray will choose an appropriate amount; see https://docs.ray.io/en/master/cluster/config.html#cluster-configuration-resources-type for more. | [optional] 
**custom_resources** | **dict(str, int)** | Declare custom resources for this node to be used by Ray autoscaler. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


