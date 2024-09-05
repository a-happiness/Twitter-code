import uuid
from crypt import methods

from flask import Flask, redirect, request, render_template, session
from functions import *

app = Flask(__name__)
app.secret_key = 'STTajUdwAUU2BPzPTPtc7ppeFpPPplhpiMeTeSoEJE'


@app.template_filter('truncatewords')
def truncate_words_filter(text, num_words=7):
    words = text.split()
    if len(words) > num_words:
        return ' '.join(words[:num_words]) + '...'
    return text


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
    msg = None
    username = session.get('username')
    if session.get('logged_in') is not True:
        return redirect('/login')
    if request.method == 'GET':
        session['csrf_token'] = str(uuid.uuid4())
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if token == session.get('csrf_token'):
            title = request.form.get('title')
            content = request.form.get('content')
            head = ('username', 'title', 'content')
            data = (username, title, content)
            insert_to_table('Posts', head, data)
            msg = 'you added a new post.'
            session.pop('csrf_token', None)
    return render_template('add_post.html', username=username,
                           active='add_post', msg=msg, csrf_token=session.get('csrf_token'))


@app.route('/login/account/post')
def _post():
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
                                   no_user=True, search=search)
        follows = read_database('Follows', params=username)
        if search == username:
            return render_template('search_to_follow.html',
                                   username=username, active='search_to_follow',
                                   self_follow=True, search=search)
        for follow in follows:
            if search == follow[3]:
                return render_template('search_to_follow.html',
                                       username=username, active='search_to_follow',
                                       duplicate_follow=True, search=search)

        return render_template('search_to_follow.html',
                               username=username, active='search_to_follow',
                               new_follow=True, search=search)
    return render_template('search_to_follow.html',
                           username=username, active='search_to_follow')


@app.route('/login/account/add_follow', methods=["POST"])
def add_follow():
    username = session.get('username')
    if session.get('logged_in') is not True:
        return redirect('/login')
    search = request.form.get('search_to_follow')
    head = ('username', 'followers', 'followings')
    data = (username, username, search)
    insert_to_table('Follows', head, data)
    return render_template('search_to_follow.html',
                           username=username, active='search_to_follow',
                           follow_added=True, search=search)


@app.route('/login/account/followings')
def following():
    username = session.get('username')
    if session.get('logged_in') is not True:
        return redirect('/login')
    report = read_database('Follows', params=username, condition='followers')
    print(report)
    return render_template('following.html', report=report,
                           enumerate=enumerate, username=username, active='followings')


@app.route('/login/account/un_follow', methods=['GET', 'POST'])
def un_follow():
    username = session.get('username')
    if not session.get('logged_in'):
        return redirect('/login')
    if request.method == 'POST':
        table = 'Follows'
        followings = request.form.get('followings')
        followers = request.form.get('followers')

        if followings:
            deleted_count = delete_record(table, username, 'followings', followings)
            print(dict(deleted_count))
            if deleted_count is not None:
                return redirect('/login/account/followings')

        if followers:
            print('ex1')
            deleted_count = delete_record(table, followers, 'followers', followers)
            print(dict(deleted_count))
            print('ex2')
            if deleted_count is not None:
                print('ex3')
                return redirect('/login/account/followers')
        return "An error occurred while unfollowing the user", 500

    return "Title is required", 400


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
