# docs
此项目为了方便快捷的搜索各类开发语言的文档。

##### 项目产生原因：
在工作中同事推荐了 [Dash](https://kapeli.com/dash) 这一软件，能很便捷的搜索文档，但其局限于 MacOS/IOS 系统，并且因为不菲的价格，让我产生了实现其主要功能的想法。恰巧我当时刚接触 Python 这门语言，想用它来做些事情，所以有了此项目。

#### 项目相关组件：

1. [Python 3](https://www.python.org/download/releases/3.0/)
1. [PostgreSQL](https://www.postgresql.org/)
1. [Bootstrap](https://getbootstrap.com/docs/3.3/components/)
1. [Flask](http://flask.pocoo.org/)
1. [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

### 环境准备

1. 安装 Python3

   ```shell
   brew install python3 # for mac
   apt install python3  # for ubuntu
   ```


1. 安装 BeautifulSoup

   ```shell
   pip3 install bs4			# use pip3
   apt-get install Python-bs4  # use apt-get in ubuntu
   ...							# more install method in BeautifulSoup's website安装 HTML 解析包安装 HTML 解析包
   ```

1. 安装 HTML 解析器

   ```shell
   pip3 install html5lib
   ```

1. 安装 Flask

   ```shell
   pip3 install Flask
   ```

1. 安装 PostgreSQL

   ```shell
   apt install postgresql
   ```

1. 拷贝此项目到指定目录

    ```shell
    git clone git@github.com:SmallTianTian/docs.git # use ssh
    ```

1. 创建相关数据表（需要先根据 `config.json.example` 创建 `config.json`）

    ```shell
    python3 db/classDB.py
    ```

1. 启动服务

    ```shell
    python3 start.py
    ```

Q&A

​	You can [mail to](mailto:tianxuxin@126.com) me with anything.
