'''
聊天分享链接有解析
'''



class ChatInviteLinkInfo:

    '''
    聊天分享链接有解析
    '''
    def __init__(self, data):

        self.chat_id = data.get('chat_id')
        self.title = data.get('title')
        self.description = data.get('description')
        self.member = data.get('member_count')
        chat_type = data.get('type', {}).get('@type').split('inviteLink')[1]
        self.chat_type = chat_type[:1].lower() + chat_type[1:] if chat_type else None


