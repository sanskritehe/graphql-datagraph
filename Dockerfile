FROM ghcr.io/apollographql/router:v1.45.0

COPY router.yaml /dist/config/router.yaml
COPY supergraph.graphql /dist/config/supergraph.graphql

CMD ["--config", "/dist/config/router.yaml", "--supergraph", "/dist/config/supergraph.graphql"]
