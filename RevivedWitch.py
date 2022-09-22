import bs4
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import json
import time
import requests
from Class.ArcaLive import ArcaLive
from Class.DirectoryTool import DirectoryTool

class READ_WRITE:
    def READ_JSON(FILE_DIR: str) -> dict:
        """FILE_DIR에는 데이터를 읽어올 JSON데이터 파일 디렉토리를 입력해주세요.

        리턴
        --------
        READ_JSON(FILE_DIR = :func:`JSON_DIR`)\n
        ==> READ_USER_DATA[:func:`"KEY"`]
        """

        with open(f"{FILE_DIR}", "r", encoding="utf-8") as READ_USER_PROFILE:
            READ_USER_DATA = json.load(READ_USER_PROFILE)
            READ_USER_PROFILE.close()

        return READ_USER_DATA  # READ_USER_DATA타입 = DICT

class INTERNAL_FUNC:
    def __init__(self, DRIVER: webdriver.Chrome, TIME_OUT = 2):
        self.DRIVER = DRIVER
        self.TIME_OUT = TIME_OUT

    def DriverGet_CSS(self, CSS_SELECTOR):
        return self.DRIVER.find_element(by = By.CSS_SELECTOR, value = CSS_SELECTOR)

    def DriverGet_XPATH(self, XPATH):
        return self.DRIVER.find_element(by = By.XPATH, value = XPATH)

    def DriverGet_CLSNAME(self, CLSNAME):
        return self.DRIVER.find_element(by = By.CLASS_NAME, value = CLSNAME)

    def DriverGet_Wait(self, ELEMENT):
        return WebDriverWait(driver = self.DRIVER, timeout = self.TIME_OUT).until(EC.presence_of_element_located(ELEMENT))

