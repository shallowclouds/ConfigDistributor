# ConfigDistributor
### 概览(Overview)

a system to distribute configure files using Django and python.

### web管理界面(/manager)

此模块采用 Django 编写，用于提供该配置文件管理系统的 web api 以及 web 管理界面。

1. 运行环境
   * Linux 32 / 64
   * python 3.5+
   * nginx
   * docker(如果使用 docker 部署的话)
2. 部署及使用说明
   * 使用 Docker 部署（推荐）
   ```bash
    $ cd /path/to/src/manager
    $ sudo docker build -t configdistributor .
    $ sudo docker run -d --name config_distributor -p 0.0.0.0:80:80 configdistributor
   ```
   * 手动部署
       1. 进入到源码目录，执行 `pip3 install -r requirements.txt`来安装依赖的 python 包，此前请自行安装 nginx 、python3、pip3 。
       2. 执行 `python3 manage.py collectstatic` 来将静态资源文件复制到相应地方，执行 `python3 manage.py makemigrations` 以及 `python3 manage.py migrate` 来迁移数据库。
       3. 执行 `python3 manage.py createsuperuser` ，来生成初始超级管理员账户。
       4. 将 `uwsgi.ini` 中的 `chdir` 、`socket` 修改为源文件所在目录，执行 `uwsgi --ini /path/to/src/manager/uwsgi.ini` 启动uwsgi
       5. 复制`manager.conf` 到 nginx 的配置文件目录 `/etc/nginx/sites-enabled` （默认任何域名都可访问，如需修改域名或者需要 ssl ，请自行修改 `manager.conf` ；执行 `nginx -t` 检查配置文件是否有误，无误后执行 `sudo service nginx reload` 重新加载配置文件使其生效。
       6. 检查网站是否正常
3. 注意事项

   * 使用前请先编辑配置好配置文件，使配置项对应到源文件所在目录。

### 服务器端(/server)

此模块采用 python 编写，用于搭建分发管理配置文件的服务端，配置文件将通过此模块分发。

基于 pyuv 的跨平台异步非阻塞网络传输。

1. 运行环境
   - Linux 32/64
   - python 3.5 +
2. 部署及使用说明
   * 此部分一般和 manager 部分一起部署，参见前述。
   * 如需分开部署，需保证 manager 和 server 访问同一个 redis 数据库，可在 `manager/manager/settings.py` 里面修改REDIS_HOST 与 REDIS_PORT
   * 单独部署，直接运行 `server/Server.py` 即可
   * Server 可以多开，提高分发效率
3. 注意事项
   - 使用前请先编辑配置好配置文件
4. 单元测试
   - TODO

### 客户端(/agent)

此模块采用 python 编写，用于接收配置文件以及上传配置文件，该模块运行于需要进行配置文件分发的服务器节点上。

1. 运行环境
   - Linux 32/64
   - python 3.5 +
2. 部署及使用说明
   - nohup python3 client/Client.py &
   - 或者使用 supervisor 等工具

3. 注意事项
   - 使用前请先编辑配置好配置文件
4. 单元测试
   - TODO
