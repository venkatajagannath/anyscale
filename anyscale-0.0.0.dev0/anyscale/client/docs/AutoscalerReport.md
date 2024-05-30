# AutoscalerReport

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active_nodes** | **dict(str, int)** | A dictionary of active nodes. The key is the node type and the value is the number of nodes of that type that are active. | [optional] 
**pending_nodes** | **list[list[str]]** | A list of tuples where the first item is the ip address, the second item is the node type, and the third item is the status. | [optional] [default to []]
**pending_launches** | **dict(str, int)** | A dictionary of nodes pending to launch. The key is the node type and the value is the number of nodes of that type pending launch. | [optional] 
**failed_nodes** | **list[list[str]]** | A list of tuples where the first item is the ip address and the second item is the node type. | [optional] [default to []]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


