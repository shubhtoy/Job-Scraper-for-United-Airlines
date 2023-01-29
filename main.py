from undetected_chromedriver import Chrome
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import requests
import json


# URLS
base_url = "https://careers.united.com/us/en/job/{}/"
url = "https://careers.united.com/widgets"

# Output file
OUTPUT_FILE = "jobs.json"

# Options
HEADLESS = False

payload = {
    "lang": "en_us",
    "deviceType": "desktop",
    "country": "us",
    "pageName": "search-results",
    "ddoKey": "refineSearch",
    "sortBy": "",
    "subsearch": "",
    "from": 0,
    "jobs": True,
    "counts": True,
    "all_fields": ["category", "country", "state", "city", "type", "jobId"],
    "size": 100,
    "clearAll": False,
    "jdsource": "facets",
    "isSliderEnable": False,
    "pageId": "page16",
    "siteType": "external",
    "keywords": "",
    "global": True,
    "selected_fields": {"country": ["India"]},
    "locationData": {},
}

headers = {
    "authority": "careers.united.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.7",
    "content-type": "application/json",
    "cookie": "VISITED_LANG=en; VISITED_COUNTRY=us; PHPPPE_NPS=a; PLAY_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7IkpTRVNTSU9OSUQiOiJhYmY3YmI5Ny1jNDVmLTQzOTAtYjU1MC04NTJhMGNiNWZiZDMifSwibmJmIjoxNjc0OTI0NTI1LCJpYXQiOjE2NzQ5MjQ1MjV9.TSD5soLUToBBS_TAxUrH8e9_gNym8FyLXOZXSbqx5Lg; JSESSIONID=abf7bb97-c45f-4390-b550-852a0cb5fbd3; PHPPPE_GCC=a; JSESSIONID=8e00760b-3ca2-47f3-87d4-2797e9af7051; PLAY_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7IkpTRVNTSU9OSUQiOiI4ZTAwNzYwYi0zY2EyLTQ3ZjMtODdkNC0yNzk3ZTlhZjcwNTEifSwibmJmIjoxNjc1MDA5NTUyLCJpYXQiOjE2NzUwMDk1NTJ9.37pRkW6C13L00jHeYur4pPlO2CobkalzuhxphumlZTk",
    "origin": "https://careers.united.com",
    "referer": "https://careers.united.com/us/en/search-results",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "x-csrf-token": "e7786bad83174c8a828049d412a18684",
}


def get_total_jobs():
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    data = json.loads(response.text)
    no_of_jobs = int(data["refineSearch"]["totalHits"])

    return [no_of_jobs // 100, no_of_jobs % 100]


def get_jobs(no: list):
    all_jobs = []
    if no[0] != 0:
        for i in range(no[0]):
            payload["from"] = i * 100
            response = requests.request(
                "POST", url, headers=headers, data=json.dumps(payload)
            )
            data = json.loads(response.text)
            jobs = data["refineSearch"]["data"]["jobs"]
            all_jobs.extend(jobs)
    if no[1] != 0:
        payload["from"] = no[0] * 100
        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(payload)
        )
        data = json.loads(response.text)
        jobs = data["refineSearch"]["data"]["jobs"]
        all_jobs.extend(jobs)

    return all_jobs


def get_description(jobs):
    options = Options()
    if HEADLESS:
        options.add_argument("--headless")
    driver = Chrome(options=options)
    for job in jobs:
        jobId = job["jobId"]
        url = base_url.format(jobId)
        driver.get(url)
        element = WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[section[@class="job-description"]]',
                )
            )
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        for data in soup.findAll("section", {"class": "job-description"}):
            job["description"] = data.text
            break
    driver.close()
    return jobs


def to_json(jobs):
    new_json = {}
    new_json["Company"] = "United Airlines"
    new_json["Career Page"] = base_url
    new_json["data"] = jobs
    with open(OUTPUT_FILE, "w") as f:
        json.dump(new_json, f, indent=4)
    return


def main():

    print("Starting")
    print("Getting total jobs")
    no_of_jobs = get_total_jobs()
    print("Total jobs: ", (no_of_jobs[0] * 100) + no_of_jobs[1])
    print("Getting jobs")
    jobs = get_jobs(no_of_jobs)
    # print("Getting description")
    jobs = get_description(jobs)
    # print(len(jobs))
    print("Total jobs scraped:", len(jobs))
    print("Writing to file")
    to_json(jobs)

    print("Done")


if __name__ == "__main__":
    main()
