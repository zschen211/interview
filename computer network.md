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
都是有用的

**长连接**：Client和Server通信完毕后，不会立刻关闭TCP连接，好处是连接可以复用，并减去了创建TCP
连接的时间
(滥用长连接会导致Server的压力越来越大，因此需要特殊的机制关闭闲置的TCP连接，避免Server压力
过大的问题)



### **6. TCP拆包、粘包及解决办法**

**为什么TCP有拆包粘包而UDP没有：**
UDP是面向报文并有消息边界的，而TCP是面向字节流且无边界的，因此TCP传输的字节流需要经过缓冲区
进行组装和拆分（Nagle算法，避免发送太小的数据包影响网络IO性能）

**拆包**：发送数据大于TCP缓冲区剩余空间大小（MSS：maximum segment size)，导致单个数据包拆成两次传输
**粘包**：发送数据小于TCP缓冲区剩余空间大小，TCP将写入的多个数据粘成一个发送

**粘包拆包解决方法：**
固定消息长度，每个数据包都封装为固定长度（末尾不够可以靠padding 0填充）
设置消息边界，在数据包结尾添加符号分割（如回车符）
在消息头部指定数据长度，这样接收方在读取时便知道完整数据包的长度



### **7. TCP如何保证可靠传输**

**a. 校验和**：接收方会对数据进行校验和计算并与发送发的校验和进行比对，如果不一致则表示信息传输有误。这一
步是为了保证传输的信息没有损毁

**b. 三次握手建立连接**：TCP在消息传递前会通过三次握手建立连接，保证消息传输通道的可靠性

**c. ack应答机制和seq序列号**：TCP的seq对数据中的字节进行了编号，数据的接收方会通过检验seq值并发送ACK
信息，告诉发送方自己接收了多少数据并提示发送方下次数据应该从哪个序号开始发。用seq排序可以避免数据
漏传并避免接收重复数据。

**d. 超时重传**：发送方如果在一段时间内没有收到接受方的应答消息，会重新传输数据。TCP协议会根据
RTT（round-trip time）动态计算超时重传的timeout值（RTO：retransmission time-out）

**e. 流量控制**：如果接收方的缓冲区空间不够，而同时发送方持续不断的发送消息，则会导致多条信息丢包，并导致
后续的一系列超时重传。因此TCP利用滑动窗口对信息传输进行了流量控制。

<img src="/Users/zhoushichen/Desktop/面试基础知识/image/tcp flow control.jpeg" alt="alt text" style="zoom:100%;" align="left"/>

接收方在发送ACK信息的时候，会在头部Window size字段指定窗口的大小，窗口的大小又发送方的缓冲区大小
及接收方的缓冲区大小决定，窗口大小越大表示发送方下次能传输的消息大小越大。这一设计使得接收方能根据
自己缓冲区剩余空间大小决定信息传输的速度，实现流量控制。当窗口大小为0的时候，发送方不能正常发送新的
数据，这时发送方会发送窗口探测消息，让接受方应答以获取最新的窗口大小

**f. 拥塞控制**：TCP拥塞控制的目的是在避免拥塞的前提下，使数据尽可能快地传输。这一机制既保证了传输的可靠性
也维护了传输的高效性。

<img src="/Users/zhoushichen/Desktop/面试基础知识/image/tcp congestion control.jpeg" alt="alt text" style="zoom:80%;" align="left"/>

**当服务器收到ACK时**：
持续收到ACK意味着传输通道是通畅的，这时cwnd（congested window）应该增大以更大程度地利用网络资源，
cwnd的增长主要分为两种模式：**慢开始**和**拥塞避免**
**慢启动**：慢开始阶段的开始cwnd等于1，接着cwnd值会呈指数增长，直到cwnd >= ssthresh（slow start threshold）
**拥塞避免**：在拥塞避免阶段，cwnd的大小呈线性增长，增长会持续到出现超时

**当服务器未收到ACK时（RTO超时）**：
服务器未收到ACK信息意味着传输出现了拥塞，这时需要将拥塞模式回调成慢开始，cwnd设置成1，并将ssthresh
值设置成原来的一半

**TCP Reno**：
TCP Reno是TCP算法实现的一个版本，在TCP Reno版本中有**快重传**和**快启动**的设计，帮助TCP进一步提升网络资源
利用率
**快重传&快恢复**：当发送方收到3个重复ACK消息时，说明ACK对应的数据丢包或是乱序抵达了，Reno算法在这一
场景下会假设ACK对应的数据丢包，重新传输ACK对应的数据包并进入快恢复阶段。快恢复阶段下，算法会将ssthresh
和cwnd设置为当前cwnd的1/2，跳过慢启动，直接进入拥塞避免阶段。跳过慢启动阶段的原因是如果将cwnd重置为1，
会需要很长时间让发送率回到合适的状态，降低了网络资源的利用率。而跳过慢启动则优化了对网络资源的利用。



### **8. 提升网络利用率**

**a. Nagle算法**：Nagle算法通过减少消息的发送量来提升网络利用率

<img src="/Users/zhoushichen/Desktop/面试基础知识/image/nagle algorithm.png" alt="alt text" style="zoom:50%;" align="left"/>

Nagle算法处理了发送包太小的问题，这一算法会将多个体积小的包重组成一个较大的包并一次性发送出去

**b. 延时ACK**：延时ACK机制使得ACK信息会延迟200-500ms发送，延时可能使得多个ACK可以被合成一个ACK发送并
进行一次性应答，从而减少ACK信息的数量并提升网络利用率

**c. 捎带ACK**：捎带ACK机制使得data和ACK信息合成同一个消息一次性传输，提升网络利用率









