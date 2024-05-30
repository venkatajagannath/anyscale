# anyscale_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apply_service**](DefaultApi.md#apply_service) | **PUT** /services/ | Apply Service
[**archive_cluster**](DefaultApi.md#archive_cluster) | **POST** /clusters/{cluster_id}/archive | Archive Cluster
[**cancel_build**](DefaultApi.md#cancel_build) | **POST** /builds/{build_id}/cancel | Cancel Build
[**cancel_cluster_environment_build**](DefaultApi.md#cancel_cluster_environment_build) | **POST** /cluster_environment_builds/{cluster_environment_build_id}/cancel | Cancel Cluster Environment Build
[**create_app_config**](DefaultApi.md#create_app_config) | **POST** /app_configs/ | Create App Config
[**create_build**](DefaultApi.md#create_build) | **POST** /builds/ | Create Build
[**create_byod_cluster_environment**](DefaultApi.md#create_byod_cluster_environment) | **POST** /cluster_environments/byod | Create Byod Cluster Environment
[**create_cloud**](DefaultApi.md#create_cloud) | **POST** /clouds/ | Create Cloud
[**create_cluster**](DefaultApi.md#create_cluster) | **POST** /clusters/ | Create Cluster
[**create_cluster_compute**](DefaultApi.md#create_cluster_compute) | **POST** /cluster_computes/ | Create Cluster Compute
[**create_cluster_environment**](DefaultApi.md#create_cluster_environment) | **POST** /cluster_environments/ | Create Cluster Environment
[**create_cluster_environment_build**](DefaultApi.md#create_cluster_environment_build) | **POST** /cluster_environment_builds/ | Create Cluster Environment Build
[**create_compute_template**](DefaultApi.md#create_compute_template) | **POST** /compute_templates/ | Create Compute Template
[**create_job**](DefaultApi.md#create_job) | **POST** /production_jobs/ | Create Job
[**create_project**](DefaultApi.md#create_project) | **POST** /projects/ | Create Project
[**create_service**](DefaultApi.md#create_service) | **POST** /services/ | Create Service
[**create_session**](DefaultApi.md#create_session) | **POST** /sessions/ | Create Session
[**create_session_command**](DefaultApi.md#create_session_command) | **POST** /session_commands/ | Create Session Command
[**delete_app_configs**](DefaultApi.md#delete_app_configs) | **DELETE** /app_configs/{app_config_id} | Delete App Configs
[**delete_build**](DefaultApi.md#delete_build) | **DELETE** /builds/{build_id} | Delete Build
[**delete_cloud**](DefaultApi.md#delete_cloud) | **DELETE** /clouds/{cloud_id} | Delete Cloud
[**delete_cluster**](DefaultApi.md#delete_cluster) | **DELETE** /clusters/{cluster_id} | Delete Cluster
[**delete_cluster_compute**](DefaultApi.md#delete_cluster_compute) | **DELETE** /cluster_computes/{cluster_compute_id} | Delete Cluster Compute
[**delete_cluster_environment**](DefaultApi.md#delete_cluster_environment) | **DELETE** /cluster_environments/{cluster_config_id} | Delete Cluster Environment
[**delete_cluster_environment_build**](DefaultApi.md#delete_cluster_environment_build) | **DELETE** /cluster_environment_builds/{cluster_environment_build_id} | Delete Cluster Environment Build
[**delete_compute_template**](DefaultApi.md#delete_compute_template) | **DELETE** /compute_templates/{template_id} | Delete Compute Template
[**delete_project**](DefaultApi.md#delete_project) | **DELETE** /projects/{project_id} | Delete Project
[**delete_session**](DefaultApi.md#delete_session) | **DELETE** /sessions/{session_id} | Delete Session
[**get_actor**](DefaultApi.md#get_actor) | **GET** /actors/{actor_id} | Get Actor
[**get_actor_logs**](DefaultApi.md#get_actor_logs) | **GET** /actors/{actor_id}/logs | Get Actor Logs
[**get_app_config**](DefaultApi.md#get_app_config) | **GET** /app_configs/{app_config_id} | Get App Config
[**get_build**](DefaultApi.md#get_build) | **GET** /builds/{build_id} | Get Build
[**get_build_logs**](DefaultApi.md#get_build_logs) | **GET** /builds/{build_id}/logs | Get Build Logs
[**get_cloud**](DefaultApi.md#get_cloud) | **GET** /clouds/{cloud_id} | Get Cloud
[**get_cluster**](DefaultApi.md#get_cluster) | **GET** /clusters/{cluster_id} | Get Cluster
[**get_cluster_compute**](DefaultApi.md#get_cluster_compute) | **GET** /cluster_computes/{cluster_compute_id} | Get Cluster Compute
[**get_cluster_environment**](DefaultApi.md#get_cluster_environment) | **GET** /cluster_environments/{cluster_environment_id} | Get Cluster Environment
[**get_cluster_environment_build**](DefaultApi.md#get_cluster_environment_build) | **GET** /cluster_environment_builds/{cluster_environment_build_id} | Get Cluster Environment Build
[**get_cluster_environment_build_logs**](DefaultApi.md#get_cluster_environment_build_logs) | **GET** /cluster_environment_builds/{cluster_environment_build_id}/logs | Get Cluster Environment Build Logs
[**get_cluster_environment_build_operation**](DefaultApi.md#get_cluster_environment_build_operation) | **GET** /cluster_environment_build_operations/{cluster_environment_build_operation_id} | Get Cluster Environment Build Operation
[**get_cluster_operation**](DefaultApi.md#get_cluster_operation) | **GET** /cluster_operations/{cluster_operation_id} | Get Cluster Operation
[**get_compute_template**](DefaultApi.md#get_compute_template) | **GET** /compute_templates/{template_id} | Get Compute Template
[**get_default_cloud**](DefaultApi.md#get_default_cloud) | **GET** /clouds/default | Get Default Cloud
[**get_default_cluster_compute**](DefaultApi.md#get_default_cluster_compute) | **GET** /cluster_computes/default | Get Default Cluster Compute
[**get_default_cluster_environment_build**](DefaultApi.md#get_default_cluster_environment_build) | **GET** /cluster_environment_builds/default | Get Default Cluster Environment Build
[**get_default_compute_config**](DefaultApi.md#get_default_compute_config) | **GET** /compute_templates/default/{cloud_id} | Get Default Compute Config
[**get_default_project**](DefaultApi.md#get_default_project) | **GET** /projects/default_project | Get Default Project
[**get_job**](DefaultApi.md#get_job) | **GET** /jobs/{job_id} | Get Job
[**get_job_logs**](DefaultApi.md#get_job_logs) | **GET** /jobs/{job_id}/logs | Get Job Logs
[**get_namespace**](DefaultApi.md#get_namespace) | **GET** /namespaces/{namespace_id} | Get Namespace
[**get_organization_temporary_object_storage_credentials**](DefaultApi.md#get_organization_temporary_object_storage_credentials) | **GET** /organizations/{organization_id}/{region}/temporary_object_storage_config | Get Organization Temporary Object Storage Credentials
[**get_production_job**](DefaultApi.md#get_production_job) | **GET** /production_jobs/{production_job_id} | Get Production Job
[**get_project**](DefaultApi.md#get_project) | **GET** /projects/{project_id} | Get Project
[**get_runtime_environment**](DefaultApi.md#get_runtime_environment) | **GET** /runtime_environments/{runtime_environment_id} | Get Runtime Environment
[**get_service**](DefaultApi.md#get_service) | **GET** /services/{service_id} | Get Service
[**get_session**](DefaultApi.md#get_session) | **GET** /sessions/{session_id} | Get Session
[**get_session_command**](DefaultApi.md#get_session_command) | **GET** /session_commands/{session_command_id} | Get Session Command
[**get_session_event_log**](DefaultApi.md#get_session_event_log) | **GET** /session_events/ | Get Session Event Log
[**get_session_for_job**](DefaultApi.md#get_session_for_job) | **GET** /production_jobs/{production_job_id}/session | Get Session For Job
[**get_session_operation**](DefaultApi.md#get_session_operation) | **GET** /session_operations/{session_operation_id} | Get Session Operation
[**kill_session_command**](DefaultApi.md#kill_session_command) | **POST** /session_commands/{session_command_id}/kill | Kill Session Command
[**list_app_configs**](DefaultApi.md#list_app_configs) | **GET** /app_configs/ | List App Configs
[**list_builds**](DefaultApi.md#list_builds) | **GET** /builds/ | List Builds
[**list_cluster_environment_builds**](DefaultApi.md#list_cluster_environment_builds) | **GET** /cluster_environment_builds/ | List Cluster Environment Builds
[**list_production_jobs**](DefaultApi.md#list_production_jobs) | **GET** /production_jobs/ | List Production Jobs
[**list_projects**](DefaultApi.md#list_projects) | **GET** /projects/ | List Projects
[**list_services**](DefaultApi.md#list_services) | **GET** /services/ | List Services
[**list_session_commands**](DefaultApi.md#list_session_commands) | **GET** /session_commands/ | List Session Commands
[**list_sessions**](DefaultApi.md#list_sessions) | **GET** /sessions/ | List Sessions
[**partial_update_organization**](DefaultApi.md#partial_update_organization) | **PUT** /organizations/{organization_id} | Partial Update Organization
[**search_actors**](DefaultApi.md#search_actors) | **POST** /actors/search | Search Actors
[**search_clouds**](DefaultApi.md#search_clouds) | **POST** /clouds/search | Search Clouds
[**search_cluster_computes**](DefaultApi.md#search_cluster_computes) | **POST** /cluster_computes/search | Search Cluster Computes
[**search_cluster_environments**](DefaultApi.md#search_cluster_environments) | **POST** /cluster_environments/search | Search Cluster Environments
[**search_clusters**](DefaultApi.md#search_clusters) | **POST** /clusters/search | Search Clusters
[**search_compute_templates**](DefaultApi.md#search_compute_templates) | **POST** /compute_templates/search | Search Compute Templates
[**search_jobs**](DefaultApi.md#search_jobs) | **POST** /jobs/search | Search Jobs
[**search_projects**](DefaultApi.md#search_projects) | **POST** /projects/search | Search Projects
[**search_sessions**](DefaultApi.md#search_sessions) | **POST** /sessions/{project_id}/search | Search Sessions
[**start_cluster**](DefaultApi.md#start_cluster) | **POST** /clusters/{cluster_id}/start | Start Cluster
[**start_session**](DefaultApi.md#start_session) | **POST** /sessions/{session_id}/start | Start Session
[**terminate_cluster**](DefaultApi.md#terminate_cluster) | **POST** /clusters/{cluster_id}/terminate | Terminate Cluster
[**terminate_job**](DefaultApi.md#terminate_job) | **POST** /production_jobs/{production_job_id}/terminate | Terminate Job
[**terminate_service**](DefaultApi.md#terminate_service) | **POST** /services/{service_id}/terminate | Terminate Service
[**terminate_session**](DefaultApi.md#terminate_session) | **POST** /sessions/{session_id}/terminate | Terminate Session
[**update_app_configs**](DefaultApi.md#update_app_configs) | **PUT** /app_configs/{app_config_id} | Update App Configs
[**update_cloud**](DefaultApi.md#update_cloud) | **PUT** /clouds/{cloud_id} | Update Cloud
[**update_cluster**](DefaultApi.md#update_cluster) | **PUT** /clusters/{cluster_id} | Update Cluster
[**update_compute_template**](DefaultApi.md#update_compute_template) | **PUT** /compute_templates/{template_id} | Update Compute Template
[**update_project**](DefaultApi.md#update_project) | **PUT** /projects/{project_id} | Update Project
[**update_session**](DefaultApi.md#update_session) | **PUT** /sessions/{session_id} | Update Session
[**upsert_sso_config**](DefaultApi.md#upsert_sso_config) | **POST** /sso_configs/ | Upsert Sso Config
[**upsert_test_sso_config**](DefaultApi.md#upsert_test_sso_config) | **POST** /sso_configs/test | Upsert Test Sso Config


# **apply_service**
> ProductionserviceResponse apply_service(create_production_service)

Apply Service

PUT a service. This endpoint will create a service with the given name if it doesn't exist, and will otherwise update the service.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_production_service = anyscale_client.CreateProductionService() # CreateProductionService | 

    try:
        # Apply Service
        api_response = api_instance.apply_service(create_production_service)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->apply_service: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_production_service** | [**CreateProductionService**](CreateProductionService.md)|  | 

### Return type

[**ProductionserviceResponse**](ProductionserviceResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **archive_cluster**
> archive_cluster(cluster_id)

Archive Cluster

Archives the cluster. It is a no-op if the cluster is already archived.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_id = 'cluster_id_example' # str | 

    try:
        # Archive Cluster
        api_instance.archive_cluster(cluster_id)
    except ApiException as e:
        print("Exception when calling DefaultApi->archive_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancel_build**
> CreateResponse cancel_build(build_id)

Cancel Build

DEPRECATED: Use Cluster Environment Builds API instead. Cancels a Build that is still in progress. This is a long running operation.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    build_id = 'build_id_example' # str | 

    try:
        # Cancel Build
        api_response = api_instance.cancel_build(build_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->cancel_build: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **build_id** | **str**|  | 

### Return type

[**CreateResponse**](CreateResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancel_cluster_environment_build**
> ClusterenvironmentbuildoperationResponse cancel_cluster_environment_build(cluster_environment_build_id)

Cancel Cluster Environment Build

Cancels a Cluster Environment Build that is still in progress. This is a long running operation.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_environment_build_id = 'cluster_environment_build_id_example' # str | ID of the Cluster Environment Build to cancel.

    try:
        # Cancel Cluster Environment Build
        api_response = api_instance.cancel_cluster_environment_build(cluster_environment_build_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->cancel_cluster_environment_build: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_environment_build_id** | **str**| ID of the Cluster Environment Build to cancel. | 

### Return type

[**ClusterenvironmentbuildoperationResponse**](ClusterenvironmentbuildoperationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_app_config**
> AppconfigResponse create_app_config(create_app_config)

Create App Config

DEPRECATED: Use Cluster Environments API instead. Creates an App Config.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_app_config = anyscale_client.CreateAppConfig() # CreateAppConfig | 

    try:
        # Create App Config
        api_response = api_instance.create_app_config(create_app_config)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_app_config: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_app_config** | [**CreateAppConfig**](CreateAppConfig.md)|  | 

### Return type

[**AppconfigResponse**](AppconfigResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_build**
> BuildResponse create_build(create_build)

Create Build

DEPRECATED: Use Cluster Environment Builds API instead. Creates and starts a Build. This is a long running operation.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_build = anyscale_client.CreateBuild() # CreateBuild | 

    try:
        # Create Build
        api_response = api_instance.create_build(create_build)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_build: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_build** | [**CreateBuild**](CreateBuild.md)|  | 

### Return type

[**BuildResponse**](BuildResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_byod_cluster_environment**
> ClusterenvironmentResponse create_byod_cluster_environment(create_byod_cluster_environment)

Create Byod Cluster Environment

Creates a BYOD Cluster Environment.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_byod_cluster_environment = anyscale_client.CreateBYODClusterEnvironment() # CreateBYODClusterEnvironment | 

    try:
        # Create Byod Cluster Environment
        api_response = api_instance.create_byod_cluster_environment(create_byod_cluster_environment)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_byod_cluster_environment: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_byod_cluster_environment** | [**CreateBYODClusterEnvironment**](CreateBYODClusterEnvironment.md)|  | 

### Return type

[**ClusterenvironmentResponse**](ClusterenvironmentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_cloud**
> CloudResponse create_cloud(create_cloud)

Create Cloud

Creates a Cloud.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_cloud = anyscale_client.CreateCloud() # CreateCloud | 

    try:
        # Create Cloud
        api_response = api_instance.create_cloud(create_cloud)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_cloud: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_cloud** | [**CreateCloud**](CreateCloud.md)|  | 

### Return type

[**CloudResponse**](CloudResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_cluster**
> ClusterResponse create_cluster(create_cluster)

Create Cluster

Creates a Cluster.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_cluster = anyscale_client.CreateCluster() # CreateCluster | 

    try:
        # Create Cluster
        api_response = api_instance.create_cluster(create_cluster)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_cluster** | [**CreateCluster**](CreateCluster.md)|  | 

### Return type

[**ClusterResponse**](ClusterResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_cluster_compute**
> ClustercomputeResponse create_cluster_compute(create_cluster_compute)

Create Cluster Compute

Creates a Cluster Compute.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_cluster_compute = anyscale_client.CreateClusterCompute() # CreateClusterCompute | 

    try:
        # Create Cluster Compute
        api_response = api_instance.create_cluster_compute(create_cluster_compute)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_cluster_compute: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_cluster_compute** | [**CreateClusterCompute**](CreateClusterCompute.md)|  | 

### Return type

[**ClustercomputeResponse**](ClustercomputeResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_cluster_environment**
> ClusterenvironmentResponse create_cluster_environment(create_cluster_environment)

Create Cluster Environment

Creates a Cluster Environment.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_cluster_environment = anyscale_client.CreateClusterEnvironment() # CreateClusterEnvironment | 

    try:
        # Create Cluster Environment
        api_response = api_instance.create_cluster_environment(create_cluster_environment)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_cluster_environment: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_cluster_environment** | [**CreateClusterEnvironment**](CreateClusterEnvironment.md)|  | 

### Return type

[**ClusterenvironmentResponse**](ClusterenvironmentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_cluster_environment_build**
> ClusterenvironmentbuildoperationResponse create_cluster_environment_build(create_cluster_environment_build)

Create Cluster Environment Build

Creates and starts a Cluster Environment Build. This is a long running operation.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_cluster_environment_build = anyscale_client.CreateClusterEnvironmentBuild() # CreateClusterEnvironmentBuild | 

    try:
        # Create Cluster Environment Build
        api_response = api_instance.create_cluster_environment_build(create_cluster_environment_build)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_cluster_environment_build: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_cluster_environment_build** | [**CreateClusterEnvironmentBuild**](CreateClusterEnvironmentBuild.md)|  | 

### Return type

[**ClusterenvironmentbuildoperationResponse**](ClusterenvironmentbuildoperationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_compute_template**
> ComputetemplateResponse create_compute_template(create_compute_template)

Create Compute Template

DEPRECATED: Use Cluster Computes API instead. Creates a compute template.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_compute_template = anyscale_client.CreateComputeTemplate() # CreateComputeTemplate | 

    try:
        # Create Compute Template
        api_response = api_instance.create_compute_template(create_compute_template)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_compute_template: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_compute_template** | [**CreateComputeTemplate**](CreateComputeTemplate.md)|  | 

### Return type

[**ComputetemplateResponse**](ComputetemplateResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_job**
> ProductionjobResponse create_job(create_production_job)

Create Job

Create an Production Job

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_production_job = anyscale_client.CreateProductionJob() # CreateProductionJob | 

    try:
        # Create Job
        api_response = api_instance.create_job(create_production_job)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_production_job** | [**CreateProductionJob**](CreateProductionJob.md)|  | 

### Return type

[**ProductionjobResponse**](ProductionjobResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_project**
> ProjectResponse create_project(create_project)

Create Project

Creates a Project.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_project = anyscale_client.CreateProject() # CreateProject | 

    try:
        # Create Project
        api_response = api_instance.create_project(create_project)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_project: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_project** | [**CreateProject**](CreateProject.md)|  | 

### Return type

[**ProjectResponse**](ProjectResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_service**
> ProductionserviceResponse create_service(create_production_service)

Create Service

Create a service

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_production_service = anyscale_client.CreateProductionService() # CreateProductionService | 

    try:
        # Create Service
        api_response = api_instance.create_service(create_production_service)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_service: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_production_service** | [**CreateProductionService**](CreateProductionService.md)|  | 

### Return type

[**ProductionserviceResponse**](ProductionserviceResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_session**
> SessionResponse create_session(create_session)

Create Session

DEPRECATED: Use Clusters API instead. Creates a Session.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_session = anyscale_client.CreateSession() # CreateSession | 

    try:
        # Create Session
        api_response = api_instance.create_session(create_session)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_session** | [**CreateSession**](CreateSession.md)|  | 

### Return type

[**SessionResponse**](SessionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_session_command**
> SessioncommandResponse create_session_command(create_session_command)

Create Session Command

Creates and executes a shell command on a session.This API makes no assumption about the details of the shell command.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_session_command = anyscale_client.CreateSessionCommand() # CreateSessionCommand | 

    try:
        # Create Session Command
        api_response = api_instance.create_session_command(create_session_command)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->create_session_command: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_session_command** | [**CreateSessionCommand**](CreateSessionCommand.md)|  | 

### Return type

[**SessioncommandResponse**](SessioncommandResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_app_configs**
> delete_app_configs(app_config_id)

Delete App Configs

DEPRECATED: Use Cluster Environments API instead. Deletes an App Config.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    app_config_id = 'app_config_id_example' # str | 

    try:
        # Delete App Configs
        api_instance.delete_app_configs(app_config_id)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_app_configs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_config_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_build**
> delete_build(build_id)

Delete Build

DEPRECATED: Use Cluster Environment Builds API instead. Deletes a Build.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    build_id = 'build_id_example' # str | 

    try:
        # Delete Build
        api_instance.delete_build(build_id)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_build: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **build_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_cloud**
> delete_cloud(cloud_id)

Delete Cloud

Deletes a Cloud. Will delete all clusters that are using this cloud. If any of those clusters are not terminated, this call will fail.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cloud_id = 'cloud_id_example' # str | ID of the Cloud to delete.

    try:
        # Delete Cloud
        api_instance.delete_cloud(cloud_id)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_cloud: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cloud_id** | **str**| ID of the Cloud to delete. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_cluster**
> delete_cluster(cluster_id)

Delete Cluster

Deletes a Cluster.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_id = 'cluster_id_example' # str | ID of the Cluster to delete.

    try:
        # Delete Cluster
        api_instance.delete_cluster(cluster_id)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_id** | **str**| ID of the Cluster to delete. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_cluster_compute**
> delete_cluster_compute(cluster_compute_id)

Delete Cluster Compute

Deletes a Cluster Compute.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_compute_id = 'cluster_compute_id_example' # str | ID of the Cluster Compute to delete.

    try:
        # Delete Cluster Compute
        api_instance.delete_cluster_compute(cluster_compute_id)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_cluster_compute: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_compute_id** | **str**| ID of the Cluster Compute to delete. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_cluster_environment**
> delete_cluster_environment(cluster_config_id)

Delete Cluster Environment

Deletes a Cluster Environment.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_config_id = 'cluster_config_id_example' # str | ID of the Cluster Environment to delete.

    try:
        # Delete Cluster Environment
        api_instance.delete_cluster_environment(cluster_config_id)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_cluster_environment: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_config_id** | **str**| ID of the Cluster Environment to delete. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_cluster_environment_build**
> delete_cluster_environment_build(cluster_environment_build_id)

Delete Cluster Environment Build

Deletes a Cluster Environment Build.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_environment_build_id = 'cluster_environment_build_id_example' # str | ID of the Cluster Environment Build to delete.

    try:
        # Delete Cluster Environment Build
        api_instance.delete_cluster_environment_build(cluster_environment_build_id)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_cluster_environment_build: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_environment_build_id** | **str**| ID of the Cluster Environment Build to delete. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_compute_template**
> delete_compute_template(template_id)

Delete Compute Template

DEPRECATED: Use Cluster Computes API instead. Deletes a compute template.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    template_id = 'template_id_example' # str | 

    try:
        # Delete Compute Template
        api_instance.delete_compute_template(template_id)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_compute_template: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **template_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_project**
> delete_project(project_id)

Delete Project

Deletes a Project.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    project_id = 'project_id_example' # str | ID of the Project to delete.

    try:
        # Delete Project
        api_instance.delete_project(project_id)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_project: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**| ID of the Project to delete. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_session**
> delete_session(session_id)

Delete Session

DEPRECATED: Use Clusters API instead. Deletes a session.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    session_id = 'session_id_example' # str | 

    try:
        # Delete Session
        api_instance.delete_session(session_id)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_actor**
> ActorResponse get_actor(actor_id)

Get Actor

Gets an Actor by ID.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    actor_id = 'actor_id_example' # str | ID of the Actor to retrieve.

    try:
        # Get Actor
        api_response = api_instance.get_actor(actor_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_actor: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **actor_id** | **str**| ID of the Actor to retrieve. | 

### Return type

[**ActorResponse**](ActorResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_actor_logs**
> ActorlogsResponse get_actor_logs(actor_id)

Get Actor Logs

Gets an Actor's logs.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    actor_id = 'actor_id_example' # str | ID of the Actor to get logs for.

    try:
        # Get Actor Logs
        api_response = api_instance.get_actor_logs(actor_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_actor_logs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **actor_id** | **str**| ID of the Actor to get logs for. | 

### Return type

[**ActorlogsResponse**](ActorlogsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_app_config**
> AppconfigResponse get_app_config(app_config_id)

Get App Config

DEPRECATED: Use Cluster Environments API instead. Retrieves an App Config.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    app_config_id = 'app_config_id_example' # str | 

    try:
        # Get App Config
        api_response = api_instance.get_app_config(app_config_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_app_config: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_config_id** | **str**|  | 

### Return type

[**AppconfigResponse**](AppconfigResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_build**
> BuildResponse get_build(build_id)

Get Build

DEPRECATED: Use Cluster Environment Builds API instead. Retrieves a Build.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    build_id = 'build_id_example' # str | 

    try:
        # Get Build
        api_response = api_instance.get_build(build_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_build: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **build_id** | **str**|  | 

### Return type

[**BuildResponse**](BuildResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_build_logs**
> BuildlogresponseResponse get_build_logs(build_id)

Get Build Logs

DEPRECATED: Use Cluster Environment Builds API instead. Retrieves logs for a Build.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    build_id = 'build_id_example' # str | 

    try:
        # Get Build Logs
        api_response = api_instance.get_build_logs(build_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_build_logs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **build_id** | **str**|  | 

### Return type

[**BuildlogresponseResponse**](BuildlogresponseResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cloud**
> CloudResponse get_cloud(cloud_id)

Get Cloud

Retrieves a Cloud.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cloud_id = 'cloud_id_example' # str | ID of the Cloud to retrieve.

    try:
        # Get Cloud
        api_response = api_instance.get_cloud(cloud_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_cloud: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cloud_id** | **str**| ID of the Cloud to retrieve. | 

### Return type

[**CloudResponse**](CloudResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster**
> ClusterResponse get_cluster(cluster_id)

Get Cluster

Retrieves a Cluster.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_id = 'cluster_id_example' # str | ID of the Cluster to retreive.

    try:
        # Get Cluster
        api_response = api_instance.get_cluster(cluster_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_id** | **str**| ID of the Cluster to retreive. | 

### Return type

[**ClusterResponse**](ClusterResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster_compute**
> ClustercomputeResponse get_cluster_compute(cluster_compute_id)

Get Cluster Compute

Retrieves a Cluster Compute.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_compute_id = 'cluster_compute_id_example' # str | ID of the Cluster Compute to retrieve.

    try:
        # Get Cluster Compute
        api_response = api_instance.get_cluster_compute(cluster_compute_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_cluster_compute: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_compute_id** | **str**| ID of the Cluster Compute to retrieve. | 

### Return type

[**ClustercomputeResponse**](ClustercomputeResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster_environment**
> ClusterenvironmentResponse get_cluster_environment(cluster_environment_id)

Get Cluster Environment

Retrieves a Cluster Environment.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_environment_id = 'cluster_environment_id_example' # str | ID of the Cluster Environment to retrieve.

    try:
        # Get Cluster Environment
        api_response = api_instance.get_cluster_environment(cluster_environment_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_cluster_environment: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_environment_id** | **str**| ID of the Cluster Environment to retrieve. | 

### Return type

[**ClusterenvironmentResponse**](ClusterenvironmentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster_environment_build**
> ClusterenvironmentbuildResponse get_cluster_environment_build(cluster_environment_build_id)

Get Cluster Environment Build

Retrieves a Cluster Environment Build.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_environment_build_id = 'cluster_environment_build_id_example' # str | ID of the Cluster Environment Build to retrieve.

    try:
        # Get Cluster Environment Build
        api_response = api_instance.get_cluster_environment_build(cluster_environment_build_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_cluster_environment_build: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_environment_build_id** | **str**| ID of the Cluster Environment Build to retrieve. | 

### Return type

[**ClusterenvironmentbuildResponse**](ClusterenvironmentbuildResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster_environment_build_logs**
> ClusterenvironmentbuildlogresponseResponse get_cluster_environment_build_logs(cluster_environment_build_id)

Get Cluster Environment Build Logs

Retrieves logs for a Cluster Environment Build.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_environment_build_id = 'cluster_environment_build_id_example' # str | ID of the Cluster Environment Build to retrieve logs for.

    try:
        # Get Cluster Environment Build Logs
        api_response = api_instance.get_cluster_environment_build_logs(cluster_environment_build_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_cluster_environment_build_logs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_environment_build_id** | **str**| ID of the Cluster Environment Build to retrieve logs for. | 

### Return type

[**ClusterenvironmentbuildlogresponseResponse**](ClusterenvironmentbuildlogresponseResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster_environment_build_operation**
> ClusterenvironmentbuildoperationResponse get_cluster_environment_build_operation(cluster_environment_build_operation_id)

Get Cluster Environment Build Operation

Retrieves a Cluster Environment Build Operation.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_environment_build_operation_id = 'cluster_environment_build_operation_id_example' # str | ID of the Cluster Environment Build Operation to retrieve.

    try:
        # Get Cluster Environment Build Operation
        api_response = api_instance.get_cluster_environment_build_operation(cluster_environment_build_operation_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_cluster_environment_build_operation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_environment_build_operation_id** | **str**| ID of the Cluster Environment Build Operation to retrieve. | 

### Return type

[**ClusterenvironmentbuildoperationResponse**](ClusterenvironmentbuildoperationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cluster_operation**
> ClusteroperationResponse get_cluster_operation(cluster_operation_id)

Get Cluster Operation

Retrieves a Cluster Operation.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_operation_id = 'cluster_operation_id_example' # str | ID of the Cluster Operation to retrieve.

    try:
        # Get Cluster Operation
        api_response = api_instance.get_cluster_operation(cluster_operation_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_cluster_operation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_operation_id** | **str**| ID of the Cluster Operation to retrieve. | 

### Return type

[**ClusteroperationResponse**](ClusteroperationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_compute_template**
> ComputetemplateResponse get_compute_template(template_id)

Get Compute Template

DEPRECATED: Use Cluster Computes API instead. Retrieves a compute template.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    template_id = 'template_id_example' # str | 

    try:
        # Get Compute Template
        api_response = api_instance.get_compute_template(template_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_compute_template: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **template_id** | **str**|  | 

### Return type

[**ComputetemplateResponse**](ComputetemplateResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_default_cloud**
> CloudResponse get_default_cloud()

Get Default Cloud

Retrieves the default cloud for the logged in user. First prefers the default cloud set by the user's org, then the last used cloud.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    
    try:
        # Get Default Cloud
        api_response = api_instance.get_default_cloud()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_default_cloud: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**CloudResponse**](CloudResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_default_cluster_compute**
> ClustercomputeResponse get_default_cluster_compute(cloud_id=cloud_id)

Get Default Cluster Compute

Returns a default cluster compute that can be used with a given cloud.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cloud_id = 'cloud_id_example' # str | The cloud id whose default cluster compute you want to fetch. If None, will use the default cloud. (optional)

    try:
        # Get Default Cluster Compute
        api_response = api_instance.get_default_cluster_compute(cloud_id=cloud_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_default_cluster_compute: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cloud_id** | **str**| The cloud id whose default cluster compute you want to fetch. If None, will use the default cloud. | [optional] 

### Return type

[**ClustercomputeResponse**](ClustercomputeResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_default_cluster_environment_build**
> ClusterenvironmentbuildResponse get_default_cluster_environment_build(python_version, ray_version)

Get Default Cluster Environment Build

Retrieves a default cluster environment with the preferred attributes.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    python_version = anyscale_client.PythonVersion() # PythonVersion | Python version for the cluster environment
ray_version = 'ray_version_example' # str | Ray version to use for this cluster environment. Should match a version string found in the ray version history on pypi. See here for full list: https://pypi.org/project/ray/#history

    try:
        # Get Default Cluster Environment Build
        api_response = api_instance.get_default_cluster_environment_build(python_version, ray_version)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_default_cluster_environment_build: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **python_version** | [**PythonVersion**](.md)| Python version for the cluster environment | 
 **ray_version** | **str**| Ray version to use for this cluster environment. Should match a version string found in the ray version history on pypi. See here for full list: https://pypi.org/project/ray/#history | 

### Return type

[**ClusterenvironmentbuildResponse**](ClusterenvironmentbuildResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_default_compute_config**
> ComputetemplateconfigResponse get_default_compute_config(cloud_id)

Get Default Compute Config

DEPRECATED: Use Cluster Computes API instead. Return a default compute configuration for this cloud.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cloud_id = 'cloud_id_example' # str | 

    try:
        # Get Default Compute Config
        api_response = api_instance.get_default_compute_config(cloud_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_default_compute_config: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cloud_id** | **str**|  | 

### Return type

[**ComputetemplateconfigResponse**](ComputetemplateconfigResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_default_project**
> ProjectResponse get_default_project()

Get Default Project

Retrieves the default project.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    
    try:
        # Get Default Project
        api_response = api_instance.get_default_project()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_default_project: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ProjectResponse**](ProjectResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job**
> JobResponse get_job(job_id)

Get Job

Retrieves a Job by ID.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    job_id = 'job_id_example' # str | ID of the Job to retrieve.

    try:
        # Get Job
        api_response = api_instance.get_job(job_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| ID of the Job to retrieve. | 

### Return type

[**JobResponse**](JobResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_logs**
> JobslogsResponse get_job_logs(job_id)

Get Job Logs

Retrieves a Job's logs.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    job_id = 'job_id_example' # str | ID of the Job to fetch logs for.

    try:
        # Get Job Logs
        api_response = api_instance.get_job_logs(job_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_job_logs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| ID of the Job to fetch logs for. | 

### Return type

[**JobslogsResponse**](JobslogsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_namespace**
> NamespaceResponse get_namespace(namespace_id)

Get Namespace

Retrieves a Namespace.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    namespace_id = 'namespace_id_example' # str | ID of the Namespace to retrieve.

    try:
        # Get Namespace
        api_response = api_instance.get_namespace(namespace_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_namespace: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace_id** | **str**| ID of the Namespace to retrieve. | 

### Return type

[**NamespaceResponse**](NamespaceResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_organization_temporary_object_storage_credentials**
> ObjectstorageconfigResponse get_organization_temporary_object_storage_credentials(organization_id, region)

Get Organization Temporary Object Storage Credentials

Retrieves temporary object storage config and credentials scoped to an organization and region.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    organization_id = 'organization_id_example' # str | 
region = 'region_example' # str | 

    try:
        # Get Organization Temporary Object Storage Credentials
        api_response = api_instance.get_organization_temporary_object_storage_credentials(organization_id, region)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_organization_temporary_object_storage_credentials: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_id** | **str**|  | 
 **region** | **str**|  | 

### Return type

[**ObjectstorageconfigResponse**](ObjectstorageconfigResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_production_job**
> ProductionjobResponse get_production_job(production_job_id)

Get Production Job

Get an Production Job

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    production_job_id = 'production_job_id_example' # str | 

    try:
        # Get Production Job
        api_response = api_instance.get_production_job(production_job_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_production_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **production_job_id** | **str**|  | 

### Return type

[**ProductionjobResponse**](ProductionjobResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_project**
> ProjectResponse get_project(project_id)

Get Project

Retrieves a Project.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    project_id = 'project_id_example' # str | ID of the Project to retrieve.

    try:
        # Get Project
        api_response = api_instance.get_project(project_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_project: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**| ID of the Project to retrieve. | 

### Return type

[**ProjectResponse**](ProjectResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_runtime_environment**
> RuntimeenvironmentResponse get_runtime_environment(runtime_environment_id)

Get Runtime Environment

Retrieves a Runtime Environment.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    runtime_environment_id = 'runtime_environment_id_example' # str | ID of the Runtime Environment to retrieve.

    try:
        # Get Runtime Environment
        api_response = api_instance.get_runtime_environment(runtime_environment_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_runtime_environment: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **runtime_environment_id** | **str**| ID of the Runtime Environment to retrieve. | 

### Return type

[**RuntimeenvironmentResponse**](RuntimeenvironmentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_service**
> ProductionserviceResponse get_service(service_id)

Get Service

**EXPERIMENTAL FEATURE**: Get a Service

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    service_id = 'service_id_example' # str | 

    try:
        # Get Service
        api_response = api_instance.get_service(service_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_service: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_id** | **str**|  | 

### Return type

[**ProductionserviceResponse**](ProductionserviceResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session**
> SessionResponse get_session(session_id)

Get Session

DEPRECATED: Use Clusters API instead. Retrieves a Session.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    session_id = 'session_id_example' # str | 

    try:
        # Get Session
        api_response = api_instance.get_session(session_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 

### Return type

[**SessionResponse**](SessionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_command**
> SessioncommandResponse get_session_command(session_command_id)

Get Session Command

Retrieves a session command with ID.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    session_command_id = 'session_command_id_example' # str | ID of the Session Command to retrieve.

    try:
        # Get Session Command
        api_response = api_instance.get_session_command(session_command_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_session_command: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_command_id** | **str**| ID of the Session Command to retrieve. | 

### Return type

[**SessioncommandResponse**](SessioncommandResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_event_log**
> SessioneventListResponse get_session_event_log(session_id, before=before, after=after, event_types=event_types, log_level_types=log_level_types, paging_token=paging_token, count=count)

Get Session Event Log

Retrieves a session's event log.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    session_id = 'session_id_example' # str | ID of the Session to retrieve event logs for.
before = '2013-10-20T19:20:30+01:00' # datetime | Filters events occurring before this datetime. (optional)
after = '2013-10-20T19:20:30+01:00' # datetime | Filters events occurring after this datetime. (optional)
event_types = [anyscale_client.SessionEventTypes()] # list[SessionEventTypes] | Filters events to these types. (optional)
log_level_types = [anyscale_client.LogLevelTypes()] # list[LogLevelTypes] | Filters logs to these leves. (optional)
paging_token = 'paging_token_example' # str |  (optional)
count = 20 # int |  (optional) (default to 20)

    try:
        # Get Session Event Log
        api_response = api_instance.get_session_event_log(session_id, before=before, after=after, event_types=event_types, log_level_types=log_level_types, paging_token=paging_token, count=count)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_session_event_log: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**| ID of the Session to retrieve event logs for. | 
 **before** | **datetime**| Filters events occurring before this datetime. | [optional] 
 **after** | **datetime**| Filters events occurring after this datetime. | [optional] 
 **event_types** | [**list[SessionEventTypes]**](SessionEventTypes.md)| Filters events to these types. | [optional] 
 **log_level_types** | [**list[LogLevelTypes]**](LogLevelTypes.md)| Filters logs to these leves. | [optional] 
 **paging_token** | **str**|  | [optional] 
 **count** | **int**|  | [optional] [default to 20]

### Return type

[**SessioneventListResponse**](SessioneventListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_for_job**
> SessionResponse get_session_for_job(production_job_id)

Get Session For Job

Get Session for Production Job

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    production_job_id = 'production_job_id_example' # str | 

    try:
        # Get Session For Job
        api_response = api_instance.get_session_for_job(production_job_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_session_for_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **production_job_id** | **str**|  | 

### Return type

[**SessionResponse**](SessionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_operation**
> SessionoperationResponse get_session_operation(session_operation_id)

Get Session Operation

     DEPRECATED: use /cluster_operations.     Get the status of a session operation for the given session.     

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    session_operation_id = 'session_operation_id_example' # str | 

    try:
        # Get Session Operation
        api_response = api_instance.get_session_operation(session_operation_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_session_operation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_operation_id** | **str**|  | 

### Return type

[**SessionoperationResponse**](SessionoperationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **kill_session_command**
> SessioncommandResponse kill_session_command(session_command_id)

Kill Session Command

Kills a session command. Returns the updated session command.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    session_command_id = 'session_command_id_example' # str | ID of the Session Command to kill.

    try:
        # Kill Session Command
        api_response = api_instance.kill_session_command(session_command_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->kill_session_command: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_command_id** | **str**| ID of the Session Command to kill. | 

### Return type

[**SessioncommandResponse**](SessioncommandResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_app_configs**
> AppconfigListResponse list_app_configs(project_id=project_id, creator_id=creator_id, name_contains=name_contains, paging_token=paging_token, count=count)

List App Configs

DEPRECATED: Use Cluster Environments API instead. Lists all App Configs that satisfies the query parameters. If none are provided, we show all App Configs within your orgranization.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    project_id = 'project_id_example' # str |  (optional)
creator_id = 'creator_id_example' # str |  (optional)
name_contains = 'name_contains_example' # str |  (optional)
paging_token = 'paging_token_example' # str |  (optional)
count = 100 # int |  (optional) (default to 100)

    try:
        # List App Configs
        api_response = api_instance.list_app_configs(project_id=project_id, creator_id=creator_id, name_contains=name_contains, paging_token=paging_token, count=count)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->list_app_configs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | [optional] 
 **creator_id** | **str**|  | [optional] 
 **name_contains** | **str**|  | [optional] 
 **paging_token** | **str**|  | [optional] 
 **count** | **int**|  | [optional] [default to 100]

### Return type

[**AppconfigListResponse**](AppconfigListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_builds**
> BuildListResponse list_builds(application_template_id, paging_token=paging_token, count=count)

List Builds

DEPRECATED: Use Cluster Environment Builds API instead. Lists all Builds belonging to an App Config.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    application_template_id = 'application_template_id_example' # str | 
paging_token = 'paging_token_example' # str |  (optional)
count = 10 # int |  (optional) (default to 10)

    try:
        # List Builds
        api_response = api_instance.list_builds(application_template_id, paging_token=paging_token, count=count)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->list_builds: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_template_id** | **str**|  | 
 **paging_token** | **str**|  | [optional] 
 **count** | **int**|  | [optional] [default to 10]

### Return type

[**BuildListResponse**](BuildListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_cluster_environment_builds**
> ClusterenvironmentbuildListResponse list_cluster_environment_builds(cluster_environment_id, desc=desc, paging_token=paging_token, count=count)

List Cluster Environment Builds

Lists all Cluster Environment Builds belonging to an Cluster Environment.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_environment_id = 'cluster_environment_id_example' # str | ID of the Cluster Environment to list builds for.
desc = False # bool | Orders the list of builds from latest to oldest. (optional) (default to False)
paging_token = 'paging_token_example' # str |  (optional)
count = 10 # int |  (optional) (default to 10)

    try:
        # List Cluster Environment Builds
        api_response = api_instance.list_cluster_environment_builds(cluster_environment_id, desc=desc, paging_token=paging_token, count=count)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->list_cluster_environment_builds: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_environment_id** | **str**| ID of the Cluster Environment to list builds for. | 
 **desc** | **bool**| Orders the list of builds from latest to oldest. | [optional] [default to False]
 **paging_token** | **str**|  | [optional] 
 **count** | **int**|  | [optional] [default to 10]

### Return type

[**ClusterenvironmentbuildListResponse**](ClusterenvironmentbuildListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_production_jobs**
> ProductionjobListResponse list_production_jobs(project_id=project_id, name=name, state_filter=state_filter, creator_id=creator_id, paging_token=paging_token, count=count)

List Production Jobs

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    project_id = 'project_id_example' # str | project_id to filter by (optional)
name = 'name_example' # str | name to filter by (optional)
state_filter = [] # list[HaJobStates] | A list of session states to filter by (optional) (default to [])
creator_id = 'creator_id_example' # str | filter by creator id (optional)
paging_token = 'paging_token_example' # str |  (optional)
count = 56 # int |  (optional)

    try:
        # List Production Jobs
        api_response = api_instance.list_production_jobs(project_id=project_id, name=name, state_filter=state_filter, creator_id=creator_id, paging_token=paging_token, count=count)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->list_production_jobs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**| project_id to filter by | [optional] 
 **name** | **str**| name to filter by | [optional] 
 **state_filter** | [**list[HaJobStates]**](HaJobStates.md)| A list of session states to filter by | [optional] [default to []]
 **creator_id** | **str**| filter by creator id | [optional] 
 **paging_token** | **str**|  | [optional] 
 **count** | **int**|  | [optional] 

### Return type

[**ProductionjobListResponse**](ProductionjobListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_projects**
> ProjectListResponse list_projects(paging_token=paging_token, count=count)

List Projects

Lists all Projects the user has access to. DEPRECATED: Use the /search endpoint instead

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    paging_token = 'paging_token_example' # str |  (optional)
count = 10 # int |  (optional) (default to 10)

    try:
        # List Projects
        api_response = api_instance.list_projects(paging_token=paging_token, count=count)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->list_projects: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **paging_token** | **str**|  | [optional] 
 **count** | **int**|  | [optional] [default to 10]

### Return type

[**ProjectListResponse**](ProjectListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_services**
> ProductionserviceListResponse list_services(project_id=project_id, name=name, state_filter=state_filter, creator_id=creator_id, paging_token=paging_token, count=count)

List Services

**EXPERIMENTAL FEATURE**: List Services

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    project_id = 'project_id_example' # str | project_id to filter by (optional)
name = 'name_example' # str | name to filter by (optional)
state_filter = [] # list[HaJobStates] | A list of session states to filter by (optional) (default to [])
creator_id = 'creator_id_example' # str | filter by creator id (optional)
paging_token = 'paging_token_example' # str |  (optional)
count = 56 # int |  (optional)

    try:
        # List Services
        api_response = api_instance.list_services(project_id=project_id, name=name, state_filter=state_filter, creator_id=creator_id, paging_token=paging_token, count=count)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->list_services: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**| project_id to filter by | [optional] 
 **name** | **str**| name to filter by | [optional] 
 **state_filter** | [**list[HaJobStates]**](HaJobStates.md)| A list of session states to filter by | [optional] [default to []]
 **creator_id** | **str**| filter by creator id | [optional] 
 **paging_token** | **str**|  | [optional] 
 **count** | **int**|  | [optional] 

### Return type

[**ProductionserviceListResponse**](ProductionserviceListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_session_commands**
> SessioncommandListResponse list_session_commands(session_id, paging_token=paging_token, count=count)

List Session Commands

Retrieves a list of commands that were created on the Session.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    session_id = 'session_id_example' # str | ID of the Session to list Commands for.
paging_token = 'paging_token_example' # str |  (optional)
count = 10 # int |  (optional) (default to 10)

    try:
        # List Session Commands
        api_response = api_instance.list_session_commands(session_id, paging_token=paging_token, count=count)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->list_session_commands: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**| ID of the Session to list Commands for. | 
 **paging_token** | **str**|  | [optional] 
 **count** | **int**|  | [optional] [default to 10]

### Return type

[**SessioncommandListResponse**](SessioncommandListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_sessions**
> SessionListResponse list_sessions(project_id, paging_token=paging_token, count=count)

List Sessions

DEPRECATED: Use Clusters API instead. Lists all Sessions belonging to the Project.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    project_id = 'project_id_example' # str | 
paging_token = 'paging_token_example' # str |  (optional)
count = 10 # int |  (optional) (default to 10)

    try:
        # List Sessions
        api_response = api_instance.list_sessions(project_id, paging_token=paging_token, count=count)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->list_sessions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **paging_token** | **str**|  | [optional] 
 **count** | **int**|  | [optional] [default to 10]

### Return type

[**SessionListResponse**](SessionListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **partial_update_organization**
> OrganizationResponse partial_update_organization(organization_id, update_organization)

Partial Update Organization

Update an organization's requirement for Single Sign On (SSO). If SSO is required for an organization, SSO will be the only way to log in to it.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    organization_id = 'organization_id_example' # str | ID of the Organization to update.
update_organization = anyscale_client.UpdateOrganization() # UpdateOrganization | 

    try:
        # Partial Update Organization
        api_response = api_instance.partial_update_organization(organization_id, update_organization)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->partial_update_organization: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_id** | **str**| ID of the Organization to update. | 
 **update_organization** | [**UpdateOrganization**](UpdateOrganization.md)|  | 

### Return type

[**OrganizationResponse**](OrganizationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_actors**
> ActorListResponse search_actors(actors_query)

Search Actors

Lists all Actors the user has access to, matching the input query.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    actors_query = anyscale_client.ActorsQuery() # ActorsQuery | 

    try:
        # Search Actors
        api_response = api_instance.search_actors(actors_query)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->search_actors: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **actors_query** | [**ActorsQuery**](ActorsQuery.md)|  | 

### Return type

[**ActorListResponse**](ActorListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_clouds**
> CloudListResponse search_clouds(clouds_query)

Search Clouds

Searches for all accessible Clouds that satisfies the query.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    clouds_query = anyscale_client.CloudsQuery() # CloudsQuery | 

    try:
        # Search Clouds
        api_response = api_instance.search_clouds(clouds_query)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->search_clouds: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **clouds_query** | [**CloudsQuery**](CloudsQuery.md)|  | 

### Return type

[**CloudListResponse**](CloudListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_cluster_computes**
> ClustercomputeListResponse search_cluster_computes(cluster_computes_query)

Search Cluster Computes

Lists all Cluster Computes the user has access to, matching the input query.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_computes_query = anyscale_client.ClusterComputesQuery() # ClusterComputesQuery | 

    try:
        # Search Cluster Computes
        api_response = api_instance.search_cluster_computes(cluster_computes_query)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->search_cluster_computes: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_computes_query** | [**ClusterComputesQuery**](ClusterComputesQuery.md)|  | 

### Return type

[**ClustercomputeListResponse**](ClustercomputeListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_cluster_environments**
> ClusterenvironmentListResponse search_cluster_environments(cluster_environments_query)

Search Cluster Environments

Lists all Cluster Environments that the logged in user has permissions to access.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_environments_query = anyscale_client.ClusterEnvironmentsQuery() # ClusterEnvironmentsQuery | 

    try:
        # Search Cluster Environments
        api_response = api_instance.search_cluster_environments(cluster_environments_query)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->search_cluster_environments: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_environments_query** | [**ClusterEnvironmentsQuery**](ClusterEnvironmentsQuery.md)|  | 

### Return type

[**ClusterenvironmentListResponse**](ClusterenvironmentListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_clusters**
> ClusterListResponse search_clusters(clusters_query)

Search Clusters

Searches for all Clusters the user has access to that satisfies the query.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    clusters_query = anyscale_client.ClustersQuery() # ClustersQuery | 

    try:
        # Search Clusters
        api_response = api_instance.search_clusters(clusters_query)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->search_clusters: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **clusters_query** | [**ClustersQuery**](ClustersQuery.md)|  | 

### Return type

[**ClusterListResponse**](ClusterListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_compute_templates**
> ComputetemplateListResponse search_compute_templates(compute_template_query, paging_token=paging_token, count=count)

Search Compute Templates

DEPRECATED: Use Cluster Computes API instead. List all compute templates matching the search parameters. If no parameters are specified, lists all templates created by the user.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    compute_template_query = anyscale_client.ComputeTemplateQuery() # ComputeTemplateQuery | 
paging_token = 'paging_token_example' # str |  (optional)
count = 10 # int |  (optional) (default to 10)

    try:
        # Search Compute Templates
        api_response = api_instance.search_compute_templates(compute_template_query, paging_token=paging_token, count=count)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->search_compute_templates: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compute_template_query** | [**ComputeTemplateQuery**](ComputeTemplateQuery.md)|  | 
 **paging_token** | **str**|  | [optional] 
 **count** | **int**|  | [optional] [default to 10]

### Return type

[**ComputetemplateListResponse**](ComputetemplateListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_jobs**
> JobListResponse search_jobs(jobs_query)

Search Jobs

Lists all Jobs that the logged in user has access to, matching the input query.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    jobs_query = anyscale_client.JobsQuery() # JobsQuery | 

    try:
        # Search Jobs
        api_response = api_instance.search_jobs(jobs_query)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->search_jobs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jobs_query** | [**JobsQuery**](JobsQuery.md)|  | 

### Return type

[**JobListResponse**](JobListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_projects**
> ProjectListResponse search_projects(projects_query)

Search Projects

Searches for all Projects the user has access to that satisfies the query.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    projects_query = anyscale_client.ProjectsQuery() # ProjectsQuery | 

    try:
        # Search Projects
        api_response = api_instance.search_projects(projects_query)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->search_projects: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **projects_query** | [**ProjectsQuery**](ProjectsQuery.md)|  | 

### Return type

[**ProjectListResponse**](ProjectListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_sessions**
> SessionListResponse search_sessions(project_id, sessions_query)

Search Sessions

DEPRECATED: Use Clusters API instead. Searches for all Sessions the user has access to that satisfies the query.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    project_id = 'project_id_example' # str | 
sessions_query = anyscale_client.SessionsQuery() # SessionsQuery | 

    try:
        # Search Sessions
        api_response = api_instance.search_sessions(project_id, sessions_query)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->search_sessions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **sessions_query** | [**SessionsQuery**](SessionsQuery.md)|  | 

### Return type

[**SessionListResponse**](SessionListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_cluster**
> ClusteroperationResponse start_cluster(cluster_id, start_cluster_options)

Start Cluster

Initializes workflow to transition the Cluster into the Running state. The Cluster will be updated if Cluster Environment Build or Cluster Compute is provided in the options. This is a long running operation. Clients will need to poll the operation's status to determine completion.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_id = 'cluster_id_example' # str | ID of the Cluster to start.
start_cluster_options = anyscale_client.StartClusterOptions() # StartClusterOptions | 

    try:
        # Start Cluster
        api_response = api_instance.start_cluster(cluster_id, start_cluster_options)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->start_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_id** | **str**| ID of the Cluster to start. | 
 **start_cluster_options** | [**StartClusterOptions**](StartClusterOptions.md)|  | 

### Return type

[**ClusteroperationResponse**](ClusteroperationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_session**
> SessionoperationResponse start_session(session_id, start_session_options)

Start Session

     DEPRECATED: Use Clusters API instead.     Initializes workflow to transition the Session into the Running state.      The session's cluster config will be updated if it is provided in the options.      This is a long running operation.     Clients will need to poll the opertation's status to determine completion.     

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    session_id = 'session_id_example' # str | 
start_session_options = anyscale_client.StartSessionOptions() # StartSessionOptions | 

    try:
        # Start Session
        api_response = api_instance.start_session(session_id, start_session_options)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->start_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **start_session_options** | [**StartSessionOptions**](StartSessionOptions.md)|  | 

### Return type

[**SessionoperationResponse**](SessionoperationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **terminate_cluster**
> ClusteroperationResponse terminate_cluster(cluster_id, terminate_cluster_options)

Terminate Cluster

Initializes workflow to transition the Cluster into the Terminated state. This is a long running operation. Clients will need to poll the operation's status to determine completion.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_id = 'cluster_id_example' # str | ID of the Cluster to terminate.
terminate_cluster_options = anyscale_client.TerminateClusterOptions() # TerminateClusterOptions | 

    try:
        # Terminate Cluster
        api_response = api_instance.terminate_cluster(cluster_id, terminate_cluster_options)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->terminate_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_id** | **str**| ID of the Cluster to terminate. | 
 **terminate_cluster_options** | [**TerminateClusterOptions**](TerminateClusterOptions.md)|  | 

### Return type

[**ClusteroperationResponse**](ClusteroperationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **terminate_job**
> ProductionjobResponse terminate_job(production_job_id)

Terminate Job

Terminate an Production Job

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    production_job_id = 'production_job_id_example' # str | 

    try:
        # Terminate Job
        api_response = api_instance.terminate_job(production_job_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->terminate_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **production_job_id** | **str**|  | 

### Return type

[**ProductionjobResponse**](ProductionjobResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **terminate_service**
> ProductionserviceResponse terminate_service(service_id)

Terminate Service

**EXPERIMENTAL FEATURE**: Terminate an Service

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    service_id = 'service_id_example' # str | 

    try:
        # Terminate Service
        api_response = api_instance.terminate_service(service_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->terminate_service: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_id** | **str**|  | 

### Return type

[**ProductionserviceResponse**](ProductionserviceResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **terminate_session**
> SessionoperationResponse terminate_session(session_id, terminate_session_options)

Terminate Session

     DEPRECATED: Use Clusters API instead.     Initializes workflow to transition the Session into the Terminated state.      This is a long running operation.     Clients will need to poll the opertation's status to determine completion.     

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    session_id = 'session_id_example' # str | 
terminate_session_options = anyscale_client.TerminateSessionOptions() # TerminateSessionOptions | 

    try:
        # Terminate Session
        api_response = api_instance.terminate_session(session_id, terminate_session_options)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->terminate_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **terminate_session_options** | [**TerminateSessionOptions**](TerminateSessionOptions.md)|  | 

### Return type

[**SessionoperationResponse**](SessionoperationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_app_configs**
> AppconfigResponse update_app_configs(app_config_id, update_app_config)

Update App Configs

DEPRECATED: Renaming an App Config will no longer be supported moving forward. Updates an App Config.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    app_config_id = 'app_config_id_example' # str | 
update_app_config = anyscale_client.UpdateAppConfig() # UpdateAppConfig | 

    try:
        # Update App Configs
        api_response = api_instance.update_app_configs(app_config_id, update_app_config)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->update_app_configs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_config_id** | **str**|  | 
 **update_app_config** | [**UpdateAppConfig**](UpdateAppConfig.md)|  | 

### Return type

[**AppconfigResponse**](AppconfigResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_cloud**
> CloudResponse update_cloud(cloud_id, update_cloud)

Update Cloud

Updates a Cloud.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cloud_id = 'cloud_id_example' # str | ID of the Cloud to update.
update_cloud = anyscale_client.UpdateCloud() # UpdateCloud | 

    try:
        # Update Cloud
        api_response = api_instance.update_cloud(cloud_id, update_cloud)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->update_cloud: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cloud_id** | **str**| ID of the Cloud to update. | 
 **update_cloud** | [**UpdateCloud**](UpdateCloud.md)|  | 

### Return type

[**CloudResponse**](CloudResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_cluster**
> ClusterResponse update_cluster(cluster_id, update_cluster)

Update Cluster

Updates a Cluster.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    cluster_id = 'cluster_id_example' # str | ID of the Cluster to update.
update_cluster = anyscale_client.UpdateCluster() # UpdateCluster | 

    try:
        # Update Cluster
        api_response = api_instance.update_cluster(cluster_id, update_cluster)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->update_cluster: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_id** | **str**| ID of the Cluster to update. | 
 **update_cluster** | [**UpdateCluster**](UpdateCluster.md)|  | 

### Return type

[**ClusterResponse**](ClusterResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_compute_template**
> ComputetemplateResponse update_compute_template(template_id, update_compute_template)

Update Compute Template

Updates a compute template. DEPRECATED: Compute templates will be immutable. Please create a new one instead of updating existing ones.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    template_id = 'template_id_example' # str | 
update_compute_template = anyscale_client.UpdateComputeTemplate() # UpdateComputeTemplate | 

    try:
        # Update Compute Template
        api_response = api_instance.update_compute_template(template_id, update_compute_template)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->update_compute_template: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **template_id** | **str**|  | 
 **update_compute_template** | [**UpdateComputeTemplate**](UpdateComputeTemplate.md)|  | 

### Return type

[**ComputetemplateResponse**](ComputetemplateResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_project**
> ProjectResponse update_project(project_id, update_project)

Update Project

Updates a Project.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    project_id = 'project_id_example' # str | ID of the Project to update.
update_project = anyscale_client.UpdateProject() # UpdateProject | 

    try:
        # Update Project
        api_response = api_instance.update_project(project_id, update_project)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->update_project: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**| ID of the Project to update. | 
 **update_project** | [**UpdateProject**](UpdateProject.md)|  | 

### Return type

[**ProjectResponse**](ProjectResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_session**
> SessionResponse update_session(session_id, update_session)

Update Session

DEPRECATED: Use Clusters API instead. Updates a Session.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    session_id = 'session_id_example' # str | 
update_session = anyscale_client.UpdateSession() # UpdateSession | 

    try:
        # Update Session
        api_response = api_instance.update_session(session_id, update_session)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->update_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **update_session** | [**UpdateSession**](UpdateSession.md)|  | 

### Return type

[**SessionResponse**](SessionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_sso_config**
> SsoconfigResponse upsert_sso_config(create_sso_config)

Upsert Sso Config

Create or update the single sign on (SSO) configuration for your organization.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_sso_config = anyscale_client.CreateSSOConfig() # CreateSSOConfig | 

    try:
        # Upsert Sso Config
        api_response = api_instance.upsert_sso_config(create_sso_config)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->upsert_sso_config: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_sso_config** | [**CreateSSOConfig**](CreateSSOConfig.md)|  | 

### Return type

[**SsoconfigResponse**](SsoconfigResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_test_sso_config**
> SsoconfigResponse upsert_test_sso_config(create_sso_config)

Upsert Test Sso Config

Create or update the test single sign on (SSO) configuration for your organization.

### Example

```python
from __future__ import print_function
import time
import anyscale_client
from anyscale_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with anyscale_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = anyscale_client.DefaultApi(api_client)
    create_sso_config = anyscale_client.CreateSSOConfig() # CreateSSOConfig | 

    try:
        # Upsert Test Sso Config
        api_response = api_instance.upsert_test_sso_config(create_sso_config)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->upsert_test_sso_config: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_sso_config** | [**CreateSSOConfig**](CreateSSOConfig.md)|  | 

### Return type

[**SsoconfigResponse**](SsoconfigResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

