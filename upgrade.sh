#!/bin/bash
source venv/bin/activate
export $(cat env | grep -v ^# | xargs)
cd improviser
flask db upgrade
