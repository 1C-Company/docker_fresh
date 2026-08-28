import requests
import os
import time
import re
import getpass
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from struct import unpack
import zlib
import tempfile
import shutil

DOWNLOAD_DIR = "distr"

TIMEOUT = 60
DELAY_BETWEEN_DOWNLOADS = 1

BASE_URL = "https://releases.1c.ru"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
})

necessary_components = [
    r"^Менеджер сервиса\. Версия .+?\. Полный дистрибутив$",
    r"^Агент сервиса\. Версия .+?\. Полный дистрибутив$",
    r"^Управление службой поддержки, версия .+?\. Полный дистрибутив$",
    r"^Менеджер доступности, версия .+?\. Полный дистрибутив$",
    r"^Демо приложение \"Работа в модели сервиса\", версия .+?\. Полный дистрибутив$",
    r"^Сайт, версия .+?\. DEB, RPM для Linux и WAR-файл в одном архиве$",
    r"^Форум, версия .+?\. DEB, RPM для Linux и WAR-файл в одном архиве$",
    r"^Шлюз приложений, версия .+?\. DEB, RPM для Linux и JAR-файл в одном архиве$",
    r"^Страница недоступности, версия .+?\. DEB, RPM для Linux и WAR в одном архиве$",
    r"^Сервер исполнителя скриптов подсистемы 1С:Фреш, версия .*$",
    r"^Приложение 1С:Шины, версия .*$",
    r"^.*Дистрибутив 1С:Исполнитель \(U\).*$",
    r"^.*Сервер взаимодействия \(64-bit\) Linux$",
    r"^.*Сервер 1С:Шины для ОС Linux$",
    r"^.*Дистрибутив СУБД PostgreSQL для Debian 13\.0 x86 \(64-bit\) одним архивом.*$",
    r"^Полный дистрибутив$",
    r"^Клиент 1С:Предприятия \(64-bit\) для DEB-based Linux-систем$",
    r"^Технологическая платформа 1С:Предприятия \(64-bit\) для Linux$",
    r"^Утилита лицензирования 1С:Предприятия для Linux \(64-bit\)$",
    r"^Axiom 17 Full JRE \(64-bit\) для DEB-based Linux-систем"
]

def login_1c(username: str, password: str) -> bool:
    print("Открываем страницу логина...")

    r = session.get("https://login.1c.ru/login", timeout=TIMEOUT, allow_redirects=True)
    soup = BeautifulSoup(r.text, "html.parser")

    form = soup.find("form")
    if not form:
        print("Форма не найдена.")
        return False

    action = form.get("action")
    if action and action.startswith("/"):
        action = "https://login.1c.ru" + action
    elif not action:
        action = "https://login.1c.ru/login"

    data = {
        "username": username,
        "password": password,
        "_eventId": "submit",
    }

    for inp in form.find_all("input", {"type": "hidden"}):
        name = inp.get("name")
        value = inp.get("value")
        if name:
            data[name] = value

    print("Отправляем форму на", action)
    r = session.post(action, data=data, timeout=TIMEOUT, allow_redirects=True)

    print("Статус:", r.status_code, "| URL:", r.url)

    if "/user/profile" in r.url:
        print("Попали в личный кабинет. Переходим на releases.1c.ru...")
        r = session.get("https://releases.1c.ru/", timeout=TIMEOUT, allow_redirects=True)
        print("После перехода ->", r.url)

    if "releases.1c.ru" in r.url and r.status_code == 200:
        print("Успешно авторизовались на releases.1c.ru!")
        return True
    else:
        print("Не удалось войти на releases.1c.ru")
        return False

def get_urls_from_page(url: str) -> list:
    try:
        r = session.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all("a", href=True)
        urls = {}
        for link in links:
            href = link['href']
            if href.startswith("/version_file") and any(re.fullmatch(pattern, link.text) for pattern in necessary_components):
                urls[link.text] = href
        return urls
    except Exception as e:
        print("Ошибка при получении URL-ов:", e)
        return []

