
import logging
import time

from Log import loginfo
from datetime import datetime
from config import config
from v2raycode import V2rayCocde
from testnode import TestNode
from assemble import Assemble




# 配置日志记录
log = loginfo('Main', logging.DEBUG, logging.ERROR)


if not config.init_config_path():
    raise 'config.ini not found'

v2ray_exe = V2rayCocde().main()
test = TestNode(v2ray_exe)


class Main:
    '''
    e
    '''
    def __init__(self):

        # 节点池文件 ***
        self.aggregatorNodes = config.aggregatorNodes

        # 待测试的节点文件
        self.v2rayNodes = config.v2rayNodes

    def maintain_aggregator(self):
        '''
        维护节点池，定期测试节点池内的订阅节点，确保最佳状态
        新的测试结果将履盖原节点内容
        :return:
        '''
        retult = self.test_node(self.aggregatorNodes)

        if retult:
            with open(self.aggregatorNodes, 'w', encoding='utf-8') as file:
                file.write('\n'.join(retult))



    def assemble_subscribe(self):
        '''
        从网络收集订阅节点，经测试后追加写入节点池文件
        :return:
        '''
        # 运行节点收集程序，此程序会将收集到的订阅节点储存到特定的文件
        Assemble().main()

        # 测试收集到的订阅节点
        retult = self.test_node(self.v2rayNodes)

        if retult:
            # 将测试可用的订阅节点追加写入节点池文件
            with open(self.aggregatorNodes, 'a', encoding='utf-8') as file:
                file.write('\n'.join(retult))

        # 清空已经测试完成的文件
        with open(self.v2rayNodes, 'w', encoding='utf-8') as file:
            file.write('')

    @classmethod
    def test_node(cls, path):
        """

        """
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read().splitlines()

        len_content = len(content)
        result = test.parallel_execution(content, 10)
        for row, tested in reversed(result):
            if tested is None:
                del content[row]
        print('Connect succeed:', f'{len(content)}/{len_content}')
        return content


if __name__ == '__main__':


    aggregator = Main()
    now_time = datetime.now().hour

    # 每四小时参节点进行维护
    aggregator.maintain_aggregator()

    log.info('Aggregator update is complete, start to collect subscribe content.')
    time.sleep(6)

    # 每天两次摘取订阅内容
    if now_time in [13, 14, 15, 16, 2, 3, 4]:
        aggregator.assemble_subscribe()

    # 清空配置文件夹
    test.clear_folder(config.test_configs_path)






