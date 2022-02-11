[![Build Status](https://travis-ci.com/acidjunk/improviser.svg?branch=master)](https://travis-ci.com/acidjunk/improviser) 
[![Coverage Status](https://coveralls.io/repos/github/acidjunk/improviser/badge.svg?branch=master)](https://coveralls.io/github/acidjunk/improviser?branch=master)

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


Note: kinda broken somehow. Newest python I can use is 3.8 with the [pre-compiled binaries](https://github.com/jkehler/awslambda-psycopg2/tree/master/psycopg2-3.8) for psycopg2 manually installed in `improviser/improviser/psycopg2`
Last succesful deploy from ec2 internship box.

```
workon improviser_deploy
zappa update
```

Note: with python 3.8 I had to use a binary psycopg package that works with amazon lambda. Still not sure what changed, anyway, some instructions:

Clone this somewhere:

`git clone git@github.com:jkehler/awslambda-psycopg2.git`

install all deps in your deploy ven with: 

`pip install -r requirements/deploy.txt`

Now go to the site-packafes in your `deploy/lib/python3.8` and copy the `psycopg2-3.8` folder from the cloned repo.

Run this after the copy from inside the `site-packages` folder:

```
rm -rf psycopg2
rm -rf psycopg2_binary-2.8.5.dist-info
mv psycopg2-3.8 psycopg2
```

Now the deploy should be working nicely with postgres support again.

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
Copyright (C) 2019 René Dohmen <acidjunk@gmail.com>

Licensed under the GNU GENERAL PUBLIC LICENSE Version 3
A copy of the LICENSE is included in the project.
