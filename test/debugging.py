



callablequery_01 = {        # 一条设置签到周期的回调更新
    'update_id': 63771210,
    'callback_query': {
        'id': '4813328791221414564',
        'from': {
            'id': 1120690440, 'is_bot': False, 'first_name': '大', 'last_name': '苹果', 'username': 'bigapple699', 'language_code': 'zh-hans'
        },
        'message': {
            'message_id': 352,
            'from': {
                'id': 8598030336, 'is_bot': True, 'first_name': 'rulesbot', 'username': 'wellwen_bot'
            },
            'chat': {
                'id': 1120690440, 'first_name': '大', 'last_name': '苹果', 'username': 'bigapple699', 'type': 'private'
            },
            'date': 1775932957,
            'edit_date': 1776004938,
            'text': '规则机器人 >> Test >> 签到管理\n\n签到管理，为群组设置一个签到规则，帮你统计群组的活跃程度，点击相应按钮可设置签到规则，'
                    '设置好后会弹出【启动签到按钮】，每个只能运行一个签到规则，启动后无法修改签到规则\n\n🔔 已清空当前规则',
            'entities': [
                {'offset': 0, 'length': 5, 'type': 'bold'},
                {'offset': 111, 'length': 7, 'type': 'bold'}
            ],
            'reply_markup': {
                'inline_keyboard': [
                    [{'text': '签到周期', 'callback_data': 'rules|register|period|0|-1003606614850'}],
                    [{'text': '签到描述', 'callback_data': 'rules|register|explain|0|-1003606614850'}],
                    [{'text': '查看签到数据', 'callback_data': 'rules|register|view|0|-1003606614850'}],
                    [{'text': '清空规则', 'callback_data': 'rules|register|clear|0|-1003606614850'}],
                    [{'text': '返回', 'callback_data': 'rules|0|0|1|-1003606614850'}]
                ]
            }
        }, 
        'chat_instance': '-6124905536428867626',
        'data': 'rules|register|period|0|-1003606614850'
    }
}
callablequery_06 = {        # 一条清空签到规则的消息
    'update_id': 63771209,
    'callback_query': {
        'id': '4813328790733170269',
        'from': {
            'id': 1120690440,
            'is_bot': False,
            'first_name': '大',
            'last_name': '苹果',
            'username': 'bigapple699',
            'language_code': 'zh-hans'
        },
        'message': {
            'message_id': 352,
            'from': {
                'id': 8598030336,
                'is_bot': True,
                'first_name': 'rulesbot',
                'username': 'wellwen_bot'
            },
            'chat': {
                'id': 1120690440,
                'first_name': '大',
                'last_name': '苹果',
                'username': 'bigapple699',
                'type': 'private'
            },
            'date': 1775932957,
            'edit_date': 1776003165,
            'text': '规则机器人 >> Test >> 签到管理\n\n签到管理，为群组设置一个签到规则，帮你统计群组的活跃程度，点击相应按钮可设'
                    '置签到规则，设置好后会弹出【启动签到按钮】，每个只能运行一个签到规则，启动后无法修改签到规则\n签到周期：'
                    ' 31\n签到描述： 欢迎签到\n当前状态： 进行中\n🔔 已启动签到',
            'entities': [
                {'offset': 0, 'length': 5, 'type': 'bold'},
                {'offset': 107, 'length': 9, 'type': 'blockquote'},
                {'offset': 140, 'length': 5, 'type': 'bold'}
            ],
            'reply_markup': {
                'inline_keyboard': [
                    [{'text': '签到周期', 'callback_data': 'rules|register|period|0|-1003606614850'}],
                    [{'text': '签到描述', 'callback_data': 'rules|register|explain|0|-1003606614850'}],
                    [{'text': '查看签到数据', 'callback_data': 'rules|register|view|0|-1003606614850'}],
                    [{'text': '清空规则', 'callback_data': 'rules|register|clear|0|-1003606614850'}],
                    [{'text': '返回', 'callback_data': 'rules|0|0|1|-1003606614850'}]
                ]
            }
        },
        'chat_instance': '-6124905536428867626',
        'data': 'rules|register|clear|0|-1003606614850'
    }
}

