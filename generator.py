import os
import random
import csv
from moviepy.editor import *
import configparser
import ast
from utils import *
import glob
import itertools

file_dir = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
config.read(os.path.join(file_dir, 'config.cfg'))

dim_str = config['Video']['resolution']
VIDEO_DIMENSIONS = ast.literal_eval(dim_str)

def generate_video(genre, index = 0) -> str:
    # Read the CSV and randomly select a row for data
    all_rows = []
    chosen_row = None
    csv_file = random.choice(glob.glob(TEXTS_PATH + genre + '/*.csv'))
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        all_rows = list(reader)
        if not all_rows:
            raise EmptyDataList(f"The CSV file of '{genre}' section is empty.")
        chosen_row = random.choice(all_rows)
        # all_rows.remove(chosen_row)  # Remove the chosen row

        # Define maximum width in characters
        max_chars_per_line = int(config['Text']['chars_per_line'])

        chosen_row = {key: wrap_text(value, max_chars_per_line) for key, value in chosen_row.items()}

    final_video_duration = 0
    if len(chosen_row.keys()) < 3:
        raise NoSuitableMedia("The CSV provided doesn't have at least 3 columns.")
    elif len(chosen_row.keys()) == 3:
        final_video_duration = int(config['Video']['slide_duration']) + int(config['Video']['slide_duration']) * 1.5
    else:
        final_video_duration = int(config['Video']['pause_before_first']) + int(config['Video']['slide_duration']) * len(chosen_row.keys())

    # Get a random background video that is long enough
    video_durations = {file: get_video_duration(BACKGROUND_VIDEO_PATH + genre + '/' + file) for file in os.listdir(BACKGROUND_VIDEO_PATH + genre)}
    accepted_videos = [file for file, duration in video_durations.items() if duration >= final_video_duration]
    if not accepted_videos:
        raise NoSuitableMedia(f"Couldn't find a background clip that is at least {final_video_duration}s long.")
    video_filename = random.choice(accepted_videos)

    # Get a random background song that is long enough
    audio_durations = {file: get_audio_duration(BACKGROUND_MUSIC_PATH + genre + '/' + file) for file in os.listdir(BACKGROUND_MUSIC_PATH + genre)}
    accepted_audio_files = [file for file, duration in audio_durations.items() if duration >= final_video_duration]
    music_filename = random.choice(accepted_audio_files)

    video = VideoFileClip(os.path.join(BACKGROUND_VIDEO_PATH + genre, video_filename))
    audio = AudioFileClip(os.path.join(BACKGROUND_MUSIC_PATH + genre, music_filename))

    # Set text overlays
    text_overlays = []
    title_txt = (TextClip(chosen_row["Title"], 
                          font = config['Text']['font_family'],
                          fontsize=int(config['Text']['font_size']), 
                          color=config['Text']['font_color'], 
                          stroke_color=config['Text']['stroke_color'], 
                          stroke_width=int(config['Text']['stroke_width']))
             .set_position(("center", 0.1), relative=True)
             .set_duration(final_video_duration)
             .set_start(0))
    if len(chosen_row.keys()) == 3:
        text_overlays.append(TextClip(next(itertools.islice(chosen_row.values(), 1, None)), 
                                      font = config['Text']['font_family'],
                                      fontsize=int(config['Text']['font_size']), 
                                      color=config['Text']['font_color'], 
                                      stroke_color=config['Text']['stroke_color'], 
                                      stroke_width=int(config['Text']['stroke_width']))
            .set_position(('center', 'center'))
            .set_duration(int(config['Video']['slide_duration']) * 1.5 - int(config['Video']['pause_before_first']))
            .set_start(int(config['Video']['pause_before_first'])))
        text_overlays.append(TextClip(next(itertools.islice(chosen_row.values(), 2, None)), 
                                      font = config['Text']['font_family'],
                                      fontsize=int(config['Text']['font_size']), 
                                      color=config['Text']['font_color'], 
                                      stroke_color=config['Text']['stroke_color'], 
                                      stroke_width=int(config['Text']['stroke_width']))
            .set_position(('center', 'center'))
            .set_duration(int(config['Video']['slide_duration']))
            .set_start(int(config['Video']['slide_duration']) * 1.5))
    else:
        for count, text_clip in enumerate(chosen_row):
            text_overlays.append(TextClip(chosen_row[text_clip], 
                                          font = config['Text']['font_family'],
                                          fontsize=int(config['Text']['font_size']), 
                                          color=config['Text']['font_color'], 
                                          stroke_color=config['Text']['stroke_color'], 
                                          stroke_width=int(config['Text']['stroke_width']))
                .set_position(('center', 'center'))
                .set_duration(int(config['Video']['slide_duration']))
                .set_start(int(config['Video']['pause_before_first'])) + count * int(config['Video']['slide_duration']))

    # Overlay text on video
    final_clips = [video, title_txt]
    final_clips.extend(text_overlays)
    final = CompositeVideoClip(final_clips).set_audio(audio).subclip(0, final_video_duration)

    # Resize to the YouTube Shorts aspect ratio and export
    final_path = genre + "_output_" + str(index) + ".mp4"
    final.resize(height=VIDEO_DIMENSIONS[1]).write_videofile(final_path, codec="libx264", audio_codec="aac")

    # Write the remaining rows back to the CSV
    # with open(TEXTS_PATH + genre + '.csv', 'w', newline='') as file:
    #     writer = csv.DictWriter(file, fieldnames=["Title", "Part 1", "Part 2"])
    #     writer.writeheader()
    #     for row in all_rows:
    #         writer.writerow(row)

    print("Video generation complete!")

    return final_path