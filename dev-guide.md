## Small Board Development Guide

### Getting started

There are two ways to set up Small Board locally.

To run Small Board in Docker, you will need:

- Git
- Docker (on Mac or Windows, install Docker Desktop; on Linux, docker and docker-compose)

To run Small Board manually, you will need:

- Git
- Python
- Pipenv
- [NodeJS](https://nodejs.org/en/download/package-manager/) (version 10 or later)
- [Yarn](https://classic.yarnpkg.com/en/docs/install/)
- a local database (e.g.: PostgreSQL or SQLite)

### Checking out the code

To check out the code, you first need to [install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git). Then you can checkout the code using:

```
git clone git@github.com:cardinalitypuzzles/smallboard.git
```

### Set up an `.env` file

Both Docker and manual setup read environment variables from an `.env` file. An example `.env.test` file is provided, which you should copy to `.env`:

```
cp .env.test .env
```

See below for more details on the `.env` file. You probably want to set at least `DJANGO_SECRET_KEY` so that your session isn't invalidated each time you restart the web container.


### Docker setup

Docker allows a simple, consistent setup of Small Board. After checking out the code, navigate to the directory and run:

```
# You can pass the -d flag to run in the background.
# In that case, run `docker-compose logs` to view the output.
docker-compose up --build
```

The first time you run this, it will build Docker images locally and then run the web server and postgres in separate containers.

After the initial build, you may use `docker-compose up` to start Small Board without rebuilding container images. Doing a rebuild with `--build` is required after adding new library dependencies, however.

To run a command inside the web container, you can run

```
docker-compose exec web [command]
```

For example, to run tests, you can run

```
docker-compose exec web python manage.py test
```

This is pretty verbose, so on my machine I added a local alias for `smallboard-manage` to `docker-compose exec web python manage.py`. Then `smallboard-manage test` will run tests.

Our docker setup reads environmental variables from .env as described earlier. This file must exist, though by default it may be empty.

### Manual setup

#### Setting up a Python environment

Begin by installing [python](https://wiki.python.org/moin/BeginnersGuide/Download) (you likely already have this installed)
On Ubuntu, you can accomplish this by running:

```
$ sudo apt install python3
```

Next, install [pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv)
On Ubuntu, you can accomplish this by running:

```
$ sudo apt install pipenv
```

Once you have pipenv, you can create an environment by running:

```
pipenv install --dev
```

This creates a virtual environment and installs the dependencies and dev dependencies
You can then activate the virtual environment by running

```
pipenv shell
```

**Going forward, assume that any commands should be run inside the virtual environment**

#### <a name='database'>Setting up a local database</a>

Django supports multiple databases but here we use Postgres as an example. For most OS distributions, you should be able to install it using your package manager, similar to:

```
sudo apt-get install postgresql
```

As of 11/23/2019, postgresql doesn't work out of the box. You'll need to add the following 2 config files to the right places:

```
sudo -u postgres touch /var/lib/postgresql/10/main/postgresql.conf
sudo -u postgres cp missing_postgres_configs/pg_hba.conf /var/lib/postgresql/10/main/pg_hba.conf
```

Start the database server using a command like:

```
# by default, the server runs as the "postgres" user,
# so you'll need to run this as the postgres user
sudo -u postgres /usr/lib/postgresql/10/bin/pg_ctl -D /var/lib/postgresql/10/main -l logfile start
```

Once the database server is running, connect to it and set up a database, user, and password for Small Board:

```
# run as postgres user
sudo -u postgres psql

# inside postgres shell
create database smallboard;

create user myuser with encrypted password 'mypass';
grant all privileges on database smallboard to myuser;

# needed for tests
ALTER USER myuser CREATEDB;
```

Create a `.env` file in the `smallboard/` root directory with the database connection info:

```
# .env file contents
DATABASE_URL=postgres://myuser:mypass@localhost/smallboard
```

Once this is set up, you'll need to run a one-time database migration to set up the database tables:

```
# from smallboard/ root directory
$ python manage.py migrate
```

#### Local deployment

Once the Python environment and database are set up and running, you can run Small Board locally using

```
$ python manage.py runserver
```

You can view the app in your browser at [http://127.0.0.1:8000/]().

#### React pages

Some pages are rendered using React JS. To compile these pages, make sure you've
installed javascript deps using `yarn`.

```
yarn install
```

Then, in a separate terminal window from the one where you run the django
`runserver` command, build the React pages using

```
yarn run dev
```

This will start a compilation daemon that watches for local changes and
hot-reloads them during development.

#### Running Tests

To run tests:

```
python manage.py test
```

The test environment settings are in `.env.test`. If you encounter an error `Got an error creating the test database: permission denied to create database`, make sure you run `ALTER USER myuser CREATEDB` as described above in the [Setting up a local database](#database) section.

### Copying production data to local database

For testing and development, it can be helpful to load the production data into your local database. You can do so as follows:

```
# download production data
# get the postgres connection string from https://dashboard.heroku.com/apps/smallboard/settings
heroku run pg_dump postgres://user:pass@....compute-1.amazonaws.com:5432/database > prod_db.sql

# edit prod_db.sql and replace all instances of "Owner: <random_string_of_letters>" with "Owner: myuser"

# drop all tables
psql postgres://myuser:mypass@localhost/smallboard
# run the following to generate the drop table commands
SELECT  'DROP TABLE IF EXISTS "' || tablename || '" CASCADE;' FROM pg_tables WHERE tableowner = 'myuser';
# run the drop table commands

# load production data
\i prod_db.sql
```

### <a name='env'>Local `.env` file: credentials, API Tokens, configuration</a>

This app uses various secrets including Google API tokens that need to be present in the environment. Locally, you can put these in the `.env` file. In the production Heroku deployment, they're set as Config Vars at https://dashboard.heroku.com/apps/smallboard/settings. For most of these configs, you can just use the production settings. The ones you probably want to change are `DATABASE_URL`, `DJANGO_SECRET_KEY`, and `DEBUG`. You can contact a Collaborator to give you access to the Heroku Small Board settings or to share their `.env` file with you.

The environment variables used by Small Board are listed below. The only required variables are `DATABASE_URL`. When running with Docker, there are no required variables; `DATABASE_URL` is ignored.

```
# for connecting to the database (see "Setting up a local database" section above)
DATABASE_URL=postgres://myuser:mypass@localhost/smallboard

# for accessing Google APIs
GOOGLE_API_PRIVATE_KEY=...

# id of the Google Drive hunt folder
# when you go to the folder, it's the last part of the URL
# drive.google.com/drive/folders/<HUNT_FOLDER_ID>
# the whitelist of emails allowed access to Small Board
# are the emails of the users who have access to this folder
GOOGLE_DRIVE_HUNT_FOLDER_ID=...

# id of the Google Spreadsheet template to be copied for
# each puzzle. The id is in the URL when you open the spreadsheet:
# docs.google.com/spreadsheets/d/<SHEETS_ID>/...
# This file should in inside the hunt folder, since when
# this template is copied, the new spreadsheet will be
# put in the same folder as the template.
GOOGLE_SHEETS_TEMPLATE_FILE_ID=...

# for Google OAuth2 login
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=...

# secret used by Django framework for sessions, passwords, etc.
# rather than use the production secret key locally, you can easily generate a new one using:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DJANGO_SECRET_KEY=...

# whether to enable debug info when errors happen
# for dev, you probably want to set to True, but in production,
# we should set to False
DEBUG=...
```

### Google OAuth2 login integration (optional)

The app uses Google OAuth2 to authenticate users. If the `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` environment variable isn't set, the app will fall back to a "Signup" flow where users can create their own username and password. Even with Google OAuth2 enabled, you can still create superusers using `python manage.py createsuperuser`. The OAuth2 settings are configured at https://console.developers.google.com/apis/credentials?project=smallboard-test-260001.

You should be able to use Google OAuth2 locally as well, since the OAuth2 settings above include `localhost` and `127.0.0.1` as authorized redirect URLs.

The whitelist of allowed emails is the emails of the users who have access to `GOOGLE_DRIVE_HUNT_FOLDER_ID`. If you don't have access, please message a Collaborator to be added.

### Google Sheets Integration (optional)

When a puzzle is created, a Google Sheet is created that is a copy of the template specified by `GOOGLE_SHEETS_TEMPLATE_FILE_ID` (which should have some useful formulas pre-added). The copied sheet is created in the same folder as the template.

You need to have access to the Google Drive folder to view it. Please message a Collaborator if you don't.

These Google Drive and Sheets related settings can be found in [smallboard/settings.py](smallboard/settings.py).

### Deployment to Heroku

Though our development repo is this GitHub repo ([cardinalitypuzzles/smallboard](https://github.com/cardinalitypuzzles/smallboard)), to deploy to Heroku, you need to push the latest code to the Heroku Git server. To do so, you need to be added as a collaborator for the Heroku app first. Please message one of the collaborators on this project to be added.

Once you've been added as a collaborator for the smallboard Heroku app, you can deploy changes by following [this guide](https://devcenter.heroku.com/articles/git). Install Git and the Heroku CLI. Then run

```
heroku login
heroku git:remote -a smallboard
```

After this, you can deploy changes by running

```
git push heroku master
```

We encourage you to keep the `origin` remote as our GitHub repo and make it the default for `git push`s, and use `git push heroku master` to push to the Heroku Git servers when you are ready to deploy changes to production.

### Environment variables

We rely on various secrets and tokens for Google integration, etc. These are set as Config Vars at https://dashboard.heroku.com/apps/smallboard/settings. See the [Local `.env` file](#env) section above for more details.

### Set up pre-commit checks

The `pre-commit` tool will run linters and formatters so that you can spend more time coding and waste less time aligning indents. To set up pre-commit, run:

```
pre-commit install -t pre-commit -t commit-msg
```

After you run this command once, each time you run `git commit`, a series of checks will automatically run on modified files and inform you of any issues (sometimes fixing files for you!).

To run pre-commit checks on the entire codebase without running `git commit`, run:

```
pre-commit run --all-files
```

### Test Coverage Report

Test coverage measures how many lines of production code your tests actually run. It's a reasonable metric of the impact of your tests. To generate a coverage report, first run tests with this modified command:

```
coverage run --source='.' manage.py test
```

Then generate the report based on data collected by the previous command:

```
coverage report
```