message_01 = {
    'update_id': 63771283,
    'message': {
        'message_id': 380,
        'from': {
            'id': 1120690440,
            'is_bot': False,
            'first_name': '大',
            'last_name': '苹果',
            'username': 'bigapple699',
            'language_code': 'zh-hans'
        },
        'chat': {
            'id': 1120690440,
            'first_name': '大',
            'last_name': '苹果',
            'username': 'bigapple699',
            'type': 'private'
        }, 'date': 1777064272,
        'text': '/start',
        'entities': [
            {'offset': 0, 'length': 6, 'type': 'bot_command'}
        ]
    }
}

# 机器人被添加到某个群组
message_02 = {
    'update_id': 63771288,
    'message': {
        'message_id': 279,
        'from': {
            'id': 1120690440,
            'is_bot': False,
            'first_name': '大',
            'last_name': '苹果',
            'username': 'bigapple699',
            'language_code': 'zh-hans'
        },
        'chat': {
            'id': -1003606614850,
            'title': 'Test',
            'type': 'supergroup'
        },
        'date': 1777089610,
        'text': '/start@ADDBOT true',
        'entities': [
            {'offset': 0, 'length': 13, 'type': 'bot_command'}
        ]
    }
}

message_03 = {
    'update_id': 63771296,
    'message': {
        'message_id': 286,
        'from': {
            'id': 1120690440,
            'is_bot': False,
            'first_name': '大',
            'last_name': '苹果',
            'username': 'bigapple699',
            'language_code': 'zh-hans'
        },
        'chat': {
            'id': -1003606614850,
            'title': 'Test',
            'type': 'supergroup'
        },
        'date': 1777145894,
        'new_chat_participant': {
            'id': 8598030336,
            'is_bot': True,
            'first_name': 'rulesbot',
            'username': 'wellwen_bot'
        },
        'new_chat_member': {
            'id': 8598030336,
            'is_bot': True,
            'first_name': 'rulesbot',
            'username': 'wellwen_bot'
        },
        'new_chat_members': [
            {'id': 8598030336, 'is_bot': True, 'first_name': 'rulesbot', 'username': 'wellwen_bot'}
        ]
    }
}

# 群组的管理员发生改变
my_chat_member_01 = {
    'update_id': 63771297,
    'my_chat_member': {
        'chat': {
            'id': -1003606614850,
            'title': 'Test',
            'type': 'supergroup'
        },
        'from': {
            'id': 1120690440,
            'is_bot': False,
            'first_name': '大',
            'last_name': '苹果',
            'username': 'bigapple699',
            'language_code': 'zh-hans'
        },
        'date': 1777145986,
        'old_chat_member': {
            'user': {
                'id': 8598030336,
                'is_bot': True,
                'first_name': 'rulesbot',
                'username': 'wellwen_bot'
            },
            'status': 'administrator',
            'can_be_edited': False,
            'can_manage_chat': True,
            'can_change_info': True,
            'can_delete_messages': True,
            'can_invite_users': True,
            'can_restrict_members': True,
            'can_pin_messages': True,
            'can_manage_topics': False,
            'can_promote_members': True,
            'can_manage_video_chats': True,
            'can_post_stories': False,
            'can_edit_stories': False,
            'can_delete_stories': False,
            'can_manage_tags': False,
            'is_anonymous': True,
            'can_manage_voice_chats': True
        },
        'new_chat_member': {
            'user': {
                'id': 8598030336,
                'is_bot': True,
                'first_name': 'rulesbot',
                'username': 'wellwen_bot'
            },
            'status': 'member'
        }
    }
}

