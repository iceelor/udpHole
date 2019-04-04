# -*- coding:utf-8 -*-
import socket
import time
import json
import threading
import traceback

buffer_size = 512 * 1024
socket_timeout = 1024
server = ('118.25.44.238', 9999)
local = None
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(socket_timeout)

lock = threading.Lock()

client_list = {}
server_flag = False
id = None


class Heartbeat(threading.Thread):
    """
        用于保持心跳
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.num = 40

    def run(self):
        global s
        while True:
            # 循环发送心跳包
            Write('1', server)
            try:
                lock.acquire()
                for i in client_list:
                    Write('1', (client_list[i]["address"], client_list[i]["port"]))
            except Exception as e:
                traceback.print_exc()
            finally:
                lock.release()
            while self.num > 0:
                time.sleep(1)
                self.num = self.num - 1
            self.num = 40

    def init_num(self):
        self.num = 0

class Read(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global s, client_list, server_flag, id,hb
        while True:
            try:
                buf, addr = s.recvfrom(buffer_size)
            except:
                continue
            if addr == server:
                server_flag = True
            if b'1' == buf: continue
            try:
                data = json.loads(str(buf, encoding="utf-8"))
                t = data["t"]
                if t == "list":
                    lock.acquire()
                    client_list = data["data"]
                    lock.release()
                    hb.init_num()
                elif t == "msg":
                    print('\n' + get_name(data["id"]) + "：" + data["d"])
                elif t == "id":
                    id = data["d"]
                elif t =="c":
                    # 请求连接
                    address = (data["address"],data["port"])
                    pass
            except Exception as e:
                traceback.print_exc()
            time.sleep(0.5)


def get_name(id):
    try:
        lock.acquire()
        if id in client_list:
            return client_list[id]["name"]
        return "匿名"
    except Exception as e:
        traceback.print_exc()
    finally:
        lock.release()


def WriteJSON(js, addr):
    """
        向服务器发送json
    :param js:
    :param addr:
    :return:
    """
    s.sendto(bytes(json.dumps(js), encoding="utf-8"), addr)
    time.sleep(0.5)

def Write(js, addr):
    try:
        s.sendto(bytes(js, encoding="utf-8"), addr)
    except:
        pass

def send_msg(msg):
    try:
        lock.acquire()
        for i in client_list:
            WriteJSON(msg, (client_list[i]["address"], client_list[i]["port"]))
            time.sleep(0.5)
    except Exception as e:
        traceback.print_exc()
    finally:
        lock.release()

hb = Heartbeat()
read = Read()
if __name__ == "__main__":
    read.start()

    hb.start()
    print('loading', flush=True, end='')
    while not server_flag:
        print('.', flush=True, end='')
        time.sleep(1)
    name = input("\n给自己起个昵称：")
    WriteJSON({"t": "n", "n": name}, server)
    # 启动心跳
    cmd = ["list"]
    result = {"t": "msg", "d": "", "id": id}
    while True:
        msg = input("")
        if msg in cmd:
            if msg == cmd[0]:
                WriteJSON({"t": "list"}, server)
        else:
            result["d"] = msg
            send_msg(result)
