from flask import flash, redirect, request, url_for
from flask_admin import expose
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms import (BooleanField, PasswordField, RadioField, SelectField,
                     StringField, SubmitField, ValidationError)

from app.db import db
from app.models import BlackList


class BlackListModelView(ModelView):
    # idも表示させるようにする
    column_display_pk = True    
    
    # address列を非表示に
    column_exclude_list = ["address"]
    
    # 検索可能な列
    column_searchable_list = ["id","name","address","reason"]
    
    # フィルタリング可能な列
    column_filters = ["id","name","address","reason","level","state","created_at"]
    
    # 表示させる列名
    column_labels = {
        "name":"名前",
        "address":"住所",
        "reason":"理由",
        "level":"危険度",
        "state":"状態",
        "manager":"担当者"
    }
    
    # フィールドの値を変換する
    # state列がTrueなら済,Falseなら未済
    # reason列の表示させる文字数を20文字に制限
    column_formatters = {
        "state": lambda v, c, m, p: '済' if getattr(m, p) else '未済',
        'reason': lambda v, c, m, p: (getattr(m, p)[:20] + '...') if len(getattr(m, p, '')) > 20 else getattr(m, p),
    }
    
    # 詳細ビューを有効化
    can_view_details=True
    
    
    form_extra_fields = {        
        "postcode": StringField(label="郵便番号")
    }

    
    form_columns = [
        "name",
        "postcode",
        "address",
        "level",
        "state",
        "manager"
    ]
    
    form_widget_args = {
        "name":{
            "placeholder":"田中太郎",
        },

    }
    column_descriptions = {
        "name":"名前を入力してください",
        "postcode":"郵便番号を入力すると自動で住所が入力されます",
        "address": "住所を入力してください",
        "level": "危険度を1から5の整数で入力してください",
        "state": "制裁済みか",
        "manager": "担当者を追加してください"
    }
    
    @expose("/get_address/<string:postcode>/", methods=["GET"])
    def get_address(self, postcode):
        from jusho import Jusho
        postman = Jusho()
        if(len(postman.by_zip_code(postcode))>=1):
            res = postman.by_zip_code(postcode)[0].concat_kanji.replace("　","")
            return res
        else:
            return ""
        
    create_template = "/blacklist/create.html"
    edit_template = "/blacklist/edit.html"
        
        
    
    @property
    def can_edit(self):
        return current_user.role>=2
    @property
    def can_create(self):
        return current_user.role>=2
    @property
    def can_delete(self):
        return current_user.role>=2
    
    
    @action('update_dones', 'Update Dones', '一括 done ok?')
    def action_update_due_dates(self, ids):
        try:
            query = BlackList.query.filter(BlackList.id.in_(ids))
            for staff in query.all():
                staff.state = True
            db.session.commit()
            flash(f'Successfully')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(f'Failed')
    
    
    
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.login_view', next=request.url))
    
    
    