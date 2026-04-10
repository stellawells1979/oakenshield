

import requests
from test import debugging


def send_test_update():
    url = "http://127.0.0.1:5000/telegram/rules"

    payload = debugging.message_example_9['result'][0]

    response = requests.post(url, json=payload, timeout=10)
    print("状态码:", response.status_code)
    print("响应内容:", response.text)


if __name__ == "__main__":
    send_test_update()