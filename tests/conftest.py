import sys
import re
from pathlib import Path
import importlib
import pytest

@pytest.fixture(scope="session")
def project_root() -> Path:
    # この conftest.py から見たプロジェクトルート（app.py があるディレクトリ）
    return Path(__file__).resolve().parents[1]

@pytest.fixture()
def app(monkeypatch, tmp_path, project_root):
    """
    - CWD を一時ディレクトリに変更してから app.py をインポート
    - 相対パス SQLite が tmp_path に作成される（テスト汚染防止）
    """
    # app.py / models.py などを import できるようにパスを追加
    sys.path.insert(0, str(project_root))

    # DB を tmp に作らせるため CWD を移動
    monkeypatch.chdir(tmp_path)

    # 既に import 済みならリロードを避けるため除去（クリーンインポート）
    for name in ["app", "models", "login", "userRegister"]:
        if name in sys.modules:
            del sys.modules[name]

    # 通常インポートでOK（sys.path に project_root を追加済み）
    import app as app_module  # noqa: E402

    yield app_module.app  # Flask app オブジェクトを返す

@pytest.fixture()
def db_models():
    """
    models モジュールを提供（db, Task などを使うため）
    """
    import models
    return models

@pytest.fixture()
def client(app):
    """
    ログイン済みセッションでのクライアントを返す（user_id=1 を想定）
    """
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["logged_in"] = True
            sess["user_id"] = 1
        yield c

def extract_ids_from_html(html: str):
    # 一覧の行は <div class="list-group-item" data-id="..."> で表現される
    # モーダル等にもIDに数字は含まれるが、data-id のみ抽出する
    return [int(x) for x in re.findall(r'data-id="(\d+)"', html)]
