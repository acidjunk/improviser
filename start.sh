#!/bin/bash
source ~/.virtualenvs/improviser/bin/activate
export $(cat env | grep -v ^# | xargs)
cd improviser
flask run
