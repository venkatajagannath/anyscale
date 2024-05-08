__version__ = "1.0.0"

def get_provider_info():
    return {
        "package-name": "airflow-provider-anyscale",  # Required
        "name": "Anyscale",  # Required
        "description": "A sample template for Apache Airflow providers.",  # Required
        "connection-types": [
            {"connection-type": "anyscale", "hook-class-name": "sample_provider.hooks.sample.AnyscaleHook"}
        ],
        "extra-links": ["sample_provider.operators.sample.SampleOperatorExtraLink"],
        "versions": [__version__],  # Required
    }