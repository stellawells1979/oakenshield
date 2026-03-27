import requests
import os


class GeoIPUpdate:
    """
    更新 GeoIP 数据库的工具类。
    """

    def __init__(self, geoip_url, output_dir="./data"):
        """
        初始化 GeoIP 更新类。

        :param geoip_url: GeoIP 数据库文件的远程下载地址。
        :param output_dir: 保存文件的输出路径。
        """
        self.geoip_url = geoip_url
        self.output_dir = output_dir
        self.output_path = os.path.join(output_dir, "geoip.mmdb")

    def update(self):
        """
        执行 GeoIP 数据库文件的下载更新。
        """
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            response = requests.get(self.geoip_url, stream=True, timeout=10)
            response.raise_for_status()

            # 将文件保存到目标路径
            with open(self.output_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"GeoIP 数据库已更新: {self.output_path}")
        except Exception as e:
            print(f"更新 GeoIP 数据库失败: {e}")
