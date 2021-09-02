from movie_creator.thumbnail_creator.design_engine.foreground_protocol_handler import ForegroundProtocolHandler


class ForegroundHandler:
    def __init__(self, canvas_width, canvas_height):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        # Background creator
        self.foreground_creator = ForegroundProtocolHandler(canvas_width=canvas_width,
                                                            canvas_height=canvas_height)

    def set_position(self, positioning_style, foreground_canvas):
        # Set x, y position to attach
        x = 0
        y = 0

        if positioning_style == 'center':
            x = self.canvas_width // 2 - foreground_canvas.width // 2
            y = self.canvas_height // 2 - foreground_canvas.height // 2

        return x, y

    def resize_foreground_cavnas(self, image_size_ratio, foreground_canvas):
        if image_size_ratio != 1.0:
            foreground_width = int(self.canvas_width * image_size_ratio)
            foreground_height = int((foreground_width / foreground_canvas.width) * foreground_canvas.height)

            foreground_canvas = foreground_canvas.resize((foreground_width, foreground_height))

        return foreground_canvas

    def foreground_create_process(self, target_image, design_pattern, image_size_ratio, positioning_style):
        # Create foreground canvas
        foreground_canvas = self.foreground_creator.design_main_component(design_pattern=design_pattern,
                                                                          target_image=target_image)

        # Resize foreground canvas
        resized_foreground_canvas = self.resize_foreground_cavnas(image_size_ratio=image_size_ratio,
                                                                  foreground_canvas=foreground_canvas)

        # Set attaching position
        position_x, position_y = self.set_position(positioning_style=positioning_style,
                                                   foreground_canvas=resized_foreground_canvas)

        return resized_foreground_canvas, position_x, position_y
