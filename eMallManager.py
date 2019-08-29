from models import Package
import socket


def main():
    upd_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip_port = ('127.0.0.1', 25365)
    
    instructions = ["/msg", "/opennewshop", "/enter", "/goods", "/customers", "/shops", "/users", "/closeshop", "/bye"]
    
    while True:  # 通信循环
        msg = input('请输入您的指令:')
        text = msg.split()
        try:
            assert text[0] in instructions
            if text[0] == "/bye":
                break
            msg = Package("header#" + text[0], 999, ",".join(text[1:]))
            upd_client.sendto(msg.send(), server_ip_port)  # 发送信息,信息量,服务端地址
            data, server_ip = upd_client.recvfrom(1024)  # 管理员不需要异步加载消息，防止管理员徇私舞弊
            text = Package(data.decode("utf-8"))
            for each in text.reply.split("\n"):
                print(each)
        except AssertionError:
            print("没有该类型的指令!")
            print("正确的指令有：", instructions)


if __name__ == "__main__":
    main()
