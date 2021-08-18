from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import os
import time


class SeleniumController:
    def __init__(self):
        self.user_agent = "MusicScraper"
        #self.driver = self.get_image_blocked_driver(show_browser=True)
        self.driver = self.get_image_unblocked_driver(show_browser=True)

    def get_to_bottom(self, scroll_pause_time):
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(scroll_pause_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break

            last_height = new_height

    def mouse_over_on_tag(self, table_row, child_element_xpath):
        action = ActionChains(self.driver)
        first_level_menu = table_row.find_element_by_xpath(xpath=child_element_xpath)
        action.move_to_element(first_level_menu).perform()

    def get_image_unblocked_driver(self, show_browser, additional_option_list=None):
        options = Options()

        chrome_prefs = dict()
        options.experimental_options["prefs"] = chrome_prefs

        options.add_argument(f'user-agent={self.user_agent}')

        if additional_option_list is not None:
            for additional_option in additional_option_list:
                options.add_argument(additional_option)

        if show_browser is False:
            options.add_argument("start-maximized")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-browser-side-navigation")
            options.add_argument("enable-automation")
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-extensions")
            options.add_argument("--dns-prefetch-disable")
            options.add_argument("--disable-gpu")

        if os.name == 'nt':
            # If Windows
            chrome_driver_file = "chromedriver.exe"

        else:
            # If Linux
            chrome_driver_file = "chromedriver"
        try:
            # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # Import secrets
            DB_DIR = os.path.join(BASE_DIR, '../../')
            base_path = f'{DB_DIR}/music_scraper/selenium_storage'

            driver = webdriver.Chrome(base_path + chrome_driver_file, options=options)

        except:
            print("이 에러 난 것")
            # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # Import secrets
            DB_DIR = os.path.join(BASE_DIR, '../..')
            base_path = f'{DB_DIR}/music_scraper/selenium_storage/'

            print(base_path)

            driver = webdriver.Chrome(base_path + chrome_driver_file, options=options)

        return driver

    def get_image_blocked_driver(self, show_browser, additional_option_list=None):
        options = Options()

        chrome_prefs = dict()
        options.experimental_options["prefs"] = chrome_prefs

        d_json = {'cookies': 2, 'images': 2,
                            'plugins': 2, 'popups': 2, 'geolocation': 2,
                            'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2,
                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
                            'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2,
                            'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
                            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2,
                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2}

        a_json = {'images': 2}

        chrome_prefs["profile.default_content_settings"] = a_json

        chrome_prefs["profile.managed_default_content_settings"] = a_json
        '''
        {'cookies': 2, 'images': 2, 
                            'plugins': 2, 'popups': 2, 'geolocation': 2, 
                            'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2, 
                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 
                            'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2, 
                            'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2, 
                            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2, 
                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 
                            'durable_storage': 2}
        '''

        options.add_argument(f'user-agent={self.user_agent}')

        if additional_option_list is not None:
            for additional_option in additional_option_list:
                options.add_argument(additional_option)

        if show_browser is False:
            options.add_argument("start-maximized")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-browser-side-navigation")
            options.add_argument("enable-automation")
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-extensions")
            options.add_argument("--dns-prefetch-disable")
            options.add_argument("--disable-gpu")

        if os.name == 'nt':
            # If Windows
            chrome_driver_file = "chromedriver.exe"

        else:
            # If Linux
            chrome_driver_file = "chromedriver"

        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'media'}

        try:
            driver = webdriver.Chrome('driver/' + chrome_driver_file, options=options)

        except:
            # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # Import secrets
            DB_DIR = os.path.join(BASE_DIR, '../../')
            base_path = f'{DB_DIR}/music_scraper/selenium_storage'

            driver = webdriver.Chrome(base_path + chrome_driver_file, options=options)

        return driver




