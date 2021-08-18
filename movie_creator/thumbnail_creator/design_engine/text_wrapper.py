from PIL import Image, ImageDraw


class TextWrapper():
    def __init__(self, font_setting):
        self.font_setting = font_setting

        self.drawing_canvas = ImageDraw.Draw(
            Image.new(
                mode='RGB',
                size=(500, 500)
            )
        )

        self.space_length = self.get_space_length()

    def get_space_length(self):
        space_length = dict()

        for role, each_font_setting in self.font_setting.items():
            if each_font_setting is not None:
                space_length[role] = dict()

                space_w, space_h = self.drawing_canvas.textsize(text=' ', font=each_font_setting)

                space_length[role]['w'] = space_w
                space_length[role]['h'] = space_h

        return space_length

    def get_text_length(self, text, role):
        text_w, text_h = self.drawing_canvas.textsize(text=text,
                                                      font=self.font_setting[role])

        return {'text_w': text_w, 'text_h': text_h}

    def wrap_text(self, role, text, layout_width, layout_height):
        max_length = max(layout_width, layout_height)

        text_lines = [' '.join([w.strip() for w in l.split(' ') if w]) for l in text.split('\n') if l]

        wrapped_lines = []
        max_height = 0
        max_width = 0

        buf = []
        buf_length = 0

        for line in text_lines:
            for word in line.split(' '):
                word_length = self.get_text_length(text=word, role=role)

                word_width = word_length['text_w']

                expected_length = word_width if not buf else \
                    buf_length + self.space_length[role]['w'] + word_width

                if expected_length <= max_length:
                    # word fits in line
                    buf_length = expected_length
                    buf.append(word)
                else:
                    # word doesn't fit in line
                    wrapped_lines.append({'text': ' '.join(buf), 'text_w': word_length['text_w'],
                                          'text_h': word_length['text_h']})

                    # update max width, max height
                    if word_length['text_w'] > max_width:
                        max_width = word_length['text_w']

                    if word_length['text_h'] > max_height:
                        max_height = word_length['text_h']

                    buf = [word]
                    buf_length = word_width

            if buf:
                buf_text = ' '.join(buf)

                word_length = self.get_text_length(text=buf_text, role=role)

                wrapped_lines.append({'text': buf_text, 'text_w': word_length['text_w'],
                                      'text_h': word_length['text_h']})

                # update max width, max height
                if word_length['text_w'] > max_width:
                    max_width = word_length['text_w']

                if word_length['text_h'] > max_height:
                    max_height = word_length['text_h']

                buf = []
                buf_length = 0

        return wrapped_lines
