# 分布式事务



## 项目概要

1. 使用二阶段提交及随机协调者的设计，保证事物一致性 
2. 使用时间戳排序协议实现乐观锁，提供系统并发能力并保证事务隔离性和原子性 
3. 解决分布式事务中存在的死锁问题，通过自动回滚事物实现死锁解除



## 项目描述

​	分布式事务这个项目实现了一个分布式事务系统，系统采用了二阶段提交+时间戳排序协议，实现了事务四大特性中的ACI。其中原子性和隔离性是通过实现时间戳排序实现的，隔离级别为read committed（读提交），一致性是在二阶段提交的第一阶段进行检查，如果违反一致性则会执行事务回滚操作。系统中有固定的5台服务器，分别代表5个分支，用户可以通过标明前缀的方式决定对象存储在哪台服务器中。用户的操作主要为BEGIN（开启事务），ABORT（中断并会滚事务），COMMIT（提交事务），DEPOSIT（账户存款），BALANCE（查询余额），WITHDRAW（提取余额）。同一事物可以对不同分支下的账户进行查询或修改，事物会在提交时判断事物执行的成功与否，如果该事物破坏了隔离性或一致性则会进行回滚。



## 相关知识点



### CAP定理

在分布式系统架构设计中，CAP三大特性只能最多满足其二。Consistency代表数据的一致性，指的是对所有节点查询同一变量时，返回值都是一样的。Availablility代表节点可用性，指的是所有节点能够正常相应接收到的请求。Partition Tolerance代表分区容错性，指的是系统出现网络分区的情况下还是否能够正常运作。    

**CA**：当满足一致性和可靠性时，系统中的每两节点之间都需要正常通信以更新存储变量的值，如果出现网络分区的情况则打破了正常通信的条件。

**CP**：当满足一致性和分区容错性时，如果产生网络分区的情况，由于系统需要维持一致性而不同分区之间又无法进行通信，因此只能将其中一个分区定义为可用状态，违反了可用性。

**AP**：当满足可用性和分区容错性时，出现网络分区时需要节点节点都为可用状态，但不同分区的节点不能互相通信，因此无法保证一致性。

在现实的分布式系统中，网络故障是常态，在这种情况下分区容错性几乎成为了一个必要特性。因此真实的分布式系统CAP特性通常会在C和A之间做取舍。

***Reference***：

1. https://courses.grainger.illinois.edu/ece428/sp2021//assets/slides/lect25-after.pdf



### 二阶段提交与三阶段提交

**二阶段提交**：

二阶段提交协议用于分布式事务的提交，其主要分为两个阶段，分别是投票阶段和决定阶段：

<img src="/Users/zhoushichen/Desktop/interview/Distributed-System/image/The-2-phase-commit-protocol.png" alt="The-2-phase-commit-protocol" style="zoom:50%;" />

1. 在投票阶段，协调者会给每一参与事务的服务器发送prepare信息，接收到prepare信息的服务器会根据内部的事务隔离规则和一致性检查决定事物是否能提交，并发送YES/NO信息回协调人。
2. 在决定阶段，协调者如果收到服务器的应答信息都为YES，则发送COMMIT信息，代表事物能够成功提交；否则协调者发送ABORT信息，表示投票阶段有服务器投了NO，代表事物需要回滚。服务器接收到COMMIT/ABORT后会在本地提交或者回滚信息，并发送ack应答信息回协调者，代表二阶段提交结束。

**应对协调者和服务器故障**：

1. 协调者需要持久化存储所有二阶段提交中的状态，例如收到的投票信息以及自己发送过的信息和做出的提交决定
2. 服务器需要持久化存储所有存储对象的暂定修改信息

**二阶段提交存在的问题**：

1. 在任何阶段，如果因服务器故障导致协调者没有收到正确数量的响应，或者协调者发生故障时，对应的事务提交的流程会被阻塞
2. 协调人发送COMMIT/ABORT信息后，如果有的服务器收到decision信息而有的服务器没收到时，会出现数据不一致

**三阶段提交**：

