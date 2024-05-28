FROM quay.io/astronomer/astro-runtime:11.3.0

# Switch to the root user
USER root

# Install necessary build tools
RUN apt-get update && apt-get install -y build-essential

# Switch back to the astro user
USER astro

# Copy the anyscale-0.0.0.dev0 folder into the Docker image
COPY anyscale-0.0.0.dev0 /tmp/anyscale-0.0.0.dev0

# Set the working directory
WORKDIR /tmp/anyscale-0.0.0.dev0

# Install build dependencies
RUN pip install --upgrade pip setuptools wheel

# Build the wheel file
RUN python setup.py bdist_wheel

# Install the built wheel file using pip
RUN pip install dist/anyscale-0.0.0.dev0-*.whl

# Clean up the wheel file and build directory after installation (optional)
RUN rm -rf /tmp/anyscale-0.0.0.dev0