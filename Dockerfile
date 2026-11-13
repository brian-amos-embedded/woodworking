FROM debian:trixie-slim
ARG SOLIDCRAFT_VERSION=0.40.1
ARG SOLIDCRAFT_SHA256=0244019d315b37fa9506e09a4ae1cada50713f557dd6be413bd578147350966e
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl python3 libgcc-s1 libstdc++6 fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
RUN curl --fail --location --retry 3 "https://github.com/tangency-labs/solidcraft/releases/download/v${SOLIDCRAFT_VERSION}/solidcraft-${SOLIDCRAFT_VERSION}-linux-x86_64.tar.gz" -o /tmp/solidcraft.tar.gz \
 && echo "${SOLIDCRAFT_SHA256}  /tmp/solidcraft.tar.gz" | sha256sum -c - \
 && mkdir /opt/solidcraft \
 && tar -xzf /tmp/solidcraft.tar.gz -C /opt/solidcraft --strip-components=1 \
 && rm /tmp/solidcraft.tar.gz \
 && ln -s /opt/solidcraft/bin/solidcraft-cli /usr/local/bin/solidcraft-cli
RUN useradd --create-home --uid 1000 cad && mkdir /work && chown cad:cad /work
COPY scripts /opt/trial/scripts
ENV SOLIDCRAFT_GPU=cpu
USER cad
WORKDIR /work
ENTRYPOINT ["solidcraft-cli"]
CMD ["mcp", "--headless", "--param-check", "strict", "--allow-path", "/work"]
