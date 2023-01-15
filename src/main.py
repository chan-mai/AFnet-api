from flask import *
import uuid
from util.return_json import ReturnJson
from config import config
import hashlib
import os
import pymysql
import re
from util.token import Token

app = Flask(__name__)

# アカウント作成
@app.route('/api/account_add', methods=['POST'])
def account_add():
    # ユーザー名
    name = request.form.get('name')
    # メール
    email = request.form.get('email')
    # パスワード
    password = request.form.get('password')

    print(name, email, password)

    # パラメータのチェック
    if name == None or email == None or password == None:
        return ReturnJson.err('パラメータが不正です。')

    # パスワードのハッシュ化
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    # ユーザーIDの生成
    user_id = str(uuid.uuid4())


    # メールアドレスの有効性を確認
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return ReturnJson.err('メールアドレスが不正です。')
    
    # パスワードの長さを確認
    if len(password) >= 255:
        return ReturnJson.err('パスワードが長すぎます。')
    
    # ユーザー名の長さを確認
    if len(name) >= 255:
        return ReturnJson.err('ユーザー名が長すぎます。')
    
    try:
        connection = pymysql.connect(host=config.db_host,
                                    port=config.db_port,
                                    user=config.db_user,
                                    password=config.db_pass,
                                    db='afnet_account',
                                    cursorclass=pymysql.cursors.DictCursor,
                                    charset='utf8mb4')
        cursor = connection.cursor()
        
        # メールアドレスが既に登録されているか確認
        cursor.execute('SELECT * FROM userdata WHERE email = %s', (email,))

        connection.commit()
        connection.close()
        
        result = cursor.fetchall()
        if len(result) > 0:
            return ReturnJson.err('メールアドレスが既に登録されています。')

        connection = pymysql.connect(host=config.db_host,
                                    port=config.db_port,
                                    user=config.db_user,
                                    password=config.db_pass,
                                    db='afnet_account',
                                    charset='utf8mb4')
        cursor = connection.cursor()
        
        # 保存
        cursor.execute('INSERT INTO userdata (user_id, name, email, password) VALUES (%s, %s, %s, %s)', (user_id, name, email, password_hash))
        
        connection.commit()
        connection.close()

        # トークンの生成
        token = str(Token.create(user_id))

        return ReturnJson.ok('アカウントを作成しました。', {'user_id': user_id, 'token': token})

    
    except Exception as e:
        print(e)
        return ReturnJson.err('内部でエラーが発生しました。')