def get_direct_download_url(page_url: str) -> str:
    try:
        r = session.get(page_url, timeout=TIMEOUT, allow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        link = soup.find("a", string=re.compile(r"Скачать дистрибутив", re.IGNORECASE))
        if link and link.get("href"):
            href = link["href"]
            if href.startswith("http"):
                return href
            else:
                return BASE_URL + href if href.startswith("/") else href
    except Exception as e:
        print("Ошибка при поиске 'Скачать дистрибутив':", e)

    return None

def download_file(url: str):

    # Получаем имя файла из заголовка
    try:
        head = session.head(url, timeout=TIMEOUT, allow_redirects=True)
        content_disposition = head.headers.get("Content-Disposition", "")
        filename = None
        if "filename=" in content_disposition:
            match = re.search(r'filename\*?="?([^";]+)', content_disposition)
            if match:
                filename = match.group(1).strip().strip('"')
    except Exception:
        filename = None

    if not filename:
        filename = os.path.basename(urlparse(url).path)
        if not filename or "." not in filename:
            filename = "1c_file_" + str(int(time.time())) + ".zip"

    filepath = os.path.join(DOWNLOAD_DIR, filename)

    # Проверка на существование файла
    if os.path.exists(filepath):
        print("Файл уже существует, пропускаем")
        return

    print("Скачиваем файл по ссылке:", url)
    part_filepath = filepath + ".part"
    try:
        with session.get(url, stream=True, timeout=TIMEOUT) as response:
            response.raise_for_status()

            with open(part_filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=32*1024):
                    if chunk:
                        f.write(chunk)

        os.rename(part_filepath, filepath)
        size_mb = os.path.getsize(filepath) // (1024 * 1024)
        print("Скачано:", filename, "(" + str(size_mb) + " МБ)")
    except Exception as e:
        print("Ошибка скачивания:", e)
        if os.path.exists(part_filepath):
            os.remove(part_filepath)

def download_components_from_page(page_url: str, component_name: str = "компонент"):
    print(f"\n=== Обработка {component_name} ===")
    print(f"Страница: {page_url}")

    try:
        urls = get_urls_from_page(page_url)

        if not urls:
            print(f"Не найдено подходящих файлов на странице {page_url}")
            return

        print(f"Найдено файлов для скачивания: {len(urls)}")

        for name, url in urls.items():
            try:
                download_url = get_direct_download_url(BASE_URL + url)
                if download_url:
                    print(f"Скачиваем компонент: {name}")
                    download_file(download_url)
                else:
                    print(f"Не удалось получить прямую ссылку скачивания для: {name}")
            except Exception as e:
                print(f"Ошибка при обработке файла '{name}': {e}")

            time.sleep(DELAY_BETWEEN_DOWNLOADS)

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА при обработке группы '{component_name}': {e}")
        print("Продолжаем обработку следующих групп компонентов...\n")

def read_string(file):
    str_len = unpack("I", file.read(4))[0]
    size = str_len * 2
    data = file.read(size)
    return data.decode("utf-16-le")

def read_supply_info(file):
    file.read(4)
    lang = read_string(file)
    supply_name = read_string(file)
    provider_name = read_string(file)
    description_path = read_string(file)
    return lang, supply_name, provider_name, description_path

def read_included_file_info(file):
    file.read(4)
    filename = read_string(file)
    filetime = unpack("Q", file.read(8))[0]
    file.read(4)
    file_size = unpack("I", file.read(4))[0]
    return filename, filetime, file_size

def extract_efd(efd_path: str, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    with open(efd_path, "rb") as f:
        with tempfile.TemporaryFile() as temp:
            # Распаковка zlib (raw deflate, windowBits=-15)
            decompressor = zlib.decompressobj(-15)
            CHUNK_SIZE = 10 * 1024 * 1024
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                temp.write(decompressor.decompress(chunk))
            temp.seek(0)

            # Получение заголовка
            header, supply_info_count = unpack("II", temp.read(8))

            for _ in range(supply_info_count):
                info = read_supply_info(temp)

            # Получение списка файлов
            included_files_count = unpack("I", temp.read(4))[0]

            included_files = []
            for _ in range(included_files_count):
                inc = read_included_file_info(temp)
                included_files.append(inc)

            # Извлечение файлов
            for src_path, filetime, size in included_files:
                clean_path = src_path.replace("\\\\", "/").replace("\\", "/")
                filename = os.path.basename(clean_path)
                out_path = os.path.join(output_dir, filename)

                with open(out_path, "wb") as out_file:
                    data = temp.read(size)
                    out_file.write(data)

if __name__ == "__main__":
    print("=== Авторизация на releases.1c.ru ===")
    username = input("Введите логин (обычно email): ").strip()
    password = getpass.getpass("Введите пароль: ")
    print("=== Указание версий компонентов ===")
    from components_config import COMPONENTS

    component_pages = []
    for comp in COMPONENTS:
        version = input(f"Введите версию {comp['name']} (оставьте пустым для значения по умолчанию '{comp['version']}'): ").strip()
        if version == "":
            version = comp['version']

        page_url = f"{BASE_URL}/version_files?nick={comp['nick']}&ver={version}"
        component_pages.append((page_url, comp['name']))

    if not login_1c(username, password):
        print("Авторизация не удалась.")
        input("Нажмите Enter для выхода...")
        exit(1)

    for page_url, component_name in component_pages:
        download_components_from_page(page_url, component_name)

    print("\n=== Поиск и обработка EFD-файлов в distr ===")
    for filename in os.listdir(DOWNLOAD_DIR):
        if filename.lower().endswith('.zip'):
            cf_filename = filename.split("_")[0].lower() + ".cf"
            zip_path = os.path.join(DOWNLOAD_DIR, filename)
            print(f"Проверяем ZIP: {filename}")
            try:
                import zipfile
                with zipfile.ZipFile(zip_path) as z:
                    for name in z.namelist():
                        if name.lower().endswith('.efd'):
                            print(f"  Найден EFD: {name}")
                            efd_filename = os.path.basename(name)
                            efd_temp = os.path.join(DOWNLOAD_DIR, efd_filename)
                            if not os.path.abspath(efd_temp).startswith(os.path.abspath(DOWNLOAD_DIR)):
                                print(f"  Подозрительный путь: {name}")
                                continue
                            efd_data = z.read(name)
                            with open(efd_temp, "wb") as f:
                                f.write(efd_data)

                            extracted_dir = os.path.join(DOWNLOAD_DIR, "tmp_extracted")
                            extract_efd(efd_temp, extracted_dir)
                            os.remove(efd_temp)

                            for extracted_filename in os.listdir(extracted_dir):
                                if extracted_filename == "1cv8.cf":
                                    print(f"Копирую {extracted_filename} в {cf_filename}")
                                    shutil.copy(os.path.join(extracted_dir, extracted_filename), os.path.join(DOWNLOAD_DIR, cf_filename))
                            shutil.rmtree(extracted_dir)
                            os.remove(zip_path)
                            break



            except Exception as e:
                print(f"  Ошибка обработки {filename}: {e}")

    print(f"\nФайлы конфигураций извлечены в {os.path.abspath(DOWNLOAD_DIR)}")