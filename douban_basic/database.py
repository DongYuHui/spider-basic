import bs4
import sqlite3


def get_connection(database):
    """
    获取数据库的连接
    """
    connection = sqlite3.connect(database)
    return connection


def initial(connection):
    """
    初始化建表
    """
    create_table_catalog(connection)
    create_table_error(connection)


# 以下是关于 subject 表相关的操作


def get_subject_list_all(connection, year, subject_type):
    """
    获取所有 subject 列表
    """
    select_sql = 'SELECT id, subject_id, type, name, year, rating_value, rating_count, image, url, duration, genre, directors, authors, actors, release, districts, imdb, remark FROM subject WHERE year = ? AND type = ?'
    cursor = connection.cursor()
    cursor.execute(select_sql, (year, subject_type))
    result = list(map(lambda x: map_subject(x), cursor))
    return result


def get_subject_list(connection, year, start, page_size):
    """
    获取 subject 分页
    """
    select_sql = 'SELECT id, subject_id, type, name, year, rating_value, rating_count, image, url, duration, genre, directors, authors, actors, release, districts, imdb, remark FROM subject WHERE year = ? ORDER BY id LIMIT ?, ?'
    cursor = connection.cursor()
    cursor.execute(select_sql, (year, start, page_size))
    result = list(map(lambda x: map_subject(x), cursor))
    return result


def map_subject(row):
    """
    映射 subject 数据行
    """
    item = {}
    item['id'] = row[0]
    item['subject_id'] = row[1]
    item['type'] = row[2]
    item['name'] = row[3]
    item['year'] = row[4]
    item['rating_value'] = row[5]
    item['rating_count'] = row[6]
    item['image'] = row[7]
    item['url'] = row[8]
    item['duration'] = row[9]
    item['genre'] = row[10]
    item['directors'] = row[11]
    item['authors'] = row[12]
    item['actors'] = row[13]
    item['release'] = row[14]
    item['districts'] = row[15]
    item['imdb'] = row[16]
    item['remark'] = row[17]
    return item


def insert_subject(connection, subject):
    """
    插入新的 subject 记录
    """
    insert_sql = 'INSERT INTO subject (subject_id, type, name, year, rating_value, rating_count, image, url, duration, genre, directors, authors, actors, release, districts, imdb, remark) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    if 'genre' in subject:
        str_genre = str(subject['genre'])
    else:
        str_genre = '[]'
    str_directors = str(subject['directors'])
    str_authors = str(subject['authors'])
    str_actors = str(subject['actors'])
    str_release = str(subject['release'])
    str_districts = str(subject['districts'])
    str_subject = str(subject)
    insert_tuple = (subject['id'], subject['type'], subject['name'], subject['year'], subject['ratingValue'], subject['ratingCount'], subject['image'],
                    subject['url'], subject['duration'], str_genre, str_directors, str_authors, str_actors, str_release, str_districts, subject['imdb'], str_subject)
    cursor = connection.cursor()
    cursor.execute(insert_sql, insert_tuple)
    result = cursor.rowcount
    cursor.close()
    connection.commit()
    return result > 0


def update_subject_district(connection, subject_id, districts):
    update_sql = 'UPDATE subject SET districts = ? WHERE subject_id = ?'
    cursor = connection.cursor()
    cursor.execute(update_sql, (str(districts), subject_id))
    connection.commit()


# 以下是关于 pre 表相关的操作


def create_table_catalog(connection):
    """
    创建 pre 表
    """
    create_sql = 'CREATE TABLE IF NOT EXISTS "catalog" ("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"subject_id" TEXT,"title" TEXT,"year" INTEGER,"rate" REAL,"url" TEXT,"is_handle" INTEGER NOT NULL DEFAULT 0,UNIQUE ("subject_id" COLLATE BINARY ASC) ON CONFLICT REPLACE)'
    cursor = connection.cursor()
    cursor.execute(create_sql)
    connection.commit()


def get_catalog_min_year(connection):
    """
    获取 pre 表中最小年份，没有则返回 None
    """
    select_sql = 'SELECT MIN(year) FROM catalog'
    cursor = connection.cursor()
    cursor.execute(select_sql)
    result = cursor.fetchone()[0]
    return result


