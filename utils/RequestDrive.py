'''
j
'''
import os
import json
import time
import random
import threading
from json import JSONDecodeError

import requests
import logging
import config
from queue import Queue
from fake_useragent import UserAgent
from utils.tools import tools
from utils.WholeTime import wholetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from logmanage import LogManager

log = LogManager('Requestdrive', logging.WARNING, logging.INFO)


class ProxiesAssemble:
    '''
    https/socks代理集合器
    1.  定时从 https://proxylist.geonode.com/api/proxy-list?protocols=socks5&page=1&limit=500&sort_by=responseTime&sort_type=asc
        获取代理数据解析并测试后加入代理汉

    '''

    def __init__(self):

        self.proxies_queue = Queue()
        self.invalid_proxies = []  # 无效或检查过的代理容器，避免过量检测
        self.unknown_proxies = []  # 未检查过的代理
        self.test_url = [
            'https://www.instagram.com/',
        ]

    def get_proxy(self):
        '''
        从代理池获取一个可用代理
        :return:
        '''
        if self.proxies_queue.empty():
            return None

        return self.proxies_queue.get()

    def check_proxies(self, session_obj, timeout=5):
        '''
        测试代理的可用性
        '''
        requsest_error = {
            404: '链接不存在',
            500: '目标服务器错误'
        }

        url = random.choice(self.test_url)
        try:
            res = session_obj.get(url, timeout=timeout)

            if res.status_code == 200:
                return True

            log.info(f"Requsest Error: {res.status_code} {requsest_error.get(res.status_code, '未知错误')}")
            return None

        except requests.exceptions.Timeout:
            Error = "Error: 请求超时"
            return None

        except requests.exceptions.ProxyError:
            Error = f"Error: 代理连接失败"
            return None

        except requests.exceptions.ConnectionError:
            Error = "Error: 网络连接失败"
            return None

        except requests.exceptions.RequestException as e:
            Error = f"Error: 请求异常 {e}"
            return None

    def get_original_proxy(self):
        '''
        获取原始代理数据
        '''
        result = []

        result.extend(self.get_original_proxy_form_geonode())

        result.extend(self.get_original_proxy_form_911proxy())

        result.extend(self.get_original_proxy_form_proxyfreeonly())

        for row in result:
            if row not in self.invalid_proxies:
                self.unknown_proxies.append(row)
                self.invalid_proxies.append(row)

    def get_original_proxy_form_geonode(self):
        '''
        从 https://geonode.com/free-proxy-list 获取 https/socks5 代理
        下载地址：https://proxylist.geonode.com/api/proxy-list?protocols=socks5%2Chttps&page=1&limit=500&sort_by=responseTime&sort_type=asc
        下载内容返回的数据示例 {"data":[proxy data .....],"total":1420,"page":1,"limit":500}
        :return: list
        '''
        page = 1
        result = []
        for _ in range(5):
            # 最多尝试5次下载，当下载到最后一页是会退出

            original_url = (f'https://proxylist.geonode.com/api/proxy-list?protocols=socks5%2Chttps&page={page}'
                            f'&limit=500&sort_by=responseTime&sort_type=asc')
            save_path = os.path.join(config.local_proxies_dir, f'proxies-{page}.txt')

            print(f'正在从 https://geonode.com/free-proxy-list 下载代理列表/{page}.......')

            if not tools.download_file(original_url, save_path):
                continue

            time.sleep(0.2)

            proxy_list = self.read_file_content(save_path)

            try:
                proxy_list = json.loads(proxy_list)

            except json.JSONDecodeError:

                log.warning(f"Error: 读取原始代理数据失败，文件内容不是有效的JSON格式")

            except Exception as e:
                log.warning(f"Error: 读取原始代理数据失败 {e}")
                continue

            result.extend(proxy_list.get("data", []))

            all_page = proxy_list.get("total", 0) // proxy_list.get("limit", 0) + 1

            if page >= all_page:
                break

            page += 1

        return self.parse_proxy_data(result)

    def get_original_proxy_form_911proxy(self) -> list:
        '''
        https://www.911proxy.com/zh-hans/proxyfree/
        下载地址
        https://www.911proxy.com/web_v1/free-proxy/list?page_size=60&page=1&protocol=2
        https://www.911proxy.com/web_v1/free-proxy/list?page_size=60&page=1&protocol=8
        protocol=2: https
        protocol=8: socks5
        :return:
        '''

        url = 'https://api.911proxy.com/web_v1/free-proxy/list?page_size=60&page={}&protocol={}'

        proxy_list = []
        protocols = {2: 'https', 8: 'socks5', }
        for key, protocol in protocols.items():

            for index in range(10):

                curr_url = url.format(index + 1, key)
                save_path = os.path.join(config.local_proxies_dir, f'911proxy-{protocol}-{index + 1}.txt')

                print(f'正在从 https://911proxy.com 下载代理列表 {protocol}/{index + 1}.......')
                if not tools.download_file(curr_url, save_path):
                    continue

                try:
                    data = json.loads(self.read_file_content(save_path))
                except Exception as e:
                    continue

                if data.get('msg') != 'SUCCESS' or not data.get('data'):
                    continue

                data = data.get('data')

                curr_page = data.get('page')
                page_count = data.get('page_count')
                proxy_list.extend(data.get('list', []))

                if curr_page >= page_count:
                    break

        result = []
        for row in proxy_list:
            protocol = protocols.get(row.get('protocol'))
            result.append({
                'https': f"{'http' if protocol == 'https' else protocol}://{row.get('ip')}:{row.get('port')}",
            })
        return result

    def get_original_proxy_form_proxyfreeonly(self):
        '''
        从 https://proxyfreeonly.com/ 下载代理数据
        下载地址 https://proxyfreeonly.com/api/free-proxy-list?limit=1000&page=1&sortBy=lastChecked&sortType=desc
        :return:
        '''
        print(f'正在从 https://proxyfreeonly.com 下载代理列表 .......')

        url = 'https://proxyfreeonly.com/api/free-proxy-list?limit=1000&page=1&sortBy=lastChecked&sortType=desc'
        save_path = os.path.join(config.local_proxies_dir, 'proxyfreeonly.txt')

        if not tools.download_file(url, save_path):
            return []

        try:
            data = json.loads(self.read_file_content(save_path))
        except Exception as e:
            return []

        return self.parse_proxy_data(data)

    @classmethod
    def parse_proxy_data(cls, data):
        '''

        :param data:
        :return:
        '''
        result = []
        for row in data:
            protocols = None
            for p in ['socks5', 'socks4', 'https']:
                if p in row.get('protocols'):
                    protocols = p
                    break
            if not protocols:
                continue

            result.append({
                'https': f"{'http' if protocols == 'https' else protocols}://{row.get('ip')}:{row.get('port')}"
            })
        return result

    @classmethod
    def read_file_content(cls, path):
        '''
        读取文件内容
        :param path:
        :return:
        '''
        result = None
        try:
            with open(path, "r", encoding="utf-8") as f:
                result = f.read()
        except Exception as e:
            log.warning(f"Error: 下载或读取原始代理数据失败 {e}")

        return result

    @classmethod
    def update_proxies_local(cls, data, path=None):
        '''
        储存部分代理到本地，以便调试或程序频繁重启是重复使用这时代理
        :param data:
        :param path: 本地路径，如果不提供，则使用项目配置文件中的路径
        :return:
        '''
        if not data:
            return False

        if not path:
            path = config.local_proxies_queue_path

        try:
            with open(path, "r", encoding="utf-8") as f:
                local_data = json.loads(f.read())
        except Exception as e:
            local_data = []

        local_proxies = [row.get('proxy') for row in local_data]

        curr_unix = wholetime.datetime(Mat="%Y-%m-%d %H:%M:%S")
        for row in data:
            if row.get('proxy') not in local_proxies:
                local_data.append({
                    'created_at': curr_unix,
                    'proxy': row,
                })

        return tools.write_json_content(local_data, path)


