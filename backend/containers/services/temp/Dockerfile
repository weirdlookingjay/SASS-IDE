
FROM codercom/code-server:latest

USER root

# Set environment variables first
ENV PATH=/usr/local/go/bin:/home/coder/go/bin:/home/coder/.local/bin:/home/coder/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV GOROOT=/usr/local/go
ENV GOPATH=/home/coder/go
ENV GOBIN=/home/coder/go/bin

# Run setup commands
RUN set -ex && apt-get update && apt-get install -y --no-install-recommends wget ca-certificates git curl && wget -q https://golang.org/dl/go1.21.0.linux-amd64.tar.gz && rm -rf /usr/local/go && tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz && rm go1.21.0.linux-amd64.tar.gz && mkdir -p /home/coder/go/{bin,pkg,src} && chown -R coder:coder /home/coder/go

# Add environment variables to profile and bashrc
RUN echo 'export PATH=/usr/local/go/bin:/home/coder/go/bin:$PATH' >> /etc/profile && \
    echo 'export GOROOT=/usr/local/go' >> /etc/profile && \
    echo 'export GOPATH=/home/coder/go' >> /etc/profile && \
    echo 'export GOBIN=/home/coder/go/bin' >> /etc/profile && \
    echo 'export PATH=/usr/local/go/bin:/home/coder/go/bin:$PATH' >> /home/coder/.bashrc && \
    echo 'export GOROOT=/usr/local/go' >> /home/coder/.bashrc && \
    echo 'export GOPATH=/home/coder/go' >> /home/coder/.bashrc && \
    echo 'export GOBIN=/home/coder/go/bin' >> /home/coder/.bashrc && \
    chown -R coder:coder /home/coder/.bashrc

USER coder

# Final verification
RUN bash -c 'source /etc/profile && source ~/.bashrc && \
    echo "=== Final Verification ===" && \
    echo "PATH=$PATH" && \
    echo "GOROOT=$GOROOT" && \
    echo "GOPATH=$GOPATH" && \
    ls -la /usr/local/go/bin && \
    which go && \
    go version'
