from music_scraper.src.selenium_controller import SeleniumController
import time
import pickle
import os
import pandas as pd


class Scp:
    def __init__(self):
        pass

    def start_scrape(self):
        selenium_controller = SeleniumController()
        driver = selenium_controller.driver

        time.sleep(5)

        driver.get("http://study.korean.net/servlet/action.kei.HsiAction?p_menuCd=m40261&p_year_id=2020")

        time.sleep(10)

        search_btn = driver.find_element_by_xpath(xpath="/html/body/section/form/div/div/div/div[4]/div/div/ul/li[2]/p/a/img")
        search_btn.click()

        data_set = list()

        for i in range(261):
            try:
                print("=" * 50)
                print(f"{i+1} / 261")
                print("=" * 50)

                driver.execute_script(f"javascript:goPage('{i+1}');")

                time.sleep(1)

                rows = driver.find_elements_by_xpath(xpath='//*[@id="board_list"]/table/tbody/tr/td[5]/a')

                for s_tag in rows:
                    #s_tag = k.find_element_by_xpath(xpath="descendant::td[5]/a")

                    s_name = s_tag.text
                    s_href = s_tag.get_attribute("href")

                    print(f"{s_href}, {s_name}")

                    data_set.append({"name": s_name.strip(), "href": s_href})

            except:
                pass

        # Set path to save
        save_path = f'/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/test_database/sc_files'

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Pickle data
        print('Pickling data @', f"{save_path}/sc_path.pkl")

        file_handler = open(f"{save_path}/sc_path.pkl", "wb")
        pickle.dump(data_set, file_handler, protocol=4)
        # pickle.dump(data, file_handler,protocol=4)
        file_handler.close()

    def s_c(self):
        save_path = f'/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/test_database/sc_files'

        selenium_controller = SeleniumController()
        driver = selenium_controller.driver

        sc_name_list = list()
        updated_date_list = list()
        phone_list = list()
        nation_list = list()
        official_list = list()


        with open(f"{save_path}/sc_path.pkl", 'rb') as f:
            data_set = pickle.load(f)

        driver.get("http://study.korean.net/servlet/action.kei.HsiAction?p_menuCd=m40261&p_year_id=2020")
        time.sleep(1)

        for i, data in enumerate(data_set):
            print(f"{i} / {len(data_set)}")
            try:
                print(data['href'])
                driver.execute_script(f"{data['href']}")

                official = driver.find_element_by_xpath(xpath='/html/body/section/form/div/div/div/table[1]/tbody/tr[1]/td[4]').text.strip()
                last_day = driver.find_element_by_xpath(xpath='//*[@id="board_list"]/div[4]/span').text[5:].strip()
                nation = driver.find_element_by_xpath(xpath='//*[@id="board_list"]/table[1]/tbody/tr[1]/td[2]').text.strip()
                phone = driver.find_element_by_xpath(xpath='//*[@id="board_list"]/table[1]/tbody/tr[5]/td[2]').text.strip()

                if len(nation) != 0 and len(phone) != 0:
                    print(official)
                    sc_name_list.append(data['name'])
                    updated_date_list.append(last_day)
                    phone_list.append(phone)
                    nation_list.append(nation)
                    official_list.append(official)

                driver.get("http://study.korean.net/servlet/action.kei.HsiAction?p_menuCd=m40261&p_year_id=2020")

            except:
                pass

        return {"학교명": sc_name_list, "전화번호": phone_list, "국가": nation_list, "최종수정일": updated_date_list, "공관": official_list}

if __name__ == "__main__":

    s = Scp()
    #s.start_scrape()
    da = s.s_c()

    # 마지막에 판다스 지워.
    k = pd.DataFrame(da)

    # Set path to save
    save_path = f'/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/test_database/sc_files'

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Pickle data
    print('Pickling data @', f"{save_path}/sc_final.pkl")

    file_handler = open(f"{save_path}/sc_final.pkl", "wb")
    pickle.dump(k, file_handler, protocol=4)
    # pickle.dump(data, file_handler,protocol=4)
    file_handler.close()


    save_path = f'/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/test_database/sc_files'

    with open(f"{save_path}/sc_final.pkl", 'rb') as f:
        k = pickle.load(f)

    print(k)

    xlxs_dir = f"{save_path}/sc_final.xlsx"

    k.to_excel(xlxs_dir,  # directory and file name to write
                sheet_name='Sheet1',
                na_rep='NaN',
                float_format="%.2f",
                header=True,
                # columns = ["group", "value_1", "value_2"], # if header is False
                index=True,
                index_label="id",
                startrow=0,
                startcol=0,
                # engine = 'xlsxwriter',
                freeze_panes=(2, 0)
                )
