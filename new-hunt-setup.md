## Setting up Small Board for a new hunt

### Prerequisites

This guide assumes you have already configured Slack and Google API service accounts and have configured the following environment variables accordingly:

* `SLACK_API_TOKEN` - user token for user that installed the Slack app
* `SLACK_VERIFICATION_TOKEN` - for verifying Slack requests
* `GOOGLE_API_PRIVATE_KEY` - private key used for Google OAuth2 authentication
* `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` - Google OAuth2 client secret

To create service accounts and obtain these secrets, visit [https://api.slack.com/apps]() and [https://console.developers.google.com/]().


### New hunt setup

Currently, Small Board only supports one hunt at a time. (If you try to have multiple hunts, they may interfere with one another.) Thus, it's advisable to clear the database before each hunt. You can do this by running:

```
heroku run python manage.py flush
```

Small Board expects a hunt Google Drive folder to already be set up with a template spreadsheet in it (from which puzzle spreadsheets will be cloned). Small Board uses the list of users who have access to the Google Drive folder as the whitelist for authorizing users on login. Once you've created a hunt Google Drive folder and placed a template spreadsheet in it, you should set the following environment variables:

* `GOOGLE_DRIVE_HUNT_FOLDER_ID`
* `GOOGLE_SHEETS_TEMPLATE_FILE_ID`

You should also have created a Slack workspace for the puzzlehunt. Make sure you've set the following environment variable accordingly:

```
SLACK_BASE_URL=https://<your-slack-workspace>.slack.com
```

If you are reusing an existing workspace, make sure to delete all channels to avoid conflicts with puzzles in the new hunt. You can use [`slack.py`](https://github.com/santiagobasulto/slack.py) to easily delete channels.

You should now be able to login to your Small Board deployment, create a new hunt, and start adding puzzles. In case the hunt id of the newly created hunt is not `1`, update `ACTIVE_HUNT_ID` to the new hunt id (check the database).


### Giving a new user access to Small Board

The authorized users for a Small Board deployment are the Google users who have access to the Google Drive folder for the hunt (configured by the `GOOGLE_DRIVE_HUNT_FOLDER_ID` variable). To give a new user access, share the Google Drive folder with that user, and then restart Small Board using `heroku restart`.

The new user should also be invited to the Slack workspace in order to access the puzzle Slack channels.


### Other Configuration

Some other things you may want to tweak before hunt include:

* Setting `DEBUG=False`
* Increasing the number or tier of the dynos in your Heroku deployment
