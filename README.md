# Batch quick setup for Linux

#### 应用场景：

在批量克隆虚拟机后，批量设置网卡、修改用户密码、设置主机名等操作。

#### 工作原理

使用 `paramiko` 模块连接 ssh 进行修改

#### 工作环境

+ 任意python 3.6+（代码编写于3.7.9）
+ `pip install paramiko`



#### 使用说明

当前兼容发行版：

[x] Centos 7

##### 参数说明

使用命令行传参，参数列表如下：

|      参数      |                             说明                             |    默认值     |
| :------------: | :----------------------------------------------------------: | :-----------: |
|   -h, --help   |                     帮助页，显示参数列表                     |               |
| -e, --example  |                   生成样例列表（功能见下）                   |               |
|  -l, --list=   |              \*操作列表，必填，用于确定工作内容              |               |
|  -u, --user=   |                  ssh用户，建议使用默认root                   |     root      |
| -r, --rsa-key= |                  ssh私钥路径，默认使用私钥                   | ~/.ssh/id_rsa |
| -p, --passwd=  | ssh用户密码，默认不使用<br />当密码与密钥同时显式指定时，使用密码 |               |

使用样例：

```shell
python main.py -h
python main.py --example
python main.py -l ./example.csv --passwd=123456
```

##### CSV详细说明

csv文件用于指定具体操作内容，使用 UTF-8 编码

至少一行，两列：

第一行为表头，第一列为目标主机当前IP地址，[0,0]位置必然为"HOST"

每一列代表一个操作类型，字段名为操作类型

多个同名字段，靠后者生效

|          |  字段名   |            字段内容            |
| :------: | :-------: | :----------------------------: |
| 目标主机 |   HOST    |         目标主机当前IP         |
|   网卡   | bootproto |   网卡工作模式,如static,dhcp   |
|    ..    |  ipaddr   |           静态IP地址           |
|    ..    |  netmask  |              掩码              |
|    ..    |  gateway  |              网关              |
|    ..    | dns1,dns2 |              DNS               |
|   密码   |  passwd   | 重置用户名密码，格式特殊，见下 |
|  主机名  | hostname  |             主机名             |

> 密码字段：
>
> 密码字段为一个“以空格分割的字符串”，有且只有一个空格
>
> 如：“root 12345”即将root用户的密码设为12345
>
> 不同用户的字段互不干扰，同用户字段靠后者生效。

样例:

假设当前虚拟机在10.10.21.34，root密码123456，需对其执行以下操作：

+ 静态IP 10.10.20.100，掩码 255.255.0.0，网关10.10.20.254，DNS1 114.114.114.114
+ 设置root密码为root
+ 设置user1密码为123456
+ 设置主机名为host1

example.csv如下（严格控制空格，注意区分逗号和点号）

```
HOST,bootproto,ipaddr,netmask,gateway,dns1,passwd,passwd,hostname
10.10.21.34,static,10.10.20.100,255.255.0.0,10.10.20.254,114.114.114.114,root root, user1 123456,host1
```

执行命令

```
python main.py -l example.csv -p 123456
```



#### 二次开发

##### 文件结构

+ os_exec
  + \__init__.py：检测系统类型，自动选择执行器
  + linux.py：基类，虚基础执行器，提供通用方法如set_passwd
  + centos.py：Centos7执行器

+ main.py：主入口

##### 操作系统发行版检测

> 不同的发行版甚至不同版本会使用不同的网卡控制方式

读取 `/etc/os-release` 文件中的 `NAME` 字段和 `VERSION_ID` 字段

+ Centos like "Centos Linux 7"
+ Ubuntu like "Ubuntu 20.04"

##### 新增发行版兼容

继承 `os_exec.linux.Linux` 派生新类，

并在 `os_exec.\__init__.get_exec_for_os()` 中添加识别

##### 新增字段

修改 `os_exec` 内代码，

LinuxABC类用于字段解析，所有字段在此类中均需有虚方法。

通用字段写于 Linux 类中。