def get_catalog_min_rate(connection, year):
    """
    获取 pre 表中相应年份的最小分数，如果该年份数据已全，则返回 -1
    """
    select_null = 'SELECT COUNT(*) FROM catalog WHERE year = ? AND rate IS NULL'
    cursor = connection.cursor()
    cursor.execute(select_null, (year,))
    result = cursor.fetchone()[0]
    if not result == None and result > 0:
        # 如果数据量大于 9950，则算作该年份数据齐全
        if result > 9950:
            return -1
        else:
            return 0
    select_sql = 'SELECT MIN(rate) FROM catalog WHERE year = ?'
    cursor = connection.cursor()
    cursor.execute(select_sql, (year,))
    result = cursor.fetchone()[0]
    if result == None or result == 0:
        return 9
    return result


def get_catalog_page(connection, year, is_handle, start, page_size):
    """
    分页获取目录内容
    """
    select_sql = 'SELECT id, subject_id, title, year, rate, url FROM catalog WHERE year = ? AND is_handle = ? AND rate IS NOT NULL ORDER BY id LIMIT ?, ?'
    cursor = connection.cursor()
    cursor.execute(select_sql, (year, is_handle, start, page_size))
    result = list(map(lambda x: map_from_catalog(x), cursor))
    return result


def map_from_catalog(row):
    """
    将检索行映射成
    """
    item = {}
    item['id'] = row[0]
    item['subject_id'] = row[1]
    item['title'] = row[2]
    item['year'] = row[3]
    item['rate'] = row[4]
    item['url'] = row[5]
    return item


def update_catalog_handle(connection, subject_id, is_handle):
    """
    更新该项目录的处理状态
    """
    update_sql = 'UPDATE catalog SET is_handle = ? WHERE subject_id = ?'
    cursor = connection.cursor()
    cursor.execute(update_sql, (is_handle, subject_id))
    connection.commit()


def insert_catalog_list(connection, subject_list, year, rate):
    """
    批量插入 subject 数据
    """
    if len(subject_list) == 0:
        return 0
    insert_sql = 'INSERT INTO catalog (subject_id, title, url, year, rate) VALUES (?, ?, ?, ?, ?)'
    insert_list = list(map(lambda x: map_to_catalog(x, year), subject_list))
    cursor = connection.cursor()
    cursor.executemany(insert_sql, insert_list)
    result = cursor.rowcount
    cursor.close()
    connection.commit()
    return result


def map_to_catalog(subject_json, year):
    """
    将 subject JSON 格式映射成字典
    """
    rate = 0
    try:
        rate = float(subject_json['rate'])
    except:
        rate = None
    return (subject_json['id'], subject_json['title'], subject_json['url'], year, rate)


# 以下是关于 error 的相关操作


def create_table_error(connection):
    """
    创建错误表
    """
    create_sql = 'CREATE TABLE IF NOT EXISTS "error" ("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"subject_id" TEXT,"year" INTEGER,UNIQUE ("subject_id" COLLATE BINARY ASC) ON CONFLICT IGNORE)'
    cursor = connection.cursor()
    cursor.execute(create_sql)
    connection.commit()


def get_error_list(connection, start, page_size):
    """
    获取错误列表
    """
    select_sql = 'SELECT id, subject_id FROM error LIMIT ?, ?'
    cursor = connection.cursor()
    cursor.execute(select_sql, (start, page_size))
    result = list(map(lambda x: map_error(x), cursor))
    return result


def map_error(row):
    item = {}
    item['id'] = row[0]
    item['subject_id'] = row[1]
    return item


def insert_error(connection, subject_id, year):
    """
    插入错误
    """
    insert_sql = 'INSERT INTO error (subject_id, year) VALUES (?, ?)'
    cursor = connection.cursor()
    cursor.execute(insert_sql, (subject_id, year))
    connection.commit()


def delete_error(connection, subject_id):
    delete_sql = 'DELETE FROM error WHERE subject_id = ?'
    cursor = connection.cursor()
    cursor.execute(delete_sql, (subject_id,))
    connection.commit()
