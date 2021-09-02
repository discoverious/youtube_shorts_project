from PIL import Image, ImageFilter
import numpy as np

from movie_creator.thumbnail_creator.design_engine.design_engine_utility import DesignEngineUtility
from movie_creator.thumbnail_creator.design_engine.image_color_net import ItemColorNet


class BackgroundProtocolHandler:
    def __init__(self, canvas_width, canvas_height):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.design_engine_utility = DesignEngineUtility()
        self.color_net = ItemColorNet()

    @staticmethod
    def get_gradient_2d(start, stop, width, height, is_horizontal):
        if is_horizontal:
            return np.tile(np.linspace(start, stop, width), (height, 1))
        else:
            return np.tile(np.linspace(start, stop, height), (width, 1)).T

    def get_gradient_3d(self, start_list, stop_list, is_horizontal_list):
        result = np.zeros((self.canvas_height, self.canvas_width, len(start_list)), dtype=np.float)

        for i, (start, stop, is_horizontal) in enumerate(zip(start_list, stop_list, is_horizontal_list)):
            result[:, :, i] = self.get_gradient_2d(start, stop, self.canvas_width, self.canvas_height, is_horizontal)

        return result

    def design_background_with_gradation(self, target_image):
        # Get color set of cover image
        color_set = self.color_net.get_clustered_color(pil_image=target_image)

        # Get specific color from gradation palette
        gradation_color_set = self.color_net.get_closest_color_from_gradation_palette(rgb=color_set['prime_color'])

        # Get gradation color canvas
        result = self.get_gradient_3d(start_list=gradation_color_set[1], #(199, 56, 102),
                                      stop_list=gradation_color_set[2],
                                      is_horizontal_list=(False, False, False))

        gradation_background_canvas = Image.fromarray(np.uint8(result))

        return gradation_background_canvas

    def design_plain_background(self, target_image):
        plain_background_canvas = Image.new(mode="RGBA",
                                            size=(self.canvas_width, self.canvas_height),
                                            color=(0, 0, 0, 255))

        return plain_background_canvas

    def design_main_component(self, design_pattern, target_image):
        if design_pattern == 'gradation':
            return self.design_background_with_gradation(target_image=target_image)

        if design_pattern == 'plain_black':
            return self.design_plain_background(target_image=target_image)


if __name__ == "__main__":
    b_path = '/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/temperary_database'
    album_cover_image = Image.open(fp=f'{b_path}/album_cover_images/20412824.jpg')

    album_cover_image.show()

    protocol_handler = BackgroundProtocolHandler(450, 900)
    im = protocol_handler.design_main_component(design_pattern='gradation',
                                                target_image=album_cover_image)

    im.show()

