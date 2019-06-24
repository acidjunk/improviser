#!/bin/bash
echo "dropping"
dropdb improviser
echo "creating"
createdb improviser
echo "populating"
psql -d improviser < improviser_prod.psql
