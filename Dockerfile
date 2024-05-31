FROM quay.io/astronomer/astro-runtime:11.3.0

RUN pip install --user airflow_provider_anyscale-1.0.0-py2.py3-none-any.whl
