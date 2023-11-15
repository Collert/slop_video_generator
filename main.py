from generator import *
from utils import *
import configparser
import os

file_dir = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
config.read(os.path.join(file_dir, 'config.cfg'))

VIDEO_QUOTA_COST = 1600
AVAILABLE_QUOTA = int(config['Misc']['API_quota'])
GENRES = config['Misc']['genres'].split(',')

videos_per_genre = int(round(AVAILABLE_QUOTA / VIDEO_QUOTA_COST) / len(GENRES))

for genre in GENRES:
    yt_obj = auth_youtube(genre)
    for i in range(videos_per_genre):
        video_path = generate_video(genre, i)
        upload_video(yt_obj, video_path)
        if os.path.exists(video_path):
            os.remove(video_path)