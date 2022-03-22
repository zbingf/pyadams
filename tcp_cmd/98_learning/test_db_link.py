# -*- coding: utf-8 -*-
"""
数据库
Created on Sat Mar 19 20:35:13 2022

@author: zbingf
"""

import sqlite3


# 连接数据库
def get_db_connect(db_file):
    conn = None
    try:    
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)  
    return conn


# 关闭数据库
def close_db_connect(cur, conn):
    
    if cur is not None:
        cur.close()
    
    if conn is not None:
        conn.close()


# 判定是否时list or tuple
def is_tuple_or_list(data):
    if isinstance(data, tuple):
        return True
    if isinstance(data, list):
        return True
    
    return False


# 涉及 commit
def db_commit(db_file, line, **kwargs):
    conn = get_db_connect(db_file)
    cur = conn.cursor()
    try:
        if "execute_insert" in kwargs:
            data = kwargs['execute_insert']
            if is_tuple_or_list(data[0]):
                cur.executemany(line, data)
            else:
                cur.execute(line, data)
        else:
            cur.execute(line)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
        
    close_db_connect(cur, conn)


def create_db_table(db_file, table_name, keys, key_types):
    """
        创建table
    """
    k = ','.join([f' {key} {key_type} ' for key, key_type in zip(keys, key_types)])
    line = f"CREATE TABLE {table_name} ({k})"
    print('create_db_table:', line)
    
    db_commit(db_file, line)


def insert_db_data(db_file, table_name, keys, data):
    """
        table 插入数据
        data 类型目前仅允许 list, tuple
    """
    
    str_key = ', '.join(keys)
    str_v = '?,'*len(keys)
    str_v = str_v[:-1]
    
    # insert into +表名 (列1, 列2, ...) values(?, ?, ...)
    line = f"INSERT INTO {table_name} ({str_key}) VALUES ({str_v})"
    print('insert_db_data:', line)
    
    db_commit(db_file, line, execute_insert=data)



db_file = 'test.db'
# create_db_table(db_file, 'table1', ['id', 'type', 'keys'], ['INTEGER PRIMARY KEY AUTOINCREMENT', 'text', 'text'])
insert_db_data(db_file, 'table1', ['type', 'keys'], ('t0', 'k0'))
insert_db_data(db_file, 'table1', ['type', 'keys'], [('t1', 'k1'), ('t2', 'k2')])


