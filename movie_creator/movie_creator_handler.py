from movie_creator.video_creator.video_handler import VideoHandler
from movie_creator.thumbnail_creator.cover_design_handler import CoverDesignHandler
from movie_creator.translator.translation_api_handler import TranslationApiHandler
import pickle
import os
import json


class MovieCreatorHandler:
    def __init__(self):
        # Instance of translator
        self.translator = TranslationApiHandler()

        # Font info for each language
        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Import secrets
        ROOT_DIR = os.path.dirname(BASE_DIR)
        SECRET_DIR = os.path.join(ROOT_DIR, 'youtube_shorts_project/.secrets')

        self.font_settings = json.load(open(os.path.join(SECRET_DIR, 'font_setting.json'), 'rb'))

        self.base_path = '/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/temperary_database'

    @staticmethod
    def convert_lyrics_data_to_list(lyric_data_list, clip_length):
        text_list = list()
        time_list = list()

        for lyric_data in lyric_data_list:
            if float(lyric_data['time']) <= clip_length:
                # Append text
                text_list.append(lyric_data['lyric'])

                # Append time
                time_list.append(float(lyric_data['time']))

        return text_list, time_list

    def music_video_creator_process(self, target_language_list, lyric_data_list, selected_track_info, clip_length):
        # Convert dict to list
        lyrics_text_list, lyrics_time_list = self.convert_lyrics_data_to_list(lyric_data_list=lyric_data_list, clip_length=clip_length)

        # Translate lyrics
        for target_language in target_language_list:
            # Get font setting for each language
            language_font_setting = self.font_settings[target_language]

            print(language_font_setting)

            # Create thumbnail
            cover_design_handler = CoverDesignHandler(canvas_width=450,
                                                      canvas_height=900,
                                                      track_title_font_name=language_font_setting['track_title_font']['name'],
                                                      musician_title_font_name=language_font_setting['musician_title_font']['name'])

            # Translate title, musician name
            translated_title = self.translator.translate_mono_sentence(text=selected_track_info['track_title'], target_language=target_language)
            translated_musician = self.translator.translate_mono_sentence(text=selected_track_info['musician_title'], target_language=target_language)

            # Create cover image
            cover_design = cover_design_handler.cover_create_process(track_image_path=f"{self.base_path}/album_cover_images/{selected_track_info['album_id']}.jpg",
                                                                     background_design_pattern='gradation',
                                                                     foreground_design_pattern='album_with_record',
                                                                     logo_image_path=f'{self.base_path}/asset_images/logo/logo.png',
                                                                     asset_image_path_list=[f'{self.base_path}/asset_images/player/player.png'],
                                                                     track_title=translated_title,
                                                                     musician_title=translated_musician,
                                                                     text_color=(255, 255, 255))

            # Translate korean to target language
            translated_lyrics_list = self.translator.get_translated_data_list(text_list=lyrics_text_list,
                                                                              target_language=target_language)

            # Create video
            video_handler = VideoHandler(subtitle_font_name=language_font_setting['subtitle_font']['name'])
            
            video_handler.video_create_process(cover_image=cover_design,
                                               music_file_path=f"{video_handler.base_path}/musics/{selected_track_info['track_id']}.wav",
                                               lyrics_text_list=translated_lyrics_list,
                                               lyrics_time_list=lyrics_time_list,
                                               music_length=clip_length,
                                               layout_x=57,
                                               layout_y=564,
                                               layout_width=337,
                                               layout_height=228,
                                               file_name=f"{self.base_path}/videos/{selected_track_info['track_id']}_{language_font_setting['name']}.webm")


if __name__ == "__main__":
    def load_track_file_list(file_name):
        base_path = '/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/temperary_database'

        with open(f"{base_path}/track_data_set/{file_name}.pkl", 'rb') as f:
            data_set = pickle.load(f)

        return data_set

    # Load track file list
    track_file_list = load_track_file_list(file_name='2021_8_14_2_32_58')[:1]

    # Set handler instance
    handler = MovieCreatorHandler()

    for track_data in track_file_list:
        handler.music_video_creator_process(target_language_list=['ja', 'vi', 'th', 'en'], #'id'
                                            lyric_data_list=track_data['lyric_data'][:10],
                                            selected_track_info=track_data['track_information_dict'],
                                            clip_length=60)

