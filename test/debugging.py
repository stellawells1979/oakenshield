

'''
消息实例，收集各类消息实例，用于调试


'''

import time

now_date = time.time()

message_example_0 = {
    'ok': True,
    'result': [
        {
            'update_id': 988429064,
            'my_chat_member': {
                'chat': {
                    'id': -1002798527828,
                    'title': '搜索🔥🔥',
                    'username': 'psytss',
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
                'date': now_date,
                'old_chat_member': {
                    'user': {
                        'id': 7921354496,
                        'is_bot': True,
                        'first_name': 'baisou',
                        'username': 'baisc_bot'
                    },
                    'status': 'left'
                },
                'new_chat_member': {
                    'user': {
                        'id': 7921354496,
                        'is_bot': True,
                        'first_name': 'baisou',
                        'username': 'baisc_bot'
                    },
                    'status': 'member'
                }
            }
        },
        {
            'update_id': 988429065,
            'message': {
                'message_id': 205,
                'from': {
                    'id': 1120690440,
                    'is_bot': False,
                    'first_name': '大',
                    'last_name': '苹果',
                    'username': 'bigapple699',
                    'language_code': 'zh-hans'
                },
                'chat': {
                    'id': -1002798527828,
                    'title': '搜索🔥🔥',
                    'username': 'psytss',
                    'type': 'supergroup'
                },
                'date': 1772038257,
                'new_chat_participant': {
                    'id': 7921354496,
                    'is_bot': True,
                    'first_name': 'baisou',
                    'username': 'baisc_bot'
                },
                'new_chat_member': {
                    'id': 7921354496,
                    'is_bot': True,
                    'first_name': 'baisou',
                    'username': 'baisc_bot'
                },
                'new_chat_members': [
                    {'id': 7921354496, 'is_bot': True, 'first_name': 'baisou', 'username': 'baisc_bot'}
                ]
            }
        }
    ]
}

message_example_01 = {
    'ok': True,
    'result': [
        {
            'update_id': 988429066,
            'my_chat_member': {
                'chat': {
                    'id': -1002798527828, 'title': '搜索🔥🔥', 'username': 'psytss', 'type': 'supergroup'
                },
                'from': {
                    'id': 1120690440, 'is_bot': False, 'first_name': '大', 'last_name': '苹果',
                    'username': 'bigapple699', 'language_code': 'zh-hans'
                },
                'date': now_date,
                'old_chat_member': {
                    'user': {
                        'id': 7921354496, 'is_bot': True, 'first_name': 'baisou', 'username': 'baisc_bot'
                    },
                    'status': 'member'
                },
                'new_chat_member': {
                    'user': {
                        'id': 7921354496,
                        'is_bot': True,
                        'first_name': 'baisou', 'username': 'baisc_bot'
                    },
                    'status': 'administrator', 'can_be_edited': False, 'can_manage_chat': True,
                    'can_change_info': True, 'can_delete_messages': True, 'can_invite_users': True,
                    'can_restrict_members': True, 'can_pin_messages': True, 'can_manage_topics': False,
                    'can_promote_members': False, 'can_manage_video_chats': True, 'can_post_stories': True,
                    'can_edit_stories': True, 'can_delete_stories': True, 'is_anonymous': False,
                    'can_manage_voice_chats': True
                }
            }
        }
    ]
}

message_example_02 = {
    'ok': True,
    'result': [
        {
            'update_id': 988429073,
            'message': {
                'message_id': 214,
                'from': {
                    'id': 1120690440,
                    'is_bot': False,
                    'first_name': '大',
                    'last_name': '苹果',
                    'username': 'bigapple699',
                    'language_code': 'zh-hans'
                },
                'chat': {
                    'id': -1002798527828,
                    'title': '搜索🔥🔥', 'username': 'psytss', 'type': 'supergroup'
                },
                'date': now_date,
                'text': '/start',
                'entities': [{'offset': 0, 'length': 6, 'type': 'bot_command'}]
            }
        }
    ]
}

message_example_1 = {
    'ok': True,
    'result': [
        {
            'update_id': 63769455,
            'message': {
                'message_id': 36,
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
                'date': now_date,
                'animation': {
                    'file_name': '220a09431a30d3e40c586d41b896e72079711665051000005_online_video_cutter.mp4',
                    'mime_type': 'video/mp4',
                    'duration': 6,
                    'width': 140,
                    'height': 248,
                    'thumbnail': {
                        'file_id': 'AAMCBQADIQUABNb4k0IAAyRpZHjWRvJz2fvldj2NNKgW0k9dNQACLwEAAi2IiFSii0EWyPPL-AEAB20AAzgE',
                        'file_unique_id': 'AQADLwEAAi2IiFRy',
                        'file_size': 12105,
                        'width': 140,
                        'height': 248
                    },
                    'thumb': {
                        'file_id': 'AAMCBQADIQUABNb4k0IAAyRpZHjWRvJz2fvldj2NNKgW0k9dNQACLwEAAi2IiFSii0EWyPPL-AEAB20AAzgE',
                        'file_unique_id': 'AQADLwEAAi2IiFRy',
                        'file_size': 12105, 'width': 140, 'height': 248
                    },
                    'file_id': 'CgACAgUAAyEFAATW-JNCAAMkaWR41kbyc9n75XY9jTSoFtJPXTUAAi8BAAItiIhUootBFsjzy_g4BA',
                    'file_unique_id': 'AgADLwEAAi2IiFQ', 'file_size': 202430
                },
                'document': {
                    'file_name': '220a09431a30d3e40c586d41b896e72079711665051000005_online_video_cutter.mp4',
                    'mime_type': 'video/mp4',
                    'thumbnail': {
                        'file_id': 'AAMCBQADIQUABNb4k0IAAyRpZHjWRvJz2fvldj2NNKgW0k9dNQACLwEAAi2IiFSii0EWyPPL-AEAB20AAzgE',
                        'file_unique_id': 'AQADLwEAAi2IiFRy', 'file_size': 12105, 'width': 140, 'height': 248
                    },
                    'thumb': {
                        'file_id': 'AAMCBQADIQUABNb4k0IAAyRpZHjWRvJz2fvldj2NNKgW0k9dNQACLwEAAi2IiFSii0EWyPPL-AEAB20AAzgE',
                        'file_unique_id': 'AQADLwEAAi2IiFRy', 'file_size': 12105, 'width': 140, 'height': 248
                    },
                    'file_id': 'CgACAgUAAyEFAATW-JNCAAMkaWR41kbyc9n75XY9jTSoFtJPXTUAAi8BAAItiIhUootBFsjzy_g4BA',
                    'file_unique_id': 'AgADLwEAAi2IiFQ', 'file_size': 202430
                }
            }
        }
    ]
}

# 有新成功加入群组和消息

message_example_2 = {
    'ok': True,
    'result': [
        {
            'update_id': 63768958,
            'message': {
                'message_id': 19,
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
                'date': 1766329965,
                'text': 'hello wellwen# 如果当前数据表储存了当前群\n\n\n\n\n\n\n组(group)的规则数据，则将规则参数和参数值加入参数容器(values)# 构建数据'
                        '库查询语句，将参数容器中的数据写入数据表中的相应字段(option)',
                'entities': [{'offset': 0, 'length': 6, 'type': 'bot_command'}]
            }
        }
    ]
}
# 转发的消息
message_example_3 = {
    'ok': True,
    'result': [
        {
            'update_id': 63769479,
            'message': {
                'message_id': 38,
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
                'date': 1768416123,
                'forward_origin': {
                    'type': 'user',
                    'sender_user': {
                        'id': 7310642736,
                        'is_bot': True,
                        'first_name': 'baisou',
                        'username': 'go_bbot'
                    },
                    'date': 1761662338
                },
                'forward_from': {
                    'id': 7310642736,
                    'is_bot': True,
                    'first_name': 'baisou',
                    'username': 'go_bbot'
                },
                'forward_date': 1761662338,
                'text': '【推广】 onlin【推广】 onlin【推广】 onlin【推广】 onlin【推广】 onlin【推广】 onlin【推广】 onlin',
                'link_preview_options': {'is_disabled': True}
            }
        }
    ]
}

message_example_4 = {
    'ok': True,
    'result': [
        {
            'update_id': 63768974,
            'message': {
                'message_id': 6,
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
                'date': now_date,
                'text': 'hello wellwen'
            }
        }
    ]
}

message_example_5 = {
    'ok': True,
    'result': [
        {'update_id': 63769212,
         'message': {
             'message_id': 13,
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
                 'type': 'private'
             },
             'date': now_date,
             'text': '/help',
             'entities': [
                 {'offset': 0, 'length': 13, 'type': 'bot_command'}
             ]
         }
         }
    ]
}

