# socket-eMall

这是大二计算机网络的课程项目，使用 Python 标准包编写的 UDP 通信系统。
整个项目比较简单，主要的亮点是编写了方便操作的 DictData 类，使 models 的编写更简洁。

## 设计文档

本次项目全部用 Python3 完成，使用了 Python 内置的 socket 和 socketserver 包进行开发。

项目分为四个文件：

+ models.py 为项目所需的各种数据类
+ server.py 为 socket 信息交换服务器
+ eMallManager.py 为管理员使用程序
+ eMallClient.py 为普通用户使用的程序

交互方式为命令行交互，具体的操作方式见 [用户手册](./用户手册.md)

### models.py

我在 models.py 里面设计 DictData 基础类，它继承了 Python 内置的字典，
但也支持用 `obj.attr` 的方式进行访问，给后续开发提供了方便。我以DictData为基类设计了如下几个类：

+ User 用户类
+ Shop 商店类
+ Goods 商品类
+ Database 手写的数据库类
+ Package 本系统中所需的 UDP 包类

### server.py

服务器端，我设计了应答类 Handler，利用多线程异步应答消息

### eMallManager.py

为了防止管理员上班期间以权谋私，我设计这个程序只能在每次发送消息给 server 后获取消息，与普通用户程序区分。

### eMallClient.py

一般用户作为卖家会收到一些额外的消息，所以我建立了一个 receive 线程用来接收消息，同时主线程负责输入和给 server 发送操作命令。