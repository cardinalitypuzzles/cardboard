## Setting up smallboard for a new hunt

Currently, smallboard is not multi-tenant (#501), so each team for the same hunt needs their own smallboard instance.

### Prerequisites

This guide assumes you have already created the following at [https://console.developers.google.com/]():

* a Google Cloud project
* a Google API service account (go to APIs & Services > Credentials) under that project
* an OAuth 2.0 Client (also under APIs & Services > Credentials) in the same project

You will need to configure the following Google API environment variables in Heroku accordingly:

- `GOOGLE_API_PROJECT_ID` - the "Project ID" of the Google Cloud project your service account belongs to. You can find it under "Project info" on the Google Cloud dashboard for your project.
- `GOOGLE_API_CLIENT_ID` - the "Unique ID" found on your service account's "Details" page
- `GOOGLE_API_CLIENT_EMAIL` - email address of your service account (should end in `.iam.gserviceaccount.com`)
- `GOOGLE_API_PRIVATE_KEY_ID` - the 40-character hex id of the key you added on the "Keys" page of your service account
- `GOOGLE_API_PRIVATE_KEY` - the private key for the key you added, with newlines replaced with `\n` (should look something like `-----BEGIN PRIVATE KEY-----\n...<long base64-encoded key>...\n-----END PRIVATE KEY-----\n`)
- `GOOGLE_API_X509_CERT_URL` - the value of the `client_x509_cert_url` field in the downloaded JSON when you [created the key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys)
- `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` - this is the "Client ID" of the OAuth 2.0 Client you created on the API & Services > Credentials page.
- `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` - the "Client secret" for your OAuth2 Client (click on the Name of the OAuth2 Client you created on the APIs & Services > Credentials page, which will bring you to a details page that shows the Client secret)


### New hunt setup

Small Board expects a hunt Google Drive folder to already be set up with a template spreadsheet in it (from which puzzle spreadsheets will be cloned). Small Board uses the list of users who have access to the Google Drive folder as the whitelist for authorizing users on login. Once you've created a hunt Google Drive folder and placed a template spreadsheet in it, you should set the following environment variables:

- `GOOGLE_DRIVE_HUNT_FOLDER_ID`
- `GOOGLE_SHEETS_TEMPLATE_FILE_ID`

You should now be able to login to your Small Board deployment, create a new hunt, and start adding puzzles.

### Giving a new user access to Small Board

The authorized users for a Small Board deployment are the Google users who have access to the Google Drive folder for the hunt (configured by the `GOOGLE_DRIVE_HUNT_FOLDER_ID` variable). To give a new user access, share the Google Drive folder with that user, and then restart Small Board using `heroku restart`.

### Other Configuration

Some other things you may want to tweak before hunt include:

- Setting `DEBUG=False`
- Increasing the number or tier of the dynos in your Heroku deployment
