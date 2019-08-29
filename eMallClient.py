from models import Package
import socket
import threading
import time

# 全局变量 running 用于控制多线程的退出
running = [True]
upd_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_ip_port = ('127.0.0.1', 25365)
cookie = {
    "user_id": 0,
}


def receive():
    while running[0]:
        data, server_ip = upd_client.recvfrom(1024)  # 接收信息
        text = Package(data.decode("utf-8"))
        cookie["user_id"] = text.user_id
        if text.header == "reply":
            for each in text.reply.split("\n"):
                print(each)
        if text.header == "msg":
            print("您有一条新消息：", text.context)


def main():
    instructions = ["/login", "/shops", "/enter", "/goods", "/customers", "/buy", "/leave", "/addgoods", "/bye"]
    th0 = threading.Thread(target=receive)
    th0.start()
    
    while True:
        msg = input('请输入您的指令:')
        text = msg.split()
        try:
            assert text[0] in instructions
            if text[0] == "/bye":
                upd_client.sendto(Package("header#/bye").send(), server_ip_port)
                break
            msg = Package("header#" + text[0], cookie["user_id"], ",".join(text[1:]))
            upd_client.sendto(msg.send(), server_ip_port)
            time.sleep(0.2)
        except AssertionError:
            print("没有该类型的指令!")
            print("正确的指令有：", instructions)
    
    running[0] = False


if __name__ == "__main__":
    main()
