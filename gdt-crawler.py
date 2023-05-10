import os
import shutil
from time import sleep
import asyncio
import traceback
import zipfile
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from config import Config
from werkzeug.wrappers import Response
import json
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
from constants import Constant
from anticaptchaofficial.imagecaptcha import *
import urllib.request
import time
from selenium.webdriver.chrome.service import Service
from croniter import croniter


async def retryIfFailure(retryCount=1, func=None, secondsBetweenRetry=0):
    if not func:
        raise ValueError("Function is not defined for retry!")
    for i in range(1, retryCount + 1):
        if i > 1:
            print(f"Retrying {i} time.")

        try:
            result = await func()
            return result
        except Exception as error:
            print(f"Call function {func.__name__}: {error}")
            if i < retryCount:
                sleep(secondsBetweenRetry)


query_url = "https://hoadondientu.gdt.gov.vn:30000/query/invoices/purchase?sort=tdlap:desc,khmshdon:asc,shdon:desc&size={{size}}&search=tdlap=ge={{startDate}};tdlap=le={{endDate}};ttxly==5"
invoices = []
username = "0107731027"
password = "Tsc2023!@#"
DOWNLOAD_DIRECTORY = ""


def downloadChromeDriver(version):
    urllib.request.urlretrieve(
        "https://chromedriver.storage.googleapis.com/"
        + version
        + "/chromedriver_win32.zip",
        "chromedriver_win32.zip",
    )
    while not os.path.exists("chromedriver_win32.zip"):
        time.sleep(1000)
    if os.path.exists(os.getcwd() + "\\webdriver\\chromedriver.exe"):
        os.remove(os.getcwd() + "\\webdriver\\chromedriver.exe")
    with zipfile.ZipFile("chromedriver_win32.zip", "r") as zip:
        zip.extractall(os.getcwd() + "\\webdriver\\")
    if os.path.exists("chromedriver_win32.zip"):
        os.remove("chromedriver_win32.zip")


async def do_crawl_gdt(crawlInfo):
    driver = None
    try:
        global query_url, invoices

        startDate = crawlInfo.get("startDate")
        endDate = crawlInfo.get("endDate")
        username = crawlInfo.get("username")
        password = crawlInfo.get("password")
        worker_index = 1

        DOWNLOAD_DIRECTORY = os.getcwd() + "\\Downloads\\" + str(worker_index) + "\\"
        if os.path.exists(DOWNLOAD_DIRECTORY):
            shutil.rmtree(DOWNLOAD_DIRECTORY, ignore_errors=True)
        os.makedirs(DOWNLOAD_DIRECTORY)
        options = webdriver.ChromeOptions()
        options.add_argument("no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--safebrowsing-disable-download-protection")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--start-maximized")
        options.headless = Config.HEADLESS
        # Chỉ sử dụng với On-Prem PLX (khi bị hỏi harmful)
        # ua = UserAgent(browsers=["edge"])
        # userAgent = ua.random
        userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        # userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        # options.add_argument("user-data-dir=" + os.getcwd() + "\\profiledir\\" + str(worker_index) + "\\User Data") #Path to your chrome profile
        options.add_argument(f"user-agent={userAgent}")

        extset = ["enable-automation", "ignore-certificate-errors"]
        options.add_experimental_option("excludeSwitches", extset)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--safebrowsing-disable-download-protection")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-site-isolation-trials")
        options.add_argument("safebrowsing-disable-extension-blacklist")
        prefs = {
            "download.default_directory": DOWNLOAD_DIRECTORY,  # set up download directory
            "safebrowsing.enabled": True,  # disable xml download asking
            "profile.default_content_setting_values.automatic_downloads": 1,  # allow multiple files download
            "download.prompt_for_download": False,
        }
        # if rpa.get('options') == 'AUTO_DOWNLOAD_PDF':
        #     prefs.update({ 'plugins.plugins_list': [{ 'enabled': False, 'name': 'Chrome PDF Viewer' }] })
        #     prefs.update({ 'plugins.always_open_pdf_externally': True })
        #     prefs.update({"pdfjs.disabled": True})
        #     prefs.update({"pdfjs.enabledCache.state": False})
        #     prefs.update({ 'browser.helperApps.neverAsk.saveToDisk': 'application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml' })
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        params = {"behavior": "allow", "downloadPath": DOWNLOAD_DIRECTORY}
        driver.execute_cdp_cmd("Page.setDownloadBehavior", params)

        # OPEN_URL
        driver.get("https://hoadondientu.gdt.gov.vn/")
        # EXECUTE_SCRIPT
        # const modal = document.querySelector("div.ant-modal-content")
        # if (modal) {
        #     const closeButton = document.evaluate('//button[@aria-label="Close" and contains(@class, "ant-modal-close")]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
        #     closeButton.singleNodeValue.click()
        # }
        notifModal = driver.find_element(
            By.CSS_SELECTOR, Constant.SELECTOR["modalContentTag"]
        )
        if notifModal != None:
            closeModalButton = driver.find_element(
                By.XPATH, Constant.SELECTOR["closeModalContentX"]
            )
            if closeModalButton != None:
                closeModalButton.click()

        # CLICK
        # XPATH
        # //span[text()="Đăng nhập"]
        loginButton = driver.find_element(By.XPATH, Constant.SELECTOR["openLoginFormX"])
        loginButton.click()
        # INPUT_TEXT
        # CSS_SELECTOR
        # input#username
        usernameField = driver.find_element(
            By.CSS_SELECTOR, Constant.SELECTOR["usernameInput"]
        )
        usernameField.send_keys(username)
        # INPUT_TEXT
        # CSS_SELECTOR
        # input#password
        passwordField = driver.find_element(
            By.CSS_SELECTOR, Constant.SELECTOR["passwordInput"]
        )
        passwordField.send_keys(password)
        # GET_CAPTCHA
        # CSS_SELECTOR
        # body > div:nth-child(9) > div > div.ant-modal-wrap.ant-modal-centered > div > div.ant-modal-content > div.ant-modal-body > form > div > div:nth-child(3) > div > div.ant-col.ant-col-24.ant-form-item-control-wrapper > div > span > div > img
        ele = driver.find_element(By.CSS_SELECTOR, Constant.SELECTOR["captchaImgTag"])
        with open(DOWNLOAD_DIRECTORY + "captcha.png", "wb") as file:
            file.write(ele.screenshot_as_png)
        solver = imagecaptcha()
        solver.set_verbose(1)
        solver.set_key("17b427ab988978f05102996f17cd706d")
        loginCaptcha = solver.solve_and_return_solution(
            DOWNLOAD_DIRECTORY + "captcha.png"
        )
        print("CAPTCHA: " + loginCaptcha)
        # INPUT_TEXT
        # CSS_SELECTOR
        # div.ant-modal-content input#cvalue
        captchaInput = driver.find_element(
            By.CSS_SELECTOR, Constant.SELECTOR["captchaInputTag"]
        )
        captchaInput.send_keys(loginCaptcha)
        # CLICK
        # XPATH
        # //button[@type='submit' and span[text()='Đăng nhập']]
        loginButton = driver.find_element(By.XPATH, Constant.SELECTOR["loginButtonTag"])
        loginButton.click()
        # DELAY
        # 2
        time.sleep(2)
        # REFRESH
        driver.refresh()
        # EXECUTE_SCRIPT
        # DIRECT
        # return JSON.parse(document.querySelector("script#__NEXT_DATA__").innerHTML).props.initialState.authReducer.jwt
        script = 'return JSON.parse(document.querySelector("script#__NEXT_DATA__").innerHTML).props.initialState.authReducer.jwt'
        auth_token = driver.execute_script(script)
        headers = {"Authorization": "Bearer " + auth_token}
        print(headers)
        state = None
        size = 30

        query_url = (
            query_url.replace("{{size}}", str(size))
            .replace("{{startDate}}", str(startDate))
            .replace("{{endDate}}", str(endDate))
        )

        while True:
            url = (
                str(query_url)
                if (state is None)
                else str(query_url + "&state=" + state)
            )

            print("url: " + url)
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception("Fail to crawl: ", response.content)
            json_data = response.json()
            temp_invoices = json_data.get("datas")
            temp_state = json_data.get("state")
            invoices.extend(temp_invoices)
            if temp_state is not None:
                state = temp_state
            else:
                break

        return invoices
    except Exception as error:
        driver.quit()
        print(error)
        raise error