class RevivedWitch:
    def __init__(self, CHANNEL: str, ARCA_API_OBJECT: ArcaLive, ACCOUNT: dict = None):
        self.CHANNEL_URL = "https://arca.live/b/" + CHANNEL
        self.ARCA_API = ARCA_API_OBJECT

        if ACCOUNT is None:
            self.BOT_ACCOUNT = {
                "ID": "",
                "PW": "비번"
            }
        else:
            self.BOT_ACCOUNT = ACCOUNT

        self.CAFE_NOTICE_URL = "https://cafe.naver.com/ArticleList.nhn?search.clubid=30450887&search.menuid=1&search.boardtype=L"
        self.CAFE_BASE_URL = "https://cafe.naver.com"

        # self.DRIVER_DIR = "chromedriver.exe" if __name__ == "__main__" else ".//Class//chromedriver.exe"
        self.DRIVER_DIR = DirectoryTool.ChromeDriverDir()
        self.BROWSER_DIR = DirectoryTool.ChromeBrowserDir()
        self.NOTICE_DATA_DIR = "NOTICE_DATA.json" if __name__ == "__main__" else ".//Class//NOTICE_DATA.json"
        self.CHROME_DRIVER_OPTION = self._ChromeDriverOption()


    def _ChromeDriverOption(self) -> webdriver.ChromeOptions:
        OPTION = webdriver.ChromeOptions()
        OPTION.add_argument("headless")
        OPTION.add_argument("--disable-gpu")
        OPTION.add_argument("--no-sandbox")
        OPTION.add_argument('--disable-dev-shm-usage')
        OPTION.binary_location = self.BROWSER_DIR
        return OPTION

    def _IsNewNotice(self, NOTICE_HTML: bs4.element.Tag) -> bool:
        ARTICLE_NUMBER_SELECTOR = 'td[class="td_article"] > div[class="board-number"] > div[class="inner_number"]'
        ARTICLE_NUMBER = int(NOTICE_HTML.select_one(ARTICLE_NUMBER_SELECTOR).text)
        LASTEST_ARTICEL_NUMBER = READ_WRITE.READ_JSON(FILE_DIR = self.NOTICE_DATA_DIR).get("LASTEST_NOTICE_NUMBER")

        return ARTICLE_NUMBER > LASTEST_ARTICEL_NUMBER

    def _GetNoticeArticle_URL(self, NOTICE_HTML: bs4.element.Tag) -> str:
        ARTICLE_URL_SELECTOR = 'td[class="td_article"] > div[class="board-list"] > div[class="inner_list"] > a[class="article"]'
        ARTICLE_URL = NOTICE_HTML.select_one(ARTICLE_URL_SELECTOR).get("href")

        return ARTICLE_URL

    def _GetIframeHtmlSrc_URL(self, NOTICE_HTML: bs4.element.Tag) -> str:
        IFRAME_SELECTOR = 'iframe[id="cafe_main"][name="cafe_main"][title="카페 메인"]'
        IFRAME_SRC_URL = NOTICE_HTML.select_one(IFRAME_SELECTOR).get("src")

        return IFRAME_SRC_URL

    def _GetArticleNumber(self, NOTICE_HTML: bs4.element.Tag) -> int:
        return int(NOTICE_HTML.select_one('td[class="td_article"] > div[class="board-number"] > div[class="inner_number"]').text)

    def _GetArticleTitle(self, NOTICE_HTML: bs4.element.Tag) -> str:
        return NOTICE_HTML.select_one('td[class="td_article"] > div[class="board-list"] > div[class="inner_list"] > a[class="article"]').text


    def _GetArticleData(self, NOTICE_HTML: bs4.element.Tag) -> dict:

        RT_NOTICE_ARTICLE_DATA = {
            "TITLE": self._GetArticleTitle(NOTICE_HTML).strip(),
            "NUMBER": self._GetArticleNumber(NOTICE_HTML),
            "CONTENT": ""

        }


        NOTICE_CONTENT_HTML = self.GetCafeNoticeArticle_HTML(
            ARTICLE_URL = self._GetNoticeArticle_URL(NOTICE_HTML = NOTICE_HTML)
        )
        NOTICE_ARTICLE_DATAS = NOTICE_CONTENT_HTML.select(
            'div[class="se-module se-module-text"] > p[class="se-text-paragraph se-text-paragraph-align-"]')

        for NOTICE_ARTICLE_DATA in NOTICE_ARTICLE_DATAS:
            NOTICE_ARTICLE_LINE = NOTICE_ARTICLE_DATA.text
            RT_NOTICE_ARTICLE_DATA["CONTENT"] += NOTICE_ARTICLE_LINE + "\n"


        return RT_NOTICE_ARTICLE_DATA




    def GetCafeNoticeBoard_HTML(self, SITE_REQUEST_RESPONSE: requests.models.Response) -> BeautifulSoup:
        if SITE_REQUEST_RESPONSE.status_code == 200:
            return BeautifulSoup(SITE_REQUEST_RESPONSE.text, "html.parser")

        else:
            raise ConnectionError("깨어난 마녀 카페와 연결하는데 실패하였습니다.")

    def GetCafeNoticeArticle_HTML(self, ARTICLE_URL: str) -> BeautifulSoup:
        WEBDRIVER = webdriver.Chrome(self.DRIVER_DIR, options = self.CHROME_DRIVER_OPTION)
        IN_FUNC = INTERNAL_FUNC(DRIVER = WEBDRIVER)
        IN_FUNC.DRIVER.get(self.CAFE_BASE_URL + ARTICLE_URL)
        time.sleep(5)
        IN_FUNC.DRIVER.switch_to.frame("cafe_main")
        NOTICE_ARTICLE_HTML = IN_FUNC.DRIVER.page_source
        IN_FUNC.DRIVER.quit()

        return BeautifulSoup(NOTICE_ARTICLE_HTML, "html.parser")



    def GetCafeNewNotice(self) -> list:
        RT_NOTICE_ARTICLE_DATAS = []

        CAFE_HTML = self.GetCafeNoticeBoard_HTML(
            SITE_REQUEST_RESPONSE = requests.get(self.CAFE_NOTICE_URL)
        )

        NOTICE_BOARD_CONTENTS = [ELEM for ELEM in CAFE_HTML.select('div[class="article-board m-tcol-c"]:not([id="upperArticleList"]) > table > tbody > tr ')]
        print(f"1페이지 공지글 개수{NOTICE_BOARD_CONTENTS.__len__()}")
        for NOTICE_CONTENT_NUM in range(NOTICE_BOARD_CONTENTS.__len__()):
            NOTICE_CONTENT = NOTICE_BOARD_CONTENTS[NOTICE_CONTENT_NUM]
            if self._IsNewNotice(NOTICE_HTML = NOTICE_CONTENT):
                print(f"크롤링된 {NOTICE_BOARD_CONTENTS.__len__()}개의 공지글중 {NOTICE_CONTENT_NUM + 1}번 게시글은 새로 등록된 게시글입니다.\n\n")
                RT_NOTICE_ARTICLE_DATAS.append(
                    self._GetArticleData(
                        NOTICE_HTML = NOTICE_CONTENT
                    )
                )
            else:
                READ_DATA = READ_WRITE.READ_JSON(FILE_DIR = self.NOTICE_DATA_DIR)
                with open(self.NOTICE_DATA_DIR, "w", encoding = "utf-8") as WRITE_PROFILE:
                    READ_DATA["LASTEST_NOTICE_NUMBER"] = self._GetArticleNumber(NOTICE_HTML = NOTICE_BOARD_CONTENTS[0])
                    json.dump(READ_DATA, WRITE_PROFILE, indent = 4)




        return RT_NOTICE_ARTICLE_DATAS


    def UploadArticleToArcaLiveChannel(self, NOTICE_ARTICLE_DATA_LIST: [dict]):
        for NOTICE_ARTICLE_DATA in NOTICE_ARTICLE_DATA_LIST:
            self.ARCA_API.WriteArticle(
                TITLE = NOTICE_ARTICLE_DATA.get("TITLE"),
                CONTENT = NOTICE_ARTICLE_DATA.get("CONTENT")
            )


    def DataReadTest(self) -> int:
        return READ_WRITE.READ_JSON(FILE_DIR = self.NOTICE_DATA_DIR).get("LASTEST_NOTICE_NUMBER")

    def SetTestData(self, TEST_VAR: int) -> None:

        with open(self.NOTICE_DATA_DIR, "w", encoding = "utf-8") as WRITE_PROFILE:
            TEST_DATA = {
                "LASTEST_NOTICE_NUMBER": TEST_VAR
            }

            json.dump(TEST_DATA, WRITE_PROFILE, indent = 4)




    # 공지사항 내용 iframe src경로 ==> //cafe.naver.com/MyCafeIntro.nhn?clubid=30450887&tc=naver_search




if __name__ == "__main__":
    ARCA_API = ArcaLive(CHANNEL_URL_PART = "revivedwitch")
    RW = RevivedWitch(CHANNEL = "1", ARCA_API_OBJECT = ARCA_API)

