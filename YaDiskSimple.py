import requests


class YaDiskSimple:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://cloud-api.yandex.net/v1/disk/resources"

    def _request(self, method, path, params=None, json_data=None):
        headers = {"Authorization": f"OAuth {self.token}"}
        url = f"{self.base_url}{path}"
        response = requests.request(
            method,
            url,
            params=params,
            json=json_data,
            headers=headers
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise FileNotFoundError(f"Resource not found: {path}") from e
            raise
        return response.json()

    def exists(self, path):
        try:
            self._request("GET", f"?path={path}")
            return True
        except FileNotFoundError:
            return False

    def is_dir(self, path):
        try:
            resource_info = self._request("GET", f"?path={path}")
            return resource_info.get("type") == "dir"
        except FileNotFoundError:
            return False

    def mkdir(self, path):
        self._request("PUT", f"?path={path}")

    def read_file(self, path, encoding='utf-8'):
        """
        Чтение файла с указанной кодировкой
        По умолчанию используется UTF-8
        """
        download_url = self._request("GET", f"/download?path={path}")["href"]
        response = requests.get(download_url)
        response.raise_for_status()

        # Устанавливаем кодировку для правильного чтения кириллицы
        if encoding:
            response.encoding = encoding
        return response.text

    def write_file(self, path, content, encoding='utf-8'):
        """
        Запись файла с указанной кодировкой
        По умолчанию используется UTF-8
        """
        upload_url = self._request("GET", f"/upload?path={path}&overwrite=true")["href"]

        # Кодируем содержимое в указанную кодировку
        if encoding and isinstance(content, str):
            content = content.encode(encoding)

        response = requests.put(upload_url, data=content)
        response.raise_for_status()

    def listdir(self, path):
        """Список файлов в директории"""
        if not self.exists(path):
            raise FileNotFoundError(f"Path not found: {path}")
        if not self.is_dir(path):
            raise NotADirectoryError(f"Path is not a directory: {path}")

        items = []
        offset = 0
        limit = 1000

        while True:
            params = {
                "path": path,
                "limit": limit,
                "offset": offset,
                "fields": "_embedded.items.name,_embedded.items.type"
            }
            resource_info = self._request("GET", "", params=params)

            # if resource_info.get("type") != "dir":
            #     raise NotADirectoryError(f"Path is not a directory: {path}")

            embedded = resource_info.get("_embedded", {})
            batch = embedded.get("items", [])

            items.extend(item["name"] for item in batch)

            if len(batch) < limit:
                break

            offset += limit

        return items