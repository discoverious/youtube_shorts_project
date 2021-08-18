from PIL import Image
import pickle
from movie_creator.thumbnail_creator.design_engine.background_handler import BackgroundHandler
from movie_creator.thumbnail_creator.design_engine.foreground_handler import ForegroundHandler
from movie_creator.thumbnail_creator.design_engine.text_handler import TextHandler
from movie_creator.thumbnail_creator.design_engine.design_engine_utility import DesignEngineUtility
import os


class CoverDesignHandler:
    def __init__(self, canvas_width, canvas_height, track_title_font_name, musician_title_font_name):
        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Import secrets
        DB_DIR = os.path.join(BASE_DIR, '../../')
        self.base_path = f'{DB_DIR}/temperary_database'

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        # Instance to create background
        self.background_handler = BackgroundHandler(canvas_width=self.canvas_width,
                                                    canvas_height=self.canvas_height)

        # Instance to create foreground
        self.foreground_handler = ForegroundHandler(canvas_width=self.canvas_width,
                                                    canvas_height=self.canvas_height)

        # Instance for utility
        self.design_utility = DesignEngineUtility()

        # Instance for text
        self.text_handler = TextHandler(canvas_width=self.canvas_width,
                                        canvas_height=self.canvas_height,
                                        track_title_font_name=track_title_font_name,
                                        musician_title_font_name=musician_title_font_name)

    def load_track_data_list(self, file_name):
        with open(f"{self.base_path}/track_data_set/{file_name}.pkl", 'rb') as f:
            data_set = pickle.load(f)

        return data_set

    def cover_create_process(self, track_image_path, background_design_pattern, foreground_design_pattern, logo_image_path, track_title, musician_title, text_color, asset_image_path_list):
        # Load track cover image
        album_cover_image = Image.open(fp=track_image_path)

        # Create background image
        background_canvas = self.background_handler.background_create_process(design_pattern=background_design_pattern,
                                                                              track_cover_image=album_cover_image)

        # Create foreground image
        foreground_canvas, foreground_x, foreground_y = self.foreground_handler.foreground_create_process(design_pattern=foreground_design_pattern,
                                                                                                          track_cover_image=album_cover_image,
                                                                                                          image_size_ratio=0.75,
                                                                                                          positioning_style='center')

        foreground_y -= 60

        # Merge foreground, background
        image_composite_canvas = self.design_utility.alpha_merging(canvas=background_canvas,
                                                                   asset_image=foreground_canvas,
                                                                   x=foreground_x,
                                                                   y=foreground_y)

        # Todo Attach asset to canvas
        for asset_image_path in asset_image_path_list:
            asset_image = Image.open(fp=asset_image_path).convert('RGBA')

            center_x = self.canvas_width // 2 - asset_image.width // 2

            image_composite_canvas = self.design_utility.alpha_merging(canvas=image_composite_canvas,
                                                                       asset_image=asset_image,
                                                                       x=center_x,
                                                                       y=self.canvas_height - asset_image.height - 140)


        # Resize and attach logo to canvas
        logo_image = Image.open(fp=logo_image_path).convert('RGBA')
        logo_composite_canvas = self.design_utility.alpha_merging(canvas=image_composite_canvas,
                                                                  asset_image=logo_image,
                                                                  x=58,
                                                                  y=115)

        # Attach text
        text_canvas = self.text_handler.create_title_text(track_title=track_title,
                                                          musician_title=musician_title,
                                                          foreground_y=foreground_y,
                                                          text_color=text_color)

        text_composite_canvas = self.design_utility.alpha_merging(canvas=logo_composite_canvas,
                                                                  asset_image=text_canvas,
                                                                  x=0,
                                                                  y=0)

        text_composite_canvas.show()

        return text_composite_canvas


if __name__ == "__main__":
    # 2021_8_14_2_32_58
    file_name_selected = False

    while file_name_selected is True:
        print("기록한 플레이리스트 제목을 입력하시오. (ex: 2021_8_14_2_32_58.pkl )")
        file_name = input()



    cover_design_handler = CoverDesignHandler(canvas_width=450,
                                              canvas_height=900,
                                              track_title_font_name='Cafe24Oneprettynight.ttf',
                                              musician_title_font_name='Cafe24Oneprettynight.ttf')

    data_set = cover_design_handler.load_track_data_list(file_name='2021_8_14_2_32_58')

    b_path = '/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/temperary_database'

    print(data_set[0])

    #selected_data = data_set[0]

    for selected_data in data_set[:1]:
        composite_canvas_result = cover_design_handler.cover_create_process(track_image_path=f"{b_path}/album_cover_images/{selected_data['track_information_dict']['album_id']}.jpg",
                                                                            background_design_pattern='gradation',
                                                                            foreground_design_pattern='album_with_record',
                                                                            logo_image_path=f'{b_path}/asset_images/logo/logo.png',
                                                                            asset_image_path_list=[f'{b_path}/asset_images/player/player.png'],
                                                                            track_title=selected_data['track_information_dict']['track_title'],
                                                                            musician_title=selected_data['track_information_dict']['musician_title'],
                                                                            text_color=(255, 255, 255))



        #composite_canvas_result.save(f"{b_path}/test_results/{selected_data['track_information_dict']['track_id']}.png", quality=100)



