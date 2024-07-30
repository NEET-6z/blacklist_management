import os

from dotenv import dotenv_values, load_dotenv
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import LoginManager
from flask_migrate import Migrate

# 環境変数を読み込みconfigに代入
load_dotenv()
config = dotenv_values()


login_manager = LoginManager() 



from app.admin_index import MyAdminIndexView
from app.models import BlackList, Manager
from app.views import BlackListModelView, ManagerModelView


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(config)

    from app.db import db
    db.init_app(app)
    # flask db migrateを有効に
    migrate = Migrate(app,db)
    
    # flask-loginの設定
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login_view'
    
   
    
    with app.app_context():
        db.create_all()

    with app.app_context():    
        admin_user = Manager.query.filter_by(name='admin').first()
        if admin_user is None:
            admin_password = os.getenv('ADMIN_PASSWORD')
            if admin_password:
                admin_user = Manager(
                    name='admin',
                    email='admin@example.com',
                    role=3
                )
                admin_user.set_password(admin_password)
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created.")
    
    # indexviewにMyAdminIndexViewを指定
    admin = Admin(app, name="管理画面だぇ", template_mode="bootstrap4", index_view=MyAdminIndexView(name="ホーム"))
    admin.add_view(BlackListModelView(BlackList, db.session,"ブラックリスト"))
    admin.add_view(ManagerModelView(Manager,db.session,"管理者"))
    admin.add_link(MenuLink(name="ログアウト",url="/admin/logout"))
    return app
