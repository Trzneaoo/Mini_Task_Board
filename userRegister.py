
from flask import Blueprint, render_template_string, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

user_register_bp = Blueprint("user_register", __name__)

REGISTER_TEMPLATE = """
<!doctype html>
<html lang=\"ja\">
<head>
  <meta charset=\"utf-8\"/>
  <title>ユーザー登録</title>
  <style>
    body { background: #f8f8f8; }
    .register-box {
      width: 360px; margin: 60px auto; background: #fff;
      border-radius: 8px; box-shadow: 0 0 8px #b2d8e6;
      padding: 28px 28px 18px 28px; border: 2px solid #b2d8e6;
    }
    .register-title {
      text-align: center; color: #2cbfd9; font-size: 2em; font-weight: bold;
      margin-bottom: 10px; border-bottom: 2px solid #2cbfd9; padding-bottom: 6px;
    }
    .register-label { display: block; margin-top: 14px; margin-bottom: 4px; }
    .register-input { width: 100%; padding: 6px; font-size: 1em; }
    .register-actions { text-align: right; margin-top: 16px; }
    .register-btn {
      background: linear-gradient(#5fd0e6, #2cbfd9);
      color: #fff; border: none; border-radius: 6px;
      padding: 8px 28px; font-size: 1.1em; font-weight: bold;
      box-shadow: 2px 2px 6px #b2d8e6;
      cursor: pointer;
    }
    .register-btn:active { box-shadow: none; }
  </style>
</head>
<body>
  <div class=\"register-box\">
    <div class=\"register-title\">User Register</div>
    <form method=\"post\" action=\"{{ url_for('user_register.register') }}\">
      <label class=\"register-label\">Email</label>
      <input type=\"email\" name=\"email\" class=\"register-input\" required>
      <label class=\"register-label\">Password</label>
      <input type=\"password\" name=\"password\" class=\"register-input\" required>
      <label class=\"register-label\">Password（確認）</label>
      <input type=\"password\" name=\"password2\" class=\"register-input\" required>
      <div class=\"register-actions\">
        <button class=\"register-btn\" type=\"submit\">登録</button>
        <a href=\"{{ url_for('login.login') }}\" style=\"margin-left:10px;\">ログインへ戻る</a>
      </div>
    </form>
  </div>
</body>
</html>
"""

@user_register_bp.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    from models import db, User  # models.pyからdb, Userをimport
    email = request.form.get("email")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    if not email or not password or not password2:
      flash("全ての項目を入力してください。", "danger")
    elif password != password2:
      flash("パスワードが一致しません。", "danger")
    elif User.query.filter_by(email=email).first():
      flash("このメールアドレスは既に登録されています。", "danger")
    else:
      user = User(email=email, password_hash=generate_password_hash(password))
      db.session.add(user)
      db.session.commit()
      flash("ユーザー登録が完了しました。ログインしてください。", "success")
      return redirect(url_for("login.login"))
  return render_template_string(REGISTER_TEMPLATE)
