'''
解析超级群组信息
'''

class SupergroupFullInfo:
    '''
    解析超级群组信息
    '''
    def __init__(self, data):

        self.group_id = data.get('id')
        self.name = data.get('usernames', {}).get('active_usernames', [None])[0]
        self.member = data.get('member_count')
        self.channel = data.get('is_channel')
        self.description = data.get('description')
        self.get_members = data.get('can_get_members')  # 是否可以通过getSupergroupMembers或searchChatMembers检索聊天成员。