2PC最大的缺陷在于，当服务器接收到decision信息时不会去确认其于服务器是否也收到decision信息，而是直接根据decision信息作出相应的提交或回滚操作。这时如果协调者和已提交事物的服务器宕机，则无法判断事物最终的提交决定。剩余的服务器既不能悲观地回滚（因为可能某一宕机的服务器已经提交了），也不能乐观地提交（因为最终决定未知），导致永久阻塞。3PC就是为了解决这一问题而设计。

<img src="/Users/zhoushichen/Desktop/interview/Distributed-System/image/The-3-phase-commit-protocol.png" alt="The-3-phase-commit-protocol" style="zoom:50%;" />

三阶段提交的三个阶段分别是投票阶段、传播阶段、决定阶段：

1. 在投票阶段，协调者发送vote request信息给所有服务器，如果所有服务器都投YES，则进入传播阶段；如果有任意一个服务器投NO，则直接进入决定阶段进行回滚。
2. 在传播阶段，协调者会发送prepareToCommit（预提交）信息，服务器接收到预提交信息后会进入预提交状态，但不会立马执行提交操作
3. 在决定阶段，协调者会发送COMMIT/ABORT信息，服务器收到后会相应做出提交或回滚操作。此时即使协调者宕机，服务器也能在超时后自动提交或回滚（因为预提交阶段后服务器知道了其余服务器的最终决定）

***Reference***：

1. https://courses.grainger.illinois.edu/ece428/sp2021//assets/slides/lect22-after.pdf
2. https://www.the-paper-trail.org/post/2008-11-27-consensus-protocols-two-phase-commit/
3. https://www.the-paper-trail.org/post/2008-11-29-consensus-protocols-three-phase-commit/



### 乐观锁、悲观锁

乐观锁和悲观锁是两种不同的并发控制模型（并非真正的锁）

**乐观锁**：乐观锁会假设访问数据不会被修改，因此操作数据时不会给数据加锁，而是在之后判断操作冲突（例如提交时）。实现协议：时间戳排序

**悲观锁**：悲观锁会假设访问的数据总是会被修改，因此操作数据时会给数据加锁。实现协议：二阶段锁

***Reference***：

1. https://courses.grainger.illinois.edu/ece428/sp2021//assets/slides/lect19-after.pdf



### 时间戳排序协议（T/O）

T/O（时间戳排序）协议是乐观锁的一种实现。T/O协议是一种无锁的协议，它在读写操作时不会给对象加读写锁，并且从时间上后发起的事物不会等待先发事物结束，这一性质使得T/O协议默认不存在死锁的问题。T/O协议的隔离等级为read committed（因为事物每次做读操作都会读取最新提交的值，因此并不能做到repeatable read）

**读写冲突**：

T/O协议的读写冲突是通过协议中的读写规则判断并解决，如果出现序列冲突事物会默认自动中断并回滚。T/O协议为每个事物按时间顺序分配了一个id，id大的事物有更高的读写优先级。T/O协议保证了以下两点的正确性，假设有一条事物T和对象O：

1. **write限制**：T的id必须大于等于所有其余对O进行过读或写操作的事物id
2. **read限制**：T的id必须大于上次写入并提交O的事物id

**存储对象维护的变量**：

1. **提交值**：对象的最新值
2. **提交id**：最新提交和修改了对象的事物id
3. **读id列表（Read timestamp list）**：存储所有进行过读操作的事物id的列表（提交或回滚过的事物id会被抛出）
4. **暂定写列表（Tentative write list）**：存储所有进行过写操作的（事物id，value）元组的列表（提交或回滚过的元素会被抛出）

**读写规则**：

<img src="/Users/zhoushichen/Desktop/interview/Distributed-System/image/t:o read rule.png" alt="t:o read rule" style="zoom:30%;"/>

<img src="/Users/zhoushichen/Desktop/interview/Distributed-System/image/t:o write rule.png" alt="t:o write rule" style="zoom:30%;" />

**T/O协议的缺陷**：

1. 当对象存储的值非常占空间时，维护RW列表的开销非常大
2. 运行时间久的事物更容易被中断回滚，因为读到后发起的事物的提交值的概率增加了

