
'''
浏览器支持类
本项目采用可视化浏览器服务（selenium）加 google chrome 浏览器
由 webdriver 驱动浏览器
由于 chrome 浏览器更新频繁且必须与 webdriver 鸡翅版本匹配，为保证服务稳定运行
本项目采用自适应式服务模式，当检测到 chrome 因 webdriver 驱动不匹配时会自动
下载正确的 webdriver 安装
'''



import time
import winreg
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess
import re
import requests
import zipfile
import os
import shutil


def red(text):
    """
    打印红色错误信息
    """
    return f"\033[31m{text}\033[0m"

class DriverFile:
    '''
    文件管理类，包括对文件夹和文件的创建，修改，删除等操作
    检查目标文件夹是否存在，如果不存在则创建指定文件夹

    此类被 SeleniumService 继承

    '''

    def __init__(self):
        '''
        初始化参数
        :var self.folder_path 储存 chromedriver 驱动程序的本地路径
        :var self.extract_path 临时文件夹，程序在解压，安装驱动程序时使用的临时数据储存路径，完成成会清空此文件夹
        :var self.download_path 临时文件夹，程序下载文件的临时储存路径

        '''
        self.folder_path = 'D:/chromedriver/chromedriver-win64'
        self.extract_path = 'D:/chromedriver/temp'
        self.download_path = 'D:/chromedriver/temp'
        self.chromedriver_name = 'chromedriver.exe'

        # 检查上述文件夹是否存在，如果没有则创建
        self.check_and_create_folder()

    def find_file_by_name(self, path, file_name=None):
        '''
        在目标文件夹及其子文件夹中查找指定文件名
        :param path: 要查找的根文件夹路径
        :param file_name: 要查找的文件名
        :return: 指定文件名的文件所在的父目录
        '''
        if not file_name:
            file_name = self.chromedriver_name

        # 遍历目标文件夹及其子目录
        for root, dirs, files in os.walk(path):
            # 检查当前目录中的文件
            for name in files:
                if name == file_name:  # 判断文件名是否匹配
                    return root
        return None

    def move_all_files(self, src_folder, dest_folder=None):
        """
        将一个文件夹中的所有文件移动到另一个指定文件夹
        :param src_folder: 源文件夹路径
        :param dest_folder: 目标文件夹路径
        """
        # 确保源文件夹存在
        if not dest_folder:
            dest_folder = self.folder_path

        if not os.path.exists(src_folder):
            print(f"源文件夹不存在：{src_folder}")
            return None

        # 如果目标文件夹不存在，创建它
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        # 遍历源文件夹中的所有内容
        for file_name in os.listdir(src_folder):
            src_file_path = os.path.join(src_folder, file_name)
            dest_file_path = os.path.join(dest_folder, file_name)

            # 检查是否为文件（忽略子文件夹）
            if os.path.isfile(src_file_path):
                shutil.move(src_file_path, dest_file_path)
                print(f"已移动文件: {src_file_path} -> {dest_file_path}")

        print("所有文件已成功移动！")
        return dest_folder

    def extract_zip(self, zip_path, extract_path=None):
        '''
        解压文件到指定文件夹
        :param zip_path: 需要解压的文件
        :param extract_path: 将文件解压到这个路牌
        :return:
        '''
        if not extract_path:
            extract_path = self.extract_path
        try:
            with zipfile.ZipFile(zip_path) as zip_ref:
                zip_ref.extractall(extract_path)
                print(f"文件已解压到: {extract_path}")
            os.remove(zip_path)
            return extract_path
        except Exception as e:
            print('解压文件失败', str(e))
        return None

    def check_and_create_folder(self):
        """
        检测指定文件夹是否存在，如果不存在则创建。
        """
        for index in [self.folder_path, self.download_path, self.extract_path]:
            if not os.path.exists(index):
                os.makedirs(index)
                print(f"文件夹 '{index}' 不存在，已创建。")
            else:
                print(f"文件夹 '{index}' 已存在。")