message_example_6 = {
    'ok': True,
    'result': [
        {
            'update_id': 63769288,
            'message': {
                'message_id': 35,
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
                    'type': 'private'
                },
                'date': now_date,
                'text': '/strat',
                'entities': [
                    {'offset': 0, 'length': 53, 'type': 'url'}
                ],
                'link_preview_options': {'url': 'https://core.telegram.org/bots/api'}
            }
        }
    ]
}

message_example_7 = {
    'ok': True,
    'result': [
        {
            'update_id': 63769244,
            'message': {
                'message_id': 24,
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
                'date': now_date,
                'new_chat_participant': {
                    'id': 7557645689,
                    'is_bot': False,
                    'first_name': '双囍'
                },
                'new_chat_member': {
                    'id': 7557645689,
                    'is_bot': False,
                    'first_name': '双囍'
                },
                'new_chat_members': [
                    {'id': 7557646089, 'is_bot': False, 'username': 'cfunfun', 'first_name': '双囍'},
                    {'id': 7557645589, 'is_bot': False, 'first_name': '双囍', 'last_name': ''},
                    {'id': 7577645689, 'is_bot': False, 'first_name': '双', 'last_name': '囍临门'},
                    {'id': 7507645689, 'is_bot': True, 'username': 'nmnmfunbot', 'first_name': '双囍'},
                ]
            }
        }
    ]
}
# 机器人被提升为管理员
message_example_8 = {
    'ok': True,
    'result': [
        {
            'update_id': 63769541,
            'my_chat_member': {
                'chat': {
                    'id': -1002798527828,
                    'title': '搜索🔥🔥',
                    'username': 'psytss',
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
                'date': now_date,
                'old_chat_member': {
                    'user': {
                        'id': 8598030336,
                        'is_bot': True,
                        'first_name': 'rulesbot',
                        'username': 'wellwen_bot'
                    },
                    'status': 'member'
                },
                'new_chat_member': {
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
                    'can_promote_members': False,
                    'can_manage_video_chats': True,
                    'can_post_stories': True,
                    'can_edit_stories': True,
                    'can_delete_stories': True,
                    'is_anonymous': False,
                    'can_manage_voice_chats': True
                }
            }
        }
    ]
}

message_example_9 = {
    'ok': True,
    'result': [
        {
            'update_id': 63770607,
            'message': {
                'message_id': 197,
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
                },
                'date': time.time(),
                'text': '/start',
                'entities': [
                    {'offset': 0, 'length': 6, 'type': 'bot_command'}
                ]
            }
        }
    ]
}

