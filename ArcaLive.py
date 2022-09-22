import requests
from bs4 import BeautifulSoup
from cloudscraper import create_scraper
import json

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

class ArcaLive:
    def __init__(self, CHANNEL_URL_PART: str, ACCOUNT: dict = None):
        if ACCOUNT is None:
            self.BOT_ACCOUNT = {
                "ID": "",
                "PW": "비번"
            }
        else:
            self.BOT_ACCOUNT = ACCOUNT
        self.CHANNEL_URL_PART = CHANNEL_URL_PART
        self.LOGIN_URL = "https://arca.live/u/login"
        self.RW_CHANNEL_POST_URL = "https://arca.live/b/revivedwitch/write"
        # self.SESSION = requests.Session()
        self.SESSION = self._CreateSession_BYPASS()

    def _CreateSession_BYPASS(self):
        # self.SESSION = create_scraper()
        return create_scraper()


    def _GetSiteHtml(self, SITE_REQUEST_RESPONSE: requests.models.Response) -> BeautifulSoup:
        if SITE_REQUEST_RESPONSE.status_code == 200:
            return BeautifulSoup(SITE_REQUEST_RESPONSE.text, "html.parser")
        else:
            raise ConnectionError(f"스테이터스 코드가 200이 아닙니다. \n current response status code : {SITE_REQUEST_RESPONSE}")

    def _GetData_CSRF(self, URL) -> str:
        HTML = self._GetSiteHtml(SITE_REQUEST_RESPONSE = self.SESSION.get(URL))
        CSRF = HTML.find("input", {"name": "_csrf"}).attrs.get("value")
        # print(f'CSRF : {CSRF}\nELEMENT : {HTML.find("input", {"name": "_csrf"})}')
        return CSRF

    def _GetData_GOTO(self, URL) -> str:
        HTML = self._GetSiteHtml(SITE_REQUEST_RESPONSE = self.SESSION.get(URL))
        GOTO = HTML.find("input", {"name": "goto"}).attrs.get("value")
        # print(f'GOTO : {GOTO}\nELEMENT : {HTML.find("input", {"name": "goto"})}')
        return GOTO if GOTO != "" else "/"

    def _GetData_TOKEN(self, URL) -> str:
        HTML = self._GetSiteHtml(SITE_REQUEST_RESPONSE = self.SESSION.get(URL))
        TOKEN = HTML.find("input", {"name": "token"}).attrs.get("value")

        return TOKEN

    def ArticleLineChanger(self, ARTICLE_DATA: str) -> str:
        # return string은 html의 형식으로 이루어진 string으로 리턴
        RT_ARTICLE_DATA = ""
        for ARTICLE_LINE in ARTICLE_DATA.split("\n"):
            RT_ARTICLE_DATA += f"<p>{ARTICLE_LINE}</p>"
        return RT_ARTICLE_DATA


    def CreateLoginPayloadData(self, URL) -> dict:
        LOGIN_PAYLOAD = {
            "username": self.BOT_ACCOUNT.get("ID"),
            "password": self.BOT_ACCOUNT.get("PW"),
            "_csrf": self._GetData_CSRF(URL = URL),
            "goto": self._GetData_GOTO(URL = URL)
        }

        # print(f"PAYLOAD : {LOGIN_PAYLOAD}")

        return LOGIN_PAYLOAD

    def CreateWritePayload(self, URL, TITLE: str, CONTENT: str) -> dict:
        ARTICLE_WRITE_PAYLOAD = {
            "_csrf": self._GetData_CSRF(URL),
            "token": self._GetData_TOKEN(URL),
            "contentType": "html",
            "category": "게임공지/공식",
            "title": TITLE,
            "content": CONTENT
        }

        return ARTICLE_WRITE_PAYLOAD

    def Login(self):
        LOGIN_RQ_RESPONSE = self.SESSION.post(self.LOGIN_URL, data = self.CreateLoginPayloadData(self.LOGIN_URL))
        if LOGIN_RQ_RESPONSE.status_code == 200:
            print("로그인에 성공하였습니다.")
        else:
            raise ConnectionError(f"로그인에 실패하였습니다.\nrequest response current status code : {LOGIN_RQ_RESPONSE.status_code}")


    def WriteArticle(self, TITLE: str, CONTENT: str):
        # 글머리 element : <input type="radio" name="category" id="category-<글머리 종류>" value="<글머리 종류>" data-prevent-delete="true">
        # 글머리 종류 : 질문, 정보, 공략, 공지, 창작/짤/핫산, 19+, 나눔/이벤트/인증, 모집, 청문회, 운영

        # token - input 태그 element : <input type="hidden" name="token" value="2edc099da1cf1d0a">

        # contentType element : <input type="hidden" name="contentType" value="html">

        # write payload
        # _csrf: nycSFMGd-grDjqe-ecdZAN1D0JO-1kR8b9mk
        # token: 2edc099da1cf1d0a
        # contentType: html
        # category: 게임공지/공식
        # title: 깨어난?
        # content: <p>도배하는건 아닌대..</p><p>페이로드 확인좀 하고갈께..</p><p><img src="//ac2.namu.la/20220329sac2/3ed258d0802f80cb2ea1fb95a112361ac8b90cdfb68b505623b160fd22e6f7f8.jpg" class="arca-emoticon fr-fic fr-dii" width="100" height="100" data-type="emoticon"></p>

        WRITE_RQ_RESPONSE = self.SESSION.post(
            self.RW_CHANNEL_POST_URL,
            data = self.CreateWritePayload(
                URL = self.RW_CHANNEL_POST_URL,
                TITLE = TITLE,
                CONTENT = self.ArticleLineChanger(ARTICLE_DATA = CONTENT)
            )
        )

        print(WRITE_RQ_RESPONSE)






if __name__ == "__main__":
    ARCA_API = ArcaLive(
        CHANNEL_URL_PART = "revivedwitch",
    )
    ARCA_API.Login()
    ARCA_API.WriteArticle(
        TITLE = "봇검증 우회 테스트",
        CONTENT = "현재 아카라이브 사이트에 적용되어있는 봇검증을 우회하는 기능 적용테스트입니다."
    )




