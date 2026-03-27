'''
v2ray 应用的配置脚本
'''

import os
import json
import time

import requests
import zipfile
from config import config
import platform
from datetime import datetime
from tqdm import tqdm
import logging
from Log import loginfo


log = loginfo('V2RayCode', logging.DEBUG, logging.ERROR)

class V2rayCocde:
    '''
    e
    '''
    v2ray_download_url = "https://github.com/v2fly/v2ray-core/releases/latest/download"
    v2ray_files = {
        "Windows": "v2ray-windows-64.zip",  # 针对 64 位 Windows 系统
        "Linux": "v2ray-linux-64.zip",  # 针对 64 位 Linux 系统
        "Darwin": "v2ray-macos-64.zip",  # 针对 macOS 系统
        # 你可以扩展其他架构和系统版本的支持
    }

    def __init__(self):

        self.versions_url = config.v2ray_versions_url
        self.v2ray_version = None
        self.v2ray_download_url = None
        self.v2ray_file_size = 0
        self.system = platform.system().lower()  # 获取系统类型，如 'windows', 'linux', 'darwin'
        self.architecture = platform.machine().lower()  # 获取架构，如 'x86_64', 'arm64'


        self.v2ray_path = os.path.join(config.v2ray_path, self.system)
        self.v2ray_code = os.path.join(self.v2ray_path, 'v2ray.exe') if self.system == 'windows' else os.path.join(self.v2ray_path, 'v2ray')


    def main(self):
        '''

        :return:
        '''
        if self.system not in ['windows', 'linux']:
            log.error('当前系统不支持运行')
            exit()

        if self.check_v2ray():
            return self.v2ray_code

        if not self.get_v2ray_versions():
            log.error('获取 v2ray 版本信息失败')
            return None
        log.info(f'当前 v2ray 最新版本： {self.v2ray_version}，准备下载当前文件')
        download_path = os.path.join(config.temp_path, 'v2ray.zip')
        if not self.download_file(self.v2ray_download_url, download_path, config.proxy):
            log.info('文件下载失败，请查看日志文件')

        if self.extract_zip_file(download_path, self.v2ray_path):
            return self.v2ray_code

        time.sleep(2)

        if self.check_v2ray():
            return self.v2ray_code


        return None

    def get_v2ray_versions(self):
        '''

        :return:
        '''


        if '64' in self.architecture:
            v2ray_name = f'v2ray-{self.system}-64.zip'
        else:
            v2ray_name = f'v2ray-{self.system}-32.zip'

        content = None
        try:
            response = requests.get(self.versions_url, proxies=config.proxy, timeout=10, stream=True)
            if response.status_code == 200:
                content = response.text
        except Exception as e:
            log.error(f'下载 v2ray 版本信息失败: {e}')
            return None

        if not content:
            log.error(f'未获取到 v2ray 版本信息')
            return None

        try:
            temp_path = os.path.join(config.temp_path, 'v2ray_version.json')
            with open(temp_path, 'w', encoding='utf-8') as file:
                json.dump(content, file, ensure_ascii=False, indent=4)
            content = json.loads(content)
        except Exception as e:
            log.error(f'写入 v2ray 版本信息失败: {e}')
            return None

        new_versions = 0
        for data in content:
            created = datetime.fromisoformat(data.get('created_at').replace("Z", "+00:00"))
            created = created.timestamp()
            if new_versions > created:
                continue

            for asset in data.get('assets'):
                if asset.get('name') == v2ray_name:
                    new_versions = created
                    self.v2ray_file_size = asset.get('size')
                    self.v2ray_download_url = asset.get('browser_download_url')
                    self.v2ray_version = data.get('tag_name')

        if self.v2ray_version:
            return True
        log.error('没有找到适合当前系统（v2ray_name）的 v2ray 版本')

        return None

    def check_v2ray(self):
        '''
        检查当前系统是否安装了 v2ray
        :return:
        '''

        if os.path.isfile(self.v2ray_code):
            return True
        log.warning(f"当前系统未安装 v2ray，尝试安装 v2ray")
        return None

    @classmethod
    def extract_zip_file(cls, zip_file_path, extract_to_path):
        """
        解压 ZIP 文件到指定路径
        :param zip_file_path: ZIP 文件路径
        :param extract_to_path: 解压后的目标路径
        """
        # 检查文件是否存在
        if not os.path.exists(zip_file_path):
            log.error(f"文件不存在: {zip_file_path}")
            return

        # 解压文件
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                zip_file.extractall(extract_to_path)
            log.info('解压文件成功')
            return True
        except Exception as e:
            log.error('解压文件失败')
        return None

    @classmethod
    def download_file(cls, url, output_path, proxy=None):
        """
        下载文件并实时显示进度条
        :param url: 文件下载链接
        :param output_path: 文件保存路径
        :param proxy: 文件保存路径
        """
        # 请求头，用于下载文件
        try:
            response = requests.get(url, proxies=proxy, timeout=10, stream=True)  # 使用 stream 模式
            total_size = int(response.headers.get("content-length", 0))  # 文件总大小

            # 使用 tqdm 显示进度条
            with tqdm(total=total_size, unit="B", unit_scale=True, desc="文件下载中", colour="green") as pbar:
                with open(output_path, "wb") as f:  # 保存文件
                    for chunk in response.iter_content(chunk_size=1024):  # 每次下载 1KB 数据
                        f.write(chunk)
                        pbar.update(len(chunk))  # 更新进度条
            return True
        except Exception as e:
            log.error(f"无法下载文件: {e}")
            return None


if __name__ == "__main__":


    v2ray = V2rayCocde()
    fv = v2ray.main()
    print(fv)


