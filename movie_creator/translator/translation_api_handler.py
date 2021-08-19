import os
import sys
import urllib.request
import json


'''
client_id = "YOUR_CLIENT_ID" # 개발자센터에서 발급받은 Client ID 값
client_secret = "YOUR_CLIENT_SECRET" # 개발자센터에서 발급받은 Client Secret 값

'''


class TranslationApiHandler:
    def __init__(self):
        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Import secrets
        ROOT_DIR = os.path.dirname(BASE_DIR)
        SECRET_DIR = os.path.join(ROOT_DIR, '.secrets')

        self.secret_info_list = json.load(open(os.path.join(SECRET_DIR, 'secret_data.json'), 'rb'))["SECRET_LIST"]
        self.current_secret_index = 0
        self.current_secret_info = self.secret_info_list[self.current_secret_index]

        # Set api url
        self.api_url = "https://openapi.naver.com/v1/papago/n2mt"

    def change_secret_index(self):
        self.current_secret_index += 1
        self.current_secret_info = self.secret_info_list[self.current_secret_index]

    def update_request_header(self):
        request = urllib.request.Request(self.api_url)
        request.add_header("X-Naver-Client-Id", self.current_secret_info['NAVER_API_CLIENT_ID'])
        request.add_header("X-Naver-Client-Secret", self.current_secret_info['NAVER_API_CLIENT_PASSWORD'])

        return request

    def translate_mono_sentence(self, text, target_language):
        # Create request
        request = urllib.request.Request(self.api_url)
        request.add_header("X-Naver-Client-Id", self.current_secret_info['NAVER_API_CLIENT_ID'])
        request.add_header("X-Naver-Client-Secret", self.current_secret_info['NAVER_API_CLIENT_PASSWORD'])

        # Send request by iter
        translated_data = None

        while translated_data is None:
            # Parse string
            enc_text = urllib.parse.quote(text)

            # Set data (target_language_list=['ja', 'vi', 'id', 'th', 'en'])
            data = f"source=ko&target={target_language}&text=" + enc_text

            try:
                # Get response
                response = urllib.request.urlopen(request, data=data.encode("utf-8"))
                rescode = response.getcode()

            except Exception as e:
                self.change_secret_index()
                request = self.update_request_header()
                continue

            if rescode == 200:
                # Decode data and add to dict
                response_body = response.read()
                translated_data = json.loads(response_body.decode('utf-8'))['message']['result']['translatedText']

            else:
                print("일일 번역 API 양 초과")
                break

        return translated_data

    def get_translated_data_list(self, text_list, target_language):
        # Create request
        request = urllib.request.Request(self.api_url)
        request.add_header("X-Naver-Client-Id", self.current_secret_info['NAVER_API_CLIENT_ID'])
        request.add_header("X-Naver-Client-Secret", self.current_secret_info['NAVER_API_CLIENT_PASSWORD'])

        # Send request by iter
        translated_list = list()
        text_index = 0

        while text_index <= len(text_list) - 1:
            # Parse string
            enc_text = urllib.parse.quote(text_list[text_index])

            # Set data (target_language_list=['ja', 'vi', 'id', 'th', 'en'])
            data = f"source=ko&target={target_language}&text=" + enc_text

            # Get response
            try:
                response = urllib.request.urlopen(request, data=data.encode("utf-8"))
                rescode = response.getcode()

            except Exception as e:
                self.change_secret_index()
                request = self.update_request_header()
                continue

            if rescode == 200:
                # Decode data and add to dict
                response_body = response.read()
                translated_list.append(json.loads(response_body.decode('utf-8'))['message']['result']['translatedText'])

                text_index += 1

            else:
                print("일일 번역 API 양 초과")
                break

        return translated_list


if __name__ == "__main__":
    translator = TranslationApiHandler()
    str_list = ['점점 비가 내려와', '세상이 어두워지고', '지금은 그대로', '어김없이 난', '벗어나질 못하네']

    print(translator.get_translated_data(text_list=str_list, target_language='en'))

