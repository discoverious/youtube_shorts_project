from movie_creator.video_creator.video_handler import VideoHandler
from movie_creator.thumbnail_creator.cover_design_handler import CoverDesignHandler
from movie_creator.translator.translation_api_handler import TranslationApiHandler
from database_handler.mongo_db_handler import MongoDbHandler
import pickle
import os
import json
import random
import time


class ContentVideoCreatorHandler:
    def __init__(self):
        # Font info for each language
        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Import secrets
        ROOT_DIR = os.path.dirname(BASE_DIR)
        SECRET_DIR = os.path.join(ROOT_DIR, 'youtube_shorts_project/.secrets')
        DB_DIR = os.path.join(BASE_DIR, '')

        self.font_settings = json.load(open(os.path.join(SECRET_DIR, 'font_setting.json'), 'rb'))
        self.base_path = f'{DB_DIR}/temperary_database'
        self.target_country_code_list = ['ja', 'vi', 'th', 'en', 'id']

        # Set db handler instance
        self.db_handler = MongoDbHandler(initial_db_name="youtube_shorts_project")

    @staticmethod
    def create_file_name():
        start_time = time.gmtime(time.time())

        starting_time = str(start_time.tm_year) + '_' + str(start_time.tm_mon) + '_' + str(
            start_time.tm_mday) + '_' + str(start_time.tm_hour) + '_' + str(start_time.tm_min) + str(start_time.tm_sec)

        return starting_time

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

    def content_video_creator_process(self, target_language, contents_set, max_source_per_content):
        # Select sources
        selected_source_list = random.sample(contents_set, max_source_per_content)

        # Get font setting for each language
        language_font_setting = self.font_settings[target_language]

        # Instance to create thumbnail
        cover_design_handler = CoverDesignHandler(canvas_width=450,
                                                  canvas_height=900,
                                                  track_title_font_name=language_font_setting['track_title_font']['name'],
                                                  musician_title_font_name=language_font_setting['musician_title_font']['name'])

        # Hold cover designs
        cover_design_list = list()

        # Iter each sources
        for selected_source in selected_source_list:
            # Create cover image
            cover_design = cover_design_handler.content_cover_create_process(content_image_path=selected_source["tag"],
                                                                             background_design_pattern="plain_black",
                                                                             foreground_design_pattern="hold_in_target_box",
                                                                             logo_image_path=f'{self.base_path}/asset_images/logo/logo.png',
                                                                             content_title=selected_source["message"],
                                                                             text_color=(255, 255, 255))

            cover_design_list.append(cover_design)

        # Set save path
        video_save_path = f"{self.base_path}/content_videos/{language_font_setting['name']}"

        if not os.path.exists(video_save_path):
            os.makedirs(video_save_path)

        # Create and save video
        video_handler = VideoHandler(subtitle_font_name=language_font_setting['subtitle_font']['name'])
        video_handler.image_content_video_create_process(file_name=f"{video_save_path}/{self.create_file_name()}.webm",
                                                         contents_set=cover_design_list,
                                                         each_interval_time=5)

    def create_each_countries_content(self, max_source_per_content):
        for target_country_code in self.target_country_code_list:
            # Search data from database
            data_set = self.db_handler.search_list_of_records(column_name="twitter_contents",
                                                              query={"country_code": target_country_code,
                                                                     "uploaded": False,
                                                                     "type": 'image'})

            if len(data_set) != 0:
                self.content_video_creator_process(target_language=target_country_code,
                                                   contents_set=data_set,
                                                   max_source_per_content=max_source_per_content)

            # Todo 컨텐츠 만든거 db에서 uploaded True 로 업데이트 해줘야함


if __name__ == "__main__":
    # Set handler instance
    handler = ContentVideoCreatorHandler()
    handler.create_each_countries_content(max_source_per_content=5)