def cron_to_vietnamese(cron_string):
    parts = cron_string.split()
    minute = parts[0]
    hour = parts[1]
    day_of_month = parts[2]
    month = parts[3]
    day_of_week = parts[4]

    # Convert minute
    if minute == "*":
        minute_str = "Mỗi phút"
    else:
        minute_str = f"Vào phút {minute}"

    # Convert hour
    if hour == "*":
        hour_str = "Mỗi giờ"
    else:
        hour_parts = hour.split("/")
        if len(hour_parts) == 2:
            hour_str = f"Qua mỗi {hour_parts[1]} giờ từ {hour_parts[0]} giờ đến 23 giờ"
        else:
            hour_str = f"Vào lúc {hour} giờ"

    # Convert day of month
    if day_of_month == "*":
        day_of_month_str = "Mỗi ngày"
    else:
        day_of_month_str = f"Vào ngày {day_of_month}"

    # Convert month
    if month == "*":
        month_str = "Mỗi tháng"
    else:
        month_str = f"Vào tháng {month}"

    # Convert day of week
    if day_of_week == "*":
        day_of_week_str = "Mỗi ngày trong tuần"
    else:
        day_of_week_parts = day_of_week.split("/")
        if len(day_of_week_parts) == 2:
            day_of_week_str = f"Qua mỗi {day_of_week_parts[1]} ngày trong tuần từ {day_of_week_parts[0]} đến 6"
        else:
            day_of_week_str = f"Vào thứ {day_of_week}"

    return f"{minute_str} {hour_str} {day_of_month_str} {month_str} {day_of_week_str}"


async def main():
    crawlInfo = {
        "startDate": "05/05/2023T00:00:00",
        "endDate": "08/05/2023T23:59:59",
        "username": "0107731027",
        "password": "Tsc2023!@#",
    }
    base = datetime.now()
    iter = croniter("23 0-20/2 * * *", base)

    next_iter = iter.get_next(datetime)
    now = datetime.now()
    print(next_iter)
    print(now)
    print(next_iter > now)
    # print(iter.get_next(datetime) > datetime)
    # print(iter.get_next(datetime) < datetime)

    print(cron_to_vietnamese("23 0-20/2 * * *"))

    # await do_crawl_gdt(crawlInfo)
    # print(len(invoices))


asyncio.run(main())
