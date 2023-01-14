from flask import *
import uuid
from return_json import ReturnJson
from config import config
import hashlib
import MySQLdb

app = Flask(__name__)

# アカウント作成
@app.route('/account_add', methods=['POST'])
def account_add():
    # ユーザー名z
    username = request.form.get('username')
    # メール
    email = request.form.get('email')
    # パスワード
    password = request.form.get('password')

    print(username, email, password)

    # パラメータのチェック
    if username == None or email == None or password == None:
        return ReturnJson.err('パラメータが不正です。')

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
                    port=3307,
                    user=config.db_user,
                    passwd=config.db_pass,
                    db='afnet_account')
        cursor = connection.cursor()
        
        # メールアドレスが既に登録されているか確認
        cursor.execute('SELECT * FROM userdata WHERE email = %s', (email,))
        if cursor.fetchone() != "":
            return ReturnJson.err('このメールアドレスは既に登録されています。')
        
        connection.commit()
        connection.close()
    
    except Exception as e:
        print(e)
        return ReturnJson.err('内部でエラーが発生しました。')

    finally:    
        try:
            connection = MySQLdb.connect(
                        host=config.db_host,
                        port=3307,
                        user=config.db_user,
                        passwd=config.db_pass,
                        db='afnet_account')
            cursor = connection.cursor()
            
            # 保存
            cursor.execute('INSERT INTO userdata (user_id, name, email, password) VALUES (%s, %s, %s, %s)', (user_id, email, username, password_hash))
            
            connection.commit()
            connection.close()

        except Exception as e:
            print(e)
            return ReturnJson.err('内部でエラーが発生しました。')

        
        finally:
            return ReturnJson.ok('アカウントを作成しました。', {'user_id': user_id, 'username': username, 'email': email})

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)