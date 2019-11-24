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
sudo -u postgres touch /var/lib/postgresql/10/main/postgresq1.conf
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


#### Automated Google Sheets creation in Google Drive

For automated Google Sheets creation locally, please contact a Collaborator to share the Google Drive API private key with you. You can then add it to your `.env` file:

```
...
GOOGLE_DRIVE_API_PRIVATE_KEY=...
```

When a puzzle is created, a Google Sheet is created that is a copy of a template with some useful formulas added. The sheet is created in the cardinalitypuzzles@gmail.com Google Drive by default. You need to have access to the Google Drive folder to view it. Please message a Collaborator if you don't.

These Google Drive and Sheets related settings can be found in [smallboard/settings.py](smallboard/settings.py).


#### Local deployment

Once the Python environment and database are set up and running, you can run Small Board locally using

```
(venv_smallboard)$ python manage.py runserver
```

You can view the app in your browser at [http://127.0.0.1:8000/]().


### Deployment to Heroku

Deploying the app to Heroku just requires pushing the code to the Heroku Git server. You need to be added as a collaborator for the Heroku app first. Please message one of the collaborators on this project to be added.

Once you've been added as a collaborator for the smallboard Heroku app, you can deploy changes by following [this guide](https://devcenter.heroku.com/articles/git). Install Git and the Heroku CLI. Then run

```
heroku login
heroku git:remote -a smallboard
```

After this, you can deploy changes by running

```
git push heroku master
```
