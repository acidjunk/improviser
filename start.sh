export $(cat env | grep -v ^# | xargs)
export FLASK_APP=main:app_factory
cd improviser
flask run
cd ..
