# DecoratedServeDeployment

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Server assigned unique identifier. | 
**status** | [**DeploymentStatus**](DeploymentStatus.md) | Status of the deployment | 
**name** | **str** | Name of this deployment. | 
**cluster_id** | **str** | ID of the Anyscale Cluster this Deployment is on. | 
**job_id** | **str** | ID of the Anyscale Job that created this Deployment | [optional] 
**creator_id** | **str** | ID of the User who created this Deployment | [optional] 
**namespace_id** | **str** | ID of the Namespace this Deployment is using. | [optional] 
**created_at** | **datetime** | Time at which this Deployment was created. | 
**finished_at** | **datetime** | Time at which this Deployment finished. If absent, this Deployment is still running. | [optional] 
**http_route** | **str** | HTTP route of this deployment | [optional] 
**grafana_dashboard_url** | **str** | URL of the grafana dashboard for this deployment. If absent, the dashboard has not been created | [optional] 
**class_name** | **str** | The class name of the deployment object. | [optional] 
**grafana_dashboard_state** | [**ServeDeploymentGrafanaDashboardStatus**](ServeDeploymentGrafanaDashboardStatus.md) | Status of the grafana dashboard. This is used to determine if we need to create a dashboard. | 
**version** | **str** | Version of this Deployment | 
**cluster** | [**MiniCluster**](MiniCluster.md) |  | 
**creator** | [**MiniUser**](MiniUser.md) |  | [optional] 
**namespace** | [**MiniNamespace**](MiniNamespace.md) |  | 
**num_actors** | **int** |  | 
**fast_api_docs_url** | **str** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