message_example_10 = {
    'ok': True,
    'result': [
        {
            'update_id': 63770662,
            'message': {
                'message_id': 204,
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
                },
                'date': time.time(),
                'text': 'D:\\PycharmProjects\\teleg'
            }
        }
    ]
}

message_example_11 = {
    'ok': True,
    'result': [
        {
            'update_id': 63770691,
            'message': {
                'message_id': 214,
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
                'date': time.time(),
                'text': '1111111111 [\'editMessageText\', {\'chat_id\': 1120690440, \'message_id\': 203, \'text\': \'一个能'
                        '在你的群组中24小时不间断监视群组活动的机器人，它没有作息时间，你可以设置任意规则来管理你的群组\\n\\n点击【帮助'
                        '】了解如何使用本机器\', \'reply_markup\': {\'inline_keyboard\': [[{\'text\': \'机器人定制\', \'ur'
                        'l\': \'https://t.me/bigapple699\'}, {\'text\': \'开始使用机器人\', \'callback_data\': \'["rule'
                        's","prelude",0,0,0]\'}], [{\'text\': \'添加到群组\', \'url\': \'https://t.me/wellwen_bot?start'
                        'group=true?startgroup=true\'}, {\'text\': \'帮助\', \'callback_data\': \'["help",0,0,0,0]\'}'
                        ']]}, \'entities\': [{\'type\': \'bold\', \'offset\': 56, \'length\': 2}]}]\n1111111111 {\'o'
                        'k\': True, \'result\': {\'message_id\': 203, \'from\': {\'id\': 8598030336, \'is_bot\': Tru'
                        'e, \'first_name\': \'rulesbot\', \'username\': \'wellwen_bot\'}, \'chat\': {\'id\': 11206904'
                        '40, \'first_name\': \'大\', \'last_name\': \'苹果\', \'username\': \'bigapple699\', \'type\': \'pr'
                        'ivate\'}, \'date\': 1771641740, \'edit_date\': 1771692560, \'text\': \'一个能在你的群组中24小时不间断'
                        '监视群组活动的机器人，它没有作息时间，你可以设置任意规则来管理你的群组\\n\\n点击【帮助】了解如何使用本机器\', \'ent'
                        'ities\': [{\'offset\': 56, \'length\': 2, \'type\': \'bold\'}], \'reply_markup\': {\'inline_keybo'
                        'ard\': [[{\'text\': \'机器人定制\', \'url\': \'https://t.me/bigapple699\'}, {\'text\': \'开始使用机器'
                        '人\', \'callback_data\': \'["rules","prelude",0,0,0]\'}], [{\'text\': \'添加到群组\', \'url\': \'htt'
                        'ps://t.me/wellwen_bot?startgroup=true?startgroup=true\'}, {\'text\': \'帮助\', \'callback_data\': \'['
                        '"help",0,0,0,0]\'}]]}}}',
                'entities': [
                    {'offset': 220, 'length': 24, 'type': 'url'},
                    {'offset': 343, 'length': 56, 'type': 'url'},
                    {'offset': 1032, 'length': 24, 'type': 'url'},
                    {'offset': 1155, 'length': 56, 'type': 'url'}
                ],
                'link_preview_options': {'url': 'https://t.me/bigapple699'}
            }
        }
    ]
}

