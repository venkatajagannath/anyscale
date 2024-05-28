# TerminateSessionOptions

Optional values to set when terminating a Session.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workers_only** | **bool** | Only destroy the workers when terminating. | [optional] [default to False]
**keep_min_workers** | **bool** | Retain the minimal amount of workers specified in the config when terminating. | [optional] [default to False]
**delete** | **bool** | Delete the session after terminating. | [optional] [default to False]
**take_snapshot** | **bool** | Takes a snapshot to preserve the state of the session before terminating. The state will be restored the next time the session is started. | [optional] [default to True]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


