# ConfigDistributor
a system to distribute configure files using Django and python.

### web管理界面(/manager)

此模块采用 Django 编写，用于提供该配置文件管理系统的 web api 以及 web 管理界面。

1. 运行环境
   * Linux 32 / 64
   * python 3.5+
   * Django库
2. 部署及使用说明
3. 注意事项
4. 单元测试

### 服务器端(/server)

此模块采用python编写，用于搭建分发管理配置文件的服务端，配置文件将通过此模块分发。

1. 运行环境
   - Linux 32/64
   - python 3.5+
2. 部署及使用说明
3. 注意事项
4. 单元测试

### 客户端(/agent)

此模块采用python编写，用于接收配置文件以及上传配置文件，该模块运行于需要进行配置文件分发的服务器节点上。

1. 运行环境
   - Linux 32/64 / Windows 32/64
   - python 3.5+
2. 部署及使用说明
3. 注意事项
4. 单元测试