message_example_12 = {
    'ok': True,
    'result': [
        {'update_id': 63770693,
         'message': {
             'message_id': 215,
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
             'date': time.time(),
             'text': '签到'
         }
         }
    ]
}
message_example_13 = {
    'ok': True,
    'result': [
        {
            'update_id': 988429151,
            'message': {
                'message_id': 247,
                'from': {
                    'id': 1120690440,
                    'is_bot': False,
                    'first_name': '大',
                    'last_name': '苹果',
                    'username': 'bigapple699',
                    'language_code': 'zh-hans'
                },
                'chat': {
                    'id': -1002798527828,
                    'title': '搜索🔥🔥',
                    'username': 'psytss',
                    'type': 'supergroup'
                },
                'date': time.time(),
                'text': '全球'
            }
        }
    ]
}

message_example_14 = {
    'ok': True,
    'result': [
        {'update_id': 63770908,
         'message': {
             'message_id': 236,
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
             'date': time.time(),
             'text': '签到ffffff'
         }
         }
    ]
}

callbackquery_example_1 = {
        'update_id': 535451741,
        'callback_query': {
            'id': '8990108583871663212',
            'from': {
                'id': 6388140064,
                'is_bot': False,
                'first_name': '关山',
                'language_code': 'zh-hans'
            },
            'message': {
                'message_id': 74,
                'from': {
                    'id': 7310642736,
                    'is_bot': True,
                    'first_name': 'go',
                    'username': 'go_bbot'
                },
                'chat': {
                    'id': -1002245506141,
                    'chat_title': '我的群组',
                    'type': 'supergroup'
                },
                'date': time.time(),
                'edit_date': 1747408389,
                'text': '搬砖套利中文群池质押中心矿池官方社区',
                'entities': [
                    {'offset': 0, 'length': 9, 'type': 'text_link', 'url': 'https://t.me/broccolicn_broccolitm'}],
                'link_preview_options': {
                    'url': 'http://t.me/broccolicn_broccolitm'
                },
                'reply_markup': {
                    'inline_keyboard': [
                        [
                            {
                                'text': '上一页',
                                'callback_data': 'SC|币安|20'
                            },
                            {
                                'text': '下一页',
                                'callback_data': 'SC|币安|60'
                            }
                        ]
                    ]
                }
            },
            'chat_instance': '-6036115718195468706',
            'data': '|rules|text|high|0|0'
        }
    }
callbackquery_example_2 = {
    'ok': True,
    'result': [
        {
            'update_id': 63770631,
            'callback_query': {
                'id': '4813328789815341205',
                'from': {
                    'id': 1120690440,
                    'is_bot': False,
                    'first_name': '大',
                    'last_name': '苹果',
                    'username': 'bigapple699',
                    'language_code': 'zh-hans'
                },
                'message': {
                    'message_id': 201,
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
                    'date': time.time(),
                    'edit_date': 1771585893,
                    'text': '规则机器人\n\n\n\n🔔 当前为你找到以下群组，点击可查看群组的规则详情，如果没有你期望的群组，请点击【帮助】按钮查看解决方案',
                    'entities': [
                        {'offset': 0, 'length': 5, 'type': 'bold'},
                        {'offset': 12, 'length': 50, 'type': 'bold'}
                    ],
                    'reply_markup': {
                        'inline_keyboard': [
                            [
                                {'text': 'Test', 'callback_data': '["rules",0,0,0,-1003606614850]'}
                            ],
                            [
                                {'text': '添加机器人到群组', 'url': 'https://t.me/addbot?startgroup=true'}
                            ],
                            [
                                {'text': '帮助', 'callback_data': '["help", 0, 0, 0, 0]'}
                            ],
                            [
                                {'text': '返回', 'callback_data': '["start", 0, 0, 0, 0]'}
                            ]
                        ]
                    }
                },
                'chat_instance': '-6124905536428867626',
                'data': '["rules","video","clear",0,-1003606614850]'
            }
        }
    ]
}
callbackquery_example_3 = {
    'ok': True,
    'result': [
        {
            'update_id': 63770622,
            'callback_query': {
                'id': '4813328790557379893',
                'from': {
                    'id': 1120690440,
                    'is_bot': False,
                    'first_name': '大',
                    'last_name': '苹果',
                    'username': 'bigapple699',
                    'language_code': 'zh-hans'
                },
                'message': {
                    'message_id': 199,
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
                    'date': time.time(),
                    'edit_date': 1771584198,
                    'text': '一个能在你的群组中24小时不间断监视群组活动的机器人，它没有作息时间，你可以设置任意规则'
                            '来管理你的群组\n\n点击【帮助】了解如何使用本机器',
                    'entities': [
                        {'offset': 56, 'length': 2, 'type': 'bold'}
                    ],
                    'reply_markup': {
                        'inline_keyboard': [
                            [
                                {'text': '机器人定制', 'url': 'https://t.me/bigapple699'},
                                {'text': '开始使用机器人', 'callback_data': '["rules","prelude",0,0,0]'}
                            ],
                            [
                                {'text': '添加到群组', 'url': 'https://t.me/wellwen_bot?startgroup=true?startgroup=true'},
                                {'text': '帮助', 'callback_data': '["help",0,0,0,0]'}
                            ]
                        ]
                    }
                },
                'chat_instance': '-6124905536428867626',
                'data': '["rules","prelude",0,0,0]'
            }
        }
    ]
}

