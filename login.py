from flask import Blueprint, render_template_string, request, redirect, url_for

login_bp = Blueprint("login", __name__)

LOGIN_TEMPLATE = """
<!doctype html>
<html lang=\"ja\">
<head>
  <meta charset=\"utf-8\"/>
  <title>Login</title>
  <style>
    body { background: #f8f8f8; }
    .login-box {
      width: 340px; margin: 60px auto; background: #fff;
      border-radius: 8px; box-shadow: 0 0 8px #b2d8e6;
      padding: 28px 28px 18px 28px; border: 2px solid #b2d8e6;
    }
    .login-title {
      text-align: center; color: #2cbfd9; font-size: 2em; font-weight: bold;
      margin-bottom: 10px; border-bottom: 2px solid #2cbfd9; padding-bottom: 6px;
    }
    .login-label { display: block; margin-top: 14px; margin-bottom: 4px; }
    .login-input { width: 100%; padding: 6px; font-size: 1em; }
    .login-actions { text-align: right; margin-top: 16px; }
    .login-btn {
      background: linear-gradient(#5fd0e6, #2cbfd9);
      color: #fff; border: none; border-radius: 6px;
      padding: 8px 28px; font-size: 1.1em; font-weight: bold;
      box-shadow: 2px 2px 6px #b2d8e6;
      cursor: pointer;
    }
    .login-btn:active { box-shadow: none; }
    .login-remember { margin-top: 10px; }
    .register-link {
      display: inline-block; margin-top: 18px; text-align: center; width: 100%;
    }
    .register-link a {
      color: #2cbfd9; text-decoration: underline; font-size: 1em;
    }
  </style>
</head>
<body>
  <div class=\"login-box\">
    <div class=\"login-title\">Login</div>
    <form method=\"post\" action=\"{{ url_for('login.login') }}\">
      <label class=\"login-label\">Email</label>
      <input type=\"email\" name=\"email\" class=\"login-input\" required>
      <label class=\"login-label\">Password</label>
      <input type=\"password\" name=\"password\" class=\"login-input\" required>
      <div class=\"login-remember\">
        <input type=\"checkbox\" id=\"remember\" name=\"remember\">
        <label for=\"remember\" style=\"font-size:0.95em;\">パスワードを保存</label>
      </div>
      <div class=\"login-actions\">
        <button class=\"login-btn\" type=\"submit\">Login</button>
      </div>
    </form>
    <div class=\"register-link\">
      <a href=\"{{ url_for('user_register.register') }}\">ユーザー登録はこちら</a>
    </div>
  </div>
</body>
</html>
"""



from flask import session, flash
from werkzeug.security import check_password_hash

@login_bp.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    from models import User  # models.pyからUserをimport
    email = request.form.get("email")
    password = request.form.get("password")
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
      session["logged_in"] = True
      session["user_id"] = user.id
      return redirect(url_for("index"))
    else:
      flash("メールアドレスまたはパスワードが間違っています。", "danger")
  # GET時は未ログイン状態にする
  session["logged_in"] = False
  return render_template_string(LOGIN_TEMPLATE)
