import os
import re
import bs4
import time
import json
import isodate
import duration
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
sync_url = 'https://movie.douban.com/subject/'


def parse_subject(content):
    """
    提取影视内容
    """
    info = {}
    # 解析新出 JSON 信息
    try:
        basic = json.loads(content.find('script', {"type": "application/ld+json"}).text)
    except Exception as error:
        raise Exception('decode error ' + str(error))
    # 名称
    if 'name' in basic and basic['name']:
        info['name'] = basic['name']
    # 海报
    if 'image' in basic and basic['image']:
        info['image'] = basic['image']
    # 片长
    if 'duration' in basic and basic['duration']:
        info['duration'] = duration.to_seconds(isodate.parse_duration(basic['duration']))
    else:
        info['duration'] = 0
    # 题材
    if 'genre' in basic and basic['genre']:
        info['genre'] = basic['genre']
    # 类型
    if '@type' in basic and basic['@type']:
        info['type'] = basic['@type']
    # 导演
    info['directors'] = list(map(lambda x: {'name': x['name'], 'url': x['url']}, basic['director']))
    # 编剧
    info['authors'] = list(map(lambda x: {'name': x['name'], 'url': x['url']}, basic['author']))
    # 演员
    info['actors'] = list(map(lambda x : {'name': x['name'], 'url': x['url']}, basic['actor']))
    # 上映时间
    info['release'] = list(map(lambda x: x.string.strip(), content.find_all('span', {"property": "v:initialReleaseDate"})))
    # 评分数量
    if basic['aggregateRating']['ratingCount']:
        info['ratingCount'] = int(basic['aggregateRating']['ratingCount'])
    else:
        info['ratingCount'] = 0
    # 评分数值
    if basic['aggregateRating']['ratingValue']:
        info['ratingValue'] = float(basic['aggregateRating']['ratingValue'])
    else:
        info['ratingValue'] = 0
    # 制片国家
    div_info = content.find('div', {"id": "info"})
    div_info_lines = str(div_info).split('\n')
    districts_line_list = list(filter(lambda x: '' in x, div_info_lines))
    if len(districts_line_list) > 0:
        districts = districts_line_list[0].replace('<span class="pl">制片国家/地区:</span>', '').replace('<br/>', '')
        info['districts'] = list(map(lambda x : x.strip(), districts.split('/')))
    else:
        info['districts'] = []
    # IMDB
    imdb_line_list = list(filter(lambda x : 'IMDb' in x, div_info_lines))
    if len(imdb_line_list) > 0:
        imdb_line = imdb_line_list[0].replace('IMDb链接:', '').strip()
        match_result = re.search('tt[0-9]+', imdb_line)
        if match_result:
            info['imdb'] = match_result.group(0)
        else:
            info['imdb'] = ''
    else:
        info['imdb'] = ''
    # 返回结果
    return info


def sync_subject_item(connection, subject_id, year, delay=sync_time_sleep):
    # # 判断该 subject 是否已经存在，如果存在，则不重复抓去
    # subject_exist = database.exist(connection, subject_id)
    # if subject_exist:
    #     return
    # 睡眠
    time.sleep(delay)
    # 拼接请求地址
    url = sync_url + subject_id + '/'
    # 获取请求内容
    try:
        response = session.get(url, timeout=30, headers=headers)
    except Exception as error:
        print('error | code 000 | url ' + url + ' | reason ' + str(error))
        sync_subject_item(connection, subject_id, 60)
        return
    # 处理结果
    if response.status_code == 200:
        # 保存到文件
        subject_file = open('html/' + str(year) + '/' + subject_id + '.html', 'w+')
        subject_file.write(response.text)
        # 解析结果
        try:
            subject = parse_subject(bs4.BeautifulSoup(response.text.replace('\n', '').replace('\t', ''), 'lxml'))
        except Exception as error:
            print('error ' + subject_id + ' | url ' + url + ' | reason ' + str(error))
            database.insert_error(connection, subject_id, year)
            database.update_catalog_handle(connection, subject_id, 1)
            return
        subject['id'] = subject_id
        subject['url'] = url
        subject['year'] = year
        if subject:
            # 保存结果
            database.insert_subject(connection, subject)
            database.update_catalog_handle(connection, subject_id, 1)
        print('get | year ' + str(year) + ' | subject ' + str(subject_id) + ' | url ' + url)
    elif response.status_code == 403:
        # 如果结果失败，则在本次延迟时间上再加 30 秒延迟，此处主要用来处理服务器 403 拦截
        # 当出现 403 时，往往是豆瓣封 IP，所以依次增加延迟时间持续调用，直到服务器不拦截
        print('auth error | url ' + url)
        sync_subject_item(connection, subject_id. year, delay + 30)
    else:
        print('error | code ' + str(response.status_code) + ' | url ' + url)
        database.insert_error(connection, subject_id, year)
        database.update_catalog_handle(connection, subject_id, 1)


def sync_specific_year(connection, year):
    """
    同步该年份的影视信息
    """
    print('=== year ' + str(year) + ' start ===')
    # 新建年份相应的目录，用于存放文件
    if not os.path.exists('html/' + str(year)):
        os.makedirs('html/' + str(year))
    # 分页读取目录中内容，并进行抓取
    while True:
        catalog_list = database.get_catalog_page(connection, year, 0, 0, sync_page_size)
        if len(catalog_list) == 0:
            break
        for catalog in catalog_list:
            sync_subject_item(connection, catalog['subject_id'], year)
    print('=== year ' + str(year) + '  end  ===')


def sync_initialization(connection):
    """
    完全同步，从当前年份一直往前抓取
    """
    year = time.localtime(time.time())[0]
    while year >= 1880:
        sync_specific_year(connection, year)
        year -= 1