callbackquery_example_4 = {
    'ok': True,
    'result': [
        {
            'update_id': 988429041,
            'callback_query': {
                'id': '4813328790404182290',
                'from': {
                    'id': 1120690440, 'is_bot': False, 'first_name': '大', 'last_name': '苹果',
                    'username': 'bigapple699', 'language_code': 'zh-hans'
                },
                'message': {
                    'message_id': 19,
                    'from': {
                        'id': 7921354496, 'is_bot': True, 'first_name': 'baisou', 'username': 'baisc_bot'
                    },
                    'chat': {
                        'id': 1120690440, 'first_name': '大', 'last_name': '苹果',
                        'username': 'bigapple699', 'type': 'private'
                    },
                    'date': time.time(),
                    'edit_date': 1771986084,
                    'text': '百搜机器人\n\n搜群组,搜频道,搜影视,搜资讯,搜遍TG的搜索小能手',
                    'entities': [
                        {'offset': 0, 'length': 5, 'type': 'bold'},
                        {'offset': 30, 'length': 3, 'type': 'bold'}
                    ],
                    'reply_markup': {
                        'inline_keyboard': [
                            [
                                {'text': '热门标签', 'callback_data': '["ST","tag",0,0,0]'},
                                {'text': '热门标签', 'callback_data': '["ST","tag",0,0,0]'}
                            ],
                            [
                                {'text': '添加收录', 'url': 'https://t.me/baisc_bot?startgroup=true?/add=true'}
                            ],
                            [
                                {'text': '添加机器人到群组', 'url': 'https://t.me/baisc_bot?startgroup=true?startgroup=true'}
                            ]
                        ]
                    }
                },
                'chat_instance': '2343827444069636676',
                'data': '["ST","tag",0,0,0]'
            }
        }
    ]
}