class SeleniumService(DriverFile):
    '''
    此类确保了 chromedriver 驱动程序一 google chrome 浏览器的匹配使用
    '''
    def __init__(self, path, headle=None):
        '''
        此类会使用网络请求，

        :var self.proxy 网络代理服务，确保在特殊网络环境下正常运行
        :var self.driver 初始化浏览器实例
        :var self.chromedriver_path chromedriver 驱动程序路径

        '''
        super().__init__()

        self.proxy = {
            'http': 'http://127.0.0.1:10809',
            'https': 'socks5://127.0.0.1:10808'
        }

        self.driver = None
        self.chromedriver_path = path
        self.chrome_options = Options()
        if headle:
            self.chrome_options.add_argument("--headless")      # 采用无头模式
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 防止被限制访问
        self.chrome_options.add_argument("--disable-blink-features=BlockCredentialedSubresources")

        # 校验 chromedriver 与 chrome 是否匹配
        self.match_browser()



    def start(self, *args):
        """
        启动浏览器
        """
        for index in args:
            self.chrome_options.add_argument(index)

        # 启动 ChromeDriver 服务并传入选项
        service = Service(self.chromedriver_path)

        try:
            return webdriver.Chrome(service=service, options=self.chrome_options)
        except Exception as e:
            print(red('Error: 无法启动浏览器'), e)
        return False

    def stop(self):
        """
        关闭浏览器
        """
        if self.driver:
            self.driver.quit()
            return True
        else:
            print(red('Error: 浏览器未启动或已关闭'))
        return False

    def match_browser(self):
        '''
        匹配浏览器
        :return:
        '''
        dr_version = self.driver_version(self.chromedriver_path)
        ch_version = self.chrome_version()
        if not ch_version:
            raise '未检测到chrome浏览器'
        if dr_version and dr_version[:3] == ch_version[:3]:
            return True
        print('driver未安装或版本不匹配')

        # 清空当前文件夹

        for file_name in os.listdir(os.path.dirname(self.chromedriver_path)):
            file_path = os.path.join(os.path.dirname(self.chromedriver_path), file_name)
            os.remove(file_path)

        result = self.match_driver(ch_version)
        if result:
            result = self.download_chromedriver(result, self.download_path)
        if result:
            result = self.extract_zip(result, self.extract_path)
        if result:
            result = self.find_file_by_name(result)
        if result:
            return self.move_all_files(result, self.folder_path)
        return False

    def match_driver(self, version):
        '''
        从网络下载 google chrome 浏览器的版本信息，获取对应的驱动程序版本并准备下载驱动程序
        :param version:
        :return:
        '''

        url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        print('正在下载版本信息..........')
        response = requests.get(url, proxies=self.proxy)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()

        for index in data.get('versions', []):
            if index['version'][:10] == version[:10]:
                for i in index['downloads']['chromedriver']:
                    if i['platform'] == 'win64':
                        return i['url']
        return None

    def download_chromedriver(self, url, path=None):
        '''
        分块下载文件
        :param url:
        :param path:
        :return: 返回下载文件的完整路径
        '''
        if not path:
            path = self.download_path
        chunk_size = 1024       # 分块大小
        local_size = 0       # 初始化已存在的文件大小参数
        if os.path.exists(path):
            local_size = os.path.getsize(path)


        print(f"准备下载 ChromeDriver: {url}")
        # 从响应头部获取文件的大小
        response = requests.head(url, proxies=self.proxy, timeout=10, stream=True)
        file_size = int(response.headers.get("Content-Length", 0))  # 远程文件大小

        # 与本地文件大小比较，如果大小相同则被认为当前已经存在所需文件
        if local_size == file_size:
            return True

        headers = {"Range": f"bytes={local_size}-"}
        # 开始下载
        file_name = url.split("/")[-1]
        download_path = f'{path}/{file_name}'

        try:
            with requests.get(url, headers=headers, stream=True) as response:

                response.raise_for_status()  # 确保请求成功
                with open(download_path, "ab") as file:  # 使用追加模式，将数据写入文件
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:  # 确保内容非空
                            file.write(chunk)
                            local_size += len(chunk)
                            print(f"\r正在下载: {local_size}/{file_size} 字节", end="")
            print(f"\n文件下载完成: {download_path}")
            return download_path

        except Exception as e:
            print('无法下载文件', str(e))
        return None

    def driver_version(self, path=None):
        '''
        获取本地安装的 chromedriver 驱动程序版本信息
        此功能函数完全由 AI Assistant 生成
        :param path: chromedriver 驱动程序路径，此参数为空时，应确保你在初始化类时正确定义了此参数
        :return:
        '''
        if not path:
            path = self.chromedriver_path
        try:
            # 执行 `chromedriver --version` 命令，获取输出
            output = subprocess.check_output([path, "--version"], stderr=subprocess.STDOUT)
            version = output.decode().strip()
            version = re.search(r"([0-9]+)\.([0-9]+\.[0-9]+\.[0-9]+)", version)
            if version:
                return version.group(1)
            return version
        except FileNotFoundError:
            print("Chromedriver 未安装或路径不正确")
        return None

    @staticmethod
    def chrome_version():
        '''
        获取 google chrome 浏览器版本信息
        此方法完全由 AI Assistant 生成
        :return:
        '''
        try:
            # 打开注册表项
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            # 获取版本号
            version, _ = winreg.QueryValueEx(reg_key, "version")
            winreg.CloseKey(reg_key)
            version = re.search(r"([0-9]+)\.([0-9]+\.[0-9]+\.[0-9]+)", version)
            if version:
                return version.group()
            return

        except FileNotFoundError:
            error = "未检测到 Chrome 安装"
        except Exception as e:
            error = f"获取 Chrome 版本时发生错误: {str(e)}"
        raise f'Error：{error}'

driver_path = 'D:/chromedriver/chromedriver-win64/chromedriver.exe'
chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'

seleniumservice = SeleniumService(driver_path)

if __name__ == '__main__':



    chrome = seleniumservice.start()
    chrome.get('https://www.baidu.com')
    time.sleep(3)
    chrome.quit()









