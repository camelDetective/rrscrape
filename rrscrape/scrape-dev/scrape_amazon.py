from typing import List, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.core.os_manager import ChromeType

from ..consts import VALUE_TYPES


def get_amazon_page_data(url: str, container_ids: List[str]) -> Optional[List[BeautifulSoup]]:
    """
    Fetches the Amazon page and returns the requested containers as BeautifulSoup objects. If the page cannot
        be fetched, returns None.

        This has a LOT of overhead because Amazon anti-bot scraping measures are very strong.

    WARNING: This function is not yet implemented. Amazon is very difficult to scrape due to anti-bot measures.
        Trying to scrape Amazon will likely result in a CAPTCHA challenge, and eventually a ban.
        Trust me, I've tried. - camelDetective

    :param url: The URL of the Amazon page.
    :param container_ids: A list of container IDs to extract from the page.
    :return: A BeautifulSoup object representing the page content.
    """
    raise NotImplementedError

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # create a driver object using driver_path as a parameter
    managers = {
        'chrome': partial(ChromeDriverManager, chrome_type=ChromeType.GOOGLE),
        'chromium': partial(ChromeDriverManager, chrome_type=ChromeType.CHROMIUM),
        'brave': partial(ChromeDriverManager, chrome_type=ChromeType.BRAVE),
        'edge': EdgeChromiumDriverManager,
        # 'firefox': GeckoDriverManager
    }
    while managers:
        try:
            choice = random.choice(list(managers.keys()))
            driver_manager = managers.pop(choice)().install()  # randomly select a driver manager
            driver = webdriver.Firefox if choice == 'firefox' else webdriver.Chrome
            service = FirefoxService if choice == 'firefox' else ChromeService
            driver = driver(options=options, service=service(driver_manager))  # assign your website to scrape
            driver.get(url)
            driver.implicitly_wait(5)
            containers = []
            for container_id in container_ids:
                container = driver.find_element(By.ID, value=container_id)
                driver.implicitly_wait(random.expovariate(0.75))  # wait for a random time
                containers.append(container)
            # # title, author, blurb, rating, ratings count, number of books in series,
            # centercol_container = driver.find_element(By.ID, value='centerColumn')
            # # publisher, publication date, page count
            # info_container = driver.find_element(By.ID, value='detailBulletsWrapper_feature_div')

            driver.quit()
        except KeyError:
            print('All browser drivers have been rejected by Amazon.')
            return
        containers = [BeautifulSoup(container.get_attribute('innerHTML'), 'lxml') for container in containers]
        return containers


def amazon_scrape(url: str) -> Dict[str, VALUE_TYPES]:
    """
    Scrapes an Amazon book page and extracts the following columns:
        'Amazon Title',
        'Amazon Author',
        'Amazon Blurb',
        'Amazon Publisher',
        'Amazon Publication TS',
        'Amazon Series Length',
        'Amazon Rating',
        'Amazon Ratings Count',
        'Amazon Page Count',
    WARNING: This function is not yet implemented. Amazon is very difficult to scrape due to anti-bot measures.
    :param url:
    :return:
    """
    raise NotImplementedError
    url = url.split('?')[0]  # remove any query parameters
    # raise NotImplementedError


    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # create a driver object using driver_path as a parameter
    driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()))
    driver.get(url)
    driver.implicitly_wait(5)