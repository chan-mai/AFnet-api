# AFnet-api
別途複数運営サービスに同一アカウントで対応させるためのAPI  
  
## 仕様
### ユーザ登録 - /api/account_add [POST]

#### 処理概要

* ユーザ情報を新しく登録する。
* 登録に成功した場合、固有のuser_idとアクセストークンを返す。

+ Request (application/json)

    + Headers

            Accept: application/json

    + Attributes
        + name: hogehoge (string, required) - ユーザー名
        + email: example@example.com (string, required) - メールアドレス（format: email）
        + password: abc123 (string, required) - パスワード

+ Response 201 (application/json)
    + Attributes
        + user_id:
        6708cb5e-9a9e-4fc7-b8ba-552c892e1fb7 (string, required) - user_id
        + accessToken: ebe38d50d77639d29a3521e21e4f0a75ed6872fbae56639cc0e02fc99517d48d (string, required) - アクセストークン


### ログイン - /api/login [POST]
#### 処理概要

* 既存のユーザー情報を照会し、認証を行う。
* 登録に成功した場合、固有のuser_idとアクセストークン、登録情報を返す。

+ Request (application/json)

    + Headers

            Accept: application/json

    + Attributes
        + email: example@example.com (string, required) - メールアドレス（format: email）
        + password: abc123 (string, required) - パスワード

+ Response 201 (application/json)
    + Attributes
        + status:
        ok (string, required)
        + message:
        example (string. required)
        + user_id:
        6708cb5e-9a9e-4fc7-b8ba-552c892e1fb7 (string, required) - user_id
        + name
        hogehoge (string, required) - 登録されているユーザー名（format: email）
        + email
        example@example.com (string, required) - 登録されているメールアドレス
        + token: ebe38d50d77639d29a3521e21e4f0a75ed6872fbae56639cc0e02fc99517d48d(string, required) - アクセストークン


### ユーザ情報の更新 - update_user_data/\<string:user_id> [POST]
#### 処理概要

* 既存ユーザ情報を更新する。

+ Request (application/json)

    + Headers

            Accept: application/json

    + Attributes
        + user_id: 6708cb5e-9a9e-4fc7-b8ba-552c892e1fb7 (string, required) - 割り当てられたuser_id
        + token: ebe38d50d77639d29a3521e21e4f0a75ed6872fbae56639cc0e02fc99517d48d (string, required) - アクセストークン
        + name: hogehoge (string) - 変更後のユーザー名
        + email: example@example.com (string) - メールアドレス（format: email）
        + password: abc123 (string) - パスワード
        + icon_img: [file] - アイコンに用いる画像ファイル
        + bio: example-user (string) - ユーザー概要
        + link: https://example.com (string) - 関連リンク (format: url)

+ Response 201 (application/json)
    + Attributes
        + status:
        ok (string, required)
        + message:
        example (string. required)
  

### ユーザー情報の消去 - /api/delete_account/\<string:user_id> [POST]
#### 処理概要

* 既存のユーザーを消去する。
* 消去に成功した場合、消去対象固有のuser_idを返す。

+ Request (application/json)

    + Headers

            Accept: application/json

    + Attributes
        + user_id: 6708cb5e-9a9e-4fc7-b8ba-552c892e1fb7 (string, required) - 割り当てられたuser_id
        + token: ebe38d50d77639d29a3521e21e4f0a75ed6872fbae56639cc0e02fc99517d48d (string, required) - アクセストークン

+ Response 201 (application/json)
    + Attributes
        + status:
        ok (string, required)
        + message:
        example (string. required)
        + user_id:
        6708cb5e-9a9e-4fc7-b8ba-552c892e1fb7 (string, required) - user_id


### トークンの有効性確認 - /api/check_token/\<string:user_id> [POST]
#### 処理概要

* トークンとユーザーを照合し有効性を確認する。
* 消去に成功した場合、消去対象固有のuser_idとアクセストークンを返す。

+ Request (application/json)

    + Headers

            Accept: application/json

    + Attributes
        + user_id: 6708cb5e-9a9e-4fc7-b8ba-552c892e1fb7 (string, required) - 割り当てられたuser_id
        + token: ebe38d50d77639d29a3521e21e4f0a75ed6872fbae56639cc0e02fc99517d48d (string, required) - アクセストークン

+ Response 201 (application/json)
    + Attributes
        + status:
        ok (string, required)
        + message:
        example (string. required)
        + user_id:
        6708cb5e-9a9e-4fc7-b8ba-552c892e1fb7 (string, required) - user_id
        + token: ebe38d50d77639d29a3521e21e4f0a75ed6872fbae56639cc0e02fc99517d48d(string, required) - アクセストークン


### ユーザーのプロフィール取得 - /api/get_user_data/\<string:user_id> [GET]
#### 処理概要

* 指定されたuser_idに該当するもののうちプロフィールとして表示できるものに限り取得。
* 成功した場合、固有のuser_idとユーザー名、ユーザー概要、関連リンクを返す。

+ Request (application/json)

    + Headers

            Accept: application/json

    + Attributes

+ Response 201 (application/json)
    + Attributes
        + status:
        ok (string, required)
        + message:
        example (string. required)
        + user_id:
        6708cb5e-9a9e-4fc7-b8ba-552c892e1fb7 (string, required) - user_id
        + name: hogehoge (string) - ユーザー名
        + bio: example-user (string) - ユーザー概要
        + link: https://example.com (string) - 関連リンク (format: url)

### ユーザーのプロフィールアイコン取得 - /api/get_icon/\<string:user_id> [GET]
#### 処理概要

* 指定されたuser_idに該当するユーザーからアイコンのバイナリを取得。
* 成功した場合、アイコンのバイナリを返す。

+ Request (application/json)

    + Headers

            Accept: application/json

    + Attributes

+ Response 201 (application/json)
    + Attributes
        + [image] (binary) - プロフィールアイコン画像
