from flask import flash, redirect, request, url_for
from flask_admin import expose
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms import StringField

from app.db import db
from app.models import BlackList


class BlackListModelView(ModelView):
    column_display_pk = True    
    column_list = ["name", "reason", "level", "state", "manager"]
    column_searchable_list = ["id", "name", "address", "reason"]
    column_filters = ["id", "name", "address", "reason", "level", "state", "created_at"]
    column_labels = {
        "name": "名前",
        "reason": "理由",
        "level": "危険度",
        "state": "状態",
        "manager": "担当者"
    }
    column_formatters = {
        "state": lambda v, c, m, p: '済' if getattr(m, p) else '未済',
        'reason': lambda v, c, m, p: (getattr(m, p)[:20] + '...') if len(getattr(m, p, '')) > 20 else getattr(m, p),
    }
    can_view_details = True
    form_extra_fields = {
        "postcode": StringField(label="郵便番号")
    }
    form_columns = [
        "name",
        "reason",
        "postcode",
        "address",
        "level",
        "state",
        "manager"
    ]
    form_widget_args = {
        "name": {
            "placeholder": "田中太郎",
        },
        "reason": {
            "rows": 10,
        }
    }
    column_descriptions = {
        "name": "名前を入力してください",
        "postcode": "郵便番号を入力すると自動で住所が入力されます",
        "address": "住所を入力してください",
        "level": "危険度を1から5の整数で入力してください",
        "state": "制裁済みか",
        "manager": "担当者を追加してください"
    }

    @expose("/get_address/<string:postcode>/", methods=["GET"])
    def get_address(self, postcode):
        from jusho import Jusho
        postman = Jusho()
        addresses = postman.by_zip_code(postcode)
        if addresses:
            res = addresses[0].concat_kanji.replace("　", "")
            return res
        else:
            return ""

    create_template = "/blacklist/create.html"
    edit_template = "/blacklist/edit.html"
        
    @property
    def editable(self):
        return current_user.role >= 2
    
    @property
    def creatable(self):
        return current_user.role >= 2
    
    @property
    def deletable(self):
        return current_user.role >= 2
    
    @action('update', 'Update', '一括 True ok?')
    def action_update_state(self, ids):
        try:
            query = BlackList.query.filter(BlackList.id.in_(ids))
            for staff in query.all():
                staff.state = True
            db.session.commit()
            flash('Successfully updated')
        except Exception as ex:
            db.session.rollback()
            if not self.handle_view_exception(ex):
                raise
            flash('Failed to update')

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.login_view', next=request.url))

class ManagerModelView(ModelView):
    column_display_pk = True    
    column_exclude_list = ["password_hash"]
    form_create_rules = ("name", "email", "password_hash", "role")
    form_edit_rules = ("name", "email", "role")

    def on_model_change(self, form, model, is_created):
        if is_created and form.password_hash.data:
            model.set_password(form.password_hash.data) 

    @property
    def editable(self):
        return current_user.role >= 3
    
    @property
    def creatable(self):
        return current_user.role >= 3
    
    @property
    def deletable(self):
        return current_user.role >= 3
    
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.login_view', next=request.url))