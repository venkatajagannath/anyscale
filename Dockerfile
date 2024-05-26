FROM quay.io/astronomer/astro-runtime:11.3.0

# Copy the wheel file into the Docker image
COPY anyscale-0.0.0.dev0-cp311-cp311-linux_aarch64.whl /tmp/

# Install the wheel file using pip
RUN pip install /tmp/anyscale-0.0.0.dev0-cp311-cp311-linux_aarch64.whl

# Clean up the wheel file after installation (optional)
RUN rm /tmp/anyscale-0.0.0.dev0-cp311-cp311-linux_aarch64.whl