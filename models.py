class DictData(dict):
    """
    既支持键值访问，也支持用 `obj.attr` 方式进行访问的类
    """
    
    def __init__(self, **kwargs):
        super().__init__()
        for each in kwargs:
            self[each] = kwargs[each]
    
    def __getattr__(self, item):
        return self[item] if item in self.keys() else None
    
    def __setattr__(self, key, value):
        self[key] = value


class Package(DictData):
    """
    系统所需的 UDP 包的类
    """
    
    def __init__(self, package, user_id=-1, parm=""):
        super().__init__()
        package = package.split("$")
        for each in package:
            two = each.split("#")
            self[two[0]] = two[1]
        self["user_id"] = user_id
        self["parm"] = parm
    
    def __str__(self):
        ans = "header#%s" % self.header
        for key in self.keys():
            if key != "header":
                ans += "$%s#%s" % (key, self[key])
        return ans
    
    def send(self):
        return self.__str__().encode('utf-8')


class User(DictData):
    """
    用户类
    """
    
    def __init__(self, user_id, user_name):
        super().__init__(user_id=user_id, user_name=user_name, client_address="", at=user_id)


class Shop(DictData):
    """
    商店类
    """
    
    def __init__(self, owner_id, shop_name):
        super().__init__(owner_id=owner_id, shop_name=shop_name, customers=[], goods=[])


class Goods(DictData):
    """
    商品类
    """
    
    def __init__(self, goods_id, goods_name, owner_id, price):
        super().__init__(goods_id=goods_id, goods_name=goods_name, owner_id=owner_id, price=price)


def find_one(table, **kwargs):
    """
    在数据库的一张表中，找到满足限制条件 (kwargs) 的对象
    
    :param table: 数据库中的一张表
    :param kwargs: 限制条件
    :return: 找到的对象
    """
    for each in table:
        flag = True
        for key in kwargs:
            if each[key] != kwargs[key]:
                flag = False
        if flag:
            return each


class Database(DictData):
    """
    简易的数据库类
    """
    
    def __init__(self, version):
        super().__init__(version=version, users=[], shops=[], goods=[])
        
        if version == "Local":
            self.users = [User(999, "Admin"), User(1, "Wang"), User(2, "Jia"), User(3, "Yu")]
            self.shops = [Shop(1, "WangShop"), Shop(2, "JiaSupermarket")]
            self.goods = [Goods(1, "Pie", 1, 12), Goods(2, "Cake", 1, 16), Goods(3, "Pie", 2, 10),
                          Goods(4, "Cake", 2, 15), Goods(5, "Jam", 2, 7), Goods(6, "Coco", 2, 22)]
            shop1 = self.get_shop(owner_id=1)
            shop1.goods = [1, 2]
            shop1.customers = [2, 3]
            self.get_shop(owner_id=2).goods = [3, 4, 5, 6]
    
    def add_user(self, **kwargs):
        if 'user_id' not in kwargs:
            kwargs['user_id'] = len(self.users) + 1
        self.users.append(User(**kwargs))
        return self.users[-1]
    
    def add_shop(self, **kwargs):
        self.shops.append(Shop(**kwargs))
        return self.shops[-1]
    
    def add_goods(self, **kwargs):
        if 'goods_id' not in kwargs:
            kwargs['goods_id'] = len(self.goods) + 1
        self.goods.append(Goods(**kwargs))
        self.get_shop(owner_id=kwargs["owner_id"]).goods.append(len(self.goods))
        return self.goods[-1]
    
    def close_shop(self, owner_id):
        """
        关闭指定 id 用户的店铺

        :param owner_id:  店主的 id
        """
        for i in range(len(self.shops)):
            if self.shops[i].owner_id == owner_id:
                del self.shops[i]
                break
    
    def get_user(self, **kwargs):
        return find_one(self.users, **kwargs)
    
    def get_shop(self, **kwargs):
        return find_one(self.shops, **kwargs)
    
    def get_goods(self, **kwargs):
        return find_one(self.goods, **kwargs)
