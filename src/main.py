import sys
import os
import requests
import json

# ссылка на созданную папку с фото
# https://disk.yandex.ru/d/JkDr_QGbJQxMpQ


class PhotosCats:
    """requests and returns a link to the photo"""

    _url = "https://cataas.com/cat/says/"
    _params = {
        "json": True,
        "font": "Georgia",
        "fontSize": 60,
        "fontColor": "#ff00ff",
    }

    def get_cat(self):
        """
        Returns the url,type and text of the photo
        order: (image_url, image_type, text)
        """
        text = f"{input("Введите фразу для фото: ").strip()}"
        url = f"{self._url}{text}"
        try:
            response = requests.get(url, params=self._params, timeout=5)
            if response.status_code != 200:
                print("Не получилось загрузить котика")
                return "", "", ""
            response_data = response.json()
            image_url = response_data.get("url")
            image_type = response_data.get("mimetype").split("/")[-1]
            return image_url, image_type, text
        except requests.exceptions.Timeout:
            print("Наверное нужно VPN включить...")
            return "", "", ""
        except Exception as e:
            print(f"Не удалось загрузить котика, Ошибка: {e}")
            return "", "", ""


class YandexDiskAPI:
    """creates a folder on yandex-disk and writes photos to it"""

    _base_url = "https://cloud-api.yandex.net"

    def __init__(self, token):
        self._headers = {"Authorization": f"OAuth {token}"}

    def create_folder(self, folder):
        """
        Creates a folder on the user's yandex-disk and returns folder's name
        """
        params = {"path": folder}
        try:
            response = requests.put(
                f"{self._base_url}/v1/disk/resources",
                headers=self._headers,
                params=params,
            )
            if response.status_code in (201, 409):
                return folder
            if response.status_code == 401:
                print("Вы не авторизованы (токен проверьте)")
            return ""
        except Exception as e:
            print("Не удалось создать папку на Яндекс-Диске")
            print(f"Ошибка: {e}")
            return ""

    def append_to_json(self, new_data):
        """writes data about photo to json-file"""

        filename = os.path.join(os.getcwd(), "files_info.json")
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data.append(new_data)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

    def upload_file(self, folder, image_url, image_type, text):
        """
        Uploads the file to yandex-disk
        :folder - returns function create_folder (class YandexDiskAPI)
        :image_url, image_type, text - returns func get_cat (class PhotosCats)
        """
        if not image_url or not image_type or not text:
            print("Не получена фотография по запросу")
            sys.exit(0)
        if not folder:
            print("Папка на Яндекс-Диске не создана")
            sys.exit(0)
        url_upload_file = f"{self._base_url}/v1/disk/resources/upload"
        params = {"path": f"{folder}/{text}.{image_type}", "url": image_url}
        try:
            response_upload = requests.post(
                url_upload_file,
                headers=self._headers,
                params=params,
            )
            upload_link = response_upload.json()["href"]
            requests.put(upload_link, timeout=10)
            self.append_to_json(f"{text}.{image_type}")
            print(
                "Загрузка изображения начата, но для проверки конечного "
                "результата пока не хватает знаний"
            )
        except Exception as e:
            print(f"Что-то пошло не так... Ошибка {e}")
            sys.exit(1)


def main():
    """main function"""
    group_name = "pd-142"

    photo_cat = PhotosCats()
    yd_api = YandexDiskAPI("")

    image_url, image_type, text = photo_cat.get_cat()
    folder = yd_api.create_folder(group_name)
    yd_api.upload_file(folder, image_url, image_type, text)


if __name__ == "__main__":
    main()
