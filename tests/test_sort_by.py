from datetime import datetime
import pytest
import re

def extract_ids_from_html(html: str):
    return [int(x) for x in re.findall(r'data-id="(\d+)"', html)]

def seed_tasks(app, db_models):
    """
    user_id=1 に3件、user_id=2 に1件のタスクを作成して ID を返す。
    優先度・期日・作成日時を明示的に設定。
    戻り値: dict 名称->id
    """
    Task = db_models.Task
    db = db_models.db

    with app.app_context():
        # クリーンアップ（既存データ削除）
        db.session.query(Task).delete()
        db.session.commit()

        # user 1 のタスク
        tA = Task(
            title="A High 2025-01-10",
            detail="",
            priority="High",
            status="todo",
            user_id=1,
            due_date=datetime(2025, 1, 10),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
        )
        tB = Task(
            title="B Mid 2025-01-05",
            detail="",
            priority="Mid",
            status="todo",
            user_id=1,
            due_date=datetime(2025, 1, 5),
            created_at=datetime(2024, 1, 1, 11, 0, 0),
        )
        tC = Task(
            title="C Low None",
            detail="",
            priority="Low",
            status="todo",
            user_id=1,
            due_date=None,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )

        # user 2 のタスク（personal では見えない想定）
        tD = Task(
            title="D High 2025-01-03 (user2)",
            detail="",
            priority="High",
            status="todo",
            user_id=2,
            due_date=datetime(2025, 1, 3),
            created_at=datetime(2024, 1, 1, 9, 0, 0),
        )

        db.session.add_all([tA, tB, tC, tD])
        db.session.commit()

        return {
            "A": tA.id,
            "B": tB.id,
            "C": tC.id,
            "D": tD.id,
        }

# デフォルト（作成日時降順）のソート
def test_default_sort_created_desc_personal(app, client, db_models):
    ids = seed_tasks(app, db_models)

    # sort_by 未指定 => Created At (Newest First)
    res = client.get("/")
    assert res.status_code == 200

    ordered_ids = extract_ids_from_html(res.get_data(as_text=True))
    # personal デフォルトなので user_id=1 の 3件のみ
    # created_at 降順: C(12:00) > B(11:00) > A(10:00)
    assert ordered_ids == [ids["C"], ids["B"], ids["A"]]

# 期日順ソート（NULL値は最後）
def test_sort_by_due_date_personal(app, client, db_models):
    ids = seed_tasks(app, db_models)

    res = client.get("/?sort_by=Due+Date")
    assert res.status_code == 200

    ordered_ids = extract_ids_from_html(res.get_data(as_text=True))
    # due_date 昇順、NULLは最後 → B(1/5) > A(1/10) > C(None)
    assert ordered_ids == [ids["B"], ids["A"], ids["C"]]

# 優先度順ソート（タイブレーク含む）
def test_sort_by_priority_with_tiebreakers_personal(app, client, db_models):
    ids = seed_tasks(app, db_models)

    res = client.get("/?sort_by=Priority")
    assert res.status_code == 200

    ordered_ids = extract_ids_from_html(res.get_data(as_text=True))
    # Priority: High < Mid < Low
    # High は A（同優先度内では due_date 昇順→ Aのみ）
    # 次に Mid（B）、最後に Low（C: due_date NULL は最後）
    assert ordered_ids == [ids["A"], ids["B"], ids["C"]]

# 全タスク表示時の優先度ソート
def test_view_all_respects_sort(app, client, db_models):
    ids = seed_tasks(app, db_models)

    # すべて表示 + Priority ソート
    res = client.get("/?view_mode=all&sort_by=Priority")
    assert res.status_code == 200

    ordered_ids = extract_ids_from_html(res.get_data(as_text=True))
    # user_id=2 の D も含まれる。High 同士は due_date 昇順で D(1/3) → A(1/10)
    assert ordered_ids[:2] == [ids["D"], ids["A"]]
    # 残り Mid(B) → Low(C)
    assert ordered_ids[2:] == [ids["B"], ids["C"]]
