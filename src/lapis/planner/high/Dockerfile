# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install base system dependencies and micromamba prerequisites
RUN apt-get update \
	&& apt-get install -y --no-install-recommends ca-certificates curl bzip2 graphviz \
	&& rm -rf /var/lib/apt/lists/*

# Install SPOT (ltl2tgba, autfilt, ...) from conda-forge via micromamba
ENV MAMBA_ROOT_PREFIX=/opt/conda
RUN curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest \
	| tar -xj -C /usr/local/bin --strip-components=1 bin/micromamba \
	&& micromamba create -y -n spot -c conda-forge spot \
	&& micromamba clean -a -y
ENV PATH=/opt/conda/envs/spot/bin:${PATH}

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire High_Level_Planner directory
COPY . .

# Set working directory to Planner for execution
WORKDIR /app/Planner

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Keep container running with tail -f /dev/null
CMD ["tail", "-f", "/dev/null"]
