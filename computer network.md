### **1. TCP和UDP的特点和区别**

a. TCP是面向连接的，而UDP是无连接的
b. TCP是面向字节流的，而UDP是面向报文的（TCP的消息传输是以字节为单位，而UDP是以报文为单位）
c. TCP保证了可靠传输，而UDP是尽最大努力传输
d. TCP只支持一对一传输，而UDP支持广播（一对一、一对多、多对一、多对多）
e. TCP传输的开销更大且速度较慢， 而UDP传输开销小且速度快



### **2. TCP和UDP的头部格式**

TCP Header（20到60字节）

<img src="/Users/zhoushichen/Desktop/面试基础知识/image/tcp header.png" alt="alt text" style="zoom:65%;" align="left"/>

UDP Header（8字节）

<img src="/Users/zhoushichen/Desktop/面试基础知识/image/udp header.gif" alt="alt text" style="zoom:67%;" align="left"/>



### **3. TCP 三次握手**

<img src="/Users/zhoushichen/Desktop/面试基础知识/image/tcp 3way handshake.jpeg" alt="alt text" style="zoom:67%;" align="left"/>

**SYN**：客户端发起TCP连接请求，将SYN bit设置成1，选择初始序列号 seq = x，将消息发送给服务器
**SYN-ACK**：服务器收到SYN请求（服务器确认客户端的发送能力正常），将SYN bit和ACK bit设置成1，
选择初始序列号 seq = y，并设置确认值 ack = x + 1，将SYN-ACK信息发送给客户端 
**ACK**：客户端收到SYN-ACK（客户端确认双方的发送和接受能力正常），将ACK bit设置成1，将序列号
和确认值设置为 seq = x + 1，ack = y + 1，将ACK信息发送给服务器。服务器收到ACK信息（服务器
确认双方的发送和接收能力正常）

（为什么TCP至少要三次握手？因为至少需要三次消息传递才能让双方都确认对方和自己的收发能力正常）



### **4. TCP四次挥手**

<img src="/Users/zhoushichen/Desktop/面试基础知识/image/tcp 4way handwave.jpeg" alt="alt text" style="zoom:67%;" align="left"/>

**为什么TCP挥手需要4次：**
当一台主机准备断开TCP连接并发起FIN消息时，另一台主机仍可能有消息没传递完，因此接收方需要在
结束所有消息的发送后，主动发起第二条FIN信息以结束TCP连接

**客户端收到FIN后为什么要等待 2MSL (max segment lifetime) :**
客户端需要确保服务器接收到了发送的最后一个ACK信息。如果服务器没有收到ACK信息，会重传FIN，
导致客户端TCP关闭连接异常
其次，等待2MSL同时确保了本次TCP连接从网络中消失，使下次TCP连接中不会出现旧的TCP连接中的
报文
(选择2 * MSL是因为如果服务器没有收到ACK信息的话，服务器重传的FIN消息会在客户端传送ACK消息
后最迟2 * MSL时间后抵达客户端)



### **5. TCP长连接和短连接**

**短连接**：每次通信都创建一个TCP连接，并在通信结束后关闭连接，好处是方便管理，建立的每次连接
都是有用的，
**长连接**：Client和Server通信完毕后，不会立刻关闭TCP连接，好处是连接可以复用，并减去了创建TCP
连接的时间
(滥用长连接会导致Server的压力越来越大，因此需要特殊的机制关闭闲置的TCP连接，避免Server压力
过大的问题)