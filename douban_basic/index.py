import catalog
import subject
import database

import auth


def sync_specific_year(database_name, year):
    """
    抓取特定年份
    """
    # 登录豆瓣
    if not auth.login():
        print('Login failed, please check for reason.')
        return
    catalog.session = auth.get_session()
    subject.session = auth.get_session()
    # 连接数据库
    connection = database.get_connection(database_name)
    # 初始化
    database.initial(connection)
    # 抓取目录
    catalog.sync_specific_year(connection, year)
    # 抓取内容
    subject.sync_specific_year(connection, year)


def sync_initialization(database_name):
    """
    从头开始抓取数据
    """
    # 登录豆瓣
    if not auth.login():
        print('Login failed, please check for reason.')
        return
    catalog.session = auth.get_session()
    subject.session = auth.get_session()
    # 连接数据库
    connection = database.get_connection(database_name)
    # 初始化
    database.initial(connection)
    # 抓取目录
    catalog.sync_initialization(connection)
    # 抓取内容
    subject.sync_initialization(connection)


if __name__ == "__main__":
    # 开始自定义抓取
    sync_specific_year('subject.db', 2018)