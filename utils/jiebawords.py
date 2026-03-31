

'''
jieba语言处理模块
'''



import jieba
import re
import logging
import run_config


class JiebaWords:

    '''
    一个高度自定义的利用 jieba 进行分词的模块
    '''

    def __init__(self):

        # 设置jieba日志级别为WARNING，避免输出分词过程中的调试信息

        logging.getLogger("jieba").setLevel(logging.WARNING)

        stop_path = run_config.stop_words

        with open(stop_path, encoding='utf-8') as file:
            words = file.read()
        self.stopwords = words      # 自定义的停用词


        # 自定义的固定词
        self.fixedwords = [
            ['ETH', 'eth', '以太币'],
            ['BTC', 'btc', '比特币'],
            ['XRP', 'xrp', '瑞波币'],
            ['LTC', 'ltc', '莱特币'],
            ['EOS', 'eos', '柚子币'],
            ['BCH', 'bch', '比特现金'],
            ['TRX', 'trx', '波场币'],
            ['XLM', 'xlm', '恒星币'],
            ['ADA', 'ada', '艾达币'],
            ['DOT', 'dot', '波卡币'],
            ['LINK', 'link', '链环币'],
            ['UNI', 'uni', 'Uniswap'],
            ['SOL', 'sol', 'Solana'],
            ['DOGE', 'doge', '狗狗币'],
            ['USDT', 'usdt', '泰达币'],
            ['BNB', 'bnb', '币安'],
            ['XMR', 'xmr', '门罗币'],
            ['telegram', '飞机', '飞机号', '飞机票'],
        ]

    def organize(self, text):
        '''
        整理搜索关键词，包括去除停用词，并丰富搜索
        :param text:
        :return:
        '''
        result = []

        # 如果是空串，当然是返回空值了
        if not text:
            return None

        # 当参数是数值型或者仅包含标点符号时，直接返回参数本身了
        if isinstance(text, int) or isinstance(text, float) or self.is_punctuation(text):
            return text

        # 一个自定义的固定词库fixedwords，
        for index in self.fixedwords:
            if text in index:
                return index

        words = self.participle(text)   # array

        # 如果仅有一个词则直接返回 words
        if len(words) == 1:
            return words

        for index in words:
            if index in self.stopwords or index in result:
                continue
            result.append(index)

        return result

    @classmethod
    def participle(cls, text):
        '''

        :param text:
        :return:
        '''
        # 使用jieba进行分词
        words = jieba.cut(text, cut_all=False)

        # 将分词结果转换为列表并去除标点符号
        words = [word for word in words if not re.match(r'[^\w\s]', word)]

        return words

    @classmethod
    def is_punctuation(cls, text):
        """
        检查字符串是否仅包含标点符号。

        Args:
            text (str): 要检查的字符串。

        Returns:
            bool: 如果字符串仅包含标点符号，则返回 True；否则返回 False。
        """
        pattern = r"^[^\w\s]+$"  # 匹配仅包含非单词字符和非空白字符的字符串
        return bool(re.match(pattern, text))

jiebas = JiebaWords()

if __name__ == '__main__':


    texts = ('影片根据故事《高文爵士与绿衣骑士》改编，讲述亚瑟王在自己的宫廷里举行宴会。一位绿衣骑士前来向圆桌骑士挑战：有谁敢当场砍下他的头，'
             '并让他一年后回敬一斧。高文接受挑战，砍下了绿衣骑士的头。那具依然活着的躯体捡起头颅，回到绿色的教堂。一年以后，高文践约去寻找绿衣骑士。')
    print(jiebas.organize(texts))





