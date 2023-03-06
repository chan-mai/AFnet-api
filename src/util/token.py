import pymysql
import hashlib
from config import config
import time

class Token():
    # トークンの生成
    def create(user_id):
        # すでにトークンが存在するか確認
        connection = pymysql.connect(host=config.db_host,
                                    port=config.db_port,
                                    user=config.db_user,
                                    password=config.db_pass,
                                    db='afnet_account',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM token WHERE user_id = %s', (user_id,))

        connection.commit()
        connection.close()

        result = cursor.fetchall()
        if len(result) != 0:
            # トークンを返す
            token = result[0]['token']
            return token
        else:
            # トークンの生成 user_id + timestamp
            timestamp = str(time.time())
            _token = user_id + str(timestamp)
            token = hashlib.sha256(_token.encode()).hexdigest()
            connection = pymysql.connect(host=config.db_host,
                                        port=config.db_port,
                                        user=config.db_user,
                                        password=config.db_pass,
                                        db='afnet_account',
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)
            cursor = connection.cursor()
            
            # トークンをデータベースに登録
            cursor.execute('INSERT INTO token (user_id, token) VALUES (%s, %s)', (user_id, token))
            
            connection.commit()
            connection.close()

            
            return token

    # トークンの削除
    def delete(user_id):
        connection = pymysql.connect(host=config.db_host,
                                    port=config.db_port,
                                    user=config.db_user,
                                    password=config.db_pass,
                                    db='afnet_account',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        
        # トークンをデータベースから消去
        cursor.execute('DELETE FROM token WHERE user_id = %s', (user_id,))
        
        connection.commit()
        connection.close()
        
        return True

    # トークンの再発行
    def renew(user_id):
        # トークンの削除
        Token.delete(user_id)
        # トークンの生成 user_id + timestamp
        token = Token.create(user_id)
        
        return token

    # トークンの有効性確認
    def check(user_id=None, token=None):
        if user_id is None or token is None:
            return False
        
        connection = pymysql.connect(host=config.db_host,
                                    port=config.db_port,
                                    user=config.db_user,
                                    password=config.db_pass,
                                    db='afnet_account',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        
        # user_idとtokenが一致するか確認
        cursor.execute('SELECT * FROM token WHERE user_id = %s', (user_id))
        
        connection.commit()
        connection.close()
        
        result = cursor.fetchall()

        if len(result) == 0:
            return False

        for row in result:
            if row['user_id'] == user_id and row['token'] == token:
                return True
            else:
                return False