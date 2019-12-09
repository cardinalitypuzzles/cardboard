### Getting started

To set up Small Board locally, you need:

* Git
* a Python environment with the packages in [requirements.txt]() installed
* a local database (e.g.: Postgres)


#### Checking out the code

To check out the code, you first need to [install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git). Then you can checkout the code using:

```
git clone git@github.com:cardinalitypuzzles/smallboard.git
```


#### Setting up a Python environment

We recommend setting up an isolated virtual environment where you install the dependencies. You can set one up by following [this guide](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment). Here are the steps for Ubuntu:

```
# install Python 3, venv, and Postgres packages
sudo apt-get install python3-dev python3-venv libpq-dev
# create a new virtual environment
python3 -m venv venv_smallboard
```

Once you've set up the new virtual environment, activate it and install Small Board's dependencies:

```
source venv_smallboard/bin/activate
(venv_smallboard)$ pip install -r requirements.txt
```

If you encounter issues during dependency installation, make sure you've installed the `python3-dev` package (and not just `python3`).


#### Setting up a local database

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

# you can customize "myuser" and "mypass" as you like
create user myuser with encrypted password 'mypass';
grant all privileges on database smallboard to myuser;
```

Create a `.env` file in the `smallboard/` root directory with the database connection info:

```
# .env file contents
DATABASE_URL=postgres://myuser:mypass@localhost/smallboard
```

Once this is set up, you'll need to run a one-time database migration to set up the database tables:

```
# activate virtual environment
source venv_smallboard/bin/activate

# from smallboard/ root directory
(venv_smallboard)$ python manage.py migrate
```


#### <a name='env'>Local `.env` file: credentials, API Tokens, configuration</a>

This app uses various secrets including Google and Slack API tokens that need to be present in the environment. Locally, you can put these in the `.env` file. In the production Heroku deployment, they're set as Config Vars at https://dashboard.heroku.com/apps/smallboard/settings. For most of these configs, you can just use the production settings. The ones you probably want to change are `DATABASE_URL`, `DJANGO_SECRET_KEY`, and `DEBUG`. You can contact a Collaborator to give you access to the Heroku Small Board settings or to share their `.env` file with you. The environment variables used by Small Board are listed below:


```
# for connecting to the database (see "Setting up a local database" section above)
DATABASE_URL=...

# for accessing Google Drive APIs
GOOGLE_DRIVE_API_PRIVATE_KEY=...

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

# for Slack integration
SLACK_BASE_URL=https://my-workspace.slack.com
SLACK_API_TOKEN=...
SLACK_VERIFICATION_TOKEN=...

# secret used by Django framework for sessions, passwords, etc.
# rather than use the production secret key locally, you can easily generate a new one using:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DJANGO_SECRET_KEY=...

# whether to enable debug info when errors happen
# for dev, you probably want to set to True, but in production,
# we should set to False
DEBUG=...
```

#### Google OAuth2 login integration

The app uses Google OAuth2 to authenticate users. If the `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` environment variable isn't set, the app will fall back to a "Signup" flow where users can create their own username and password. Even with Google OAuth2 enabled, you can still create superusers using `python manage.py createsuperuser`. The OAuth2 settings are configured at https://console.developers.google.com/apis/credentials?project=smallboard-test-260001.

You should be able to use Google OAuth2 locally as well, since the OAuth2 settings above include `localhost` and `127.0.0.1` as authorized redirect URLs.

The whitelist of allowed emails is the emails of the users who have access to `GOOGLE_DRIVE_HUNT_FOLDER_ID`. If you don't have access, please message a Collaborator to be added.


#### Google Sheets Integration

When a puzzle is created, a Google Sheet is created that is a copy of the template specified by `GOOGLE_SHEETS_TEMPLATE_FILE_ID` (which should have some useful formulas pre-added). The copied sheet is created in the same folder as the template.

You need to have access to the Google Drive folder to view it. Please message a Collaborator if you don't.

These Google Drive and Sheets related settings can be found in [smallboard/settings.py](smallboard/settings.py).

#### Slack Integration

This app interacts with a slack workspace in the following ways:
1) Channel creation upon puzzle creation
2) A '/answer' command on slack that inputs answers into the big board

When running locally, only 1) will work since the /answer command sends a direct
POST request to the heroku deployment.

You can contact a Collaborator to be added to the relevant slack workspace(s).

#### Local deployment

Once the Python environment and database are set up and running, you can run Small Board locally using

```
(venv_smallboard)$ python manage.py runserver
```

You can view the app in your browser at [http://127.0.0.1:8000/]().


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

#### Environment variables

We rely on various secrets and tokens for Google and Slack integration, etc. These are set as Config Vars at https://dashboard.heroku.com/apps/smallboard/settings. See the [Local `.env` file](#env) section above for more details.