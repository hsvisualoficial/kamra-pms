FROM frappe/bench:latest

# Arguments for Frappe/Kamra versioning
ARG FRAPPE_VERSION=v15.39.0

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    nodejs \
    npm \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Setup bench
RUN bench init --frappe-branch ${FRAPPE_VERSION} /home/frappe/frappe-bench

WORKDIR /home/frappe/frappe-bench

# Install Kamra and Payments apps
RUN bench get-app payments --branch develop
RUN bench get-app kamra https://github.com/hsvisualoficial/kamra-pms --branch develop

# Setup production environment
RUN sudo bench setup production --yes

EXPOSE 8000
CMD ["bench", "start"]
