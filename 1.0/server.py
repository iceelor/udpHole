# -*- coding:utf-8 -*-
import time
import socket
import json
import threading

buffer_size = 64 * 1024
bind_address = ('0.0.0.0', 9999)
socket_timeout = 4096
buffer_list = {}
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(socket_timeout)
s.bind(bind_address)


class Timer(threading.Thread):
    """
        定时器
    """
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            for i in buffer_list:
                if time.time() - buffer_list[i]["time"] >= 600:
                    buffer_list.pop(i)
            time.sleep(10)


if __name__ == "__main__":
    timer = Timer()
    timer.start()
    while True:
        try:
            buffer, addr = s.recvfrom(buffer_size)
            # 心跳包
            if b'1' == buffer: break
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), buffer, addr)
            buffer_str = str(buffer, encoding="utf-8")
            data = json.loads(buffer_str)
            if "c" in data:
                # 连接请求，需要判断对方是否存在以及将信息发送给对方
                conn = data["c"]
                if conn[2] in buffer_list:
                    result = {"id": data["id"], "c": [addr[0], addr[1]]}
                    # 通知对方，同步连接
                    s.sendto(bytes(json.dumps(result), encoding='utf-8'), (conn[0], conn[1]))
            else:
                # 注册请求
                id = data["id"]
                if len(id) != 32: break
                buffer_list[id] = {"address": addr[0], "port": addr[1], "time": time.time()}
                s.sendto(bytes(json.dumps({"sc": ""}), encoding="utf-8"), addr)
        except Exception as e:
            print(e)
            pass
        time.sleep(0.5)
