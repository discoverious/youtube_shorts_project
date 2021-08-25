import os
import pickle
import time


if __name__ == "__main__":
    def convert_time_format(seconds):
        # Get mm and convert to string
        mm = int(seconds / 60)
        left_time = seconds - float(60 * mm)

        string_mm = '' + str(mm)
        while len(string_mm) < 2:
            string_mm = '0' + string_mm

        # Get ss
        ss = int(left_time)
        left_time -= float(ss)

        string_ss = '' + str(ss)
        while len(string_ss) < 2:
            string_ss = '0' + string_ss

        # Get xx
        xx = int(left_time * 100)

        string_xx = '' + str(xx)
        while len(string_xx) < 2:
            string_xx = '0' + string_xx

        # Convert to string form
        string_format_time = f"[{string_mm}:{string_ss}:{string_xx}]"

        return string_format_time

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
        print(f"곡 아이디: {track_data['track_information_dict']['track_id']} , 곡 제목 : {track_data['track_information_dict']['track_title']}")

    # Iter and get input
    input_track_title_list = list()
    input_over = False

    lyrics_data_list = list()

    while input_over is False:
        print("-" * 50)
        print(f"추가할 곡 아이디를 입력하시오. (ex: 5996469). 입력이 끝났으면 y를 눌러주십시오. 현재 추가된 곡: {input_track_title_list}")
        input_data = input()

        if input_data.lower() == 'y':
            input_over = True

        else:
            for track_data in track_data_list:
                # Append to lyrics data
                if int(track_data['track_information_dict']['track_id']) == int(input_data):
                    lyrics_data_list.append({'song_length': track_data['track_information_dict']['song_length_by_second'], 'lyrics_data': track_data['lyric_data']})

                    # Append to track name list
                    input_track_title_list.append(track_data['track_information_dict']['track_title'])

    result = ""
    last_time = 0.0

    for lyrics_data in lyrics_data_list:
        # Iterate merged lyrics
        for row in lyrics_data['lyrics_data']:
            current_second = float(row['time']) + last_time

            # Convert seconds to [mm:ss:xx]
            converted_time = convert_time_format(seconds=current_second)

            # Append to result
            result += f"{converted_time}{row['lyric']}\n"

        # Add last time
        last_time += float(lyrics_data['song_length'])

    # Set path to save
    save_path = os.path.join(ROOT_DIR, 'youtube_shorts_project/temperary_database/extracted_lyrics_set')

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    start_time = time.gmtime(time.time())
    file_name = f"{start_time.tm_year}_{start_time.tm_mon}_{start_time.tm_mday}_{start_time.tm_hour}_{start_time.tm_min}_{start_time.tm_sec}"

    # Create lrc data
    print('Creating lrc data @', f"{save_path}/{file_name}.lrc")
    with open(f"{save_path}/{file_name}.lrc", "w", encoding="UTF8") as file_handler:
        file_handler.write(result)

    '''
    print('Writing lrc data @', f"{save_path}/{file_name}.pkl")
    with open(f"{save_path}/{file_name}.lrc", "a", encoding="UTF8") as file_handler:
        for


        file_handler.write(s="")
    '''


