
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, session

from models import db, User, Task

# ==== 設定 ====
app = Flask(__name__)
app.secret_key = "b7e2f8c1e4a9d3f6a2c5b8e7d1f4c3a6e9b2d7c4f1a8b5e6c2d9f3a7b6e1c4d8"  # セッション用のランダムな秘密鍵

# tasks.dbはデフォルト、users.dbはbindsで分離
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_BINDS"] = {
  "users": "sqlite:///users.db"
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

PRIORITIES = ["Low", "Med", "High"]
STATUSES = ["todo", "doing", "done"]

# DB作成（両DB）
with app.app_context():
  db.create_all()

# ==== ログイン必須化 ====

from login import login_bp
from userRegister import user_register_bp
app.register_blueprint(login_bp)
app.register_blueprint(user_register_bp)

@app.before_request
def require_login():
  # ログインしていない場合は/login, /register, staticのみ許可
  if not session.get("logged_in") and request.endpoint not in ("login.login", "user_register.register", "static"):
    return redirect(url_for("login.login"))

# ==== ルーティング ====
@app.get("/")
def index():
  q = Task.query
  status = request.args.get("status")
  priority = request.args.get("priority")
  view_mode = request.args.get("view_mode", "personal")
  user_id = session.get("user_id")
  if view_mode == "personal" and user_id:
    q = q.filter_by(user_id=user_id)
  if status in STATUSES:
    q = q.filter_by(status=status)
  if priority in PRIORITIES:
    q = q.filter_by(priority=priority)
  tasks = q.order_by(Task.created_at.desc()).all()
  return render_template_string(TEMPLATE, tasks=tasks,
                  status=status, priority=priority,
                  view_mode=view_mode,
                  PRIORITIES=PRIORITIES, STATUSES=STATUSES)

@app.post("/tasks")
def create_task():
  title = (request.form.get("title") or "").strip()
  detail = (request.form.get("detail") or "").strip()
  priority = request.form.get("priority") or "Med"
  user_id = session.get("user_id")
  if not title:
    return "Title is required", 400
  if priority not in PRIORITIES:
    return "Invalid priority", 400
  t = Task(title=title, detail=detail, priority=priority, user_id=user_id)
  db.session.add(t)
  db.session.commit()
  return redirect(url_for("index"))

@app.post("/tasks/<int:task_id>/status")
def update_status(task_id):
    new_status = request.form.get("status")
    if new_status not in STATUSES:
        return "Invalid status", 400
    t = Task.query.get_or_404(task_id)
    t.status = new_status
    db.session.commit()
    return redirect(url_for("index", **request.args))

@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    t = Task.query.get_or_404(task_id)
    db.session.delete(t)
    db.session.commit()
    return redirect(url_for("index", **request.args))

# ==== 最小テンプレート ====
TEMPLATE = """
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8"/>
  <title>Mini Task Board</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"/>
</head>
<body class="bg-light">
<div class="container py-4">
  <h1 class="mb-3">Mini Task Board</h1>

  <!-- フィルタ -->
  <form class="row g-2 align-items-end mb-3" method="get">
    <div class="col-auto">
      <label class="form-label">Type of task</label><br>
      <div class="form-check form-check-inline">
        <input class="form-check-input" type="radio" name="view_mode" id="view_personal" value="personal" {% if view_mode != 'all' %}checked{% endif %} onchange="this.form.submit()">
        <label class="form-check-label" for="view_personal">My task</label>
      </div>
      <div class="form-check form-check-inline">
        <input class="form-check-input" type="radio" name="view_mode" id="view_all" value="all" {% if view_mode == 'all' %}checked{% endif %} onchange="this.form.submit()">
        <label class="form-check-label" for="view_all">All task</label>
      </div>
    </div>
    <div class="col-auto">
      <label class="form-label">Status</label>
      <select name="status" class="form-select">
        <option value="">(all)</option>
        {% for s in STATUSES %}
          <option value="{{s}}" {{'selected' if status==s else ''}}>{{s}}</option>
        {% endfor %}
      </select>
    </div>
    <div class="col-auto">
      <label class="form-label">Priority</label>
      <select name="priority" class="form-select">
        <option value="">(all)</option>
        {% for p in PRIORITIES %}
          <option value="{{p}}" {{'selected' if priority==p else ''}}>{{p}}</option>
        {% endfor %}
      </select>
    </div>
    <div class="col-auto">
      <button class="btn btn-secondary">Filter</button>
      <a class="btn btn-outline-secondary" href="{{ url_for('index') }}">Clear</a>
    </div>
  </form>

  <!-- 新規作成 -->
  <div class="card mb-3">
    <div class="card-body">
      <h5 class="card-title">New Task</h5>
      <form method="post" action="{{ url_for('create_task') }}">
        <div class="row g-2">
          <div class="col-md-4">
            <input name="title" class="form-control" placeholder="Title (required)" maxlength="100" required>
          </div>
          <div class="col-md-4">
            <input name="detail" class="form-control" placeholder="Detail (optional)">
          </div>
          <div class="col-md-2">
            <select name="priority" class="form-select">
              {% for p in PRIORITIES %}<option value="{{p}}">{{p}}</option>{% endfor %}
            </select>
          </div>
          <div class="col-md-2 d-grid">
            <button class="btn btn-primary">Add</button>
          </div>
        </div>
      </form>
    </div>
  </div>

  <!-- 一覧 -->
  <div class="list-group">
    {% for t in tasks %}
      <div class="list-group-item">
        <div class="d-flex justify-content-between">
          <div>
            <strong>[{{ t.priority }}]</strong>
            <span class="badge text-bg-{{ 'success' if t.status=='done' else ('warning' if t.status=='doing' else 'secondary') }}">
              {{ t.status }}
            </span>
            <span class="ms-1">{{ t.title }}</span>
            {% if t.detail %}<div class="text-muted small">{{ t.detail }}</div>{% endif %}
            <div class="text-muted small">#{{t.id}} / {{t.created_at.strftime('%Y-%m-%d %H:%M')}}</div>
          </div>
          <div class="d-flex gap-2">
            <form method="post" action="{{ url_for('update_status', task_id=t.id) }}">
              <input type="hidden" name="status" value="todo">
              <button class="btn btn-sm btn-outline-secondary" {{'disabled' if t.status=='todo' else ''}}>todo</button>
            </form>
            <form method="post" action="{{ url_for('update_status', task_id=t.id) }}">
              <input type="hidden" name="status" value="doing">
              <button class="btn btn-sm btn-outline-warning" {{'disabled' if t.status=='doing' else ''}}>doing</button>
            </form>
            <form method="post" action="{{ url_for('update_status', task_id=t.id) }}">
              <input type="hidden" name="status" value="done">
              <button class="btn btn-sm btn-outline-success" {{'disabled' if t.status=='done' else ''}}>done</button>
            </form>
            <form method="post" action="{{ url_for('delete_task', task_id=t.id) }}" onsubmit="return confirm('Delete?');">
              <button class="btn btn-sm btn-outline-danger">delete</button>
            </form>
          </div>
        </div>
      </div>
    {% else %}
      <div class="alert alert-info">No tasks yet.</div>
    {% endfor %}
  </div>
</div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