***Reference***：

1. https://courses.grainger.illinois.edu/ece428/sp2021//assets/slides/lect19-after.pdf



### Innodb事物隔离级别

Innodb有四种隔离级别，隔离级别越高代表隔离性越好，并行性越差，四种隔离级别分别为：

<img src="/Users/zhoushichen/Desktop/interview/Database-System/Image/isolation level.webp" alt="isolation level" style="zoom:70%;" />

1. Read uncommitted：事物会读到未提交的值
2. Read committed：事物只能读已提交的值，解决脏读
3. Repeatable read：事物多次读同一对象值的结果相同，解决不可重复读（mvcc+间隙锁也能解决幻读）
4. Serializable：序列化执行事物，解决幻读



### Innodb事物实现

Innodb实现事务需要保证ACID特性的正确性，事务实现主要从这四个特性出发并逐一解决

**Atomicity原子性**：Innodb的原子性是通过undo log实现的，客户端输入修改数据的sql语句时，undo log会生成一个对应的回退语句（如insert对应delete）。如果事务违反了其他特性约束并需要回滚时，undo log中的sql语句会被执行，用于回滚操作。

**Consistency一致性**：一致性的实现不需要特殊机制保障，只要数据状态在合法的约束范围内（如银行账号余额不能小于0），并保证剩余的AID特性即可。

**Durability持久性**：Innodb的持久性是通过redo log实现的，用于应对数据写入磁盘前发生故障断电而导致的数据丢失情况。redo log分为两部分，分别是redo log buffer（存在于RAM中）和redo log（存在于disk中）。客户端每执行一条事务的sql语句，redo log buffer就会相应地将sql语句写入。在客户端commit事务时，redo log buffer会把数据写入磁盘中的redo log持久化保存，这一操作保证了事务提交后便永久保存。假设数据在被写入磁盘之前数据库发生故障，也不用担心数据丢失，因为当数据库恢复正常后可以通过重新写入redo log中的数据保证持久性

<img src="/Users/zhoushichen/Desktop/interview/Database-System/Image/redo log.png" alt="redo log" style="zoom:75%;" />

**Isolation隔离性**：Innodb的隔离性被划分为了四个等级，分别为read uncommitted、read committed、repeatable read、serializable。Innodb采取的协议为2PL + MVCC，隔离性的实现需要根据这四个等级分类讨论：

1. read uncommitted：读未提交等级下读写不加锁，允许读到最新纪录
2. read committed：读提交等级下写加锁，读不加锁。读取数据会通过MVCC机制找到可用的快照并进行读取
3. repeatable read：重复读等级下同样写加锁，读不加锁。读取数据通过MVCC找到可用快照读取，并且Innodb实现的重复读等级下加入了next-key lock机制，防止了幻读发生。
4. serializable：序列化等级的实现与原始2PL协议基本相同，只有读读不阻塞，读写、写读、写写均阻塞。

***Reference：***

1. https://draveness.me/mysql-transaction/
2. https://github.com/CyC2018/CS-Notes/blob/master/notes/%E6%95%B0%E6%8D%AE%E5%BA%93%E7%B3%BB%E7%BB%9F%E5%8E%9F%E7%90%86.md#%E4%BA%94%E5%A4%9A%E7%89%88%E6%9C%AC%E5%B9%B6%E5%8F%91%E6%8E%A7%E5%88%B6
3. https://cloud.tencent.com/developer/article/1431307



### 死锁

死锁是一种由于进程占有资源并等待其余进程释放所申请资源时而造成的永久阻塞问题。**死锁的产生有四个必要条件**，分别是：

1. 占有并等待：进程在占有资源时可以申请并等待其他资源
2. 互斥：单一资源仅可被一个进程所占有，不能出现多个进程占有同一资源的情况
3. 非抢占式：进程不能抢占其它进程的资源，资源必须由进程主动释放
4. 循环等待：在进程资源请求的有向图中出现了环

**处理死锁的方法**：

