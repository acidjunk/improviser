# Improviser

The REST API server for the improviser-client

## Install for development

    mkvirtualenv --python=/usr/local/bin/python3 improviser
    pip install -r requirements.txt
    createdb improviser
    createuser improviser -sP
    python app.py db upgrade
    python app.py runserver --debug

## Version handling

Bump version (first lookup up current version and commit)

    bumpversion --current-version 0.2.0 minor improviser/app.py

Will bump version to 0.3.0

    bumpversion --current-version 0.2.0 patch improviser/app.py

Will bump version to 0.2.1

## Deploy
```
mkvirtualenv improviser_deploy
pip install -r requirements/all.txt
pip install -r requirements/deploy.txt
cd improviser
zappa update
```