class SessionStore(ProxiesAssemble):
    """
    requests.Session 会话仓库。

    只在程序运行期间维护多个 requests.Session 对象。
    不保存 cookies，不保存 UA 元数据，程序退出后会话状态全部丢弃。
    """

    def __init__(self, size=5, ttl=600, max_requests=50, test=None):
        """
        初始化 session 仓库。

        :param size: int session 数量，默认创建5个
        :param ttl: int 单个 session 生存时间，单位秒，默认10分钟
        :param max_requests: int 单个 session 最大请求次数，默认50次
        :param test: bool 是否测试模式，测试模式下不会下载代理链接，而是加载本地链接汉
        """
        super().__init__()

        self.size = size
        self.session_ttl = ttl
        self.max_requests = max_requests
        self.test = test

        if not self.size:
            raise "Error: [SessionStore] - <__init__>: 第一个参数必须大于 0"

        self.thread_lock = threading.Lock()
        self.sessions = []

        print('正在初始化浏览器组件...........................')

        if self.test:
            # 如果是测试模式，则加载本地代理池
            self.load_local_proxies()

        self.update_proxies_queue(count=self.size + 5, max_workers=20)

        # 创建会话池
        self.create_sessions_pool()

        print('创建独立线程维护代理池...............')
        threading.Thread(target=self.daily_uphold_scheduler, daemon=True).start()

    def daily_uphold_scheduler(self):
        '''
        每日维护代理池
        '''
        # 测试模式下不会执行更新代理池的任务
        while not self.test:

            # 更新代理池，返回测试成功的代理和当前代理池的数量
            result = self.update_proxies_queue(max_workers=5)
            if result:
                # 将有效代理更新到本地代理池
                self.update_proxies_local(result[0])
            log.warning(f'更新代理池完成，当前代理池数量：{result[1]}')

            time.sleep(60 * 60)

    def update_proxies_queue(self, count=None, max_workers=10):
        '''
        创建代理池（使用线程池）
        在初始化阶段只创建会话池数量的代理，后续由独立的线程维护代理池
        :param count: 需要的代理数量
        :param max_workers: 最大线程数，默认10个并发
        :return:
        '''
        if not self.unknown_proxies:
            self.get_original_proxy()

        result = []  # 记录本次测试成功的代理

        def process_proxy(proxy):
            '''处理单个代理的检测和添加'''

            # 创建一个全新的会话来测试代理
            test_session = self.create_session(proxy)
            res = self.check_proxies(test_session)

            if not res:
                return proxy, False

            return proxy, True

        # 使用线程池处理
        print(f'正在检测 {len(self.unknown_proxies)} 条代理 .......')
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 创建线程线程池并提交所有任务
            futures = {executor.submit(process_proxy, proxy): proxy for proxy in self.unknown_proxies}

            # 处理完成的任务
            for future in as_completed(futures):
                # 迭代线程池读取返回值
                proxy, status = future.result()
                if status:
                    # 记录测试成功的代理
                    result.append(proxy)
                    self.proxies_queue.put(proxy)
                    # print(f'添加{proxy}到代理池 {len(result)}/{count if count else "unlimited"}')

                # 从未知的代理数据中删除检测过的代理
                self.unknown_proxies.remove(proxy)

                # 如果达到目标数量，取消剩余任务
                if count and len(result) >= count:
                    for f in futures:
                        f.cancel()
                    break

        if not count:
            # 如果没有指定数量，则全部测试完成，此时你需要确保未知的代理数据为空
            self.unknown_proxies = []

        # 返回本次测试成功的代理和当前代理池数量
        return result, self.proxies_queue.qsize()

    def create_sessions_pool(self, count=None):
        '''

        :param count:
        :return:
        '''
        if not count:
            count = self.size

        for index in range(count):
            print(f'正在创建 sessions 会话池 {index + 1}/{self.size}..........')
            self.create_sessions()

    def create_sessions(self, remove=None):
        '''
        创建一个 session 会话记录，DLid 有效时会删除 DLid 指定的 session 会话记录。
        一个完整的 session 会话记录包含以下参数：
            1. UID：唯一标识符，用于区分不同的 session 会话记录。
            2. session：session 对象，用于发送 HTTP 请求。
            3. created_at：创建时间，记录 session 会话记录的创建时间。
            4. request_count：请求次数，记录 session 会话记录的请求次数。
            5. busy：当前 session 是否正在使用，用于判断 session 是否可以被使用。
            6. product：健康指标，记录 session 会话在使用过程中的健康指标参数。

        :param remove: 如果指定 remove，则会删除些 session 会话记录。
        :return:
        '''

        uid = None
        uids = [row.get('id') for row in self.sessions]
        while not uid:
            # 确保创建了唯一的 UID
            uid = tools.brief_uid(8)
            if not uid in uids:
                break

        proxy = self.get_proxy()
        record = self.create_session(proxy)

        with self.thread_lock:
            self.sessions.append({
                "id": uid,
                "session": record,
                "created_at": time.time(),
                "request_count": 0 if proxy else self.max_requests // 2,    # 如果没有代理，则将请求次数设置为最大请求次数的一半
                "busy": False,  # 当前 session 是否正在使用
                'product': {'ErrorProxy': [0, 1], 'TimeOut': [0, 3], 'ErrorConnent': [0, 5]}  # 健康指标
            })

        if remove:
            # 移除指定的会话记录
            self.remove_sessions(remove)

        return record

    def create_session(self, proxy=None):
        """
        创建 session 连接池。
        也可以重建指定 UID 的会
        """

        user_agent = UserAgent().random
        headers = self.build_headers(user_agent)  # 创建请求头

        # 初始化一个会话对象
        session_obj = requests.Session()

        # 向会话对象添加请求头
        session_obj.headers.update(headers)
        if proxy:
            # 向会话对象添加可能存在的代理
            session_obj.proxies.update(proxy)

        return session_obj

    @classmethod
    def build_headers(cls, user_agent):
        """
        构建请求头。
        """
        return {
            "User-Agent": user_agent,
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
            ),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

    def is_valid(self, record):
        """
        判断 session 是否仍然有效。每个 session 在创建时都设定了时效和使用量
        """
        if record is None:
            return False

        if time.time() - record["created_at"] > self.session_ttl:
            # 判断是否超时
            return False

        if record["request_count"] >= self.max_requests:
            # 判断是否超量
            return False

        return True

    def acquire(self, timeout=5):
        """
        获取一个可用 session 记录。
        """

        record = False  # 初始化一个会话记录

        while timeout > 0:

            if record is None:
                # 如果没有空闲的会话，则向会话池追加一个新的会话对象
                self.create_sessions_pool(1)
                record = False

            time.sleep(0.05)
            timeout = timeout - 0.1

            with self.thread_lock:

                # 迭代 self.sessions 池，排除忙线记录，筛选出可用 session 对象
                available = [record for record in self.sessions if not record["busy"]]

                if not available:
                    # 如果没有空闲的会话，则返回一个空 record，以便向会话池追加一个新的会话对象
                    record = None
                    log.warning(f"[SessionStore] - <acquire> : 当前没有 session 对象可用，正在尝试重建 session 池")
                    continue
                else:
                    # 随机获取一个 session
                    record = random.choice(available)
                    # 将当前 session 标记为忙线
                    record["busy"] = True

            if not self.is_valid(record):
                # 检查 session 如果超时或者超量则将创建一个新会话并添加到代理池并移除当前 session 对象
                self.create_sessions(record["id"])
                continue

            return record

        log.error(f"[SessionStore] - <acquire> : 获取 session 对象出错，请检查代码逻辑")
        return None

    def get_session(self, timeout=3):
        """
        如果某些流程必须连续使用同一个 session，可以用此方法
        使用完后需要调用 release_raw_session(session_id) 归还。
        """
        record = self.acquire(timeout=timeout)

        if record is None:
            return None, None

        return record["id"], record["session"]

    def release_sessions(self, session_id, product=None):
        """
        释放 session 会话对象。
        session 会话对象在使用过程中，其代理的质量会逐步下降，当达到一定阈值时，会将其从会话池中删除。
        :param session_id: 要释放的 session 会话对象的 ID。
        :param product: 该 session 会话对象的健康指标参数。
        :return: 返回三种状态：
                None: 表示 session 会话对象不存在或未找到。
                Flase: 表示 session 会话对象的健康指标超标，已将其从会话池中删除。
                True: 表示 session 会话对象已正常释放
        """

        if product and product not in ['ErrorProxy', 'TimeOut', 'ErrorConnent']:
            # 确保接收到正确的 product 健康参数，否则不检查 sessions 的健康指标
            log.warning(
                f"[SessionStore] - <release_sessions> : product 参数必须是 ['ErrorProxy', 'TimeOut', 'ErrorConnent']"
            )
            product = None

        result = None
        with self.thread_lock:

            for record in self.sessions:

                if record["id"] == session_id and product:
                    # 检查当前 session 的健康指标，超标则删除当前记录
                    record_product = record.get('product').get(product)
                    if record_product[0] >= record_product[1]:
                        # 如果健康指标超标，将 result 设置为 False，以便稍后删除该会话
                        result = False
                    else:
                        # 更新健康指标参数以及将会话状态设置为空闲
                        record_product[0] += 1
                        record.update({"busy": False})
                        result = True
                    break

                elif record["id"] == session_id:
                    record.update({"busy": False})
                    record.update({'product': {'ErrorProxy': [0, 1], 'TimeOut': [0, 3], 'ErrorConnent': [0, 5]}})
                    result = True
                    break

        if result is False:
            # 删除健康超标的记录，必须在锁外执行
            log.warning(f"当前 session 会话的健康指标【{product}】超标，已删除：{session_id}")
            self.create_sessions(session_id)

        return result

    def remove_sessions(self, DLid):
        '''
        从 sessions 会话池中移除一个 sessions 对象
        :param DLid:
        :return:
        '''
        # 删除无效 session 对象
        with self.thread_lock:
            for record in self.sessions:
                if record["id"] == DLid:
                    self.sessions.remove(record)
                    break

    def close_all(self):
        """
        关闭所有 session。
        """
        with self.thread_lock:
            records = self.sessions[:]

        for record in records:
            try:
                record["session"].close()
                record["busy"] = False
            except Exception:
                pass

    def load_local_proxies(self):
        """
        加载本地代理链接。
        """
        data = self.read_file_content(config.local_proxies_queue_path)
        if not data:
            raise '加载本地代理池失败..........................'

        try:
            data = json.loads(data)
        except JSONDecodeError:
            raise '加载本地代理池失败 - json 反序列化失败..........................'

        for row in data:
            self.unknown_proxies.append(row.get('proxy'))


browser = SessionStore(
    size=5,
    ttl=12000,
    max_requests=300
)

if __name__ == "__main__":

    urls = [
        "https://www.google.com",
        "https://www.bing.com",
        "https://www.baidu.com",
    ]

    for link in urls:
        sid, session = browser.get_session()
        try:
            response = session.request('get', link, timeout=10)
            print(f"{link} - 状态码: {response.status_code}")
        except Exception as error:
            print(f"{link} - 错误: {error}")
        finally:
            browser.release_sessions(sid)

    time.sleep(5000)
    print(browser.proxies_queue.qsize())

    browser.close_all()


