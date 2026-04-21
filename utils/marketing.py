
'''
创建关于推广，广告之类的自定义对象，包含文本，链接，按键等
'''

from database import sql

class Marketing:
    '''
    q
    '''

    def __init__(self):
        '''


        '''
        self.marketing = self.get_marketing()



    def search_head_marketing(self):
        '''
        定义一个顶置的推广对象
        :return:
        '''
        text = '【顶置推广】'
        for row in self.marketing:
            if row.get('title') == 'onlinesim':
                text = f'【顶置推广】 {row.get("description")}\n\n'
                entities = [
                    {'text': '顶置推广', 'type': 'bold'},
                    {'text': row.get("description"), 'type': 'text_link', 'url': row.get('url')}
                ]
                return text, entities
        return '', []

    @classmethod
    def get_marketing(cls):
        '''
        从数据库获取推广数据
        :return:
        '''


        query = f"SELECT `url`, `title`, `description`, `priority` FROM marketing"
        query = sql.query(sql.database, query, None)

        return query

marketing = Marketing()

if __name__ == '__main__':

    temp = marketing.search_head_marketing()
    print('\n\n', temp)



