# -*- coding:utf-8 -*-
import time
import socket
import json
import threading
import base64
import traceback
import copy


buffer_size = 64 * 1024
bind_address = ('0.0.0.0', 9999)
socket_timeout = 4096
client_list = {}
blacklist = []
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(socket_timeout)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(bind_address)

lock = threading.Lock()

class Timer(threading.Thread):
    """
        定时器
    """

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global client_list,lock
        while True:
            try:
                lock.acquire()
                for i in client_list:
                    if time.time() - client_list[i]["time"] >= 600:
                        client_list.pop(i)
                    # 获取客户端列表,排除自身
                    temp_client_list = copy.deepcopy(client_list)
                    temp_client_list.pop(i)
                    result = {"t": "list", "data": temp_client_list}
                    WriteJSON(result, (client_list[i]["address"],client_list[i]["port"]))
            except Exception as e:
                traceback.print_exc()
            finally:
                lock.release()
            time.sleep(10)

def WriteJSON(js, addr):
    try:
        s.sendto(bytes(json.dumps(js), encoding="utf-8"), addr)
    except:
        pass
def Write(js, addr):
    try:
        s.sendto(bytes(js, encoding="utf-8"), addr)
    except:
        pass

def get_id(addr):
    """
        加密地址作为id
    :param addr:
    :return:
    """
    temp = bytes(addr[0] + ":" + str(addr[1]), encoding="utf-8")
    return str(base64.encodebytes(temp), encoding="utf-8").replace("\n","")


class Read(threading.Thread):
    """
        读取
    """

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global s,client_list,blacklist,buffer_size,lock
        try:
            while True:
                try:
                    try:
                        buf, addr = s.recvfrom(buffer_size)
                    except:
                        continue
                    # 黑名单检测
                    # if addr[0] in blacklist:
                    #     print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), addr,"加入黑名单")
                    #     continue
                    id = get_id(addr)
                    lock.acquire()
                    # 心跳包
                    if b'1' == buf:
                        if id in client_list:
                            # 检查更新速度
                            # if time.time() - client_list[id]["time"] <= 30:
                            #     # 加入黑名单
                            #     blacklist.append(addr[0])
                            # else:
                            # 更新时间
                            client_list[id]["time"] = time.time()
                        else:
                            # 加入客户端列表,name默认为id
                            client_list[id] = {"name": id, "address": addr[0], "port": addr[1], "time": time.time()}
                            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), addr, "注册成功")
                            result = {"t": "id", "d": id}
                            WriteJSON(result, addr)
                        # 回应
                        Write('1',addr)
                        continue
                    try:
                        # 其它消息一律按json处理，非json格式直接忽略
                        data = json.loads(str(buf,encoding="utf-8"))
                        # 根据t（type）来区分请求类型
                        t = data["t"]
                        if "n" == t:
                            # 客户端更新name
                            client_list[id]["name"] = data["n"]
                            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), addr, "更新昵称")
                    except Exception as e:
                        traceback.print_exc()
                except Exception as e:
                    traceback.print_exc()
                finally:
                    lock.release()
        except Exception as e:
            traceback.print_exc()
        finally:
            s.close()

if __name__ == "__main__":
    timer = Timer()
    timer.start()
    read = Read()
    read.start()