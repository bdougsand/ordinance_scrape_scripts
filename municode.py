import selenium
from selenium import webdriver

import json
import re
import time


def parent(element):
    return element.find_element_by_xpath("..")


def find_chapter_links(driver: selenium.webdriver.Chrome):
    items = driver.find_elements_by_css_selector("li a")
    for link in items:
        match = re.match(r"(?:chapter|article) (\d+)", link.text, re.I)
        if match:
            yield match.group(1), link


def find_sections(chapter_link):
    links = parent(chapter_link).find_elements_by_css_selector("li a")
    for link in links:
        match = re.match(r"sec(?:tion)?\.? ((?:\d+)(?:\.\d+)+)\. (.*)", link.text, re.I)
        if match:
            yield (match.group(1), match.group(2), link.get_attribute("href"))


def expand_and_scrape_chapter(link):
    if "active" not in parent(link).get_attribute("class"):
        link.click()
        time.sleep(0.2)
    return {sec: href for sec, _, href in find_sections(link)}


def find_all(driver):
    lis = driver.find_elements_by_tag_name("li")
    for li in lis:
        match =  re.match(
            r"(?:article|sec(?:tion)?) (\d+(?:\.\d+)*)\. - (.+)\.?", li.text, re.I)
        if match:
            link = li.find_element_by_tag_name("a")
            href = link and link.get_attribute("href")
            if link and href:
                yield (match.group(1), match.group(2), href, link)


def run():
    driver = webdriver.Chrome()
    driver.get("https://library.municode.com/ma/somerville/codes/zoning_ordinances?nodeId=ZOORSOMA01")
    return {sec: (name.title(), url)
            for sec, name, url, _ in find_all(driver)}


if __name__ == "__main__":
    with open("sections.json", "w") as output:
        json.dump(run(), output)
