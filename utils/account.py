


'''
配置机器人，分别的搜索，规则，验证机器人
包括机器的的基本信息和开发者自定义的描述和行为
开发者应为各种功能机器定义一个独立文档或者函数，
'''

bots_muster = {
    'search': '7382098323:AAHBYMEexWoHQe-JcLWgg_9l0bskaM2PVSs',
    'rules': '8598030336:AAE8TW4cmapxMqkgrvmOnhkXd8ei06Q7b_0',
    'other': '7921354496:AAFooa7EE6o3kixGiJLe_g3pgEAVBnDpfXw',
    'verify': '7719762749:AAGjKMlTKDbd-OZa0F3f8fyhtq1XmFbuq_A',
}

bot_customize = {   # 机器人的自定义参数
    'search': {
        'first_name': 'search_bot'
    },
    'verify': {
        'first_name': 'verify_bot'
    },
    'rules': {
        'first_name': 'rules_bot'
    }
}






class Account:
    '''
    初始化个人账号信息
    '''

    def __init__(self):
        '''
        机器人的基本信息通过


        '''

        self.search = {
            'id': 7921354496,
            'token': '7921354496:AAFooa7EE6o3kixGiJLe_g3pgEAVBnDpfXw',
            'url': 'https://t.me/baisc_bot?startgroup=true',
            'username': 'baisc_bot',
            'byname': 'baisou',
            'title': {'text': '百搜机器人', 'entities': [{'type': 'bold', 'text': '百搜机器人'}, ]},
            'description': '百搜机器人，搜遍TG',
            'start_description': {
                'text': "搜群组,搜频道,搜影视,搜资讯,搜遍TG的搜索小能手",
                'entities': [
                    {'type': 'bold', 'text': '小能手'},
                ]
            },
            'help_description': {
                'text': '百搜机器人专注于收集和分享telegram群组链接，集百万个群组，可按你提供的关键字为你分享相关群组链'
                        '接，点击下面的【添加收录】按钮分享你的群组链接，让你的群组暴光率成倍提升,你也可以将我添加到你的群组,分享更多搜索乐趣',
                'entities': [
                    {'type': 'bold', 'text': '百搜机器人'},
                    {'type': 'bold', 'text': '添加收录'},
                ]
            },

        }

        self.rules = {
            'id': 8598030336,
            'token': '8598030336:AAE8TW4cmapxMqkgrvmOnhkXd8ei06Q7b_0',
            'url': f'https://t.me/wellwen_bot?startgroup=true',
            'username': 'wellwen_bot',
            'byname': 'rules',
            'image': '',
            'title': {
                'text': '规则机器人',
                'entities': [
                    {'type': 'bold', 'text': '规则机器人'},
                ]
            },
            'description': '监控群组的每一个动静，按规则做出响应',
            'start_description': {
                'text': f"一个能在你的群组中24小时不间断监视群组活动的机器人，它没有作息时间，你可以设置任意规则来管理你的群组\n\n"
                        f"点击【帮助】了解如何使用本机器",
                'entities': [
                    {'type': 'bold', 'text': '帮助'},
                ]
            },
            'rules_description': {
                'text': f"欢迎使用规则机器人服务，在使用本服务前首先确认你是该群组的创建者或者管理员且拥有相应权限",
                'entities': [
                    {'type': 'bold', 'text': '帮助'},
                ]
            },
            'help_description': {
                'text': '1.首先确保你是某个群组的创建者或者管理员且有相应权限\n2.点击【添加机器人到群组】按钮并进入那个群'
                        '组\n3.在群组的用户列表中搜索找到本机器人，将机器人设为管理员并赋以相应权限\n4.向群里发送【hello wellwen】让机器'
                        '人找到你，稍等片刻机器人会回复一条信息把你带回本聊天或者你直接回到本聊天，即可进入规则设置界面',
                'entities': [
                    {'type': 'bold', 'text': '规则机器人'},
                    {'type': 'bold', 'text': '创建者或者管理员'},
                    {'type': 'bold', 'text': '添加机器人到群组'},
                    {'type': 'bold', 'text': '管理员并赋以相应权限'},
                    {'type': 'bold', 'text': 'hello wellwen'},
                ]
            },
        }

        # 数据库配置参数
        self.host = '127.0.0.1'
        self.port = 3306
        self.user = 'root'
        self.password = ''
        self.charset = 'utf8mb4',


    def attribute(self, bot, option=None):
        '''

        :param bot:
        :param option:
        :return:
        '''
        if not option:
            return self.__dict__.get(bot)

        return self.__dict__.get(bot, {}).get(option)



account = Account()

if __name__ == '__main__':

    print(account.attribute('search', 'title'))

