FROM quay.io/astronomer/astro-runtime:11.3.0

# Install necessary build tools
USER root
RUN apt-get update && apt-get install -y build-essential

# Switch back to the astro user
USER astro

# Copy the anyscale-0.0.0.dev0 folder into the Docker image
COPY anyscale-0.0.0.dev0 /tmp/anyscale-0.0.0.dev0

# Set the working directory
WORKDIR /tmp/anyscale-0.0.0.dev0

# Install build dependencies
RUN pip install --upgrade pip setuptools wheel

# Switch to the root user to build the wheel file
USER root
RUN python setup.py bdist_wheel

# Switch back to the astro user to install the wheel file
USER astro
RUN pip install dist/anyscale-0.0.0.dev0-*.whl

# Copy the test files into the Docker container
COPY tests /usr/local/airflow/tests

# Ensure the tests directory is writable
RUN mkdir -p /usr/local/airflow/tests/.pytest_cache && chmod -R 777 /usr/local/airflow/tests

# Clean up the wheel file and build directory after installation (optional)
RUN rm -rf /tmp/anyscale-0.0.0.dev0

# Set the working directory to where the tests are located
WORKDIR /usr/local/airflow/tests

# Run pytest (adjust the path to your test files if necessary)
CMD ["pytest", "--disable-warnings"]