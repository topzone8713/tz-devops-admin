FROM topzone8713/devops-utils2:latest

RUN rm -f /etc/apt/sources.list.d/kubernetes.list \
    && rm -f /etc/apt/sources.list.d/archive_uri-https_apt_releases_hashicorp_com-jammy.list

RUN apt-get update && apt-get install -y \
    sudo \
    ca-certificates \
    gnupg \
    build-essential \
    python3 \
    python3-pip \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs
#    && apt-get clean \
#    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -d /home/ubuntu -s /bin/bash ubuntu \
    && echo "ubuntu ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER ubuntu
WORKDIR /home/ubuntu

COPY . /home/ubuntu
RUN sudo chown -R ubuntu:ubuntu /home/ubuntu

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
    NODE_PATH=/home/ubuntu/node_modules

RUN mkdir -p /home/ubuntu/.aws
RUN mkdir -p /home/ubuntu/.kube
COPY resources/config /home/ubuntu/.aws/config
COPY resources/credentials /home/ubuntu/.aws/credentials
COPY resources/kubeconfig_eks-main /home/ubuntu/kubeconfig_eks-main
#COPY resources/.env /home/ubuntu/.env
COPY .env /home/ubuntu/.env
RUN sudo chown -R ubuntu:ubuntu /home/ubuntu

COPY requirements.txt /home/ubuntu
RUN pip3 install --no-cache-dir -r requirements.txt

RUN sudo npm install -g @vue/cli \
    && npm install is-wsl@3.1.0 \
    && npm install bootstrap bootstrap-vue \
    && npm install --no-cache \
    && npm run build

EXPOSE 8000

CMD [ "python3", "app/server.py" ]
#CMD ["sh", "-c", "while true; do echo $(date -u) >> out.txt; sleep 5; done"]
