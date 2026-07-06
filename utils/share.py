'''
;
'''
import json
import time
import random
import threading
import requests
import re
from lxml import html
from datetime import datetime, timedelta
import config
from utils import quick
from utils.tagmuster import tagmuster
from TDLibeObjectClass.Chat import Chat
from TDLibeObjectClass.Message import MessageLinkInfo
from TDLibeObjectClass.Supergroupfullinfo import SupergroupFullInfo
from database import sql

import logging
from logg import LogManager

log = LogManager('Share', logging.WARNING, logging.INFO)

headers = {
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

invalid_title_keywords = (
    "Telegram: Contact",
)

# 如果分享链接无效，通常会包含以下文本
invalid_description_keywords = (
    "If you have Telegram, you can contact",
    "Username not found",
    "This channel is inaccessible",
    "This group is inaccessible",
    "This username is not occupied",
)

valid_button_texts = {
    "Send Message",
    "Start Bot",
    "View in Telegram",
    "View Post",
    "PREVIEW CHANNEL",
    "VIEW IN CHANNEL",
    "Join Channel",
    "Join Group",
}

error_exp = {
    "This channel can’t be displayed because it violated Telegram's Terms of Service.": '无法显示此频道，因为它违反了Telegram的服务条款',
    "This channel can’t be displayed because it was used to spread pornographic content.": '无法显示此频道，因为它被用来传播色情内容。',
    "Post not found": '帖子未找到',
    "This group has been temporarily suspended to give its moderators time to clean up after"
    " users who posted illegal pornographic content. We will reopen the group as soon as it"
    " complies with the Telegram Terms of Service again.": '在用户发布非法色情内容后，该组已被暂时暂停，以便其版主有时间进行清理。一旦该群再'
                                                           '次符合Telegram服务条款，我们将重新开放该群',
    "This group can’t be displayed because it was used to spread pornographic content.": '无法显示此群组，因为它被用来传播色情内容。',
    "Sorry, this group is temporarily inaccessible on your device to give its moderators time to clean up after users who "
    "posted pornographic content. We will reopen the group as soon as order is restored.": '很抱歉，您的设备暂时无法访问此群，以便'
    '其管理员有时间在发布色情内容的用户之后进行清理。一旦秩序恢复，我们将重新开放该组'
}


class ParseShareFromClient:
    '''
    解析客户端分享信息，
    '''

    def __init__(self):

        self.share_queue = set()  # 用于储存分享链接的客户端队列容器
        self.share_lock = threading.Lock()  # 线程锁
        self.next_time = time.time() + random.uniform(40, 120)  # 请求分享链接的间隔时间
        self.error_429 = 0  # 致命错误，其值表示停止请求到某个时间

    def add_client_task(self, link):
        '''
        向客户端队列容器追加需要解析的分享链接
        :param link:
        :return:
        '''
        with self.share_lock:
            if link not in self.share_queue:
                self.share_queue.add(link)
                log.info(f"添加客户端任务 {link}，当前客户端任务列表长度： {len(self.share_queue)}")
                return True
        return False

    def get_sharelink(self):
        '''
        从客户端队列容器中获取需要解析的分享链接，并生成合法的请求
        :return:
        '''
        now_time = time.time()
        with self.share_lock:
            # 确保没有429错误和确保与距离上次的请求间隔一定的时间差
            if self.error_429 > now_time or self.next_time > now_time:
                return []

        self.next_time = now_time + random.uniform(60, 120)

        link = None
        link_param = None
        with self.share_lock:

            try:
                while not link and not link_param:
                    link = self.share_queue.pop()
                    if not link:
                        continue
                    link_param = quick.parse_tme_url(link)
                    if not link_param:
                        continue
            except Exception as e:
                log.error(f"获取分享链接时发生错误：{e}")
            len_share_queue = len(self.share_queue)

        if not link or not link_param:
            return []

        log.info(f"获取客户端任务 {link}，当前客户端任务队列： {len_share_queue}")

        domain, name, extra = link_param
        if extra:
            return [{
                '@type': 'getMessageLinkInfo',
                'url': link,
                '@extra': f"share|get|messageLinkInfo|{name}|0|{link}"
            }]
        return [{
            '@type': 'searchPublicChat',
            'username': name,
            '@extra': f"share|search|chat|{name}|0|{link}"
        }]

    def parse_share_content(self, data):
        '''
        解析TDLib客户端请求到的分享链接详情
        :param data:
        :return:
        '''
        send_data = []
        data_type = data.get('@type')
        steat, method, obj, name, sid, link = data.get('@extra').split('|', 5)

        result = None
        if data_type == 'error':
            self.parse_error(data)

        elif obj == 'chat':
            result, send_data = self.parse_share_content_chat(data)

        elif obj == 'messageLinkInfo':
            result, send_data = self.parse_share_content_messageLinkInfo(data)

        elif obj == 'supergroupFullInfo':
            result = self.parse_share_content_supergroup(data)

        elif obj == 'chatHistory':
            result = self.parse_share_content_album(data)

        if result:
            update_link_to_databse(link, result, origin='TDLib')

        return send_data

    @classmethod
    def parse_share_content_chat(cls, data):
        '''
        解析聊天对象
        :param data:
        :return:
        '''
        send_data = []
        steat, method, obj, name, sid, url = data.get('@extra').split('|', 5)
        data = Chat(data).__dict__

        # 构建请求获取群组的描述字段
        if data.get('chat_type') == 'chatTypeSupergroup':
            send_data = {
                '@type': 'getSupergroupFullInfo',
                'supergroup_id': data.get('group_id'),
                '@extra': f"share|get|supergroupFullInfo|{name}|{data.get('group_id')}|{url}"
            }
        # chat对象仅能获取两项有效的参数
        result = {
            'type': 'channel' if data.get('channel') else 'group',
            'title': data.get('title'),
        }

        return result, send_data

    @classmethod
    def parse_share_content_messageLinkInfo(cls, data):
        '''

        :param data:
        :return:
        '''
        steat, method, obj, name, sid, link = data.get('@extra').split('|', 5)

        data = MessageLinkInfo(data.get('message')).__dict__

        description = data.get('caption') or data.get('text') or ''  # 通常是媒体消息的附件描述内容
        share_type = data.get('message_type').split('message')[-1]

        send_data = []
        result = {
            'type': share_type.lower() if share_type else None,
            'description': description,
            'members': data.get('interaction')
        }
        if description and data.get('entity'):
            # 提取描述文本中可能存在的标签
            tag = cls.parse_tag_fromtext(data.get('entity'))
            if tag:
                result.update({'tag': tag})

        # 如果没有媒体描述内容且消息是专辑相册(album),则说明描述内容可能包含在同一相册的其它媒体中
        if not description and data.get('album') and data.get('album_id') != '0':
            # 构建请求获取当前消息的上下文，以获取当前消息的描述字段内容
            send_data = {
                '@type': 'getChatHistory',
                'chat_id': data.get('chat_id'),
                'from_message_id': data.get('message_id'),  # 从相册消息 ID 开始（如果有）
                'offset_order': -10,
                'limit': 10,
                'only_local': False,
                '@extra': f"share|get|chatHistory|{name}|{data.get('album_id')}|{link}"
            }

        return result, send_data

    @classmethod
    def parse_share_content_supergroup(cls, data):
        '''
        解析解析分享内容中的超级群组对象

        :param data:
        :return:
        '''
        data = SupergroupFullInfo(data).__dict__
        description = data.get('description')
        if not description:
            return None

        result = {'description': description}
        tag = tagmuster.extract_tag(description)
        if tag:
            result.update({'tag': tag})

        return result

    @classmethod
    def parse_share_content_album(cls, data):
        '''
        解析分享内容中关于相册对像的信息
        如果在前面解析分享的帖子信息中缺少帖子的描述，通常会触发这个逻辑
        :param data:
        :return:
        '''
        steat, method, obj, name, sid, link = data.get('@extra').split('|', 5)
        for row in data.get('messages'):

            params = MessageLinkInfo(row).__dict__

            if params.get('album_id') == sid and params.get('caption'):
                # 提取描述文本
                description = params.get('caption')

                if not description:
                    return None

                result = {'description': description}
                # 提取可能存在的标签
                tag = tagmuster.extract_tag(description)
                if tag:
                    result.update({'tag': tag})
                return result
        return None

    def parse_error(self, error):
        '''

        :return:
        '''
        if error.get('code') == 429:
            retry = error.get('message').split('retry after')[-1].strip()
            with self.share_lock:
                # 在写入error_429错误值时确保error_429是在唯一线程内
                self.error_429 = int(retry) + time.time() + random.uniform(1200, 3600)
        log.error(f"Error: {error.get('message')}")

    @classmethod
    def parse_tag_fromtext(cls, entities=None):
        '''
        从可能包含标签的 entities 对象或文本中解析出标签
        :param entities:
        :return:
        '''
        result = []
        if entities:
            tags = [entity.get('text') for entity in entities if entity.get('type') == 'textEntityTypeHashtag']  # 媒体标签
            for tag in tags:
                if tag not in result:
                    result.append(tag)
        return result


class ParseShareFromHtml(ParseShareFromClient):
    '''
    以html方式解析分享链接
    '''

    def __init__(self):
        super().__init__()

        self.proxies = config.proxies
        self.timeout = 10
        self._thread_local = threading.local()

    def session_obj(self):
        """
        为每个线程创建并复用独立的 requests.Session。
        避免多个线程共享同一个 Session，同时保留连接复用能力。
        """
        if not hasattr(self._thread_local, "session"):
            session = requests.Session()
            session.headers.update(headers)
            self._thread_local.session = session

        return self._thread_local.session

    def parse_share_html(self, link):
        """
        根据 Telegram HTML 页面结构判断链接是否有效。
        注意，此方法在解析失败时返回 None 和返回 False 是不同意义的，None表示未知，除非在解析网页是获取到明确的无效信息时才
        能返回 Flase，否则像网络原因无法请求到网页或其它的错误就应该返回 None。
        如果是在Share.uphold_share_data()中调用此方法，当返回Flase时，会从数据库中删除该分享链接
        """
        # 解析url，此处可判断该url是否贴子链接
        link_param = quick.parse_tme_url(link)
        if not link_param:
            return None
        domain, name, extra = link_param

        # 获取分享链接的html内容
        page_text = self.check(f"{domain}/{name}")
        if not page_text:
            return page_text

        html_tree = html.fromstring(page_text)

        # 获取按钮文本
        button_text = self.get_button_text(html_tree)
        if button_text in ['Send Message', 'Start Bot']:
            log.info(f"Error: {link} 这是一个用户或者是一个机器人")
            return False

        if extra:
            # 如果是贴子，则调用贴子解析程序
            return self.parse_post(link)

        title = self.get_meta(html_tree, "og:title")
        description = self.get_meta(html_tree, "og:description")

        # 检查是否命中无效特征
        if self.has_invalid_feature(link, title, description, page_text):
            return False

        if description and description.startswith('You can view and join'):
            description = None

        type_ = self._detect_type(html_tree)
        if not type_:
            return None

        result = {
            'type': type_,
            'title': title,
            'description': description,
        }

        # 提取订阅数/成员数
        extra_selectors = [
            '//div[@class="tgme_page_extra"]',
            '//div[contains(@class, "tgme_page_extra")]'
        ]

        for selector in extra_selectors:
            extra = html_tree.xpath(f'string({selector})').strip()
            if extra:
                result.update({'members': self.parse_members(extra)})
                break
        return result

    def parse_post(self, link):
        '''
        解析帖子 信息
        :param link:
        :return:
        '''
        html_tree = self.get_embed_html(link)
        if not html_tree:
            return None

        # 转换 <br> 为换行
        for br in html_tree.xpath("//br"):
            br.tail = "\n" + (br.tail or "")

        error_selectors = [
            '//div[@class="tgme_widget_message_error"]'
        ]

        for selector in error_selectors:
            error = html_tree.xpath(f'string({selector})').strip()
            if error:
                log.info(f"Error: {link} {error_exp.get(error) if error in error_exp else error}")
                if "Terms of Service" in error or "Post not found" in error:
                    return False
                if "spread pornographic content" in error:
                    self.add_client_task(link)
                return None

        result = {}
        type_ = self._detect_media_type(html_tree)
        if not type_:
            return None

        result.update({'type': type_})

        # 提取帖子正文 - 更全面的选择器
        text_selectors = [
            '//div[@class="tgme_widget_message_text"]',
            '//div[@class="tgme_widget_message_bubble"]//div[@class="tgme_widget_message_text"]',
            '//div[contains(@class, "tgme_widget_message_text")]',
            '//div[@class="js-message_text"]',
            '//div[contains(@class, "message_media_content")]//div[@class="tgme_widget_message_text"]',
        ]

        for selector in text_selectors:
            text = html_tree.xpath(f'string({selector})').strip()
            if text:
                result.update({'description': text})
                break

        # 提取浏览次数
        views_selectors = [
            '//span[@class="tgme_widget_message_views"]',
            '//div[contains(@class, "views")]',
            '//span[contains(@class, "tgme_widget_message_views")]'
        ]

        for selector in views_selectors:
            # 解析贴子的浏览次数
            views = html_tree.xpath(f'string({selector})').strip()
            if views:
                result.update({'members': self.parse_members(views)})
                break

        return result

    def get_embed_html(self, base_url):
        """
        通过 embed 地址获取帖子详细信息
        """
        embed_url = f"{base_url}?embed=1&mode=tme"

        embed_headers = headers.copy()
        embed_headers["Referer"] = base_url

        try:
            response = self.session_obj().get(
                embed_url,
                headers=embed_headers,
                proxies=self.proxies,
                timeout=15
            )
            response.raise_for_status()
            return html.fromstring(response.text)

        except Exception as e:
            print(f"Error fetching embed {embed_url}: {e}")
            return {}

    def check(self, link):
        """
        检查 Telegram 分享链接是否可用。

        :param link: Telegram 分享链接
        :return: True / False / None
        """

        try:
            response = self.session_obj().get(
                link,
                headers=headers,
                proxies=config.proxies,
                timeout=self.timeout,
                allow_redirects=True,
            )

        except requests.exceptions.Timeout:
            log.info(f"Error: {link} 请求超时")
            return None

        except requests.exceptions.ProxyError:
            log.info(f"Error: {link} 代理连接失败")
            return None

        except requests.exceptions.ConnectionError:
            log.info(f"Error: {link} 网络连接失败")
            return None

        except requests.exceptions.RequestException as error:
            log.info(f"Error：{link} 请求异常 {error}")
            return None

        if response.status_code == 404:
            log.info(f"Error: {link} HTTP 404，链接不存在")
            return False

        if response.status_code >= 500:
            log.info(f"Error: {link} Telegram 服务异常：HTTP {response.status_code}")
            return None

        if response.status_code >= 400:
            log.info(f"Error: {link} HTTP {response.status_code}")
            return False

        try:
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as error:
            log.info(f"Error: {link} HTML 解析失败：{error}")
        return None

    @classmethod
    def get_button_text(cls, tree):
        '''

        :param tree:
        :return:
        '''
        button_selectors = [
            '//a[@class="tgme_action_button_new"]/text()',
            '//a[@class="tgme_action_button_new shine"]/text()'
        ]
        for selector in button_selectors:
            button_text = tree.xpath(selector)
            if button_text:
                return button_text[0].strip()
        return None

    @classmethod
    def parse_members(cls, text):
        '''
        解析成员数量或者浏览量
        :param text:
        :return:
        '''
        re_text = text.split('members')[0].replace(' ', '')
        re_text = re.findall(r'-?\d+\.?\d*e?-?\d*?', re_text)
        if re_text:
            if 'M' in text:
                return int(float(re_text[0]) * 1000000)
            return int(float(re_text[0]) * 1000) if 'K' in text else int(re_text[0])
        return None

    @classmethod
    def _detect_type(cls, tree):
        """
        检测频道/群组类型
        """
        # 检查是否为机器人
        if tree.xpath('//div[contains(text(), "bot")]') or tree.xpath('//div[contains(text(), "Bot")]'):
            return 'bot'

        # 检查订阅数格式
        extra = tree.xpath('string(//div[@class="tgme_page_extra"])').strip().lower()

        if 'subscriber' in extra or '订阅' in extra:
            return 'channel'
        elif 'member' in extra or '成员' in extra:
            return 'group'

        return None

    @classmethod
    def _detect_media_type(cls, tree):
        """
        检测媒体类型

        """

        # 检测照片 - 使用 contains 匹配，支持多个 class
        result = None
        if tree.xpath('//div[contains(@class, "tgme_widget_message_photo")]'):
            result = 'photo'
            # 进一步检查是否为多媒体组
            if tree.xpath('//div[contains(@class, "grouped_media")]'):
                print('这是相册')


        # 检测视频
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_video")]'):
            result = 'video'
            if tree.xpath('//div[contains(@class, "grouped_media")]'):
                print('这是视频集')


        # 检测文档/文件
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_document")]'):
            result = 'document'

        # 检测贴纸
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_sticker")]'):
            result = 'sticker'

        # 检测语音消息
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_voice")]'):
            result = 'voice'

        # 检测音频
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_audio")]'):
            result = 'audio'

        # 检测动画/GIF
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_animation")]'):
            result = 'animation'

        # 检测投票
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_poll")]'):
            result = 'poll'

        # 检测位置
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_location")]'):
            result = 'location'

        # 检测联系人
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_contact")]'):
            result = 'contact'

        # 检测游戏
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_game")]'):
            result = 'game'

        # 检测服务消息
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_service")]'):
            result = 'service'

        # 检测转发消息
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_forwarded")]'):
            result = 'forwarded'

        # 检测回复消息
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_reply")]'):
            result = 'reply'

        # 检测是否包含媒体但没匹配到具体类型
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_bubble")]//img | //video | //audio'):
            result = 'mixed_media'

        # 检测纯文本消息
        elif tree.xpath('//div[contains(@class, "tgme_widget_message_text")]'):
            result = 'text'

        return result

    @classmethod
    def get_meta(cls, tree, property_name):
        """
        获取 OpenGraph meta 信息。
        """
        return cls.first_text(tree, f'//meta[@property="{property_name}"]/@content')

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
    def clean_text(cls, value):
        """
        清理文本。
        """
        if not value:
            return None

        value = str(value).replace("\xa0", " ")
        value = re.sub(r"\s+", " ", value)

        return value.strip() or None

    def has_invalid_feature(self, link, title, description, page_text):
        """
        判断是否命中明确无效特征。
        """
        title = self.clean_text(title)
        description = self.clean_text(description)
        page_text = page_text or ""

        if title:
            for keyword in invalid_title_keywords:
                if keyword.lower() in title.lower():
                    log.info(f"{link} 标题命中无效特征：{keyword}")
                    return True

        if description:
            for keyword in invalid_description_keywords:
                if keyword.lower() in description.lower():
                    log.info(f"{link} 描述命中无效特征：{keyword}")
                    return True

        if "tgme_page_extra" not in page_text and "tgme_page_title" not in page_text:
            if "If you have Telegram, you can contact" in page_text:
                log.info(f"{link} 页面内容命中联系人占位页")
                return True

        return False


class Share(ParseShareFromHtml):
    '''
    主程序

    '''

    def __init__(self):
        super().__init__()
        self.aggregator_queue = set()
        self.aggregator_lock = threading.Lock()

        # 创建线程独立运行parse_share_link()
        threading.Thread(target=self.parse_share_link, daemon=True).start()

        # 创建定时任务，执行更新数据库中分享链接的更新
        threading.Thread(target=self.daily_uphold_scheduler, daemon=True).start()

    def aggregator_share_link(self, data):
        '''
                收集分享链接，将合格的分享铁道添加到 aggregator_queue 容器
                :param data:
                :return:
                '''

        for entity in data:
            if entity.get('type') != 'textEntityTypeTextUrl':
                continue

            link = entity.get('url')

            if not link:
                continue

            if not link.startswith('https://t.me/'):
                continue

            link_param = quick.parse_tme_url(link)
            if not link_param:
                continue
            domain, name, extra = quick.parse_tme_url(link)

            if name in config.service_paths:
                # 排除无效分享链接在一些telegram的保留链接
                continue

            # 检查数据库是否包含当前链接，如果存在则检查是否超过20天未更新
            query = f"SELECT `edited` FROM `{sql.table_shares}` WHERE `url` = %s"
            edited = sql.query(sql.database, query, [link])
            edited = edited[0].get('edited') if edited and edited[0] else None
            if edited and edited > datetime.now() - timedelta(days=20):
                continue

            # 将分享铁道添加到 aggregator_queue 容器
            with self.aggregator_lock:
                if link not in self.aggregator_queue:
                    self.aggregator_queue.add(link)

    def parse_share_link(self):
        '''
        解析分享链接
        :return:
        '''
        time.sleep(20)
        while True:
            link = self.get_link()
            if not link:
                time.sleep(2)
                continue

            result = self.parse_share_html(link)
            if not result:
                continue

            update_link_to_databse(link, result)

    def uphold_share_data(self):
        '''

        维护数据库中的分享链接，
        定期更新数据库的分享链接，包含更新分享链接的标题、类型、描述、标签等信息
        并将无效的分享链接清除
        :return:
        '''
        query = f"SELECT `url` FROM `shares` WHERE `edited` < DATE_SUB(NOW(), INTERVAL 10 DAY)"
        links = sql.query(sql.database, query, None)

        random.shuffle(links)
        for index, link in enumerate(links):
            link = link.get('url')
            if link.startswith('https://t.me/+'):
                continue

            result = self.parse_share_html(link)
            if not result:
                if result is False:
                    query = f"DELETE FROM `{sql.table_shares}` WHERE `url` = %s"
                    sql.query(sql.database, query, [link])
                    log.info(f"Delete this share link: {link}")
                continue

            update_link_to_databse(link, result)

        log.warning("Daily uphold scheduler is done")

    def daily_uphold_scheduler(self):
        '''
        定时任务，执行更新数据库中分享链接的更新
        :return:
        '''
        while True:
            now = datetime.now()
            next_run = now.replace(hour=4, minute=0, second=0, microsecond=0)

            if next_run <= now:
                next_run += timedelta(days=1)

            sleep_seconds = (next_run - now).total_seconds()
            log.warning(f"Daily uphold scheduler next run at {next_run}")

            time.sleep(sleep_seconds)

            try:
                log.warning("Daily uphold scheduler is running")
                self.uphold_share_data()
            except Exception as error:
                log.warning(f"Daily uphold scheduler error: {repr(error)}")

    def get_link(self):
        '''

        :return:
        '''
        link = None
        with self.aggregator_lock:
            try:
                while not link:
                    link = self.aggregator_queue.pop()
                    if not link:
                        continue
            except Exception as e:
                pass

        return link


def update_link_to_databse(link, data, render='admin', origin='Html'):
    '''
    将分享链接的 详情写入数据库
    :param link: 要写入的链接
    :param data: 当前分享链接的详情
    :param render: 提交者，默认admin
    :param origin: 分享链接的来源
    :return:
    '''
    query = f"SELECT `tag` FROM `shares` WHERE `url`=%s"
    row_tag = sql.query(sql.database, query, [link]) or []
    if row_tag and row_tag[0].get('tag'):
        row_tag = row_tag[0].get('tag').split(',')
    else:
        row_tag = []

    if data.get('tag'):
        # 将数据表中的原标签和解析结果的标签合并
        row_tag.extend(data.pop('tag'))
    else:
        # 如果没有标签，则尝试从描述或标题文本中提取可能存在的标签
        for row in [data.get('title'), data.get('description')]:
            if not row:
                continue
            tag_param = tagmuster.extract_tag(row)
            for item in tag_param:
                if item not in row_tag:
                    row_tag.append(item)

    if row_tag:
        # 将标签参数格式为string
        data.update({'tag': ','.join(row_tag)})

    change = ['`url`']
    values = [link]
    for key, value in data.items():
        if not value:
            continue
        if type(value) in [list, dict]:
            value = json.dumps(value, ensure_ascii=False)
        change.append(f"`{key}`")
        values.append(value)

    change.append('`render`')
    values.append(render)

    query = (f"INSERT INTO `{sql.table_shares}` ({', '.join(change)}) VALUES ({', '.join(['%s'] * len(values))}) "
             f"ON DUPLICATE KEY UPDATE {', '.join([f'{key}=%s' for key in change[1:]])}")
    sql.query(sql.database, query, values + values[1:])

    log.info(f"Update this share link: {link} to database, from {origin}")

share = Share()


if __name__ == '__main__':


    parse = Share()

    parse.uphold_share_data()













