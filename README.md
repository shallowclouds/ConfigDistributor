# ConfigDistributor
### 概览(Overview)

a system to distribute configure files using Django and python.

### web管理界面(/manager)

此模块采用 Django 编写，用于提供该配置文件管理系统的 web api 以及 web 管理界面。

1. 运行环境
   * Linux 32 / 64
   * python 3.5+
   * Django库
2. 部署及使用说明
   * 使用 Docker 部署
   ```bash
    $ cd /path/to/src/manager
    $ sudo docker build -t config_distributor .
    $ sudo docker run -d --name config -p 0.0.0.0:80:80 config_distributor
   ```
   * 直接部署
3. 注意事项
   * 使用前请先编辑配置好配置文件

### 服务器端(/server)

此模块采用 python 编写，用于搭建分发管理配置文件的服务端，配置文件将通过此模块分发。

基于 pyuv 的跨平台异步非阻塞网络传输。

1. 运行环境
   - Linux 32/64
   - python 3.5 +
   - python 库 cryptography
2. 部署及使用说明
   - 使用 Docker 部署
    - 使用 Dockerfile 构建(working)
    ```bash
    $ cd path/to/src/manager
    $ docker build -t yorling/config:latest .
    $ docker run -p 0.0.0.0:80:80 yorling/config:latest -d 
    ```
   - 直接部署
3. 注意事项
   - 使用前请先编辑配置好配置文件
4. 单元测试
   - TODO

### 客户端(/agent)

此模块采用 python 编写，用于接收配置文件以及上传配置文件，该模块运行于需要进行配置文件分发的服务器节点上。

1. 运行环境
   - Linux 32/64
   - python 3.5 +
   - python cryptography
2. 部署及使用说明
   - TODO

3. 注意事项
   - 使用前请先编辑配置好配置文件
4. 单元测试
   - TODO
