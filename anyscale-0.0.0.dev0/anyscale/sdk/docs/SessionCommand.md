# SessionCommand

Model used to create and execute a command on a Session.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **str** | ID of the Session to execute this command on. | 
**shell_command** | **str** | Shell command string that will be executed. | 
**id** | **str** | Server assigned unique identifier. | 
**type** | [**SessionCommandTypes**](SessionCommandTypes.md) | Where this command was executed | [optional] 
**created_at** | **datetime** | Timestamp of when this command was created. | 
**finished_at** | **datetime** |          Timestamp of when this command completed its execution.         This value will be absent if the command is still running.          | [optional] 
**status_code** | **int** |          Exit status of this command.         This value will be absent if the command is still running.          | [optional] 
**killed_at** | **datetime** |          Timestamp of when this command was killed.         This value will be absent if the command is still running or completed its execution normally.          | [optional] 
**web_terminal_tab_id** | **str** |          The id for the web terminal tab in which this         command was executed.          | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


