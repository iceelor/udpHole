# -*- coding:utf-8 -*-
import socket
import time
import json
import threading

id = "fcbc5c6655ee11e9af3cc85b76997f30"
local_port = 3389

buffer_size = 512 * 1024
socket_timeout = 1024
server = ('118.25.44.238', 9999)
local = None
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(socket_timeout)

local_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_s.settimeout(socket_timeout)
local_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
local_s.bind(('127.0.0.1', local_port))

# 客户端列表，(addr,port)
client = None
client_id = None
connect_server = False


class Forward(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global s, client, local_s
        while True:
            buffer = local_s.recv(buffer_size)
            # 收到数据，转发给对方
            if client:
                s.sendto(buffer, client)
            time.sleep(0.5)


class Heartbeat(threading.Thread):
    """
        用于保持心跳
    """

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global s
        while True:
            # 循环发送心跳包
            s.sendto(b'1', server)
            if client:
                s.sendto(b'1', client)
            time.sleep(10)


class Read(threading.Thread):
    """
        用于杰宝
    """

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global s, client, client_id, connect_server
        while True:
            # 接受到的数据，通常为json格式
            buffer = s.recv(buffer_size)
            if b'1' == buffer: break
            if not client_id:
                try:
                    buffer_str = str(buffer, encoding="utf-8")
                    data = json.loads(buffer_str)
                    if "c" in data:
                        addr = data["c"]
                        client = (addr[0], addr[1])
                        # 有人请求连接
                        result = {"cc": ""}
                        client_id = data["id"]
                        WriteJSON(result, client)
                        # s.sendto(bytes(json.dumps(result), encoding="utf-8"), client)
                    elif "cc" in data:
                        print("id:：%s 连接成功" % client_id)
                    elif "sc" in data:
                        print("连接服务器成功")
                except:
                    pass
            else:
                # 开始转发流量
                local_s.send(buffer)
                pass
            time.sleep(0.5)


def WriteJSON(js, addr):
    s.sendto(bytes(json.dumps(js), encoding="utf-8"), addr)


if __name__ == "__main__":
    read = Read()
    read.start()
    # 服务器上注册
    WriteJSON({"id": id}, server)
    # 启动心跳
    hb = Heartbeat()
    hb.start()
    pass
