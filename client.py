# -*- coding:utf-8 -*-
import socket
import time
import threading
import json
import uuid

name = "公司笔记本"
server = ('118.25.44.238', 9999)
buffer_size = 32 * 1024
socket_timeout = 1024
resend = {"type": "resend"}
# 客户端申请握手
handshake = {"type": "handshake", "name": "", "id": ""}
# 客户端获取指定客户ip地址
connect = {"type": "connect", "id": ""}
request_connect = {"type": "client", "name": ""}


class MouseClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.settimeout(socket_timeout)
        self.last_msg = None
        self.try_connect = True
        self.client_addr = None
        self.id = None
        self.name = name

    def run(self):
        self.flag = True
        data =None
        while self.flag:
            try:
                data = self.s.recv(buffer_size)
                data = str(data, encoding='utf-8')
                result = json.loads(data)
                self.data_analysis(result)
            except:
                print("收到数据，出现错误",data)
                # 出错原因可能是丢包，发送重发命令
                # self.s.send(bytes(json.dumps(resend)))
                pass
            time.sleep(3)

    def handshake(self):
        self.try_connect = True
        # 握手
        temp_handshake = handshake
        temp_handshake["name"] = name
        temp_handshake["id"] = str(uuid.uuid1()).replace('-', '')
        self.id = temp_handshake["id"]
        self.sendto(json.dumps(temp_handshake), server)

    def connect(self, id):
        # 根据id申请连接
        temp_connect = connect
        temp_connect["id"] = id
        self.sendto(json.dumps(temp_connect), server)

    def sendto(self, msg="", addr=None, last_msg=False):
        try:
            if last_msg and self.last_msg:
                msg = self.last_msg[0]
                addr = self.last_msg[1]
            else:
                # 记录最后一条msg
                self.last_msg = (msg, addr)
            self.s.sendto(bytes(msg, encoding='utf-8'), (addr[0], int(addr[1])))
            return True
        except:
            return False

    def data_analysis(self, result):
        type = result["type"]
        if type == "connect":
            client = result["data"]
            # 尝试连接
            self.connect_client((client["address"], client["port"]),True)
        elif type == "handshake":
            if result["status"]:
                print("\n连接服务器成功")
            else:
                print("\n连接服务器失败")
        elif type == "resend":
            self.sendto(last_msg=True)
        elif type == "rc":
            try:
                # 收到客户端请求连接
                id = result["id"]
                name = result["name"]
                print("收到来自 %s（%s） 的连接请求" % (name, id))
                self.connect_client((result["address"], result["port"]))
            except:
                pass
        elif type == "client":
            try:
                if self.try_connect:
                    if self.client_addr:
                        time.sleep(2)
                        temp = {"type": "msg","name":self.name, "msg": "连接成功"}
                        self.sendto(json.dumps(temp), self.client_addr)

                self.try_connect = False
            except:
                print("连接失败")
        elif type == "msg":
            try:
                msg = result["msg"]
                if msg=='1':return
                print('\n%s：%s' % (result["name"],msg))
            except:
                pass
    def connect_client(self, addr,main=False):
        print("尝试连接 %s:%s" % addr)
        self.client_addr = addr
        temp_request_connect = request_connect
        temp_request_connect["name"] = name
        self.sendto(json.dumps(temp_request_connect), addr)



if __name__ == '__main__':
    name = input("请输入名字：")
    ser = MouseClient()
    ser.start()
    # 跟服务器握手
    ser.handshake()
    menu = input("1.主动连接\n2.等待连接")
    if menu == "1":
        id = input("1.请输入对方id：")
        ser.connect(id)
    else:
        # 创建tcp服务器
        print("本机ID：%s" % ser.id)
        print("请将id告知对方...")
        pass
    while True:
        msg = input("")
        temp = {"type": "msg", "name": name, "msg": msg}
        ser.sendto(json.dumps(temp), ser.client_addr)
