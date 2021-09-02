import time
from selenium.webdriver.common.action_chains import ActionChains
import json
import re
import requests
import pickle
import os
from PIL import Image
import sys

import sys
import os

module_path = os.path.abspath(os.getcwd())
if module_path not in sys.path:
    sys.path.append(module_path)

from music_scraper.src.selenium_controller import SeleniumController
from music_scraper.src.music_recorder.linux_internal_sound_recorder import LinuxInternalSoundRecorder


class ScraperHandler:
    def __init__(self):
        # Data to login bugs
        # Font info for each language
        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Import secrets
        ROOT_DIR = os.path.dirname(BASE_DIR)
        SECRET_DIR = os.path.join(ROOT_DIR, '.secrets')

        self.login_settings = json.load(open(os.path.join(SECRET_DIR, 'bugs_login_info.json'), 'rb'))

        self.login_data = {'id': self.login_settings["BUGS_ID"], 'password': self.login_settings["BUGS_PASSWORD"]}

        # Instance to record internal sound
        self.internal_sound_recorder = LinuxInternalSoundRecorder()

        # Base save path
        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        DB_DIR = os.path.join(BASE_DIR, '..')
        self.base_save_path = f'{DB_DIR}/temperary_database'

    def scrape_process(self):
        # Set controller instance
        selenium_controller = SeleniumController()

        # Start scrape
        track_data_set = self.start_scrape(driver=selenium_controller.driver)

        # Create file name
        start_time = time.gmtime(time.time())
        file_name = f"{start_time.tm_year}_{start_time.tm_mon}_{start_time.tm_mday}_{start_time.tm_hour}_{start_time.tm_min}_{start_time.tm_sec}"

        # Set path to save
        save_path = f'{self.base_save_path}/track_data_set'

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Pickle data
        print('Pickling data @', f"{save_path}/{file_name}.pkl")

        file_handler = open(f"{save_path}/{file_name}.pkl", "wb")
        pickle.dump(track_data_set, file_handler, protocol=4)
        # pickle.dump(data, file_handler,protocol=4)
        file_handler.close()

    def get_lyrics_response_content(self, driver, track_id):
        # List to contain lyric data
        lyrics_data_list = list()

        # Get lyrics request url from driver's network
        driver_networks = driver.execute_script("var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;")

        request_url = None

        for item in driver_networks:
            if re.search(pattern='lyrics', string=item['name']) is not None and re.search(pattern=track_id, string=item['name']):
                request_url = item['name']

        if request_url is not None:
            # Get content
            bugs_response_content = json.loads(requests.get(request_url).content)

            # Get primitive lyrics
            primitive_lyrics = bugs_response_content['lyrics'].split('＃')

            # Iterate primitive lyrics and split it to time/lyric
            for each_line in primitive_lyrics:
                split_data = each_line.split('|')

                # Append to lyrics data list
                lyrics_data_list.append({'time': split_data[0], 'lyric': split_data[1]})

        return lyrics_data_list

    def login_bugs(self, driver, waiting_time_after_execution, waiting_time_before_execution):
        time.sleep(waiting_time_before_execution)

        # Open login panel
        login_panel_btn = driver.find_element_by_xpath(xpath='/html/body/div[2]/header/div[3]/div[2]/div/div[1]/a')
        login_panel_btn.click()

        time.sleep(1)

        # Click Login btn
        login_btn = driver.find_element_by_xpath(xpath='//*[@id="to_bugs_login"]')
        login_btn.click()

        time.sleep(1)

        # Send login_data
        id_form = driver.find_element_by_xpath(xpath='//*[@id="user_id"]')
        id_form.send_keys(self.login_data['id'])

        pw_form = driver.find_element_by_xpath(xpath='//*[@id="passwd"]')
        pw_form.send_keys(self.login_data['password'])

        submit_btn = driver.find_element_by_xpath(xpath='/html/body/div[2]/header/div[3]/div[2]/div/div[1]/aside/fieldset/form/div/div[1]/button')
        submit_btn.click()

        time.sleep(waiting_time_after_execution)

    def open_play_list(self, driver, waiting_time_after_execution):
        # Open play list
        playlist_btn = driver.find_element_by_xpath(xpath='//*[@id="headerWebPlayer"]')
        playlist_btn.click()

        # Switch to playlist
        time.sleep(1)
        window_after = driver.window_handles[1]
        driver.switch_to_window(window_after)
        driver.maximize_window()

        time.sleep(waiting_time_after_execution)

    def get_my_album_list(self, driver):
        # Open album tab
        my_album_tab = driver.find_element_by_xpath(xpath='//div[contains(@class, "tabPlayer")]/ul/li[contains(@class, "myAlbum")]')
        my_album_tab.click()

        time.sleep(1.5)

        # Get album list
        my_album_list = driver.find_elements_by_xpath(xpath='//ul[contains(@class, "myList")]/li')

        return my_album_list

    def get_track_list(self, album, waiting_time_before_execution):
        time.sleep(waiting_time_before_execution)

        # Get music track list from album
        track_list = album.find_elements_by_xpath(xpath='descendant::ul[contains(@class, "playTrackList")]/li')

        return track_list

    def gather_track_information(self, driver, waiting_time_before_execution):
        time.sleep(waiting_time_before_execution)

        # Get information from track title tag
        track_title_tag = driver.find_element_by_xpath(xpath='//span[contains(@class, "tracktitle")]/a')

        track_id = track_title_tag.get_attribute('href').split('/')[-1]
        track_title = track_title_tag.get_attribute('title')

        # Get information from album tag
        album_tag = driver.find_element_by_xpath(xpath='//a[contains(@class, "albumtitle")]')

        album_id = album_tag.get_attribute('href').split('/')[-1]
        album_title = album_tag.get_attribute('title')

        # Get information from musician tag
        musician_tag = driver.find_element_by_xpath(xpath='//a[contains(@id, "newPlayerArtistName")]')

        musician_id = musician_tag.get_attribute('href').split('/')[-1]
        musician_title = musician_tag.get_attribute('title')

        # Get track length by second
        track_progress_tag = driver.find_element_by_xpath(xpath='//span[contains(@class, "time")]')

        song_length = track_progress_tag.find_element_by_xpath(xpath='descendant::em[contains(@class, "finish")]').text.split(':')

        song_length_by_second = (int(song_length[0]) * 60) + (int(song_length[1]))

        # Get album image path and save it
        album_thumbnail_path = driver.find_element_by_xpath(xpath='//div[contains(@class, "thumbnail")]/img').get_attribute('src').split('?')[0]
        album_thumbnail_path = re.sub(pattern='100', repl='600', string=album_thumbnail_path)

        # Convert album image's resolution query & Save
        image_file = Image.open(requests.get(album_thumbnail_path, stream=True).raw)

        # Set path to save
        album_cover_save_path = f'{self.base_save_path}/album_image'

        if not os.path.exists(album_cover_save_path):
            os.makedirs(album_cover_save_path)

        # Pickle data
        image_file.save(f"{album_cover_save_path}/{track_id}.png")

        return {
            'track_id': track_id,
            'track_title': track_title,
            'album_id': album_id,
            'album_title': album_title,
            'musician_id': musician_id,
            'musician_title': musician_title,
            'song_length_by_second': song_length_by_second,
            'album_thumbnail_save_path': album_thumbnail_path
        }

    def click_music_stop(self, driver):
        music_stop_btn = driver.find_element_by_xpath(xpath='//*[@class="btnStop"]')
        music_stop_btn.click()

    def click_music_prev(self, driver):
        music_pre_btn = driver.find_element_by_xpath(xpath='//*[@class="btnPrev"]')
        music_pre_btn.click()

    def click_music_play(self, driver):
        music_play_btn = driver.find_element_by_xpath(xpath='//*[@class="btnPlay"]')
        music_play_btn.click()

    def start_scrape(self, driver):
        # List to contain track data set
        track_data_list = list()

        # Get start page
        driver.get('https://music.bugs.co.kr/')

        # Login
        self.login_bugs(driver=driver, waiting_time_after_execution=3, waiting_time_before_execution=2)

        # Get play_list
        self.open_play_list(driver=driver, waiting_time_after_execution=1.5)

        # Clean play_list

        # Get Album list to iterate
        my_album_list = self.get_my_album_list(driver=driver)

        for my_album in my_album_list:
            # Open my album
            my_album.click()
            time.sleep(2)

            # Get all track list
            music_track_list = self.get_track_list(album=my_album, waiting_time_before_execution=2)

            for music_track in music_track_list:
                # Start music
                music_track.click()

                # Gather track's information
                track_information_dict = self.gather_track_information(driver=driver,
                                                                       waiting_time_before_execution=10)

                # Gather track's lyrics
                lyric_data = None

                try:
                    lyric_data = self.get_lyrics_response_content(driver=driver,
                                                                  track_id=track_information_dict['track_id'])

                except Exception as e:
                    print(f"There's no lyric data , {e}")

                # Rewind track
                self.click_music_stop(driver=driver)
                self.click_music_prev(driver=driver)

                # Start recording music
                time.sleep(0.3)
                music_file_save_path = self.internal_sound_recorder.start_recording(wave_output_filename=track_information_dict['track_id'],
                                                                                    record_seconds=track_information_dict['song_length_by_second'])

                # Append data to list
                track_data = {'track_information_dict': track_information_dict,
                              'lyric_data': lyric_data,
                              'music_file_save_path': music_file_save_path}

                if lyric_data is not None:
                    track_data_list.append(track_data)

                time.sleep(10)

        # Save

        return track_data_list


if __name__ == "__main__":
    scraper_handler = ScraperHandler()
    scraper_handler.scrape_process()
    '''
    
    with open(f"/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/temperary_database/track_data_set/2021_8_19_11_21_17.pkl", 'rb') as f:
            data_set = pickle.load(f)

    lyrics_data = list()

    for k in data_set:
        print(k)
    '''

