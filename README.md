# Mini Task Board

## 概要
`app.py`は、FlaskとSQLAlchemyを用いたシンプルなタスク管理Webアプリケーションです。タスクの登録・一覧表示・状態変更・削除・フィルタリングが可能です。

---

## 要件定義

### 1. 機能要件
- タスクの新規登録（タイトル必須、詳細・優先度任意）
- タスク一覧表示（作成日時の新しい順）
- タスクの状態変更（todo/doing/done）
- タスクの削除
- タスクの状態・優先度によるフィルタリング

### 2. 非機能要件
- WebインターフェースはBootstrapで簡易装飾
- データはSQLiteで永続化
- 1ファイルで完結（`app.py`のみ）
- 日本語UI対応

---

## 詳細設計

### 1. データベース設計
- **Taskテーブル**
  - `id`: 整数, 主キー, 自動採番
  - `title`: 文字列(100), 必須
  - `detail`: テキスト, 任意
  - `priority`: 文字列(10), 必須, デフォルト"Med"（Low/Med/High）
  - `status`: 文字列(10), 必須, デフォルト"todo"（todo/doing/done）
  - `created_at`: 日時, 必須, デフォルト現在時刻

### 2. 画面設計
- **トップページ（/）**
  - タスク一覧表示
  - 状態・優先度フィルタ
  - 新規タスク登録フォーム
  - 各タスクの状態変更・削除ボタン

### 3. ルーティング
- `GET /` : タスク一覧・フィルタ・新規作成フォーム表示
- `POST /tasks` : 新規タスク登録
- `POST /tasks/<task_id>/status` : タスク状態変更
- `POST /tasks/<task_id>/delete` : タスク削除

### 4. バリデーション
- タイトルは必須、100文字以内
- 優先度・状態は定義済みリストのみ許容

### 5. 使用技術
- Python 3.x
- Flask
- Flask-SQLAlchemy
- SQLite3
- Bootstrap 5（CDN）

---

## セットアップ手順
1. 必要なパッケージをインストール
  ```
  pip install flask flask_sqlalchemy
  ```
2. `login.py`を作成し、`app.py`と同じディレクトリに配置
3. `app.py`を実行
  ```
  python app.py
  ```
4. ブラウザで `http://localhost:5000/login` にアクセスし、ログイン画面を確認
5. ログイン後はタスク管理画面に遷移

---

## モジュール分割について
- `login.py`にログイン画面のルーティング・テンプレートをBlueprintとして分離しています。
- `app.py`では`from login import login_bp`し、`app.register_blueprint(login_bp)`で登録してください。

---

- データベースファイルは`instance/tasks.db`および`instance/users.db`に作成されます。
- 本アプリは学習・プロトタイピング用途を想定しています。
