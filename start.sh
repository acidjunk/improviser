#!/bin/bash
#source ~/.virtualenvs/improviser/bin/activate
source venv/bin/activate
export $(cat env | grep -v ^# | xargs)
cd improviser
flask run --host 0.0.0.0