1. **无视死锁**：又称鸵鸟算法，当死锁产生概率非常小时并且处理死锁所需开销非常大时，可以直接采取无视死锁的方法
2. **死锁检测**：死锁检测允许死锁的发生，并在死锁发生后通过强制进程释放资源的方式解决死锁。
3. **死锁预防**：死锁预防通过防止死锁的四个必要条件的满足，解决死锁问题

***Reference***：

https://cs241.cs.illinois.edu/coursebook/Deadlock#approaches-to-solving-livelock-and-deadlock





# Raft共识算法



## 项目概要

1. 使用Go语言实现Raft算法，实现集群节点状态的一致性 
2. 使用goroutine和channel完成线程同步，实现Raft领袖选举算法 
3. 实现Raft日志同步，并增加快速回退机制加快不一致日志的覆盖速率



## 项目描述







## 相关知识点

### 进程、线程、协程

### GMP调度模型

### Golang垃圾回收

### RPC

### 日志一致性算法（Paxos、Raft）

### **一致性哈希**





# 中间人攻击



## 项目概要

1. 伪造ARP协议响应，使主机成为中间人以进行报文传输监控及信息篡改 
2. 通过修改TCP传输报文中的序列号、应答号及校验和等头部信息，实现信息的篡改 
3. 使用Wireshark监控主机之间的TCP包传输



## 项目描述

​	中间人攻击项目实现了在虚拟的局域网中的中间人攻击。项目通过ARP欺骗是主机成为客户端和服务器之间的中间人，并在后续监控并篡改客户端接收到的HTTP信息。项目中给定的场景局域网中有三台主机，分别为攻击人主机、Web服务器、客户端，并且Web服务器和客户端默认不知道对方的MAC地址。在启动模拟场景的局域网时，Web服务器和客户端会给局域网下的所有主机发送ARP广播并试图获取Web服务器的MAC地址，这时我们作为攻击人则会不断地给两台目标主机发送ARP响应信息。当Web服务器和客户端收到ARP响应后，以为是收到了对方正确的IP-MAC地址映射，并存入本地缓存中。这一操作导致后续Web服务器和客户端之间的通信信息实际上都发送给了攻击人。攻击人此时就对双方的信息有高度的掌握，并可以随意地监控或篡改。   

​	由于服务器和客户端之间的传输使用了HTTP/TCP/IP的网络协议栈，因此为了保证信息正确到达接收端，在项目中我们还对HTTP（content-length）、TCP（seq、ack、checksum）、IP（total length、checksum）的头部信息进行了修改。



## 相关知识点

### TCP/UDP

***Reference***：

​	1.https://zhuanlan.zhihu.com/p/108822858



### ARP欺骗

​	ARP协议被用作获取目标主机的IP-MAC映射。当主机A已知主机B的IP地址并且想获取主机B的MAC地址时，会给局域网内的所有主机发送ARP请求广播。这时主机B接收到了ARP请求，并判断请求中的目标IP地址是自身的IP地址时，会给主机A发送ARP响应并在信息中包含了自己的MAC地址。主机A接收到主机B的信息后，会将主机B的IP-MAC映射存入本地的ARP缓存，并在过期前使用缓存中的IP-MAC地址进行通讯。

​	由于ARP请求是以广播的形式发送并且局域网内所有主机都会接受到ARP请求，攻击人可以借此机会伪造一份ARP响应并污染主机A的ARP缓存。此时主机A发送给主机B的所有信息都可能被监控并篡改，信息安全受到严重危害。主流的ARP伪造方法有两种：

1. 攻击人可以在接收到ARP请求以后再发送伪造响应。这种方式更加隐蔽，但是成功率大大降低，因为ARP请求在到达攻击人主机之前就可能接收到了正确的响应，请求主机也会相应的更新ARP缓存。
2. 攻击人也可以持续无脑地广播伪造响应。这种方式隐蔽性差，并且网络资源利用率高，但是成功率高，ARP请求在被发送后很短时间内就会接到伪造的响应。

***Reference***:

	1. https://www.varonis.com/blog/arp-poisoning/



### HTTPS



### 加密算法

