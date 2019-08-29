from socketserver import BaseRequestHandler, ThreadingUDPServer
from models import Database, Package
import socket


db = Database("Local")
upd_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_ip_port = ('127.0.0.1', 25365)


class Handler(BaseRequestHandler):
    """
    用于处理各种请求的类，主要实现了各种业务逻辑的细节
    """
    
    def handle(self):
        print(db)
        data = self.request[0]
        ans = Package("header#reply")
        reply = ""
        try:
            msg = Package(data.decode('utf-8'))
            header = msg.header
            parm = msg.parm.strip().split(",")
            user = db.get_user(user_id=int(msg.user_id))
            print(msg)
            print(header)
            if header == "/bye":
                reply += "Bye~"
            elif header == "/login":
                assert parm[0]
                user = db.get_user(user_name=parm[0])
                if user is None:
                    user = db.add_user(user_name=parm[0])
                reply += "您的ID为"+str(user.user_id)
                msg.user_id = user.user_id
                user.client_address = self.client_address
            elif header == "/shops":
                reply += "有以下店铺：\n"
                for each in db.shops:
                    reply += "店主:{0} 店名:{1} \n".format(each.owner_id, each.shop_name)
            elif header == "/enter":
                assert parm[0]
                shop = db.get_shop(shop_name=parm[0])
                if shop is None:
                    reply += "进店失败!"
                else:
                    shop.customers.append(user.user_id)
                    user.at = shop.owner_id
                    reply += "进店成功!"
                    # 服务器为其发送该商店的商品信息
                    reply += "该商店的商品有\n"
                    for each in shop.goods:
                        goods = db.get_goods(goods_id=int(each))
                        reply += "{0} ({1}) 单件{2}\n".format(goods.goods_name, goods.goods_id, goods.price)
                    try:
                        # 并将该信息发送给商家
                        msg1 = Package("header#msg")
                        msg1.context = "用户{0}访问了你的店铺".format(user.user_name)
                        user = db.get_user(user_id=shop.owner_id)
                        self.request[1].sendto(msg1.send(), user.client_address)
                    except:
                        pass
            elif header == "/goods":
                shop = db.get_shop(owner_id=user.at)
                if shop is None:
                    reply += "您不在任何商店中"
                else:
                    # 列出所进去的虚拟商店中的商品的情况，包括商品ID，商品名称，单价。
                    reply += "该商店的商品有\n"
                    for each in shop.goods:
                        goods = db.get_goods(goods_id=int(each))
                        reply += "{0} ({1}) 单件{2}\n".format(goods.goods_name,goods.goods_id,goods.price)
            elif header == "/customers":
                shop = db.get_shop(owner_id=user.at)
                if shop is None:
                    reply += "您不在任何商店中"
                else:
                    reply += "该商店中的顾客有\n"
                    for each in shop.customers:
                        reply += db.get_user(user_id=int(each)).user_name + "\n"
            elif header == "/buy":
                assert parm[0]
                goods = db.get_goods(goods_id=int(parm[0]))
                try:
                    msg1 = Package("header#msg")
                    msg1.context = "用户{0}想购买你的商品{1}".format(user.user_name,goods.goods_name)
                    user = db.get_user(user_id=goods.owner_id)
                    # 并将该信息发送给商家
                    self.request[1].sendto(msg1.send(), user.client_address)
                except:
                    pass
                reply += "已发送购买请求"
            elif header == "/leave":
                shop = db.get_shop(owner_id=user.at)
                if shop is None or user.at == user.user_id:
                    reply += "您不在任何商店中"
                else:
                    reply += "已成功离店"
                    user.at = user.user_id
            elif header == "/addgoods":
                assert parm[0] and parm[1]
                shop = db.get_shop(owner_id=user.user_id)
                if shop is None:
                    reply += "您还没有拥有一家店"
                else:
                    db.add_goods(goods_name=parm[0], price=int(parm[1]), owner_id=user.user_id)
                    reply += "商品添加成功"
                    msg1 = Package("header#msg$context#您正在逛的商店有商品添加")
                    try:
                        # 并将该信息发送给正在他店里“逛”的顾客
                        for each in shop.customers:
                            user = db.get_user(user_id=each)
                            self.request[1].sendto(msg1.send(), user.client_address)
                    except:
                        pass
            elif header == "/msg":
                assert parm[0]
                if user is None or user.user_id != 999:
                    reply += "您没有该权限"
                else:
                    assert parm
                    reply += "消息发送成功!"
                    msg1 = Package("header#msg$context#"+parm[0])
                    try:
                        # 群发和向指定的用户发送消息，用以发送某些提示
                        for each in parm[1:]:
                            user = db.get_user(user_id=int(each))
                            assert user.client_address
                            self.request[1].sendto(msg1.send(), user.client_address)
                    except:
                        pass
            elif header == "/opennewshop":
                if user is None or user.user_id != 999:
                    reply += "您没有该权限"
                else:
                    shop = db.get_shop(owner_id=user.user_id)
                    if shop is not None:
                        reply += "该用户已有商店"
                    assert parm[0] and parm[1]
                    db.add_shop(shop_name=parm[0], owner_id=int(parm[1]))
                    user = db.get_user(user_id=int(parm[1]))
                    reply += "已开启店铺"
                    try:
                        # 为某个用户开通一个新的虚拟商店并通知用户
                        msg1 = Package("header#msg")
                        msg1.context = "您的店已开启"
                        self.request[1].sendto(msg1.send(), user.client_address)
                    except:
                        pass
            elif header == "/closeshop":
                if user is None or user.user_id != 999:
                    reply += "您没有该权限"
                else:
                    assert parm[0]
                    shop = db.get_shop(shop_name=parm[0])
                    if shop is None:
                        reply += "不存在叫这个名字的店"
                    else:
                        user = db.get_user(user_id=shop.owner_id)
                        try:
                            # 关闭某一虚拟商城，并通知虚拟商店的拥有者和正在逛的人
                            msg1 = Package("header#msg")
                            msg1.context = "您的店已被关闭"
                            self.request[1].sendto(msg1.send(), user.client_address)
                            for each in shop.customers:
                                user = db.get_user(user_id=int(each))
                                msg2 = Package("header#msg")
                                msg2.context = "当前店铺已被关闭"
                                self.request[1].sendto(msg2.send(), user.client_address)
                        except:
                            pass
                        db.close_shop(shop.owner_id)
                        reply += "已关闭此店"
            elif header == "/users":
                if user is None or user.user_id != 999:
                    reply += "您没有该权限"
                else:
                    reply += "有以下用户\n"
                    print(db.users)
                    for each in db.users:
                        a = "用户ID: {0} 用户名: {1} \n".format(each.user_id, each.user_name)
                        reply += a
                        print(reply)
        except AssertionError:
            reply += "指令参数错误！"
        ans.reply = reply
        self.request[1].sendto(ans.send(), self.client_address)


if __name__ == '__main__':
    print("Data Version:", db["version"])
    print(db)
    server = ThreadingUDPServer(('0.0.0.0', 25365), Handler)  # 参数为监听地址和已建立连接的处理类
    print('listening')
    server.serve_forever()   # 监听，建立好UCP连接后，为该连接创建新的socket和线程，并由处理类中的handle方法处理
    print(server)
