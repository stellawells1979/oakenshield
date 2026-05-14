
'''
Telegram 分享链接 requests 预检器。

核心职责：
- True：链接可用，可以继续交给 TDLib
- False：链接明确无效，不要交给 TDLib
- None：请求超时、代理失败、网络异常、页面结构异常，暂时无法判断
'''



import re
from urllib.parse import urlparse
import requests
from lxml import html

class ShareLinkChecker:
    """
    Telegram 分享链接 requests 预检器。

    核心职责：
    - True：链接可用，可以继续交给 TDLib
    - False：链接明确无效，不要交给 TDLib
    - None：请求超时、代理失败、网络异常、页面结构异常，暂时无法判断
    """

    DEFAULT_HEADERS = {
        "Host": "t.me",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="114", "Google Chrome";v="114", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    DEFAULT_PROXIES = {
        "http": "http://127.0.0.1:10809",
        "https": "http://127.0.0.1:10809",
    }

    INVALID_TITLE_KEYWORDS = (
        "Telegram: Contact",
    )

    INVALID_DESCRIPTION_KEYWORDS = (
        "If you have Telegram, you can contact",
        "Username not found",
        "This channel is inaccessible",
        "This group is inaccessible",
        "This username is not occupied",
    )

    VALID_BUTTON_TEXTS = {
        "SEND MESSAGE",
        "START BOT",
        "VIEW IN TELEGRAM",
        "VIEW POST",
        "PREVIEW CHANNEL",
        "VIEW IN CHANNEL",
        "JOIN CHANNEL",
        "JOIN GROUP",
    }

    def __init__(self, proxies=None, headers=None, timeout=10):
        """
        :param proxies: requests 代理配置
        :param headers: 请求头
        :param timeout: 超时时间
        """
        self.proxies = proxies if proxies is not None else self.DEFAULT_PROXIES
        self.headers = headers if headers is not None else self.DEFAULT_HEADERS
        self.timeout = timeout
        self.session = requests.Session()
        self.last_error = None

    def check(self, url):
        """
        检查 Telegram 分享链接是否可用。

        :param url: Telegram 分享链接
        :return: True / False / None
        """
        self.last_error = None

        if not self.is_tme_url(url):
            self.last_error = "不是 Telegram 分享链接"
            return False

        try:
            response = self.session.get(
                url,
                headers=self.headers,
                proxies=self.proxies,
                timeout=self.timeout,
                allow_redirects=True,
            )

        except requests.exceptions.Timeout:
            self.last_error = "请求超时"
            return None

        except requests.exceptions.ProxyError:
            self.last_error = "代理连接失败"
            return None

        except requests.exceptions.ConnectionError:
            self.last_error = "网络连接失败"
            return None

        except requests.exceptions.RequestException as error:
            self.last_error = f"请求异常：{error}"
            return None

        if response.status_code == 404:
            self.last_error = "HTTP 404，链接不存在"
            return False

        if response.status_code >= 500:
            self.last_error = f"Telegram 服务异常：HTTP {response.status_code}"
            return None

        if response.status_code >= 400:
            self.last_error = f"HTTP {response.status_code}"
            return False

        try:
            response.encoding = response.apparent_encoding
            tree = html.fromstring(response.text)
        except Exception as error:
            self.last_error = f"HTML 解析失败：{error}"
            return None

        return self.check_tree(tree, response.text)

    def check_tree(self, tree, page_text):
        """
        根据 Telegram HTML 页面结构判断链接是否有效。
        """
        title = self.get_meta(tree, "og:title")
        description = self.get_meta(tree, "og:description")

        if self.has_invalid_feature(title, description, page_text):
            return False

        if self.has_valid_feature(tree, title, description, page_text):
            return True

        self.last_error = "页面没有明确的有效或无效特征"
        return None

    def has_invalid_feature(self, title, description, page_text):
        """
        判断是否命中明确无效特征。
        """
        title = self.clean_text(title)
        description = self.clean_text(description)
        page_text = page_text or ""

        if title:
            for keyword in self.INVALID_TITLE_KEYWORDS:
                if keyword.lower() in title.lower():
                    self.last_error = f"标题命中无效特征：{keyword}"
                    return True

        if description:
            for keyword in self.INVALID_DESCRIPTION_KEYWORDS:
                if keyword.lower() in description.lower():
                    self.last_error = f"描述命中无效特征：{keyword}"
                    return True

        if "tgme_page_extra" not in page_text and "tgme_page_title" not in page_text:
            if "If you have Telegram, you can contact" in page_text:
                self.last_error = "页面内容命中联系人占位页"
                return True

        return False

    def has_valid_feature(self, tree, title, description, page_text):
        """
        判断是否命中有效特征。
        """
        page_text = page_text or ""

        if title and not title.startswith("Telegram: Contact"):
            return True

        if description:
            return True

        button_text = self.first_text(
            tree,
            '//*[contains(@class, "tgme_page_action")]//a/text() | '
            '//*[contains(@class, "tgme_page_context_link_wrap")]//a/text() | '
            '//*[contains(@class, "tgme_page_widget_action")]//a/text()'
        )

        if button_text and button_text.upper() in self.VALID_BUTTON_TEXTS:
            return True

        if "tgme_page_title" in page_text:
            return True

        if "tgme_page_extra" in page_text:
            return True

        if "tgme_page tgme_page_post" in page_text:
            return True

        if "<iframe" in page_text and "telegram-widget" in page_text:
            return True

        return False

    @classmethod
    def is_tme_url(cls, url):
        """
        判断是否为 Telegram 分享链接。
        """
        if not url:
            return False

        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return False

        return parsed.netloc in {"t.me", "www.t.me", "telegram.me", "www.telegram.me"}

    @classmethod
    def clean_text(cls, value):
        """
        清理文本。
        """
        if not value:
            return None

        value = str(value).replace("\xa0", " ")
        value = re.sub(r"\s+", " ", value)

        return value.strip() or None

    @classmethod
    def first_text(cls, tree, xpath):
        """
        获取 xpath 匹配到的第一个文本。
        """
        result = tree.xpath(xpath)
        if not result:
            return None

        value = result[0]

        if isinstance(value, str):
            return cls.clean_text(value)

        return cls.clean_text(value.text_content())

    @classmethod
    def get_meta(cls, tree, property_name):
        """
        获取 OpenGraph meta 信息。
        """
        return cls.first_text(tree, f'//meta[@property="{property_name}"]/@content')


check_share = ShareLinkChecker()

if __name__ == "__main__":

    print(check_share.check('https://t.me/nbgzd/180122'))



