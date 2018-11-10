# Improviser

The REST API server for the improviser-client

## Install for development

    mkvirtualenv --python=/usr/local/bin/python3 improviser
    pip install -r requirements.txt
    createdb improviser
    createuser improviser -sP
    cd improviser
    DEBUG=1 PYTHON_PATH=. FLASK_APP=main flask db upgrade
    DEBUG=1 PYTHON_PATH=. FLASK_APP=main flask run

## WITH DB:

    DATABASE_URI=postgres://user:pass@host/db_name DEBUG=1 PYTHON_PATH=. FLASK_APP=main flask run

## Version handling

Bump version (first lookup up current version and commit)

    bumpversion --current-version 0.2.0 minor improviser/app.py

Will bump version to 0.3.0

    bumpversion --current-version 0.2.0 patch improviser/app.py

Will bump version to 0.2.1

## Deploy
```
mkvirtualenv improviser_deploy
pip install -r requirements/deploy.txt
cd improviser
zappa deploy
```

## Update deployment
```
workon imporviser_depploy
zappa update
```


## Sync pictures: from inside SVG folder!
```
rclone copy remote:improviser.education/static/rendered/svg .
```