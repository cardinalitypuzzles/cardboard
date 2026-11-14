## Setting up Cardboard

Before starting your Cardboard server:

### Google Cloud integration

Do the following at https://console.developers.google.com/:

* Create a Google Cloud project
* Create a Google API service account (APIs & Services > Credentials) under that project
* Create an OAuth 2.0 Client (APIs & Services > Credentials)
* Enable **Google Drive API** (APIs & Services > Library)
* Enable **Drive Activity API** (APIs & Services > Library)
* Enable **People API** (APIs & Services > Library)
* Enable **Google Sheets API** (APIs & Services > Library)

### Discord integration (optional)

* Set up a Discord application (https://discord.com/developers/applications)
* Create a bot for your application (can be done on the "Bot" settings page)
* Invite the application to your Discord server. To do so, go to the OAuth2 > URL Generator settings page for your application. For "Scopes", select "bot" and "applications.commands". After selecting "bot", a "Bot permissions" panel will appear, where you should select "Administrator". Copy the URL that was generated and open it in a new tab. There you can select the Discord server to add the app to. For more details, see [here](https://discordjs.guide/preparations/adding-your-bot-to-servers.html).

### Google Drive setup

* Create a new Google Drive folder for the hunt
* Add the Google API service account you created above as an Editor to the Drive folder
* Add all your team members as Editors to the Drive folder.
  * Users can login to Cardboard only if they have access to the Google Drive folder.
  * Note that adding a Google Group will *not* propagate down permissions to members of the group!
* Add a template spreadsheet file to the Drive folder

### Google OAuth2 login (optional)

* Add the URI `https://[app domain]/complete/google-oauth2/` under the "Authorized redirect URIs" in your OAuth 2.0 client settings. On Google Cloud: APIs & Services > Credentials > (click the name of the OAuth 2.0 Client you added) > scroll down to the "Authorized redirect URIs" section.
* If you skip this step, your administrator will have to manually create logins through the Django admin interface.

-----

Now you're ready to run the server.

### Using Heroku

Follow the Heroku documentation to [set up a Heroku app](https://devcenter.heroku.com/articles/git#for-an-existing-app) from an existing repository (this one).

After creating a new application on Heroku, you will need to configure some resources, settings, and config variables.

By default, Heroku may only set the heroku/nodejs buildpack when you deploy the first time, but Cardboard also requires the heroku/python buildpack. You can set the buildpacks on your application's settings page (`https://dashboard.heroku.com/apps/<YOUR_APP>/settings`) under the "Buildpacks" section. They should be set **in the following order**, mimicking the [app.json](https://github.com/cardinalitypuzzles/cardboard/blob/master/app.json) file in the repository:

  1. heroku/nodejs
  2. heroku/python

Alternatively, you can use the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli): run `heroku buildpacks` to check which buildpacks are installed, and if needed, run `heroku buildpacks:add` to add any missing ones. Make sure again that they are in the correct order.

On the Resources page, you'll need to add the Heroku Postgres and [Heroku Redis](https://elements.heroku.com/addons/heroku-redis) add-ons. When added, this will automatically add some config variables for you on the Settings page: `REDIS_URL`, `REDIS_TLS_URL`, and `DATABASE_URL`. Cardboard is already configured to read these config variables automatically.

You'll also see a few dyno instances on the Resources page: "web", "bot", and "worker". Make sure to enable the "web" and "worker" dynos. The "web" dyno runs the web application and the "worker" dyno runs a Celery process that handles Google Sheets and Discord API interactions asynchronously. The "bot" dyno is for a discord bot added in [#214](https://github.com/cardinalitypuzzles/cardboard/issues/214), which is optional. You can only run a max of 2 free dynos, so if you want to enable the "bot" dyno, you have to upgrade to a paid tier. Note that this "bot" dyno is only for supporting users typing `!<command>` in Discord to get information about puzzles. Even without the "bot" dyno, with the Discord application added to your Discord server (see Discord prerequisites above) and the Discord environment variables configured (see below), you will still get automatic Discord channel creation and puzzle solve updates.

If you have a large team or are using Cardboard for a hunt with many puzzles, you may want to increase the number or tier of the dynos in your Heroku deployment.

### Using Google Cloud Run

#### Setup

All operations should be performed on the same project.

1. Enable APIs ( https://console.cloud.google.com/apis/dashboard )
    - Cloud Run Admin API (run.googleapis.com)
    - Cloud SQL Admin API (sqladmin.googleapis.com)
    - Google Cloud Memorystore for Redis API (redis.googleapis.com)
1. `cp cloud-run/.env.template.yaml  cloud-run/.env.yaml`
1. Create the Redis instance ( https://console.cloud.google.com/memorystore/redis/instances )
    - Tier Selection: Basic
    - Capacity: 1 GB (the minimum)
1. `cloud-run/.env.yaml`

    ```yaml
    - name: REDIS_URL
      value: redis://<primary endpoint>
    ```

1. Create the Cloud SQL instance ( https://console.cloud.google.com/sql/instances )
    - Choose PostgreSQL
    - Cloud SQL edition: Enterprise
    - Zonal availability: Single zone
    - Machine: "General purpose - Shared core" - 1 vCPU, 0.614GB (db-f1-micro)
    - Storage: HDD
1. Create SQL user
1. Create SQL database (the migrations will populate the schema)
1. `cloud-run/.env.yaml`

    ```yaml
    - name: DATABASE_URL
      value: postgres://<username>:<password>@<instance name>/<dbname>
    ```

1. Configure cloud-run/.env.yaml

#### Build and Deploy
These environment variables are used in the build and deploy scripts only.
- `CARDBOARD_CR_SERVICE_ACCOUNT` - Google Service Account email (needs permission to the Cloud SQL instance)
- `CARDBOARD_CR_DOCKER_REPOSITORY` - The image name to build, `:<tag>` is appended to this to construct the full image name. Must be readable by Cloud Run. Artifact Registry is suggested, but not required.
- `CARDBOARD_CR_PROJECT` - The Google project id (not name or number)
- `CARDBOARD_CR_DB_INSTANCE` - The Cloud SQL Connection name, available on the instance overview page.

##### Requirements
- `gcloud` ( https://docs.cloud.google.com/sdk/docs/install-sdk )
- `yq` ( https://mikefarah.gitbook.io/yq )

##### Commands
Commands must be run from the repository root.
1. `./cloud-run/bin/build.sh` builds the docker image and does a `docker push`
    - Tag is autogenerated, in the format: `vYYYYMMDDHHMMSS`
    - Last line of output is the deploy command, with the version parameter prepopulated.
1. `./cloud-run/bin/deploy.sh v20261112182008`

-----

## Configuring Cardboard

Cardboard is configured via a combination of global environmental variables and per-hunt variables (called `HuntSettings`) in the Django admin.

### Admin accounts

Cardboard automatically creates an account with username `admin`. The account password is in `docker-compose.yaml`.

You can use the Django interface at `https://[app domain]/admin` to mark a user as staff or admin, logging in with the `admin` account.

Alternatively, if you're comfortable using the shell, you can run `python manage.py shell` and then type these commands:

```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(email=<YOUR EMAIL ADDRESS HERE>)
user.is_staff = True
user.is_admin = True
user.is_superuser = True
user.save()
```

### Hunt Settings

The page to edit hunt settings is visible to all staff users and above from the hunt index page or at `/hunts/<slug>/edit`.

### Discord setup

To connect a hunt with a discord server, fill out the following fields

* **Discord guild id:** your server id. It's usually part of the URL when you're in your server: `discord.com/channels/<server_id>/<channel_id>`. You can also find it on the "Widget" page in your Server Settings.
* **Discord puzzle announcements channel id:**  this is the id of the channel you want puzzle announcements (puzzle unlocked, solved, etc.) to be posted. The channel id can be found in the URL when in the channel: `discord.com/channels/<server_id>/<channel_id>`. You probably want to set this to something separate from the channel where you make human announcements or have general discussions since the puzzle announcements can be a bit noisy (users may want to mute the channel).
* **Discord metas category:** category to create text & voice channels for metas (defaults to "metas")
* **Discord unassigned text category:** category to create text channels for unassigned feeders under (defaults to "text [unassigned]")
* **Discord unassigned voice category:** category to create voice channels for unassigned feeders under (defaults to "voice [unassigned]")
* **Discord archive category:** category to archive solved puzzles' text and voice channels under (defaults to "archive")
* **Discord devs role:** the Discord role to tell users to ping in case of issues opening a puzzle's sheet link (defaults to "dev")

### Google Drive setup

For the Google Drive/Sheets integration, fill out the following fields. Many of them can also be configured as global config variables in Heroku, below; the values in the Django admin will take precedence.

* **Google Drive folder id:** the id of your Google Drive folder, should be part of the URL (`https://drive.google.com/drive/folders/<folder_id>`). This folder is where puzzle spreadsheets will be stored, and access to this folder determines login access to Cardboard.
* **Google Sheets template file id:** the id of your Google Sheets template file, should be part of the URL (`https://docs.google.com/spreadsheets/d/<sheet_id>`)
* **Google Sheets template folder id:** the id of a Google Drive folder where extra Sheet templates can be found. If this folder is not empty, Cardboard will rename and move one of these sheets when a new puzzle is created, instead of copying the template file. This maybe be useful because of #372, where scripts in Google sheets will stop working on new sheets if you create too many in one day. This way you can create sheets in advance to get around the daily limits.
* **Google Drive human URL:** the URL of a Google Drive folder where human-generated files can be uploaded. This folder is linked at the top of Cardboard. If this value is not set, there will not be a link to the folder.

###### Recent editor tracking

The active user lookback sets how recently an user needed to have edited a sheet to be considered a "recent editor." This will not work without the Celery task below for activity tracking.

##### Config variables

For logging in using Google accounts:

* `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` - this is the "Client ID" of the OAuth 2.0 Client you created on the API & Services > Credentials page.
* `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` - the "Client secret" for your OAuth2 Client (click on the Name of the OAuth2 Client you created on the APIs & Services > Credentials page, which will bring you to a details page that shows the Client secret)

For automatic Google Sheets creation:

* `GOOGLE_API_PROJECT_ID` - the "Project ID" of the Google Cloud project your service account belongs to. You can find it under "Project info" on the Google Cloud dashboard for your project.
* `GOOGLE_API_CLIENT_ID` - the "Unique ID" found on your service account's "Details" page
* `GOOGLE_API_CLIENT_EMAIL` - email address of your service account (should end in `.iam.gserviceaccount.com`)
* `GOOGLE_API_PRIVATE_KEY_ID` - the 40-character hex id of the key you added on the "Keys" page of your service account
* `GOOGLE_API_PRIVATE_KEY` - the private key for the key you added, with newlines replaced with `\n` (should be the value of the `private_key` field in the downloaded JSON when you [created the key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys); should look something like `-----BEGIN ... KEY-----\n...<long base64-encoded key>...\n-----END ... KEY-----\n`)
* `GOOGLE_API_X509_CERT_URL` - the value of the `client_x509_cert_url` field in the downloaded JSON when you [created the key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys)

For Discord integration:

* `DISCORD_API_TOKEN` - This is the "Token" for your bot, which you can find on the "Bot" settings page (you may have to click "Click to Reveal Token")

Miscellaneous:

* `DJANGO_SECRET_KEY` - used by Django to generate secrets, such as for user sessions. It's best to set this so that user sessions will not expire after each restart. You can generate a key using `python -c "import secrets; print(secrets.token_urlsafe())"`.
* `DEBUG` - you probably want to set this to `False` in production so users don't get gory error pages and so profiling is disabled.
* `APP_TITLE` - app title for page titles and headers
* `APP_SHORT_TITLE` - short version of the app title for the nav bar
* `CONTACT_AUTHOR_NAME` - contact name for privacy statement
* `CONTACT_EMAIL` - contact email for login help and privacy statement

#### Discord role pings

To associate Discord roles with Cardboard tags, so that puzzles with certain tags will ping certain roles (for example, a "comic books" Cardboard tag could ping the "@comics" Discord role), you must use the Django admin.

* Log in to the Django admin page for your Cardboard instance at `/admin`
* Go to the ChatRole tab on the left (located at `/admin/chat/chatrole`)
* Add a Chat Role for each Cardboard tag/Discord role relationship that you want to set up. The Cardboard tag name should go as "Name", and the role id is found in Discord via right-clicking a role and selecting "Copy ID", or Server Settings > Roles > ... > Copy ID.
  * You may especially want to do this for some or all of the default role tags, found in [puzzles/puzzle_tag.py](https://github.com/cardinalitypuzzles/cardboard/blob/master/puzzles/puzzle_tag.py)

#### Google Sheets activity tracking

Tracking recent editors of the Google sheets is done through the Celery task [google_api_lib.tasks.update_active_users](https://github.com/cardinalitypuzzles/cardboard/blob/master/google_api_lib/tasks.py). The task must be scheduled after the hunt is created through the Django admin:

1. In the admin page, click "Periodic tasks" and add a new task.
2. Fill out the name.
3. Pick `google_api_lib.tasks.update_active_users` under "Task (registered)"
4. Pick a interval schedule, creating a new one if needed (we recommend 60 seconds)
5. Pick a time for "Start Datetime:" for when the task should start
6. Under "Arguments", give the hunt ID of the hunt to be tracked under "Keyword Arguments" as a dictionary, i.e. `{"hunt_id": 1}`
7. Save.

### Giving a new user access to Cardboard

Share the Google Drive folder with that user and re-sync the permissions on the edit page.
