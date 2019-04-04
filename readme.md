


# 使用
在一台有公网IP的服务器上运行server.py

修改client.py中的ip为服务器上的IP
在客户端运行client.py

成功率感人，可能是代码写的不行，问题很多...

# 1.0准备做端口转发，然而bind在使用的端口会报错，放弃。。。
# 2.0为群聊，测试结果如下：
* 对象：树莓派、手机、电脑
* 网络环境：树莓派（家里电信宽带，要了公网IP）、手机为4G、电脑（公司电信宽带，公司有没有做什么限制不清楚）
## 结果：

* 树莓派能接另外两个设备的消息，发消息只有电脑能接到
* 手机发只能发消息，不能接消息
* 电脑能接到树莓派的消息，接不到手机的新消息
# 打洞关键点：
* 公网服务器负责交换A、B设备的地址信息
* A、B接到对方的信息后最好同时（间隔越短越容易成功）向对方发送点东西(发送的可能两边都接不到，可能只有一边能接到)。然后尝试互发信息

