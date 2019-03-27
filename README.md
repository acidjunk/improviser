# Improviser

The REST API server for the improviser-client

An online demo can be found on: https://api.improviser.education
If you want to see what you can build with it, grab a free account on: https://www.improviser.education/register

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

    bumpversion --current-version 0.2.0 minor version.py

Will bump version to 0.3.0

    bumpversion --current-version 0.2.0 patch version.py

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
workon improviser_deploy
zappa update
```

## Sync pictures: from inside SVG folder!
```
rclone copy remote:improviser.education/static/rendered/svg .
```

## Create a new migration

    DATABASE_URI=your-devportsgres DEBUG=1 PYTHON_PATH=. FLASK_APP=main flask db migrate

## Running tests

The setup for running unit test with fixtures to provide the correct DB data needed is ready.

```
TEST_DATABASE_URL=postgres://improviser:improviser@localhost/improviser_test PYTHONPATH='improviser' pytest
```

## License
-------
Copyright (C) 2019 René Dohmen <acidjunk@gmail.com>

Licensed under the GNU GENERAL PUBLIC LICENSE Version 3