callbackquery_example_5 = {
    'ok': True,
    'result': [
        {
            'update_id': 988429082,
            'callback_query': {
                'id': '4813328789401022366',
                'from': {
                    'id': 1120690440,
                    'is_bot': False,
                    'first_name': '大',
                    'last_name': '苹果',
                    'username': 'bigapple699',
                    'language_code': 'zh-hans'
                },
                'message': {
                    'message_id': 226,
                    'from': {
                        'id': 7921354496,
                        'is_bot': True,
                        'first_name': 'baisou',
                        'username': 'baisc_bot'
                    },
                    'chat': {
                        'id': -1002798527828, 'title': '搜索🔥🔥', 'username': 'psytss', 'type': 'supergroup'
                    },
                    'date': time.time(),
                    'message_thread_id': 225,
                    'reply_to_message': {
                        'message_id': 225,
                        'from': {
                            'id': 1120690440, 'is_bot': False, 'first_name': '大', 'last_name': '苹果',
                            'username': 'bigapple699', 'language_code': 'zh-hans'
                        },
                        'chat': {
                            'id': -1002798527828, 'title': '搜索🔥🔥', 'username': 'psytss', 'type': 'supergroup'
                        },
                        'date': 1772077942, 'text': '数据'
                    },
                    'text': '👥 公群 818 已押80888U 皇冠地推采集数据  10368人\n📢 💮快马联盟💮全球实卡接码💮国内外帐'
                            '号💮手  22437人\n👥 热门出海项目-SVIP联盟  23809人\n👥 热门出海项目-SVIP联盟  23789'
                            '人\n👥 公群618 已押67888U 天海数据采集  14141人\n📢 【接码平台】🌈国内外账号🌈源头数据 '
                            ' 4495人\n👥 公群688 已押52888U 银河国际数据采集  15720人\n👥 公群 818 已押80888U 皇冠'
                            '地推采集数据  10685人\n📢 云端数据频道  1948人\n📢 💮快马联盟💮全球实卡接码💮国内外帐号'
                            '💮手  29234人\n👥 公群688 已押52888U 银河国际数据采集  13959人\n👥 公群71275 已押15'
                            '000U【Mohei团队】贷款数据  6338人\n👥 公群234启航抖音代刷押金88888u  21046人\n👥 公群8'
                            '890 已押10000U婉宁集团小额PG洗资  4856人\n📢 达摩-精准数据源头  3880人',
                    'entities': [
                        {'offset': 3, 'length': 24, 'type': 'text_link', 'url': 'https://t.me/+9h7Hv-XSqVI3MTk1'},
                        {'offset': 39, 'length': 24, 'type': 'text_link', 'url': 'https://t.me/+a3-qRYTPSf9jZmRk'},
                        {'offset': 75, 'length': 13, 'type': 'text_link', 'url': 'https://t.me/+e57VAVSzEahkZGU1'},
                        {'offset': 100, 'length': 13, 'type': 'text_link', 'url': 'https://t.me/+e57VAVSzEahkZGU1'},
                        {'offset': 125, 'length': 21, 'type': 'text_link', 'url': 'https://t.me/+GmM8YyiZ0FBhYWE8'},
                        {'offset': 158, 'length': 19, 'type': 'text_link', 'url': 'https://t.me/+IBB4e2HWJlwyYTdl'},
                        {'offset': 188, 'length': 23, 'type': 'text_link', 'url': 'https://t.me/+K7TCTaoQP1cxMDRh'},
                        {'offset': 223, 'length': 24, 'type': 'text_link', 'url': 'https://t.me/+9h7Hv-XSqVI3MTk1'},
                        {'offset': 259, 'length': 6, 'type': 'text_link', 'url': 'https://t.me/+PjxMUdKv5cgzMzNl'},
                        {'offset': 276, 'length': 24, 'type': 'text_link', 'url': 'https://t.me/+a3-qRYTPSf9jZmRk'},
                        {'offset': 312, 'length': 23, 'type': 'text_link', 'url': 'https://t.me/+K7TCTaoQP1cxMDRh'},
                        {'offset': 347, 'length': 29, 'type': 'text_link', 'url': 'https://t.me/+W_a35hhjSZUyMjA1'},
                        {'offset': 387, 'length': 19, 'type': 'text_link', 'url': 'https://t.me/+X9uzcdYtdRYzYmE0'},
                        {'offset': 418, 'length': 25, 'type': 'text_link', 'url': 'https://t.me/+xBq8_m5HNfEyN2Ex'},
                        {'offset': 454, 'length': 9, 'type': 'text_link', 'url': 'https://t.me/+Zz6ZsH2ds1xiOWNk'}
                    ],
                    'link_preview_options': {'is_disabled': True},
                    'reply_markup': {
                        'inline_keyboard': [
                            [
                                {'text': '全部', 'callback_data': '["SC",数据,all,0,1120690440]'},
                                {'text': '👥', 'callback_data': '["SC",数据,group,0,1120690440]'},
                                {'text': '📢', 'callback_data': '["SC",数据,channel,0,1120690440]'},
                                {'text': '🎬', 'callback_data': '["SC",数据,movie,0,1120690440]'},
                                {'text': '🖼', 'callback_data': '["SC",数据,image,0,1120690440]'},
                                {'text': '🤖', 'callback_data': '["SC",数据,bot,0,1120690440]'}
                            ],
                            [
                                {'text': '下一页', 'callback_data': "['SC', '数据', 'all', 1, 1120690440]"}
                            ]
                        ]
                    }
                },
                'chat_instance': '7589616792723441831',
                'data': "['SC', '数据', 'all', 1, 1120690440]"
            }
        }
    ]
}

callbackquery_example_6 = {
    'ok': True,
    'result': [
        {
            'update_id': 988429101,
            'callback_query': {
                'id': '4813328790602005085',
                'from': {
                    'id': 1120690440,
                    'is_bot': False,
                    'first_name': '大',
                    'last_name': '苹果',
                    'username': 'bigapple699',
                    'language_code': 'zh-hans'
                },
                'message': {
                    'message_id': 19,
                    'from': {
                        'id': 7921354496,
                        'is_bot': True,
                        'first_name': 'baisou',
                        'username': 'baisc_bot'
                    },
                    'chat': {
                        'id': 1120690440,
                        'first_name': '大',
                        'last_name': '苹果',
                        'username': 'bigapple699',
                        'type': 'private'
                    },
                    'date': time.time(),
                    'edit_date': 1772162753,
                    'text': '百搜机器人\n\n搜群组,搜频道,搜影视,搜资讯,搜遍TG的搜索小能手',
                    'entities': [
                        {'offset': 0, 'length': 5, 'type': 'bold'},
                        {'offset': 30, 'length': 3, 'type': 'bold'}
                    ],
                    'reply_markup': {
                        'inline_keyboard': [
                            [
                                {'text': '热门标签', 'callback_data': '["ST","Tag",0,0,0]'},
                                {'text': '热门标签', 'callback_data': '["ST","Tag",0,0,0]'}
                            ],
                            [
                                {'text': '添加收录', 'url': 'https://t.me/baisc_bot?startgroup=true?/add=true'}
                            ],
                            [
                                {'text': '添加机器人到群组', 'url': 'https://t.me/baisc_bot?startgroup=true?startgroup=true'}
                            ]
                        ]
                    }
                },
                'chat_instance': '2343827444069636676',
                'data': '["ST","#音乐视频",0,0,0]'
            }
        }
    ]
}

