# ClusterServicesUrls

URLs for additional services running in the Cluster. (ex/ Jupyter, Ray Dashboard).  This fields can only be populated after the Cluster has finished starting. An absent field indicates the service is not available.
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**webterminal_auth_url** | **str** | URL to authenticate with the webterminal | [optional] 
**metrics_dashboard_url** | **str** | URL for Grafana (metrics) dashboard in the running cluster state. | [optional] 
**persistent_metrics_url** | **str** | URL for the persistent Grafana (metrics) dashboard in the non-running cluster state. | [optional] 
**connect_url** | **str** | URL for Anyscale connect. | [optional] 
**jupyter_notebook_url** | **str** | URL for Jupyter Lab. | [optional] 
**ray_dashboard_url** | **str** | URL for Ray dashboard. | [optional] 
**service_proxy_url** | **str** | URL for web services proxy (e.g. jupyter, tensorboard, etc). | [optional] 
**user_service_url** | **str** | URL to access user services (e.g. Ray Serve) | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


