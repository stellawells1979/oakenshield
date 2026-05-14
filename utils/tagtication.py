
'''
12
'''
import logging
import json
import re
import jieba
import config
from logg import LogManager

log = LogManager('Tagtication', logging.ERROR, logging.INFO)

class TagFication:
    '''
    u
    '''
    def __init__(self):
        tag_keys = {

            '虚拟币': '交易所,幣安,币料,代币,币安,币圈,黑u,盗U,黑币,盗币,黑卡,盗卡,黑号,盗号,黑U,区块,币盘,'
                      '合约,挖矿,usdt,USDT,TRX,trx,BNB,BXH,BSC,OKC,HECO,AVAX,ETH,矿机,矿工,矿圈,'
                      'OK链,持币,欧易,ibit,区块链,加密,库料,加密货币,比特币,数字货币,火币,OKX,去中心化,'
                      'USDT,狗狗币,能量闪租,去中心化,區塊鏈,以太坊',

            '软件编程': '软件,破解,外挂,补丁,插件,逆向,脚本,APP,開發,爬虫,木马,辅助,源码,编程,开源,开发者,'
                        '程序,github,python,java,javascript,c++,c#,php,html,css,sql,go,软件教程,'
                        'ruby,rust,swift,kotlin,typescript,perl,shell,bash,lua,scala,haskell,'
                        '编程语言,JavaScript,JS,js,程式设计,ipa,app,apk,ui,ui设计,软件开发,ui,UI,'
                        '安装包,机器人定制,定制机器人,黑客',

            '编程开发': '编程,开源,开发者,程序,github,python,java,javascript,c++,c#,php,html,css,'
                        'sql,go,ruby,rust,swift,kotlin,typescript,perl,shell,bash,lua,scala,'
                        'haskell',

            '游戏竞技': '电玩,電競,王者,原神,英雄联盟,绝地求生,吃鸡,DOTA2,CS:GO,守望先锋,炉石传说,魔兽世界,'
                        '使命召唤,彩虹六号,PUBG,九游,三角洲,和平,精英,手游，王者荣耀,和平精英,游戏,电脑游戏,'
                        '单机游戏',

            '影视剧情': '视讯,剧情,演出,电影,演员,题材,电视剧,综艺,动漫,纪录片,影视,观看,短剧,影业,'
                        '#喜剧片,播放,新片预告,影片,剪辑,看片,影视,1080P',

            '娱乐八卦': '资讯,快讯,資訊,資訊,KTV,香港艺人,八卦,签名,李宇春,张靓颖,周笔畅,何洁,刘亦菲,张含韵,陈好,'
                        '尚雯婕,张筱雨,韩雪,孙菲菲,张嘉倪,霍思燕,陈紫函,朱雅琼,江一燕,厉娜,许飞,胡灵,菲尔,'
                        '刘力扬,reborn,章子怡,维维,魏佳庆,张亚飞,李旭丹,孙艺心,巩贺,艾梦萌,闰妮,王蓉,汤加'
                        '易学,入玄门,风水,布局,面相,手相,八字,奇门,起名,择时,秘术,手相,刘玥,明星',

            '社区论坛': '社区,论坛大杂烩,讨论,大杂烩,争论,言论,部落,吹水,群聊,吹牛,群众,文化交流,世界各地,'
                        '兴趣,海外华人,交流,探讨,討論,攻略,聚集地,感兴趣段子,趣味,搞笑,讨论,热点,畅聊,'
                        '爱好者,共享,社群,吃瓜,交流,曝光,分享,观点,聊天,休闲爆料,黑幕,奇闻,趣事',

            '音乐视频': '音乐,歌曲,专辑,歌手,粉丝,杰伦,周杰伦,流媒体,高清,小视频,混剪,视频,自拍',

            '主播直播': '直播,主播,录屏,虎牙,斗鱼,网红主播,网红,主播,混剪,斗鱼,虎牙,快手,抖音',

            '网购电商': '跨境商城,网购,闲鱼,电商,购物,网店,亚马逊,淘宝,京东,苏宁易购,唯品会,国美,当当网,小红书,'
                        '考拉,天猫,拼多多,苏宁易购,購物,包邮,咸鱼,转转,现货,代收,首饰,美妆,吊牌,款式,购买地址,'
                        '槟榔,香烟,零食,服装,鞋子,阿迪达斯,耐克,奢侈品,代购',

            '健康保健': '健康成长,中医,人参,病毒,新冠,健身房,医疗器械,不孕,不育,患者,健康,运动,健身,进口药,'
                        '新冠药,抗癌药,白血病,艾滋,甲流药,奥司,处方药,靶向,保健品,丙肝,易瑞沙,药店,药房,'
                        '买药,保健',

            '美食养生': '餐饮,美食,美食资源,旅行资源,美食分享,美食社区,美食论坛,美食评论,美食推荐,美食APP,'
                        '胶原蛋白,韩药妆,彩妆,香水,护肤品,保养品,奢侈品,洗护,冰川,胶原蛋白,美白,祛痘,瘦身,'
                        '厨师,菜谱',

            '科学上网': '科学上网,梯子,节点订阅,订阅,节点,加速器,v2ray,翻墙,VPN,代理,火箭,ip,机场,测速,'
                        '机场测速,流量,搭建,vps,VPS,vpn,訂閱,CDN,域名,独享',

            'SEX': '色情,修车,探花,偷拍,脫衣舞,成人内容,成人,乱交,自慰,避孕套,偷窥,高潮,跳蛋,人妻,毛片,三级片,'
                   '人体艺术,灌肠,黄播,裸贷,恋足癖,内射,幼幼,射精,色图,小黄书,苍井空,楼凤,伪娘,色播,口交,反差,'
                   '调教,巨乳,母狗,媚黑,露出,迷奸,漏点,海角,海角社区,草莓视频,色粉,式品茶,口技,果聊,裸聊,破处,'
                   '吞精,口交,阳具,精东,绿奴,AV,av,骚货,黄色小说,麻豆,性奴,色色老司機,莞式服务,莞式,受虐,荡妇,'
                   'javhub,番号,女优,流出,jav,javdb,javdbbot,JAV,91,潮吹,伦理,黑丝,母子,番號,女優,'
                   '男同,基友,骚基,性福,无码,猥琐,啪啪,成人影片,女同,黄漫,换妻,汤不热,足交,sm,SM,重口,足控,'
                   '足控,看片,绿帽,sex,SEX,小黄片涩图,涩涩,熟女,乱伦,淫妻,恋足,三级电影,轮奸,中出,萝莉,翘臀,'
                   '成人用品,嫖娼,裸照',

            '新闻时政': '時事,重大事件,头条,时政,政策,政治,民生,政治,时讯,新闻社,惠民,新闻,时事,热点,事件,动态,'
                        '投稿,快讯,新闻频道,据报道,现场报道,热门,战地记者,新闻资讯,BBC,纽约时报,环球,最新消息,'
                        '快报,国内新闻,重大新闻,热点新闻,国际局势,资讯,News',

            '小说书籍': '小说,书籍,文学,阅读,免费小说,当当网,电子书,图书馆,杂志,文章,买书,版权,搜书,作者,圖書館,'
                        '壁纸,绘画',

            '教育培训': '学习,教育家,教育,培训课程,高考,教学,全日制,高等教育,考究,学习外语,作业,职教,题库,辅导',

            '体育赛事': '体育,世界杯,足球,體育,运动,快船,湖人,勇士,热火,凯尔特人,雄鹿,76人,太阳,掘金,马刺,猛龙,'
                        '步行者,老鹰,尼克斯,公牛,活塞,黄蜂,体育赛事,奇才,火箭,雷霆,开拓者,爵士,森林狼,灰熊,'
                        '鹈鹕,国王,篮网,体育迷,足球,比赛,足球比赛,篮球比赛,NBA,CBA,英超,西甲,意甲,中超,'
                        '羽毛球,篮球,体坛,足球运动,冠竞,冠军,联赛,球队,世界杯',

            '彩票博彩': '龙虎,上分,玩家,博彩,投注,彩金,返利,百家乐,牛牛,龙虎,体彩,捕鱼,开云,斗地主,菠菜,赌场,'
                        '娱乐厅,九游会,九游,开云,棋牌,六合彩,PG,pg,竞彩,体彩,输赢,赔率,足彩,娱乐城,新葡京,'
                        '彩票,骰子,杀猪盘,BC',

            'IT科技': '阿里,腾讯,AWS,亚马逊,谷歌云,孵化,IT,研发,算法,科技,模型,训练,路由器,服务器,AI,ai,人脸识别',

            '旅行摄影': '伴游,旅途,旅行,旅游,出游,摄影,拍摄,出差,旅游网,旅程,风景,携程,旅游攻略,飞猪',

            '社交媒体': '社交,领英,头条,tiktok,陌陌,探探,快手,抖音,微信,Facebook,脸书,抖音,外围,约炮,楼凤,传媒,'
                        'Soul,微博,小紅書,连信,油管,租闲鱼,臉書,朋友圈,TG,telegarm,ins,FB,tg,TikTok,封号,'
                        'instagram,Ins,IG,推特,知乎,谷歌,Telegram,Twitter,twitter,WhatsApp,电报,youtube,',

            '金融财经': '金融,股民,财经,投資,经济,投资,股票,基金,债券,外汇,期货,美股,理财,证券,證券,財經,资金,A股,'
                        '炒股,指数,投資,开户,股市,牛市,外汇,花呗,借呗,网商贷,微粒贷,网商贷,信用卡,网银,转账',

            '动漫二次元': '动漫,动画,漫画,動漫,二次元,COS,cos,COSMIC,COSMIC,写真,黄漫,国漫,宅次元',

            '广告营销': '查询,户籍,社工,主营,汇旺,担保,供應商,刷单,商机,网赚,下单,銷售,售后,经营范围,电销,货到付款,'
                        '服務,营销,行業,交易,买卖,运营,合营,黑产,灰产,黑产灰产,创业,广告,洽谈,发布,信息,推广,咨询,'
                        '代理,需求,企业,拓展,商业,合作,烟酒,引流,小本生意,拉裙,促销,批发,免税,批發,交易方式,推廣,'
                        '廣告,孵化,宣传,实卡,接码,三网,引流,十名,虚拟卡,好旺,国际短信,礼品卡,赚钱,捞偏门,'
                        '赚钱项目,賺錢,指導,免费赠品,汇旺,捞钱,爆粉',

            '招聘职务': '招聘,职场,职业,招人,工作,从业,招募,求职,工作,岗位,职位,人才,猎头,人力资源,兼职,入职,直招,'
                        '简历,面试,全岗,求职者,职位,人才培养,劳务,学历,实习,劳务,直聘,经理',

            '商务贸易': '商务,商贸,商旅,酒店,商务洽谈,洽谈,KTV,商务,精英,咨询,拓展,商业,合同,诚招,招商,银行卡,公户,'
                        '账单,对公,对私,账户,流水,营业执照,合同,助理,VIP,客户接待,中介,服务,外贸',

            '资源搜集': '资源,资源共享,资源整合,综合,羊毛,线报,壁纸,网赚,项目',

            '同城交友': '同城,交友,外围,市区,市内,高端',

            '暗网禁区': '暗网,迷奸,迷药,春药,性药,催情药,GHB,安眠药,三唑仑,氟烷,神仙,乖乖,安眠,睡眠,失眠,艾司唑仑思,'
                        '诺思,FM2,增粗,免税,走私,下药,黑客',

            '手机数码': '解除限制,苹果,ios,屏蔽,解锁,APP,app,apple,安卓,apk,教程,手機,手机,電腦,智能,三星,Galaxy,'
                        '电脑,iPhone,数码,华为,AppleWatch,ipa,iPA,IPA,越狱,巨魔,应用,签名,屏幕,苹果ID,手机号,'
                        '电子产品,笔记本电脑,笔记本,台式机,通讯',

        }
        indivisible_more = [
            '二次元', '苹果ID', '苹果id', '微信公众号', '区块链', '老司机', '身体健康', '万事如意', '财源广进',
            '软件开发', '虚拟卡', '成人影片', '加密货币', '比特币', '数字货币', '去中心化', '花呗套现', '私人定制',
            '汤不热', '谷歌导航', '王者荣耀', '和平精英', '能量闪租', '转U', '国际短信', '以太坊', '比特幣', '比特币',
            '微粒贷', '购买地址', '机器人定制', '定制机器人', '成人用品'
        ]
        extrawords_more = [
            '同步'
        ]
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

        self.tag_keys = self.init_tag_keys(tag_keys)
        self.stopwords = self.init_key_words(config.stop_path)
        self.extrawords = self.init_key_words(config.extr_path, extrawords_more)
        self.indivisible = self.init_key_words(config.indivisible_path, indivisible_more)

    def init_tag_keys(self, key_dict):
        '''
        初始化归类母标签（tag_keys），去除母标签中可能包含的空格和空串
        :param key_dict:
        :return:
        '''
        result = {}
        for key, value in key_dict.items():
            unique = []
            if key == '同城交友':
                # 读取全国城市名称并添加到 tag_keys 对象
                with open(config.city_path, 'r', encoding='utf-8') as file:
                    cities = file.read()
                city = ''
                for k, v in json.loads(cities).items():
                    city = city + v + ','
                value = value + ',' + city

            for index in value.replace(' ', '').replace('\n', '').split(','):
                if index in unique or index == '':
                    continue
                unique.append(index)
            result.update({key: unique})
        return result

    def init_key_words(self, path, more=None):
        '''
        初始化不可分割关键词参数
        :param path:
        :param more:
        :return:
        '''
        result = []
        with open(path, 'r', encoding='utf-8') as file:
            file.text = file.read()
        file.text = file.text.replace('\n', '').replace(' ', '')
        for index in file.text.split(','):
            if index in result or index == '':
                continue
            result.append(index)
        if more and len(more) > 0:
            text = ''
            for index in more:
                if index in result:
                    continue
                text = text + index + ','
                result.append(index)
            if len(text) > 0:
                with open(path, 'a', encoding='utf-8') as file:
                    file.write(text)
        return result

    def create_tag(self, text, spill):
        '''
        归类描述
        :param text:
        :param spill:
        :return:
        '''
        if not text:
            return []

        result = []
        container = []      # 初始化分词容器

        # jieba会把一些不可分割的词拆开，先检查字串中是否包含不可分割字符
        for index in self.indivisible:
            if text and text.find(index) != -1:
                container.append(index)

        # 使用结巴进行分词处理
        jieba_text = self.process_text(text)

        # 去除额外的停用词
        for index in jieba_text:
            if index in self.extrawords or len(index) < 2:
                continue
            container.append(index)

        if not container:
            return result
        for key, value in self.tag_keys.items():
            count = 0
            if f'#{key}' in result:
                continue
            for index, word in enumerate(container):
                if word in value:
                    count += 1
                    if word == '修车' and key == 'SEX':
                        count += 1
                    if len(container) < 3:
                        count += 1
                if count >= spill:
                    result.append(f'#{key}')
                    break
        return result

    def process_text(self, text):
        '''
        分词处理函数
        :param text: 用户输入的文本
        :return: 分词后的结果
        '''
        if text == ' ':
            return None

        for index in self.fixedwords:
            if text in index:
                return index

        if len(text) < 3:
            return [text]

        # 使用jieba进行分词
        words = jieba.cut(text, cut_all=False)
        # 将分词结果转换为列表并去除标点符号
        words = [word for word in words if not re.match(r'[^\w\s]', word)]
        result = []
        repeat = []
        if len(words) > 1:
            for index in words:
                if index in self.stopwords or index in repeat:
                    continue
                result.append(index)
                repeat.append(index)

        else:
            result = words
        return result

tagnote = TagFication()

if __name__ == '__main__':

    tag = TagFication()

    temp = tag.create_tag('😀😀😀😀长春大学车库\n😙🥹😁☹️老师经过群内管理视频验证，本榜保证百分百为老师本人，如有不符，拒绝上课,随时联系本平台管理客服.\n\n新客户尽量联系管理报备\n以免担忧\n\n老客户每一位老师都可以放心出击可无需联系管理 如有问题可随时联系 24小时在线\n\n👨\u200d💻频道管理管理客服联系：  @lksidu\n🔎双向管理联系:     @shuayebmbot\n😍😁🥸😍😬😄😊😉🌳', 2)

    print(temp)




