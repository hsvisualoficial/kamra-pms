FROM frappe/bench:latest

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    nodejs \
    npm \
    python3-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Explicitly install bench via pip to ensure it's in the PATH
RUN pip install --no-cache-dir frappe-bench

# Setup bench
# We don't need 'bench init' if using the official image,
# it's usually already initialized. We'll verify and then get apps.
RUN if [ ! -f /home/frappe/frappe-bench/env/bin/bench ]; then \
        bench init --frappe-branch v15.39.0 /home/frappe/frappe-bench; \
    fi

WORKDIR /home/frappe/frappe-bench

# Install Kamra and Payments apps
USER frappe
RUN bench get-app payments --branch develop && \
    bench get-app kamra https://github.com/hsvisualoficial/kamra-pms --branch develop

# Setup production environment
USER root
RUN bench setup production --yes

EXPOSE 8000
CMD ["bench", "start"]