# ログイン
@app.route('/api/login', methods=['POST'])
def login():
    # メール
    email = request.form.get('email')
    # パスワード
    password = request.form.get('password')

    # パラメータのチェック
    if email == None or password == None:
        return ReturnJson.err('パラメータが不正です。')

    # パスワードのハッシュ化
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    try:
        connection = pymysql.connect(host=config.db_host,
                                    port=config.db_port,
                                    user=config.db_user,
                                    password=config.db_pass,
                                    db='afnet_account',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        
        # メールアドレスがの存在確認
        cursor.execute('SELECT * FROM userdata WHERE email = %s LIMIT 1', (email))

        result = cursor.fetchall()
        if result[0]["email"] == None:
            return ReturnJson.err('このメールアドレスは登録されていません。')
        else:
            if(result[0]["password"] != password_hash):
                return ReturnJson.err('パスワードが違います。')
            else:
                # トークンの生成
                token = Token.create(result[0]["user_id"])
                return ReturnJson.ok('ログインしました。', {'user_id': result[0]["user_id"], 'name': result[0]["name"], 'email': result[0]["email"], 'token': token})
    
    except Exception as e:
        print(e)
        return ReturnJson.err('内部でエラーが発生しました。')

# ユーザー情報の取得
@app.route('/api/get_user_data/<string:user_id>', methods=['GET'])
def get_user_data(user_id=None):
    if user_id == None:
        return ReturnJson.err('URLが不正です。')
    try:
        connection = pymysql.connect(host=config.db_host,
                                    port=config.db_port,
                                    user=config.db_user,
                                    password=config.db_pass,
                                    db='afnet_account',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        
        # ユーザーIDがの存在確認
        cursor.execute('SELECT * FROM userdata WHERE user_id = %s LIMIT 1', (user_id))

        result = cursor.fetchall()
        if result[0]["user_id"] == None:
            return ReturnJson.err('このユーザーIDは登録されていません。')
        else:
            return ReturnJson.ok('取得が完了しました。', {'user_id': result[0]["user_id"], 'name': result[0]["name"], 'icon': result[0]["icon"], 'bio': result[0]["bio"], 'link': result[0]["link"]})
    
    except Exception as e:
        print(e)
        return ReturnJson.err('内部でエラーが発生しました。')

# ユーザー情報の更新
@app.route('/api/update_user_data/<string:user_id>', methods=['POST'])
def update_user_data(user_id=None):
    if(user_id == None):
        return ReturnJson.err('URLが不正です。')

    # tokenの確認
    token = request.form.get('token')
    if token == None:
        return ReturnJson.err('トークンが不正です。')
    if Token.check(user_id, token) == False:
        return ReturnJson.err('トークンが不正です。')

    # 現在のユーザー情報の取得
    try:
        connection = pymysql.connect(host=config.db_host,
                                    port=config.db_port,
                                    user=config.db_user,
                                    password=config.db_pass,
                                    db='afnet_account',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()

        # ユーザーIDがの存在確認
        cursor.execute('SELECT * FROM userdata WHERE user_id = %s LIMIT 1', (user_id))

        result = cursor.fetchall()
        if len(result) == 0:
            return ReturnJson.err('このユーザーは登録されていません。')
        else:
            name = result[0]["name"]
            name = result[0]["password"]
            email = result[0]["email"]
            icon = result[0]["icon"]
            bio = result[0]["bio"]
            link = result[0]["link"]
    except Exception as e:
        print(e)
        return ReturnJson.err('内部でエラーが発生しました。')
    
    # パラメータの取得
    if(request.form.get('name') != None):
        name = request.form.get('name')
    if(request.form.get('email') != None):
        # メールアドレスの有効性確認
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', request.form.get('email')):
            return ReturnJson.err('メールアドレスの形式が不正です。')
        # メールアドレスの重複確認
        try:
            connection = pymysql.connect(host=config.db_host,
                                        port=config.db_port,
                                        user=config.db_user,
                                        password=config.db_pass,
                                        db='afnet_account',
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)
            cursor = connection.cursor()
            
            # メールアドレスがの存在確認
            cursor.execute('SELECT * FROM userdata WHERE email = %s LIMIT 1', (email))

            result = cursor.fetchall()
            connection.close()
            if result[0]["email"] != None:
                return ReturnJson.err('このメールアドレスは既に登録されています。')
        except Exception as e:
            print(e)
            return ReturnJson.err('内部でエラーが発生しました。')
        email = request.form.get('email')
    if(request.form.get('password') != None):
        _password = request.form.get('password')
        # ハッシュ化
        password = hashlib.sha256(_password.encode()).hexdigest()
    if(request.form.get('bio') != None):
        bio = request.form.get('bio')
    if(request.form.get('link') != None):
        link = request.form.get('link')
    # ファイルがあれば更新
    file = request.files['icon_img']
    if(file != None):
        # user_id.ext
        file.save(os.path.join('./static/icon', user_id + os.path.splitext(file.filename)[1]))
        icon = user_id + os.path.splitext(file.filename)[1]

    try:
        connection = pymysql.connect(host=config.db_host,
                                    port=config.db_port,
                                    user=config.db_user,
                                    password=config.db_pass,
                                    db='afnet_account',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()

        # 更新
        cursor.execute('UPDATE userdata SET name = %s, email = %s, icon = %s, password = %s, bio = %s, link = %s WHERE user_id = %s', (name, email, icon, password, bio, link, user_id))

        connection.commit()
        return ReturnJson.ok('更新が完了しました。', {})

    except Exception as e:
        print(e)
        return ReturnJson.err('内部でエラーが発生しました。')

# アカウントの削除
@app.route('/api/delete_account/<string:user_id>', methods=['POST'])
def delete_account(user_id=None):
    if(user_id == None):
        return ReturnJson.err('URLが不正です。')

    # tokenの確認
    token = request.form.get('token')
    if token == None:
        return ReturnJson.err('トークンが不正です。')
    if Token.check(user_id, token) == False:
        return ReturnJson.err('トークンが不正です。')

    try:
        connection = pymysql.connect(host=config.db_host,
                                    port=config.db_port,
                                    user=config.db_user,
                                    password=config.db_pass,
                                    db='afnet_account',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()

        # user_idの存在確認
        cursor.execute('SELECT * FROM userdata WHERE user_id = %s LIMIT 1', (user_id))

        result = cursor.fetchall()
        if result[0]["user_id"] == None:
            return ReturnJson.err('このユーザーは登録されていません。')
        else:
            # 削除
            cursor.execute('DELETE FROM userdata WHERE user_id = %s', (user_id))
            connection.commit()
            # アイコンがあれば削除
            if result[0]["icon"] != None:
                os.remove('./static/icon/' + result[0]["icon"])
            # トークンを削除
            Token.delete(user_id)
            return ReturnJson.ok('アカウントの削除が完了しました。', {'user_id': user_id})
    except Exception as e:
        print(e)
        return ReturnJson.err('内部でエラーが発生しました。')

# トークン認証
@app.route('/api/check_token/<string:user_id>', methods=['POST'])
def check_token(user_id=None):
    if(user_id == None):
        return ReturnJson.err('URLが不正です。')

    # tokenの確認
    token = request.form.get('token')
    if token == None:
        return ReturnJson.err('トークンが不正です。')
    if Token.check(user_id, token) == False:
        return ReturnJson.err('トークンが不正です。')

    return ReturnJson.ok('トークンの有効性が認められました。', {'user_id': user_id, 'token': token})

# アイコンを取得
@app.route('/api/get_icon/<string:user_id>', methods=['GET'])
def get_icon(user_id=None):
    if(user_id == None):
        return ReturnJson.err('URLが不正です。')

    try:
        connection = pymysql.connect(host=config.db_host,
                                    port=config.db_port,
                                    user=config.db_user,
                                    password=config.db_pass,
                                    db='afnet_account',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()

        # user_idの存在確認
        cursor.execute('SELECT * FROM userdata WHERE user_id = %s LIMIT 1', (user_id))

        result = cursor.fetchall()
        if len(result[0]["user_id"]) == 0:
            return ReturnJson.err('このユーザーは登録されていません。')
        else:
            # アイコンがあれば返す
            if result[0]["icon"] != None:
                # 画像をバイナリで返す
                return send_file('./static/icon/' + result[0]["icon"], mimetype='image/jpeg')
            else:
                return ReturnJson.err('このユーザーはアイコンを登録していません。')
    except Exception as e:
        print(e)
        return ReturnJson.err('内部でエラーが発生しました。')

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=80)