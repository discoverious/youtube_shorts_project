from PIL import Image, ImageFilter
import numpy as np
from movie_creator.thumbnail_creator.design_engine.background_protocol_handler import BackgroundProtocolHandler


class BackgroundHandler:
    def __init__(self, canvas_width, canvas_height):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        # Background creator
        self.background_creator = BackgroundProtocolHandler(canvas_width=self.canvas_width,
                                                            canvas_height=self.canvas_height)

    def background_create_process(self, design_pattern, track_cover_image):
        # Create background canvas
        background_canvas = self.background_creator.design_main_component(design_pattern=design_pattern,
                                                                          track_cover_image=track_cover_image)

        background_canvas.putalpha(255)

        return background_canvas


if __name__ == "__main__":
    pass