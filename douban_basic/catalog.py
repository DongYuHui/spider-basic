import json
import time
import requests

import database


# 会话
session = requests.Session()

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
    'Cache-Control': 'no-cache'
}

# 初始参数
sync_page_size = 20
sync_time_sleep = 3

# 请求地址
sync_url = 'https://movie.douban.com/j/new_search_subjects'


def sync_subject_list(connection, year, rate, start=0, delay=sync_time_sleep):
    """
    分页获取内容列表
    :param connection: 数据库连接
    :param year: 年份
    :param rate: 评分，以 1 分为跨度
    :param start: 起点
    :param delay: 延迟
    """
    # 睡眠
    time.sleep(delay)
    # 拼接参数，构成请求地址
    condition_rate = str(rate) + ',' + str(rate + 1)
    condition_year = str(year) + ',' + str(year)
    url = sync_url + '?sort=R&year_range=' + condition_year + '&range=' + condition_rate + '&start=' + str(start)
    # 调用请求，如果请求失败，则隔 30 秒再尝试
    try:
        get_response = session.get(url, headers=headers)
    except Exception as error:
        print('error | code 000 | url ' + url + ' | reason ' + str(error))
        sync_subject_list(connection, year, rate, start, 30)
        return
    # 处理返回结果
    if get_response.status_code == 200:
        # 提取内容插入到数据库
        subject_json = json.loads(get_response.text)
        subject_list = subject_json['data']
        database.insert_catalog_list(connection, subject_list, year, rate)
        print('get | year ' + str(year) + ' | rate ' + condition_rate + ' | start ' + str(start))
        if not len(subject_list) == 0:
            sync_subject_list(connection, year, rate, start + sync_page_size)
    else:
        # 如果结果失败，则在本次延迟时间上再加 30 秒延迟，此处主要用来处理服务器 403 拦截
        # 当出现 403 时，往往是豆瓣封 IP，所以依次增加延迟时间持续调用，直到服务器不拦截
        print('error | code ' + get_response.status_code + ' | url ' + url)
        sync_subject_list(connection, year, rate, start, delay + 30)


def sync_subject_node(connection, node):
    """
    根据 node 值进行内容获取
    :param connection: 数据库连接
    :param node: 节点，五位数字，前四位为年，后一位为分
    """
    # 节点不小于 1888 年，因为第一部电影诞生于 1888 年
    if node < 18880 or node > 20300:
        return
    # 前四位为年，后一位为分
    node_str = str(node)
    node_year = int(node_str[:4])
    node_rate = int(node_str[4:])
    # 调用方法进行处理
    if node % 10 == 9:
        print('=== year ' + str(node_year) + ' start ===')
    sync_subject_list(connection, node_year, node_rate)
    if node % 10 == 0:
        print('=== year ' + str(node_year) + '  end  ===')


def sync_specific_year(connection, year):
    """
    同步特定年份
    """
    # 初始化 catalog 表
    database.create_table_catalog(connection)
    # 开始抓取数据
    node_end = year * 10
    node = node_end + 9
    print('======= start =======')
    while node >= node_end:
        sync_subject_node(connection, node)
        node -= 1
    print('=======  end  =======')


def sync_initialization(connection):
    """
    完全同步，指从当前时间到最早数据全部同步
    """
    # 初始化 catalog 表
    database.create_table_catalog(connection)
    # 初始化节点序号
    min_year = database.get_catalog_min_year(connection)
    if min_year == None:
        min_year = time.localtime(time.time())[0]
    min_rate = database.get_catalog_min_rate(connection, min_year)
    if min_rate == -1:
        return
    node = int(str(min_year) + str(int(min_rate)))
    # 开始抓取数据
    print('======= start =======')
    while node >= 18880:
        sync_subject_node(connection, node)
        node -= 1
    print('=======  end  =======')