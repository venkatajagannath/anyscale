FROM quay.io/astronomer/astro-runtime:11.3.0

RUN pip install --user astro_provider_anyscale-1.0.0-py3-none-any.whl
