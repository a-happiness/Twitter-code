from flask import Flask, redirect, request, render_template, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'STTajUdwAUU2BPzPTPtc7ppeFpPPplhpiMeTeSoEJE'


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


@app.route('/')
def index():
    return redirect('/login')


@app.route('/sign_up', methods=['GET', "POST"])
def get_sign():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        head = ('email', 'username', 'password')
        data = (email, username, password)
        user = check_info_exists(username, "Users")
        if user is None:
            insert_to_table('Users', head, data)
            return render_template('sign_up.html', new_user=True)
        return render_template('sign_up.html', duplicate_user=True)
    return render_template('sign_up.html')


@app.route('/login', methods=["GET", "POST"])
def get_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = check_info_exists(username, 'Users')
        if user is None:
            return render_template('/login.html', no_user=True)
        if user[3] != password:
            return render_template('/login.html', invalid_pwd=True)
        session['logged_in'] = True
        session['username'] = username
        return redirect('/login/account')
    return render_template('/login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect('/login')


@app.route('/login/account')
def account():
    if session.get('logged_in') is not True:
        return redirect('/login')
    username = session.get('username')
    return render_template('account.html',
                           username=username, active='account')


@app.route('/login/account/add_post', methods=['GET', 'POST'])
def add_post():
    username = session.get('username')
    if session.get('logged_in') is not True:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form.get('title')
        date = request.form.get('date')
        content = request.form.get('content')
        head = ('username', 'title', 'date', 'content')
        data = (username, title, date, content)
        insert_to_table('Posts', head, data)
        return render_template('add_post.html', username=username,
                               active='add_post', new_post=True)
    return render_template('add_post.html', username=username,
                           active='add_post')


@app.route('/login/account/post')
def post():
    username = session.get('username')
    if session.get('logged_in') is not True:
        return redirect('/login')
    post = read_database('Posts', params=username)
    return render_template('post.html', post=post[::-1], enumerate=enumerate, username=username, active='post')


@app.route('/login/account/delete_post', methods=['GET', 'POST'])
def delete_post():
    username = session.get('username')
    if session.get('logged_in') is not True:
        return redirect('/login')
    if request.method == 'POST':
        table = 'Posts'
        condition = 'title'
        info = request.form.get('title')
        if not info:
            return "Title is required", 400

        deleted_count = delete_record(table, username, condition, info)
        if deleted_count is not None:
            return redirect('/login/account/post')
        else:
            return "An error occurred while deleting the post", 500


@app.route('/login/account/search_to_follow', methods=["GET", "POST"])
def search_to_follow():
    username = session.get('username')
    if session.get('logged_in') is not True:
        return redirect('/login')
    if request.method == 'POST':
        search = request.form.get('search_to_follow')
        user = check_info_exists(search, 'Users')
        if user is None:
            return render_template('search_to_follow.html',
                                   username=username, active='search_to_follow',
                                   no_user=True)
        follows = read_database('Follows', params=username)
        if search == username:
            return render_template('search_to_follow.html',
                                   username=username, active='search_to_follow',
                                   self_follow=True)
        for follow in follows:
            if search == follow[3]:
                return render_template('search_to_follow.html',
                                       username=username, active='search_to_follow',
                                       duplicate_follow=True)
        head = ('username', 'followers', 'followings')
        data = (username, username, search)
        insert_to_table('Follows', head, data)
        return render_template('search_to_follow.html',
                               username=username, active='search_to_follow',
                               new_follow=True)
    return render_template('search_to_follow.html',
                           username=username, active='search_to_follow')


@app.route('/login/account/followings')
def following():
    username = session.get('username')
    if session.get('logged_in') is not True:
        return redirect('/login')
    report = read_database('Follows', params=username, condition='followers')
    print(report)
    return render_template('following.html', report=report,
                           enumerate=enumerate, username=username, active='followings')


@app.route('/login/account/followers')
def follower():
    username = session.get('username')
    if session.get('logged_in') is not True:
        return redirect('/login')
    report = read_database('Follows', params=username, condition='followings')
    print(report)
    return render_template('follower.html', report=report,
                           enumerate=enumerate, username=username, active='followers')


if __name__ == '__main__':
    create_tables()
    # delete_table()
    app.run(debug=True)
