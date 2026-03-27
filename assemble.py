'''
收集订阅信息
'''

import requests
from Log import loginfo
import logging
import json
from config import config
from convert import Convert

# 配置日志记录
log = loginfo('Assemble', logging.DEBUG, logging.ERROR)


class Assemble:
    '''
    V2Ray 订阅聚合工具类，从网络收集订阅内容并解码成 base64 编码格式的节点
    '''

    def __init__(self):
        '''
        初始化 Assemble 实例。
        '''

        self.v2rayNodes = config.v2rayNodes     # 收集到的节点保存到此文件
        self.subscribe_content = config.subscribe_content   # 下载的订阅内容临时保存到此文件

        self.submerge_urls = self.get_urls()    # 从订阅 url 汇总文件中提取可用的订阅URL
        self.datas = []

    def main(self):
        '''
        程序主入口
        '''
        log.info('开始从网络获取订阅内容')
        # 订阅更新模块
        for data in self.submerge_urls:
            url = data.get("url", "")
            method = data.get('update_method')
            substance = data.get('update_mark')
            level = data.get('level')       # 订阅 url 的可用级别，
            if method != 'auto' and level < 20:
                # 连续20次无法从该 url 获取到订阅内容后将跳过此 url
                continue

            # 检查是否已经更新
            result = self.check_update(url, substance)
            if not result:
                log.info(f"{url}, This subscribe update is not ")
                data.update({'level': level + 1})
                continue

            log.info(f" {url}, This subscribe is update, try download。")
            proxies = self.download_file(url)

            if not proxies:
                continue

            # 更新当前订阅 url 的更新标志
            data.update({'update_mark': result, 'level': 0})

            # 下载的订阅内容临时储存下来代后续解码
            with open(self.subscribe_content, "w", encoding="utf-8") as file:
                file.write(proxies)

            # base64 解码订阅内容，最终是一条条由 base64 编码的订阅节点
            result = Convert(self.subscribe_content).main()

            # 对解码下来的节点整理去重
            for node in result:
                if node in self.datas:
                    log.info('main: This node is duplicate')
                    continue
                self.datas.append(node)

            log.info(f'Downloaded, Parse node count： {len(self.datas)}')

        # 完成后将节点写入
        if self.datas:
            with open(self.v2rayNodes, 'w', encoding='utf-8') as file:
                file.write('\n'.join(self.datas))

        # 更新标志
        with open(config.subscribe_urls, 'w', encoding='utf-8') as file:
            json.dump(self.submerge_urls, file, ensure_ascii=False, indent=4)

        log.info(f"本次从网络收集到 {len(self.datas)} 条订阅节点")


    @classmethod
    def check_update(cls, url, substance):
        """
        判断 URL 对应的订阅内容是否需要更新，并返回最新内容（如果更新）。
        :return: 若有更新，返回订阅内容；否则返回 None。
        """
        # 获取之前缓存的头部数据或哈希值
        last_etag = None
        last_modified = None
        if substance:
            last_etag = substance.get("etag")
            last_modified = substance.get("last_modified")

        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:  # 正常返回内容

                new_etag = response.headers.get("ETag")
                new_modified = response.headers.get("Last-Modified")

                # 根据 ETag 或 Last-Modified 或 Hash 判断是否变化
                if new_etag and new_etag != last_etag:
                    return {'etag': new_etag}
                if new_modified and new_modified != last_modified:
                    return {'modified': new_modified}
        except requests.RequestException as e:
            print(f"check_update: {e}")
        return None

    @classmethod
    def download_file(cls, url):
        """
        从远程 URL 下载内容，并返回文件的文本内容。
        如果请求失败或超时，将返回 None。

        :param url: 要下载的远程文件地址。
        :return: 返回下载的内容（字符串形式），或者 None（下载失败）。
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 如果 HTTP 响应状态码不是 200，则抛出 HTTPError
            return response.text  # 返回内容（通常是 Base64 数据）
        except requests.RequestException as e:

            log.error(f"【download file】: {e}，URL: {url}")
            return None

    @classmethod
    def get_urls(cls):
        '''
        从指定路径获取订阅 URL，并检查是否需要更新数据库中的记录。
        :return: 订阅信息的列表，每个元素为字典格式，包含 URL 和相关元数据。
        工作流程：
        1. 读取指定文件以获取订阅 URL。
        2. 遍历 URL 列表，检查在数据库中是否已有记录：
            - 如果不存在，则插入新记录到数据库。
        3. 查询数据库中所有订阅条目，整理并返回为统一的列表格式。
        '''
        try:
            with open(config.subscribe_urls, encoding='utf-8') as file:
                return json.loads(file.read())
        except Exception as e:
            log.error(e)
            exit()



if __name__ == "__main__":

    submerge = Assemble()

    submerge.main()






