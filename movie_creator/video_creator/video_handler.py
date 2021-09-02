import pickle
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import Image
import numpy as np
from movie_creator.thumbnail_creator.design_engine.text_handler import TextHandler


class VideoHandler:
    def __init__(self, subtitle_font_name):
        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Import secrets
        DB_DIR = os.path.join(BASE_DIR, '../../')
        self.base_path = f'{DB_DIR}/temperary_database'
        self.text_handler = TextHandler(subtitle_font_name=subtitle_font_name)

    def load_track_data_list(self, file_name):
        with open(f"{self.base_path}/track_data_set/{file_name}.pkl", 'rb') as f:
            data_set = pickle.load(f)

        return data_set

    def create_subtitles(self, lyrics_text_list, lyrics_time_list, music_length, music_video, layout_x, layout_y, layout_width, layout_height):
        for lyric_index, lyric_row in enumerate(lyrics_text_list):
            if lyric_index + 1 < len(lyrics_text_list):
                if lyrics_time_list[lyric_index + 1] > music_length:
                    break

            # Set duration time
            duration_time = ((lyrics_time_list[lyric_index + 1] - lyrics_time_list[lyric_index])
                             if ((lyric_index + 1) < len(lyrics_text_list))
                             else music_length - lyrics_time_list[lyric_index])

            # Create subtitle text as PIL image
            text_image = self.text_handler.create_subtitle_text(text=lyric_row, layout_width=layout_width, layout_height=layout_height).convert('RGBA')
            text_image_array = np.array(text_image)

            text_x = layout_x + (layout_width // 2 - text_image.width // 2)
            text_y = layout_y + (layout_height // 2 - text_image.height // 2)

            subtitle = (ImageClip(text_image_array)
                        .set_duration(duration_time)
                        .margin(left=text_x if text_x >= 0 else 0, top=text_y, opacity=0)
                        .set_pos(("left", "top")))

            music_video = CompositeVideoClip([music_video, (subtitle
                                                            .set_start(lyrics_time_list[lyric_index])
                                                            .set_duration(duration_time))])

        return music_video

    def image_content_video_create_process(self, file_name, contents_set, each_interval_time):
        # Hold video list
        video_list = list()

        # Iter contents set
        for content in contents_set:
            # Load cover image with pil
            cover_image_array = np.array(content.convert('RGB'))

            # Convert image to clip
            image_clip = ImageClip(cover_image_array).set_duration(each_interval_time)
            video_list.append(image_clip)

        concatenated_video = concatenate_videoclips(video_list, method="compose")
        concatenated_video.write_videofile(file_name, fps=30)

    def music_video_create_process(self, file_name, cover_image, music_file_path, lyrics_text_list, lyrics_time_list, music_length, layout_x, layout_y, layout_width, layout_height):
        # Load cover image with pil cover_image = Image.open(fp=cover_image_path).convert('RGB')
        cover_image_array = np.array(cover_image.convert('RGB'))

        # Create video, length equal to music
        music_video = ImageClip(cover_image_array).set_duration(music_length)

        # Load music file clip
        music_clip = AudioFileClip(music_file_path).subclip(0, music_length - 1)

        # Set music video's audio to music clip
        music_video.audio = music_clip

        # Attach subtitle to video
        subtitle_composed_video = self.create_subtitles(lyrics_text_list=lyrics_text_list,
                                                        lyrics_time_list=lyrics_time_list,
                                                        music_length=music_length,
                                                        music_video=music_video,
                                                        layout_x=layout_x,
                                                        layout_y=layout_y,
                                                        layout_width=layout_width,
                                                        layout_height=layout_height)

        subtitle_composed_video.write_videofile(file_name, fps=30)
