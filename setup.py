import os
import csv
import configparser

genres = []

genre_in = input("Enter genre/chanel name: ")
while True:
    if genre_in == '':
        break
    genres.append(genre_in.lower())
    genre_in = input("Enter another genre (leave empty and press Enter to finish): ")

for dir in ["background", "audio", "text", "tokens"]:
    try:
        os.mkdir(dir)
    except FileExistsError:
        pass

for genre in genres:
    os.mkdir(f"background/{genre.replace(' ', '_')}")
    os.mkdir(f"audio/{genre.replace(' ', '_')}")
    os.mkdir(f"text/{genre.replace(' ', '_')}")
    os.mkdir(f"text/{genre.replace(' ', '_')}/titles")
    with open(f"text/{genre.replace(' ', '_')}/1.csv", "w") as _: 
        pass 
    for data in ["title","description","tag"]:
        with open(f"text/{genre.replace(' ', '_')}/titles/{data.lower()}s.csv", "w") as titles_file: 
            titles_data = [
                [data],
                [f"Example video {data.lower()} 1"],
                [f"Example video {data.lower()} 2"],
                [f"Example video {data.lower()} 3"]
            ]
            writer = csv.writer(titles_file)
            writer.writerows(titles_data)

genres_str = ','.join(genres)
config = configparser.ConfigParser()
config.read('config.cfg')
config['Misc']['genres'] = genres_str
with open('config.cfg', 'w') as configfile:
    config.write(configfile)

print("\nSetup successful! Now, populate the folders with video clips, songs, and CSV files with data.\nFor best results, make sure you crop your videos the way you want them to look, as well as trim your audio to the most engaging part.")