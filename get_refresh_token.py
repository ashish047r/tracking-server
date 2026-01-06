from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/adwords"]

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": "89478597744-hcivgd8j7vrphds9nsgrkdhaoo1btrb3.apps.googleusercontent.com",
            "client_secret": "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",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    SCOPES,
)

creds = flow.run_local_server(port=0)

print("\n=== COPY THIS REFRESH TOKEN ===\n")
print(creds.refresh_token)
