#!/usr/bin/env bash
# Run this once after both services are up to generate supergraph.graphql
# Requires: rover CLI (https://www.apollographql.com/docs/rover/getting-started)

rover supergraph compose --config supergraph.yaml > supergraph.graphql
echo "supergraph.graphql generated"
