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

    def video_create_process(self, file_name, cover_image, music_file_path, lyrics_text_list, lyrics_time_list, music_length, layout_x, layout_y, layout_width, layout_height):
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


if __name__ == "__main__":
    video_handler = VideoHandler(subtitle_font_name='Cafe24Oneprettynight.ttf')

    data_set = video_handler.load_track_data_list(file_name='2021_8_14_2_32_58')

    for selected_data in [data_set[0]]:
        # Load music file
        video_handler.video_create_process(track_id=selected_data['track_information_dict']['track_id'],
                                           cover_image_path=f"{video_handler.base_path}/test_results/{selected_data['track_information_dict']['track_id']}.png",
                                           music_file_path=f"{video_handler.base_path}/musics/{selected_data['track_information_dict']['track_id']}.wav",
                                           lyrics_data=selected_data['lyric_data'],
                                           music_length=selected_data['track_information_dict']['song_length_by_second'],
                                           layout_x=57,
                                           layout_y=564,
                                           layout_width=337,
                                           layout_height=228)
