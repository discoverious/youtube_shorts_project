import os
import pickle
import time


if __name__ == "__main__":
    def load_track_file_list(file_path):
        with open(file_path, 'rb') as f:
            data_set = pickle.load(f)

        return data_set

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Import secrets
    ROOT_DIR = os.path.dirname(BASE_DIR)
    TRACK_DIR = os.path.join(ROOT_DIR, 'youtube_shorts_project/temperary_database/track_data_set')

    track_data_list = list()

    # Iter path
    for (dirpath, dirnames, filenames) in os.walk(TRACK_DIR):
        for file_name in filenames:
            path_to_file = f"{dirpath}/{file_name}"

            # Load track files
            track_data_list += load_track_file_list(file_path=path_to_file)

    # Sort track data
    track_data_list = sorted(track_data_list, key=lambda k: int(k['track_information_dict']['track_id']))

    for idx, track_data in enumerate(track_data_list):
        print(track_data)
        print(f"곡 아이디: {track_data['track_information_dict']['track_id']} , 곡 제목 : {track_data['track_information_dict']['track_title']}")

    # Iter and get input
    input_track_id_list = list()
    input_over = False

    lyrics_data_list = list()

    while input_over is False:
        print("추가할 곡 아이디를 입력하시오. (ex: 5996469). 입력이 끝났으면 y를 눌러주십시오.")
        input_data = input()

        if input_data.lower() == 'y':
            input_over = True

        else:
            for track_data in track_data_list:
                if int(track_data['track_information_dict']['track_id']) == int(input_data):
                    lyrics_data_list.append({'song_length': track_data['track_information_dict']['song_length_by_second'], 'lyrics_data': track_data['lyric_data']})

    result = list()
    last_time = 0.0

    for lyrics_data in lyrics_data_list:
        print(lyrics_data)
        for row in lyrics_data['lyrics_data']:
            result.append({'time': float(row['time']) + float(last_time), 'lyric': row['lyric']})

        last_time += float(lyrics_data['song_length'])

    # Set path to save
    save_path = os.path.join(ROOT_DIR, 'youtube_shorts_project/temperary_database/extracted_lyrics_set')

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    start_time = time.gmtime(time.time())
    file_name = f"{start_time.tm_year}_{start_time.tm_mon}_{start_time.tm_mday}_{start_time.tm_hour}_{start_time.tm_min}_{start_time.tm_sec}"

    # Pickle data
    print('Pickling data @', f"{save_path}/{file_name}.pkl")

    file_handler = open(f"{save_path}/{file_name}.pkl", "wb")
    pickle.dump(result, file_handler, protocol=4)
    # pickle.dump(data, file_handler,protocol=4)
    file_handler.close()
    print("RE")

