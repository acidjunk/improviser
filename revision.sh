#!/bin/bash
source ~/.virtualenvs/improviser/bin/activate
export $(cat env | grep -v ^# | xargs)
cd improviser
flask db revision
echo "Don't forget to commit the migration, if any..."