from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/photoslibrary']
PATH_TO_CREDENTIALS = 'googleCredentials.json'


def main(client_secrets_path, scopes):
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_path, scopes=scopes
    )

    flow.run_local_server()

    print("Access token: %s" % flow.credentials.token)
    print("Refresh token: %s" % flow.credentials.refresh_token)


if __name__ == "__main__":
    """
    To create json with credentials go: https://developers.google.com/photos/library/guides/get-started
    """
    print(f"Creating token for {PATH_TO_CREDENTIALS} to {'; '.join(SCOPES)}")
    main(PATH_TO_CREDENTIALS, SCOPES)
