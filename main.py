from flask import Flask, g, request
import uuid
from return_json import ReturnJson
from config import config
import hashlib
import MySQLdb

app = Flask(__name__)

# アカウント作成
@app.route('/account_add', methods=['POST'])
def account_add():
    # ユーザー名とパスワードを確認
    if request.form['username'] == None or request.form['password'] == None or request.form['email'] == None:
        return ReturnJson.err('項目が不足しています。')
    # ユーザー名
    username = request.form['username']
    # メール
    email = request.form['email']
    # パスワード
    password = request.form['password']
    # パスワードのハッシュ化
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    # ユーザーIDの生成
    user_id = str(uuid.uuid4())


    # メールアドレスの有効性を確認
    if email.find('@') == -1:
        return ReturnJson.err('メールアドレスが不正です。')
    
    # パスワードの長さを確認
    if len(password) >= 255:
        return ReturnJson.err('パスワードが長すぎます。')
    
    # ユーザー名の長さを確認
    if len(username) >= 255:
        return ReturnJson.err('ユーザー名が長すぎます。')
    
    try:
        connection = MySQLdb.connect(
                    host=config.db_host,
                    user=config.db_user,
                    passwd=config.db_pass,
                    db='afnet_account')
        cursor = connection.cursor()
        
        # メールアドレスが既に登録されているか確認
        cursor.execute('SELECT * FROM account WHERE email = %s', (email,))
        if cursor.fetchone() != None:
            return ReturnJson.err('このメールアドレスは既に登録されています。')
        
        connection.commit()
        connection.close()
    
    except:
        return ReturnJson.err('内部でエラーが発生しました。')
    

    try:
        connection = MySQLdb.connect(
                    host=config.db_host,
                    user=config.db_user,
                    passwd=config.db_pass,
                    db='afnet_account')
        cursor = connection.cursor()
        
        # 保存
        cursor.execute('INSERT INTO account (user_id, username, email, password) VALUES (%s, %s, %s, %s)', (user_id, email, username, password_hash))
        
        connection.commit()
        connection.close()


    except:
        return ReturnJson.err('内部でエラーが発生しました。')
