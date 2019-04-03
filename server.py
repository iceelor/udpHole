# -*- coding:utf-8 -*-
import socket
import time
import threading
import json

buffer_size = 32 * 1024
bind_address = ('0.0.0.0', 9999)
socket_timeout = 1024
# 响应握手成功
handshake = {"type": "handshake", "status": True}
# 服务端返回id信息
connect = {"type": "connect", "data": {}}

request_connect = {"type":"rc","name":"","id":"","address":"","port":""}



class MouseServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.msg = ""
        self.client_list = []
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sk.settimeout(socket_timeout)
        self.last_msg = None
        # 监听端口
        self.sk.bind(bind_address)

    def run(self):
        self.flag = True
        while self.flag:
            addr = None
            try:
                buffer, addr = self.sk.recvfrom(buffer_size)
                data = str(buffer, encoding='utf-8')
                result = json.loads(data)
                result["address"] = addr[0]
                result["port"] = int(addr[1])
                self.data_analysis(result)
            except:
                pass
            finally:
                time.sleep(1)
    def check(self,addr):
        # 验证用户有效性
        for i in self.client_list:
            if (i["address"], i["port"]) == addr and time.time() - i["time"] < 300:
                return True
        return False
    def data_analysis(self, result):
        addr = (result["address"], result["port"])
        type = result["type"]
        temp_handshake = handshake
        if type == "handshake":
            try:
                temp = {}
                temp["id"] = result["id"]
                temp["name"] = result["name"]
                temp["address"] = result["address"]
                temp["port"] = result["port"]
                temp["time"] = time.time()
                self.client_list.append(temp)
                temp_handshake["status"] = True
            except:
                temp_handshake["status"] = False
            print("%s 设备 %s 连接%s id：%s" % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),result["name"],"成功" if temp_handshake["status"] else "失败",result["id"]))
            # 返回状态
            self.sendto(json.dumps(temp_handshake), addr)
        # 禁止未握手客户端继续操作
        elif self.check(addr):
            if type == "connect":
                temp_connect = connect
                temp_connect["data"] = {}
                # 客户端申请连接
                try:
                    # 检查用户是否过期
                    check = None
                    # 检查对方是否存在且未过期
                    exist = None
                    id = result["id"]
                    for i in self.client_list:
                        if i["id"] == id:
                            # 存在客户端
                            exist = i
                        # 验证当前用户有效性
                        if (i["address"],i["port"]) == addr and time.time()-i["time"]<300:
                            check = i
                    if check and exist:
                        # 通知对方，有人请求连接
                        temp_rc = request_connect
                        temp_rc["id"] = check["id"]
                        temp_rc["name"] = check["name"]
                        temp_rc["address"] = check["address"]
                        temp_rc["port"] = check["port"]
                        # 通知对方
                        self.sendto(json.dumps(temp_rc),(exist["address"],exist["port"]))
                        # 返回信息
                        temp_connect["data"] = exist
                        self.sendto(json.dumps(temp_connect),addr)
                except:
                    pass
            elif type == "resend":
                self.sendto(last_msg=True)
            # 清除超时的客户端
            for i in self.client_list:
                if time.time() - i["time"] >= 300:
                    self.client_list.remove(i)

    def sendto(self, msg="", addr=None,last_msg = False):
        try:
            if last_msg and self.last_msg:
                msg = self.last_msg[0]
                addr = self.last_msg[1]
            else:
                # 记录最后一条msg
                self.last_msg = (msg,addr)
            self.sk.sendto(bytes(msg, encoding='utf-8'), (addr[0], int(addr[1])))
            return True
        except:
            return False


if __name__ == '__main__':
    ms = MouseServer()
    ms.start()
    pass