callbackquery_example_7 = {
    'ok': True,
    'result': [
        {
            'update_id': 63770785,
            'callback_query': {
                'id': '4813328789290188071',
                'from': {
                    'id': 1120690440,
                    'is_bot': False,
                    'first_name': '大',
                    'last_name': '苹果',
                    'username': 'bigapple699',
                    'language_code': 'zh-hans'
                },
                'message': {
                    'message_id': 217,
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
                    'date': time.time(),
                    'edit_date': 1772374687,
                    'text': '规则机器人\n\n\n\n🔔 当前为你找到以下群组，点击可查看群组的规则详情，如果没有你期望的群组，'
                            '请点击【帮助】按钮查看解决方案',
                    'entities': [
                        {'offset': 0, 'length': 5, 'type': 'bold'},
                        {'offset': 12, 'length': 50, 'type': 'bold'}
                    ],
                    'reply_markup': {
                        'inline_keyboard': [
                            [{'text': 'Test', 'callback_data': 'rules|0|0|0|-1003606614850'}],
                            [{'text': '添加机器人到群组', 'url': 'https://t.me/addbot?startgroup=true'}],
                            [{'text': '帮助', 'callback_data': 'help"|0|0|0|0'}],
                            [{'text': '返回', 'callback_data': 'start|0|0|0|0'}]
                        ]
                    }
                },
                'chat_instance': '-6124905536428867626',
                'data': 'rules|0|0|0|-1003606614850'
            }
        }
    ]
}
callbackquery_example_8 = {
    'ok': True,
    'result': [
        {
            'update_id': 988429154,
            'callback_query': {
                'id': '4813328789688781754',
                'from': {
                    'id': 1120690440,
                    'is_bot': False,
                    'first_name': '大',
                    'last_name': '苹果',
                    'username': 'bigapple699',
                    'language_code': 'zh-hans'
                },
                'message': {
                    'message_id': 250,
                    'from': {
                        'id': 7921354496,
                        'is_bot': True,
                        'first_name': 'baisou',
                        'username': 'baisc_bot'
                    },
                    'chat': {
                        'id': -1002798527828,
                        'title': '搜索🔥🔥',
                        'username': 'psytss',
                        'type': 'supergroup'
                    },
                    'date': time.time(),
                    'message_thread_id': 249,
                    'reply_to_message': {
                        'message_id': 249,
                        'from': {
                            'id': 1120690440,
                            'is_bot': False,
                            'first_name': '大',
                            'last_name': '苹果',
                            'username': 'bigapple699',
                            'language_code': 'zh-hans'
                        },
                        'chat': {
                            'id': -1002798527828,
                            'title': '搜索🔥🔥',
                            'username': 'psytss',
                            'type': 'supergroup'
                        },
                        'date': 1772391264,
                        'text': '全球'
                    },
                    'text': '【顶置推广】 onlinesim接码平台，提供超过90个国家的手机号码，履盖全球热门应用，全中文支'
                            '持，API接入，更有免费的公用号码临时使用\n\n👥 2026世界杯🏆赌狗之家  93.2k'
                            '\n📢 全球实卡接码 | WhatsApp实卡 | LINE实卡 |  199\n📢 信誉全球接码平'
                            '台｜实卡接码｜短信接码｜短  5.1k\n📢 金銀珠寐娛樂-華爾街總店  16.3k\n📢 💮'
                            '快马联盟💮全球实卡接码💮国内外帐号💮手  22.4k\n👥 土豆公群15919 万象抖音代'
                            '刷 已押12345.6u  6.3k\n👥 Q003 起点电子🎰体育⚽️百家乐🃏综合娱乐  13.2k\
                            n📢 \U0001f6dc免费VPN代理-高速节点-加速器-机场-VPN免  59.2k\n👥 公群99 已'
                            '押50000U 小Z集团抖音代刷  140.1k\n📢 kk 全球🌍 妈咪高端ww➗女 男模 视频模特 '
                            '翻  19.5k\n📢 全球接码/短信接码/注册接码/接码平台  2.8k\n📢 广州高端外围【璀璨星空'
                            '】  6.1k\n📢 全球华人头条资讯大事件  84.6k\n📢 糖人街包养 - 全球可飞（新马泰越 日'
                            '韩 欧美  3.8k\n👥 天天德州竞技  2.1k\n\n当前显示【全部】，167/1页',
                    'entities': [
                        {'offset': 1, 'length': 4, 'type': 'bold'},
                        {'offset': 7, 'length': 63, 'type': 'text_link', 'url': 'https://onlinesim.io/?aref=2207071'},
                        {'offset': 75, 'length': 13, 'type': 'text_link', 'url': 'https://t.me/+-jlaZroaIzEzOGNl'},
                        {'offset': 99, 'length': 30, 'type': 'text_link', 'url': 'https://t.me/+18V0Vzl1ZJEwMTk9'},
                        {'offset': 138, 'length': 20, 'type': 'text_link', 'url': 'https://t.me/+87E788E9ZTlkMDA1'},
                        {'offset': 168, 'length': 12, 'type': 'text_link', 'url': 'https://t.me/+9vQkP9jnHrk4ZTZl'},
                        {'offset': 191, 'length': 24, 'type': 'text_link', 'url': 'https://t.me/+a3-qRYTPSf9jZmRk'},
                        {'offset': 226, 'length': 27, 'type': 'text_link', 'url': 'https://t.me/+B0c3dfLa99IzZWQ1'},
                        {'offset': 263, 'length': 24, 'type': 'text_link', 'url': 'https://t.me/+cJNNcopkZOM3Y2Jl'},
                        {'offset': 298, 'length': 26, 'type': 'text_link', 'url': 'https://t.me/+cUgOSaVMwjpiMzFl'},
                        {'offset': 335, 'length': 22, 'type': 'text_link', 'url': 'https://t.me/+eHf3Wp6MSBUyYWM9'},
                        {'offset': 369, 'length': 26, 'type': 'text_link', 'url': 'https://t.me/+EHnpUJ7QieU0NjI1'},
                        {'offset': 406, 'length': 19, 'type': 'text_link', 'url': 'https://t.me/+HHTPiRXYAgtmZmE1'},
                        {'offset': 435, 'length': 12, 'type': 'text_link', 'url': 'https://t.me/+HYqZyYBO-w1lNzZl'},
                        {'offset': 457, 'length': 11, 'type': 'text_link', 'url': 'https://t.me/+k4t0qkN8vPYzOGRl'},
                        {'offset': 479, 'length': 23, 'type': 'text_link', 'url': 'https://t.me/+kduJJNKYpd8zMTI1'},
                        {'offset': 512, 'length': 6, 'type': 'text_link', 'url': 'https://t.me/+n8kQC3ObCd1lZTc1'}
                    ],
                    'link_preview_options': {'is_disabled': True},
                    'reply_markup': {
                        'inline_keyboard': [
                            [
                                {'text': '全部', 'callback_data': '|SG|全球|all|0|1120690440'},
                                {'text': '👥', 'callback_data': '|SG|全球|group|0|1120690440'},
                                {'text': '📢', 'callback_data': '|SG|全球|channel|0|1120690440'},
                                {'text': '📝', 'callback_data': '|SG|全球|posts|0|1120690440'},
                                {'text': '🖼️', 'callback_data': '|SG|全球|image|0|1120690440'},
                                {'text': '🎬', 'callback_data': '|SG|全球|movie|0|1120690440'},
                                {'text': '🤖', 'callback_data': '|SG|全球|bot|0|1120690440'}
                            ],
                            [
                                {'text': '下一页', 'callback_data': 'SG|全球|all|1|1120690440'}
                            ]
                        ]
                    }
                },
                'chat_instance': '7589616792723441831', 'data': 'SG|全球|all|1|1120690440'
            }
        }
    ]
}

