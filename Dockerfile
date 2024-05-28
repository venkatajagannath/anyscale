FROM quay.io/astronomer/astro-runtime:11.4.0

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

# Clean up the wheel file and build directory after installation (optional)
# RUN rm -rf /tmp/anyscale-0.0.0.dev0