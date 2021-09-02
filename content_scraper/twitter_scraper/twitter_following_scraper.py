import os
import time
import re
import json
from music_scraper.src.selenium_controller import SeleniumController
from database_handler.mongo_db_handler import MongoDbHandler


class TwitterFollowingScraper:
    def __init__(self, max_content_per_scrape):
        # Set country code list
        self.target_country_code_list = ['ja', 'vi', 'th', 'en', 'id']

        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Load scrape id list from secrets
        ROOT_DIR = os.path.dirname(self.BASE_DIR)
        SECRET_DIR = os.path.join(ROOT_DIR, 'youtube_shorts_project/.secrets')

        self.scrape_id_list = json.load(open(os.path.join(SECRET_DIR, 'scrape_id_list.json'), 'rb'))["Twitter"]

        # Import secrets
        self.base_save_path = f"{os.path.join(self.BASE_DIR, '..')}/temperary_database/content_database"

        # Set twitter base url
        self.twitter_base_url = "https://twitter.com"

        # Set max content to scrape
        self.max_content_per_scrape = max_content_per_scrape

        # Set db handler instance
        self.db_handler = MongoDbHandler(initial_db_name="youtube_shorts_project")

    def load_initial_twitter_profile(self, driver, twitter_id, waiting_time_after_execution):
        # Load profile
        driver.get(f"{self.twitter_base_url}/{twitter_id}")

        # Wait until page load
        time.sleep(waiting_time_after_execution)

    def get_article_list(self, driver):
        article_list = driver.find_elements_by_xpath(xpath="//article")

        return article_list

    def extract_video_format(self):
        pass

    def extract_image_format(self):
        pass

    def extract_data_from_each_article(self, article, twitter_id, country):
        # Get article media list
        article_media_list = article.find_elements_by_xpath(xpath='descendant::img')  # [contains(@src, "https://pbs.twimg.com")]

        # Filter media
        media_tag = None

        for article_media in article_media_list:
            tag_media_path = article_media.get_attribute(name="src")

            if re.search(pattern="media", string=article_media.get_attribute(name="src")) is not None:
                media_tag = {"type": "image", "tag": tag_media_path}

            elif re.search(pattern="ext_tw_video_thumb", string=article_media.get_attribute(name="src")) is not None:
                media_tag = {"type": "video", "tag": tag_media_path}

            # Extract meta data
            if media_tag is not None:
                # Get media id
                media_id = media_tag['tag'].split('/')[4]

                if media_tag['type'] == 'image':
                    media_id = media_id.split('?')[0]

                # Get tweet message if exists
                try:
                    tweet_message = article.find_element_by_xpath(xpath='descendant::div/div/div/div[2]/div[2]/div[2]/div[1]/div/span').text

                except Exception as e:
                    print(e)
                    tweet_message = None

                # Get uploaded date
                uploaded_date = article.find_element_by_xpath(xpath='descendant::time').get_attribute('datetime')

                media_tag["message"] = tweet_message
                media_tag["uploaded_date"] = uploaded_date
                media_tag["uploader_name"] = twitter_id
                media_tag["country_code"] = country
                media_tag["media_id"] = media_id
                media_tag["uploaded"] = False

        return media_tag

    def merge_article_list(self, article_list, integrated_article_list, twitter_id, country, already_scraped):
        # Iter articles
        for article in article_list:
            # Extract data from article
            extracted_media_data = self.extract_data_from_each_article(article=article,
                                                                       twitter_id=twitter_id,
                                                                       country=country)

            if extracted_media_data is not None:
                # Check from database
                if self.db_handler.search_record(column_name="twitter_contents", query={'media_id': extracted_media_data["media_id"]}) is None:
                    # Append to integrated list
                    integrated_article_list[extracted_media_data["media_id"]] = extracted_media_data

                else:
                    already_scraped = True

        return integrated_article_list, already_scraped

    def get_content(self, twitter_id, country):
        # Set controller instance
        selenium_controller = SeleniumController()
        driver = selenium_controller.driver

        # Go to url
        self.load_initial_twitter_profile(driver=driver,
                                          twitter_id=twitter_id,
                                          waiting_time_after_execution=10)

        # Whole article list from scrape process
        integrated_article_list = dict()

        # Iterate until stop
        count_of_iteration = 0
        already_scraped = False

        while count_of_iteration < self.max_content_per_scrape and already_scraped is False:
            print(f"진행률 : {count_of_iteration + 1}/{self.max_content_per_scrape}")
            # Get articles
            article_list = self.get_article_list(driver=driver)

            # Update integrated articles
            integrated_article_list, already_scraped = self.merge_article_list(article_list=article_list,
                                                                               integrated_article_list=integrated_article_list,
                                                                               twitter_id=twitter_id,
                                                                               country=country,
                                                                               already_scraped=already_scraped)

            # Scroll down and load contents
            selenium_controller.get_to_bottom_once(scroll_pause_time=5)

            # Update count of iteration
            count_of_iteration += 1

        # Insert data to database
        if list(integrated_article_list.values()) is not None:
            self.db_handler.insert_list_of_records(column_name="twitter_contents",
                                                   list_of_records=list(integrated_article_list.values()))

    def scrape_process(self):
        for target_country_code in self.target_country_code_list:
            # If code exists in id list
            if target_country_code in self.scrape_id_list:
                for twitter_id in self.scrape_id_list[target_country_code]:
                    self.get_content(twitter_id=twitter_id, country=target_country_code)


if __name__ == "__main__":
    scraper = TwitterFollowingScraper(max_content_per_scrape=2)

    # country code ('ja', 'vi', 'id', 'th', 'en')
    scraper.scrape_process()
