import sqlite3

def create_tables():
    with sqlite3.connect('twitter_database.sqlite') as conn:
        cur = conn.cursor()
        cur.execute(
            '''
            create table if not exists Users (
                user_id integer primary key autoincrement,
                email text not null,
                username text not null unique,
                password text not null)
            ''')

        cur.execute(
            '''
            create table if not exists Posts (
                post_id integer primary key autoincrement,
                username text not null,
                title text not null,
                date datetime not null,
                content text not null,
                foreign key (username) references Users (username))
            ''')

        cur.execute(
            '''
            create table if not exists Follows (
                id integer primary key autoincrement,
                username text not null,
                followers text not null,
                followings text not null,
                foreign key (username) references Users (username),
                foreign key (followers) references Users (username))
            ''')
        conn.commit()


def delete_table():
    table_name = ('Users', 'Posts', 'Follows')
    with sqlite3.connect('twitter_database.sqlite') as conn:
        cur = conn.cursor()
        cur.execute('drop table if exists Follows')
        conn.commit()


def delete_record(table, username, condition, info):
    with sqlite3.connect('twitter_database.sqlite') as conn:
        cur = conn.cursor()
        deleted_record = cur.execute(f'delete from {table} where username = ?'
                                     f' and {condition}=?', [username, info])
        conn.commit()
        return deleted_record


def check_info_exists(info, table, username='username'):
    with sqlite3.connect('twitter_database.sqlite') as conn:
        cur = conn.cursor()
        check_value = cur.execute(f'select * from {table} where ({username})=?',
                                  [info]).fetchone()
        conn.commit()
        return check_value


def insert_to_table(table, head, data):
    with sqlite3.connect('twitter_database.sqlite') as conn:
        cur = conn.cursor()
        head_str = ', '.join(head)
        placeholder = ','.join('?' * len(data))
        cur.execute(f'insert into {table} ({head_str}) values ({placeholder})', data)
        conn.commit()


def read_database(table, params, condition="username"):
    with sqlite3.connect('twitter_database.sqlite') as conn:
        cur = conn.cursor()
        data = cur.execute(f'select * from {table} where {condition}=?',
                           [params]).fetchall()
        conn.commit()
        return data
