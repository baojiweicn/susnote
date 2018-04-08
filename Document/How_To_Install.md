### How to install
In order to use susnote, environment with python3.x(higher than 3.4) is required.
    pip3 install -r requirements.txt

After python3 installed the all the requirements, postgres database is also required.<br>
[Install Postgres in Mac](https://www.postgresql.org/download/macosx/) <br>
[Install Postgres in Linux](https://www.postgresql.org/download/linux/ubuntu/) <br>
[Install postgres in Windows](https://www.postgresql.org/download/macosx/) <br>

Enter postgres-cli:
    CREATE DATABASE susnote;
Then use the command:
    cd app
    python3 migration.py
After all these work:
    python3 server.py

### 如何安装
为了使用susnote, 需要安装python3.4以上的环境。
如果已经有这样的环境:
    pip3 install -r requirements.txt

安装完环境之后，需要初始化数据库(postgres):<br>
[Mac系统](https://www.postgresql.org/download/macosx/) <br>
[Linux系统](https://www.postgresql.org/download/linux/ubuntu/) <br>
[Windows系统](https://www.postgresql.org/download/macosx/) <br>

安装完成后，进入到postgres-cli:
    CREATE DATABASE susnote;
然后:
    cd app
    python3 migration.py
最后通过以下命令启动服务:
    python3 server.py

如果需要使用redis作为缓存。请在config文件中将redis的open选项设置为True，反之设置为False.(将使用本地缓存)

### Install through Docker:
It's much easier to install through docker. Use command:<br>
    docker-compose build<br>
then:<br>
    docker-compose up<br>

### 通过docker安装
直接使用命令:<br>
    docker-compose build<br>
然后使用命令启动:<br>
    docker-compose up<br>