callbackquery_example_9 = {
    'ok': True,
    'result': [
        {
            'update_id': 63770840,
            'callback_query': {
                'id': '4813328789372450893',
                'from': {
                    'id': 1120690440,
                    'is_bot': False,
                    'first_name': '大',
                    'last_name': '苹果',
                    'username': 'bigapple699',
                    'language_code': 'zh-hans'
                },
                'message': {
                    'message_id': 217,
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
                    'date': time.time(),
                    'edit_date': 1772755473,
                    'text': '规则机器人 >> Test >> 签到管理\n\n签到管理，为群组设置一个签到规则，帮你统计群组的活跃程度，'
                            '点击相应按钮可设置签到规则，设置好后会弹出【启动签到按钮】，只能运行一个签到规则，启动后无法'
                            '修改签到规则\n签到周期： 30\n签到描述： 帮你从素人→百万博主：流量·资源·商务·全链路变现全球平台'
                            '资源·华语\n当前状态： 就绪\n🔔 签到描述： 设置成功',
                    'entities': [
                        {'offset': 0, 'length': 5, 'type': 'bold'},
                        {'offset': 105, 'length': 59, 'type': 'blockquote'},
                        {'offset': 167, 'length': 10, 'type': 'bold'}
                    ],
                    'reply_markup': {
                        'inline_keyboard': [
                            [
                                {'text': '签到周期', 'callback_data': 'rules|register|period|0|-1003606614850'},
                                {'text': '签到描述', 'callback_data': 'rules|register|explain|0|-1003606614850'}
                            ],
                            [
                                {'text': '查看签到数据', 'callback_data': 'rules|register|view|0|-1003606614850'},
                                {'text': '启动签到', 'callback_data': 'rules|register|begin|0|-1003606614850'}
                            ],
                            [
                                {'text': '清空规则', 'callback_data': 'rules|register|clear|0|-1003606614850'},
                                {'text': '返回', 'callback_data': 'rules|0|0|1|-1003606614850'}
                            ]
                        ]
                    }
                },
                'chat_instance': '-6124905536428867626',
                'data': 'rules|register|begin|0|-1003606614850'
            }
        }
    ]
}



























