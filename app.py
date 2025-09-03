
from datetime import datetime, date
from flask import Flask, render_template_string, request, redirect, url_for, session, abort

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

PRIORITIES = ["Low", "Mid", "High"]
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
                  view_mode=view_mode, datetime=datetime, date=date,
                  PRIORITIES=PRIORITIES, STATUSES=STATUSES)

@app.post("/tasks")
def create_task():
  title = (request.form.get("title") or "").strip()
  detail = (request.form.get("detail") or "").strip()
  due_date_str = request.form.get("due_date")
  due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None
  priority = request.form.get("priority") or "Mid"
  user_id = session.get("user_id")
  if not title:
    return "Title is required", 400
  if priority not in PRIORITIES:
    return "Invalid priority", 400
  t = Task(title=title, detail=detail, priority=priority, user_id=user_id, due_date=due_date)
  db.session.add(t)
  db.session.commit()
  return redirect(url_for("index"))

@app.post("/tasks/<int:task_id>/status")
def update_status(task_id):
    new_status = request.form.get("status")
    if new_status not in STATUSES:
        return "Invalid status", 400
    t = Task.query.get_or_404(task_id)
    if t.user_id != session.get("user_id"):
        abort(403)  # Forbidden
    t.status = new_status
    db.session.commit()
    return redirect(url_for("index", **request.args))

@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    t = Task.query.get_or_404(task_id)
    if t.user_id != session.get("user_id"):
        abort(403)  # Forbidden
    db.session.delete(t)
    db.session.commit()
    return redirect(url_for("index", **request.args))

@app.post("/tasks/<int:task_id>/update")
def update_task(task_id):
    t = Task.query.get_or_404(task_id)
    if t.user_id != session.get("user_id"):
        abort(403)  # Forbidden

    t.title = (request.form.get("title") or "").strip()
    t.detail = (request.form.get("detail") or "").strip()
    t.priority = request.form.get("priority")
    due_date_str = request.form.get("due_date")
    t.due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None

    if not t.title:
        return "Title is required", 400
    if t.priority not in PRIORITIES:
        return "Invalid priority", 400
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
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
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
          <div class="col-md-3">
            <input name="title" class="form-control" placeholder="Title (required)" maxlength="100" required>
          </div>
          <div class="col-md-3">
            <textarea name="detail" class="form-control" placeholder="Detail (optional)" rows="1"></textarea>
          </div>
          <div class="col-md-2">
            <input type="date" name="due_date" class="form-control" title="Due Date">
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
            {% if t.detail %}<div class="text-muted small" style="white-space: pre-wrap;">{{ t.detail }}</div>{% endif %}
            <div class="d-flex align-items-center gap-3">
              <div class="text-muted small">#{{t.id}} / {{t.created_at.strftime('%Y-%m-%d %H:%M')}}</div>
              {% if t.due_date %}
                <div class="small {{ 'text-danger fw-bold' if not t.status == 'done' and t.due_date.date() < date.today() else 'text-muted' }}">
                  <i class="bi bi-calendar-x"></i>
                  Due: {{ t.due_date.strftime('%Y-%m-%d') }}
                </div>
              {% endif %}
            </div>
          </div>
          <div class="d-flex gap-1 align-items-center">
            <form method="post" action="{{ url_for('update_status', task_id=t.id) }}">
              <input type="hidden" name="status" value="todo">
              <button class="btn btn-sm {{ 'btn-secondary' if t.status == 'todo' else 'btn-outline-secondary' }}" {{'disabled' if t.status=='todo' else ''}}>todo</button>
            </form>
            <form method="post" action="{{ url_for('update_status', task_id=t.id) }}">
              <input type="hidden" name="status" value="doing">
              <button class="btn btn-sm {{ 'btn-warning' if t.status == 'doing' else 'btn-outline-warning' }}" {{'disabled' if t.status=='doing' else ''}}>doing</button>
            </form>
            <form method="post" action="{{ url_for('update_status', task_id=t.id) }}">
              <input type="hidden" name="status" value="done">
              <button class="btn btn-sm {{ 'btn-success' if t.status == 'done' else 'btn-outline-success' }}" {{'disabled' if t.status=='done' else ''}}>done</button>
            </form>
            <button type="button" class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#editModal{{ t.id }}" title="Edit">
              <i class="bi bi-pencil"></i>
            </button>
            <form method="post" action="{{ url_for('delete_task', task_id=t.id) }}" onsubmit="return confirm('Delete?');">
              <button class="btn btn-sm btn-outline-danger" title="Delete"><i class="bi bi-trash"></i></button>
            </form>
          </div>
        </div>
      </div>

      <!-- Edit Modal -->
      <div class="modal fade" id="editModal{{ t.id }}" tabindex="-1" aria-labelledby="editModalLabel{{ t.id }}" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <form method="post" action="{{ url_for('update_task', task_id=t.id) }}">
              <div class="modal-header">
                <h5 class="modal-title" id="editModalLabel{{ t.id }}">Edit Task #{{ t.id }}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <div class="mb-3">
                  <label class="form-label">Title</label>
                  <input name="title" class="form-control" value="{{ t.title }}" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Detail</label>
                  <textarea name="detail" class="form-control" rows="3">{{ t.detail or '' }}</textarea>
                </div>
                <div class="row">
                  <div class="col">
                    <label class="form-label">Priority</label>
                    <select name="priority" class="form-select">
                      {% for p in PRIORITIES %}
                      <option value="{{p}}" {{ 'selected' if p == t.priority }}>{{p}}</option>
                      {% endfor %}
                    </select>
                  </div>
                  <div class="col">
                    <label class="form-label">Due Date</label>
                    <input type="date" name="due_date" class="form-control" value="{{ t.due_date.strftime('%Y-%m-%d') if t.due_date }}">
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="submit" class="btn btn-primary">Save changes</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    {% else %}
      <div class="alert alert-info">No tasks yet.</div>
    {% endfor %}
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
