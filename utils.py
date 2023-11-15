from moviepy.editor import VideoFileClip
from tinytag import TinyTag
import textwrap
import csv
import os
import googleapiclient.discovery
import googleapiclient.errors
import configparser
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import ResumableUploadError
from datetime import datetime
import random

file_dir = os.path.dirname(os.path.abspath(__file__))

BACKGROUND_VIDEO_PATH = os.path.join(file_dir, 'background/')
BACKGROUND_MUSIC_PATH = os.path.join(file_dir, 'audio/')
TEXTS_PATH = os.path.join(file_dir, 'text/')

config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
config.read(os.path.join(file_dir, 'config.cfg'))

class EmptyDataList(Exception):
    pass

class NoSuitableMedia(Exception):
    pass

def get_video_duration(file_path):
    with VideoFileClip(file_path) as video:
        return video.duration

def wrap_text(text, max_width):
    '''Wrap text with a new line inserted between lines that exceed max_width characters'''
    return '\n'.join(textwrap.wrap(text, width=max_width, break_long_words=False, replace_whitespace=False))    

def get_audio_duration(file_path):
    audio = TinyTag.get(file_path)
    return audio.duration  # Duration in seconds

def get_csv_column_count(file_path):
    with open(file_path, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        first_row = next(csvreader)
        column_count = len(first_row)
    return column_count

def check_available_quota():
    now = datetime.now()  # Or any other datetime object
    date_str = now.strftime('%Y-%m-%d')

def auth_youtube(genre): 
    # Disable OAuthlib's HTTPS verification when running locally.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = os.path.join(file_dir, config['Auth']['path_to_client_secret'])
    TOKEN_JSON_PATH = os.path.join(file_dir, f'tokens/{genre}.json')
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    # Get credentials and create an API client
    credentials = None
    # Check if token file exists and can be loaded.
    if os.path.exists(TOKEN_JSON_PATH):
        credentials = Credentials.from_authorized_user_file(TOKEN_JSON_PATH, SCOPES)
        print("Loaded credentials from file.")

    # for attr_name in dir(credentials):
    #     # Filter out special methods (optional)
    #     if not attr_name.startswith('__'):
    #         # Get the value of the attribute
    #         attr_value = getattr(credentials, attr_name)
    #         print(f"{attr_name}: {attr_value}")

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        print(f"Credentials are invalid or do not exist for {genre} chanel.")
        if credentials and credentials.refresh_token:
            print("Refreshing credentials...")
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES
            )
            # This is where the access_type='offline' should be placed.
            credentials = flow.run_local_server(port=0, access_type='offline', prompt='consent')
            # Save the credentials for the next run
            with open(TOKEN_JSON_PATH, 'w') as token:
                token.write(credentials.to_json())
            print("Saved new credentials to token.json")

    if not credentials.refresh_token:
        print("No refresh token is available. Credentials may not be valid for future use.")
    else:
        print("Refresh token is available in the credentials.")

    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

def upload_video(yt_obj, video_path):
    genre = video_path.split('_')[0]
    request_body = {
        'snippet': {
            'categoryI': 22,
            'title': 'Placeholder video title',
            'description': 'Placeholder video description',
            'tags': ['placeholder', 'tags']
        },
        'status': {
            'privacyStatus': 'public',  # or 'private' or 'unlisted'
            'madeForKids': False,
        }
    }
    for attribute in ["title", "description", "tags"]:
        with open(f"{TEXTS_PATH}{genre}/titles/{attribute}{'s' if attribute != 'tags' else ''}.csv", 'r') as file:
            tags = []
            reader = csv.DictReader(file)
            all_rows = list(reader)
            if not all_rows:
                raise EmptyDataList(f"The CSV file of '{genre}' section is empty.")
            if attribute == "tags":
                for _ in range(20):
                    chosen_row = random.choice(all_rows)
                    tags.append(chosen_row["tag"])
                request_body['snippet'][attribute] = tags
            else:
                chosen_row = random.choice(all_rows)
                request_body['snippet'][attribute] = chosen_row[attribute]

    media_file = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    try:
        print("Starting upload...")
        response_upload = yt_obj.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media_file
        ).execute()
        print(f"Video uploaded to {genre} chanel.")
    except ResumableUploadError:
        print("Out of quota for today.")
        pass