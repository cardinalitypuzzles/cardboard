## Setting up Cardboard for a new hunt

Currently, Cardboard is not multi-tenant (see [#191](https://github.com/cardinalitypuzzles/cardboard/issues/191)), so each team for the same hunt needs their own Cardboard instance.

### Prerequisites

This guide assumes you have already done the following at https://console.developers.google.com/:

* created a Google Cloud project
* created a Google API service account (go to APIs & Services > Credentials) under that project
* created an OAuth 2.0 Client (also under APIs & Services > Credentials) in the same project (this is needed to enable logging to Cardboard using a Google account)
* enabled Google Drive API (APIs & Services > Library > search for "Google Drive API" > select and enable)
* enabled Google Sheets API (APIs & Services > Library > search for "Google Sheets API" > select and enable)

#### Discord prerequisites

For Discord integration (optional), you will additionally need to set up:

* a Discord application at https://discord.com/developers/applications
* a bot for your application (can be done on the "Bot" settings page)
* invite the application to your Discord server. To do so, go to the OAuth2 > URL Generator settings page for your application. For "Scopes", select "bot" and "applications.commands". After selecting "bot", a "Bot permissions" panel will appear, where you should select "Administrator". Copy the URL that was generated and open it in a new tab. There you can select the Discord server to add the app to. For more details, see [here](https://discordjs.guide/preparations/adding-your-bot-to-servers.html).


### New hunt setup

#### Google Drive setup

Cardboard expects a hunt Google Drive folder to already be set up with a template spreadsheet in it (from which puzzle spreadsheets will be cloned). Cardboard uses the list of users who have access to the Google Drive folder as the whitelist for authorizing users on login.

To set up a new hunt:

* create a new Google Drive folder for the hunt. Do not change the permissions on the folder; it should be private for now.
* add the Google API service account you created above as an Editor to the Drive folder
* add all your team members as Editors to the Drive folder
* add a template Sheet file to the Drive folder


#### Google OAuth2 login setup

In order for Google OAuth2 login to work, you need to add the URI `https://<YOUR_APP>.herokuapp.com/complete/google-oauth2/` under the "Authorized redirect URIs" in your OAuth 2.0 client settings. You can do this on Google Cloud: APIs & Services > Credentials > click the name of the OAuth 2.0 Client you added > scroll down to the "Authorized redirect URIs" section.


#### Heroku setup

After creating a new application on Heroku, you will need to configure some resources, settings, and config variables.

By default, Heroku may only set the heroku/nodejs buildpack when you deploy the first time, but Cardboard also requires the heroku/python buildpack and a buildpack specific to Python poetry. You can set the buildpacks on your application's settings page (`https://dashboard.heorku.com/apps/<YOUR_APP>/settings`) under the "Buildpacks" section. They should be set **in the following order**, mimicking the [app.json](https://github.com/cardinalitypuzzles/cardboard/blob/master/app.json) file in the repository:

  1. heroku/nodejs
  2. https://github.com/cardinalitypuzzles/python-poetry-buildpack.git
  3. heroku/python

Alternatively, you can use the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli): run `heroku buildpacks` to check which buildpacks are installed, and if needed, run `heroku buildpacks:add` to add any missing ones. Make sure again that they are in the correct order.

On the Resources page, you'll need to add the Heroku Postgres and Heroku Redis add-ons. When added, this will automatically add some config variables for you on the Settings page: `REDIS_URL`, `REDIS_TLS_URL`, and `DATABASE_URL`. Cardboard is already configured to read these config variables automatically.

You'll also see three dyno instances on the Resources page: "web", "bot", and "worker". Make sure to enable the "web" and "worker" dynos. The "web" dyno runs the web application and the "worker" dyno runs a Celery process that handles Google Sheets API interactions asynchronously. The "bot" dyno is for a discord bot added in [#214](https://github.com/cardinalitypuzzles/cardboard/issues/214), which is optional. You can only run a max of 2 free dynos, so if you want to enable the "bot" dyno, you have to upgrade to a paid tier. Note that this "bot" dyno is only for supporting users typing `!<command>` in Discord to get information about puzzles. Even without the "bot" dyno, with the Discord application added to your Discord server (see Discord prerequisites above) and the Discord environment variables configured (see below), you will still get automatic Discord channel creation and puzzle solve updates.

If you have a large team or are using Cardboard for a hunt with many puzzles, you may want to increase the number or tier of the dynos in your Heroku deployment.

##### Heroku config variables

Settings to enable logging in using a Google account:

* `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` - this is the "Client ID" of the OAuth 2.0 Client you created on the API & Services > Credentials page.
* `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` - the "Client secret" for your OAuth2 Client (click on the Name of the OAuth2 Client you created on the APIs & Services > Credentials page, which will bring you to a details page that shows the Client secret)

Google Drive, Sheets, and API settings for automatic sheets creation:

* `GOOGLE_DRIVE_HUNT_FOLDER_ID` - the id of your Google Drive folder, should be part of the URL (`https://drive.google.com/drive/folders/<folder_id>`)
* `GOOGLE_SHEETS_TEMPLATE_FILE_ID` - the id of your Google Sheets template file, should be part of the URL (`https://docs.google.com/spreadsheets/d/<sheet_id>`)
* `GOOGLE_API_PROJECT_ID` - the "Project ID" of the Google Cloud project your service account belongs to. You can find it under "Project info" on the Google Cloud dashboard for your project.
* `GOOGLE_API_CLIENT_ID` - the "Unique ID" found on your service account's "Details" page
* `GOOGLE_API_CLIENT_EMAIL` - email address of your service account (should end in `.iam.gserviceaccount.com`)
* `GOOGLE_API_PRIVATE_KEY_ID` - the 40-character hex id of the key you added on the "Keys" page of your service account
* `GOOGLE_API_PRIVATE_KEY` - the private key for the key you added, with newlines replaced with `\n` (should be the value of the `private_key` field in the downloaded JSON when you [created the key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys); should look something like `-----BEGIN ... KEY-----\n...<long base64-encoded key>...\n-----END ... KEY-----\n`)
* `GOOGLE_API_X509_CERT_URL` - the value of the `client_x509_cert_url` field in the downloaded JSON when you [created the key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys)

For Discord integration:

* `DISCORD_API_TOKEN` - This is the "Token" for your bot, which you can find on the "Bot" settings page (you may have to click "Click to Reveal Token")
* `DISCORD_GUILD_ID` - your server id. It's usually part of the URL when you're in your server: `discord.com/channels/<server_id>/<channel_id>`. You can also find it on the "Widget" page in your Server Settings.
* `DISCORD_PUZZLE_ANNOUNCEMENTS_CHANNEL` - this is the id of the channel you want puzzle announcements (puzzle unlocked, solved, etc.) to be posted. The channel id can be found in the URL when in the channel: `discord.com/channels/<server_id>/<channel_id>`. You probably want to set this to something separate from the channel where you make human announcements or have general discussions since the puzzle announcements can be a bit noisy (users may want to mute the channel).
* `DISCORD_TEXT_CATEGORY` - category to create text channels for puzzles under (defaults to "text [puzzles]")
* `DISCORD_VOICE_CATEGORY` - category to create voice channels for puzzles under (defaults to "voice [puzzles]")
* `DISCORD_ARCHIVE_CATEGORY` - category to archive solved puzzles' text and voice channels under (defaults to "archive")
* `DISCORD_DEVS_ROLE` - the Discord role to tell users to ping in case of issues opening a puzzle's sheet link (defaults to "dev")

Miscellaneous configs:

* `DJANGO_SECRET_KEY` - used by Django to generate secrets, such as for user sessions. It's best to set this so that user sessions will not expire after each restart. You can generate a key using `python -c "import secrets; print(secrets.token_urlsafe())"`.
* `DEBUG` - you probably want to set this to `False` in production so users don't get gory error pages

### Discord setup

In addition to setting the environmental variables above, you can also set up Cardboard to ping specific Discord roles when puzzles are tagged with certain tags. To do this, you must have an admin account in your Cardboard instance:

* Start `python manage.py shell`. If you are using Heroku, you can do this by running `heroku run python manage.py shell`
* Enter and run the following Python code:

```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(email=<YOUR EMAIL ADDRESS HERE>)
user.is_staff = True
user.is_admin = True
user.is_superuser = True
user.save()
```

Then to associate the Discord roles with Cardboard tags:

* Log in to the Django admin page for your Cardboard instance at `/admin`
* Go to the ChatRole tab on the left (located at `/admin/chat/chatrole`)
* Add a Chat Role for each Cardboard tag/Discord role relationship that you want to set up. The Cardboard tag name should go as "Name", and the role id is found in Discord via right-clicking a role and selecting "Copy ID", or Server Settings > Roles > ... > Copy ID. 

### Giving a new user access to Cardboard

The authorized users for a Cardboard deployment are the Google users who have access to the Google Drive folder for the hunt (configured by the `GOOGLE_DRIVE_HUNT_FOLDER_ID` variable). To give a new user access, simply share the Google Drive folder with that user.
