from PIL import Image, ImageDraw, ImageFont
from movie_creator.thumbnail_creator.design_engine.text_wrapper import TextWrapper


class TextHandler:
    def __init__(self, canvas_width=None, canvas_height=None, track_title_font_name=None, musician_title_font_name=None, subtitle_font_name=None):
        self.canvas_width = canvas_width if canvas_width is not None else 400
        self.canvas_height = canvas_height if canvas_height is not None else 400

        # Set font setting
        self.font_base_path = '/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/temperary_database/fonts'

        track_title_font = None
        if track_title_font_name is not None: track_title_font = ImageFont.truetype(font=f"{self.font_base_path}/{track_title_font_name}", size=30)

        musician_title_font = None
        if musician_title_font_name is not None: musician_title_font = ImageFont.truetype(font=f"{self.font_base_path}/{musician_title_font_name}", size=23)

        subtitle_font = None
        if subtitle_font_name is not None: subtitle_font = ImageFont.truetype(font=f"{self.font_base_path}/{subtitle_font_name}", size=19)

        self.font_setting = {'track_title_font': track_title_font,
                             'musician_title_font': musician_title_font,
                             'subtitle_font': subtitle_font}

        # Set test canvas
        self.test_canvas = Image.new('RGBA',
                                     size=(self.canvas_width, self.canvas_height),
                                     color=(255, 255, 255) + (0,))

        self.test_drawing_canvas = ImageDraw.Draw(self.test_canvas)

        # Set bottom margin titles
        self.bottom_margin = {'track_title_font': int(self.canvas_height * 0.015),
                              'musician_title_font': int(self.canvas_height * 0.045),
                              'subtitle_font': None}

        # Set text wrapper
        self.text_wrapper = TextWrapper(font_setting=self.font_setting)

        # Set text
        self.space_between_lines = {'track_title_font': None,
                                    'musician_title_font': None,
                                    'subtitle_font': 10}

    def get_text_box_size(self, text, text_role):
        text_w, text_h = self.test_drawing_canvas.textsize(text=text,
                                                           font=self.font_setting[text_role])

        return text_w, text_h

    def set_text_position(self, text_role, text_w, text_h, target_y):
        # Set text x position
        text_x = int((self.canvas_width // 2) - (text_w // 2))

        # Set text y position
        text_y = target_y - self.bottom_margin[text_role] - text_h

        return text_x, text_y

    def create_subtitle_text(self, text, layout_width, layout_height):
        # Wrap lines
        text_role = 'subtitle_font'
        wrapped_line_list = self.text_wrapper.wrap_text(role=text_role,
                                                        text=text,
                                                        layout_width=layout_width,
                                                        layout_height=layout_height)

        # Var to contain canvas layout
        text_canvas_width = 0
        text_canvas_height = 0

        # Iter wrapped lines
        for index, wrapped_line in enumerate(wrapped_line_list):
            # Get box size of text
            text_w, text_h = self.get_text_box_size(text=wrapped_line['text'],
                                                    text_role='subtitle_font')

            # Set width, height of canvas
            text_canvas_width = max(text_canvas_width, text_w)
            text_canvas_height += text_h

            if index != (len(wrapped_line_list) - 1):
                text_canvas_height += self.space_between_lines[text_role]

        # Create canvas to contain text
        text_canvas = Image.new('RGBA',
                                size=(text_canvas_width, text_canvas_height),
                                color=(0, 0, 0) + (0,))

        text_drawing_canvas = ImageDraw.Draw(text_canvas)

        # Var to save last y
        last_text_position_y = 0

        for index, wrapped_line in enumerate(wrapped_line_list):
            # Get box size of text
            text_w, text_h = self.get_text_box_size(text=wrapped_line['text'],
                                                    text_role='subtitle_font')

            # Set x, y position
            text_x = int(text_canvas_width // 2 - text_w // 2)
            text_y = last_text_position_y

            # Draw text
            text_drawing_canvas.text(xy=(text_x, text_y),
                                     text=wrapped_line['text'],
                                     fill=(255, 255, 255, 255),
                                     font=self.font_setting['subtitle_font'],
                                     align="center")

            # Update y position
            last_text_position_y += (self.space_between_lines[text_role] + text_h)

        return text_canvas

    def create_title_text(self, track_title, musician_title, foreground_y, text_color):
        # Create dummy screen & drawing canvas to draw text
        dummy_canvas = Image.new('RGBA',
                                 size=(self.canvas_width, self.canvas_height),
                                 color=(255, 255, 255) + (0,))

        dummy_drawing_canvas = ImageDraw.Draw(dummy_canvas)

        # Get size of each text type
        track_title_text_w, track_title_text_h = self.get_text_box_size(text=track_title, text_role='track_title_font')
        musician_title_text_w, musician_title_text_h = self.get_text_box_size(text=musician_title, text_role='musician_title_font')

        # Set text position
        musician_title_text_x, musician_title_text_y = self.set_text_position(text_role='musician_title_font',
                                                                              text_w=musician_title_text_w,
                                                                              text_h=musician_title_text_h,
                                                                              target_y=foreground_y)

        track_title_text_x, track_title_text_y = self.set_text_position(text_role='track_title_font',
                                                                        text_w=track_title_text_w,
                                                                        text_h=track_title_text_h,
                                                                        target_y=musician_title_text_y)

        # Draw texts
        dummy_drawing_canvas.text(xy=(track_title_text_x, track_title_text_y),
                                  text=track_title,
                                  fill=text_color,
                                  font=self.font_setting['track_title_font'],
                                  align="center")

        dummy_drawing_canvas.text(xy=(musician_title_text_x, musician_title_text_y),
                                  text=musician_title,
                                  fill=text_color,
                                  font=self.font_setting['musician_title_font'],
                                  align="center")

        return dummy_canvas


if __name__ == "__main__":
    handler = TextHandler(subtitle_font_name='Cafe24Oneprettynight.ttf')

    subtitle_image = handler.create_subtitle_text(text='내가 이 구역의 미친 놈이다 이 시발련들아 나를 어떻게 할것이냐 니들이? 시발련들아 나를 어떻게 할것이냐 니들이?',
                                                  layout_width=200,
                                                  layout_height=300)
    subtitle_image.show()
