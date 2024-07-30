from flask import flash, redirect, url_for
from flask_admin import AdminIndexView, expose
from flask_login import current_user, login_user, logout_user

from app.db import db
from app.forms import LoginForm
from app.models import Manager


class MyAdminIndexView(AdminIndexView):
    
    # ログインしてないなら自動でログイン画面に遷移
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        form = LoginForm()
        if form.validate_on_submit():
            manager = Manager.query.filter_by(name=form.name.data).first()
            if manager and manager.check_password(form.password.data):
                login_user(manager)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('.index'))
            else:
                flash('Invalid name or password.', 'danger')
        return self.render('admin/login.html', form=form)


    @expose('/logout/')
    def logout_view(self):
        logout_user()
        flash('Logged out successfully.', 'success')
        return redirect(url_for('.login_view'))
    
