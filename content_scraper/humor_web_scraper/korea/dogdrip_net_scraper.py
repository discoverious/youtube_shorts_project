'''
글자가 N개 이상 포함되면 거른다.

즉, 거름의 조건들이 필요
>> test database

외곽선 검출로 가져왕함

'''
import datetime
import os
import time
import re
import json
from music_scraper.src.selenium_controller import SeleniumController
from database_handler.mongo_db_handler import MongoDbHandler


class DogdripNetScraper:
    def __init__(self, max_content_per_scrape):
        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Load scrape id list from secrets
        ROOT_DIR = os.path.dirname(self.BASE_DIR)
        SECRET_DIR = os.path.join(ROOT_DIR, 'youtube_shorts_project/.secrets')

        # Import secrets
        self.base_save_path = f"{os.path.join(self.BASE_DIR, '..')}/temperary_database/content_database"

        # Set base dogdrip net url
        self.dogdrip_net_base_url = "https://www.dogdrip.net"

        # Set max content to scrape
        self.max_content_per_scrape = max_content_per_scrape

        # Set db handler instance
        self.db_handler = MongoDbHandler(initial_db_name="youtube_shorts_project")

    def load_initial_dogdripnet_rank_page(self, driver, page, waiting_time_after_execution):
        # Load profile
        driver.get(f"{self.dogdrip_net_base_url}/index.php?mid=dogdrip&sort_index=popular&page={page}")

        # Wait until page load
        time.sleep(waiting_time_after_execution)

    def get_article_list(self, driver):
        article_list = driver.find_elements_by_xpath(xpath="/html/body/div[1]/main/div/div[2]/div/div/table/tbody/tr")

        return article_list

    def check_proper_content(self, content_text):
        is_content_proper = True

        # If it's text based content than cut
        text_list = content_text.split('\n')[:-1]

        if len(text_list) > 1:
            is_content_proper = False

        return is_content_proper

    def extract_data_from_each_article(self, driver, article_id):
        # Get article media list ('descendant::div[contains(id, "article_1")]')
        article_section = driver.find_element_by_xpath(xpath='//div[contains(@id, "article_1")]')

        # Check if content is proper
        is_content_proper = self.check_proper_content(content_text=article_section.text)

        # Get article's data
        article_data_dict = None

        if is_content_proper is True:
            # Get image contents
            article_image_list = article_section.find_elements_by_xpath(xpath='descendant::img')

            # Get image path
            image_path_list = list()

            for article_image in article_image_list:
                image_src = article_image.get_attribute("src")
                image_path_list.append(image_src)

            if len(article_image_list) != 0:
                # Get title
                article_title = driver.find_element_by_xpath(xpath='//a[contains(@class, "ed link text-bold")]').text

                # Set data
                article_data_dict = {"type": "image",
                                     "media_list": image_path_list,
                                     "media_id": article_id,
                                     "message": article_title,
                                     "uploaded_date": datetime.datetime.now(),
                                     "uploaded": False,
                                     "country_code": "kr"}

        return article_data_dict

    def merge_article_list(self, driver, article_list, integrated_article_list, already_scraped):
        # Get each article's path list
        article_path_list = list()

        for article in article_list:
            article_href = article.find_element_by_xpath(xpath='descendant::td[contains(@class, "title")]/span/a').get_attribute("href")
            article_path_list.append(article_href)

        # Scrape data from each articles
        for article_path in article_path_list:
            # Get to page
            driver.get(article_path)

            # Set article id
            article_id = article_path.split('&')[-1].split('=')[-1]

            # Extract data
            extracted_media_data = self.extract_data_from_each_article(driver=driver,
                                                                       article_id=article_id)

            if extracted_media_data is not None:
                # Check from database
                if self.db_handler.search_record(column_name="dogdripnet_contents", query={'media_id': extracted_media_data["media_id"]}) is None:
                    # Append to integrated list
                    integrated_article_list[extracted_media_data["media_id"]] = extracted_media_data

                else:
                    already_scraped = True

        return integrated_article_list, already_scraped

    def scrape_process(self):
        # Set controller instance
        selenium_controller = SeleniumController()
        driver = selenium_controller.driver

        # Whole article list from scrape process
        integrated_article_list = dict()

        # Iterate until stop
        count_of_iteration = 0
        already_scraped = False

        while count_of_iteration < self.max_content_per_scrape and already_scraped is False:
            print(f"진행률 : {count_of_iteration + 1}/{self.max_content_per_scrape}")

            # Load web
            self.load_initial_dogdripnet_rank_page(driver=driver,
                                                   page=count_of_iteration + 1,
                                                   waiting_time_after_execution=2)

            # Get articles
            article_list = self.get_article_list(driver=driver)

            # Update integrated articles
            integrated_article_list, already_scraped = self.merge_article_list(article_list=article_list,
                                                                               integrated_article_list=integrated_article_list,
                                                                               already_scraped=already_scraped,
                                                                               driver=driver)

            # Update count of iteration

            count_of_iteration += 1

        # Insert data to database
        if list(integrated_article_list.values()) is not None:
            self.db_handler.insert_list_of_records(column_name="dogdripnet_contents",
                                                   list_of_records=list(integrated_article_list.values()))

if __name__ == "__main__":
    scraper = DogdripNetScraper(max_content_per_scrape=30)
    scraper.scrape_process()
