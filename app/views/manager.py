from flask import redirect, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class ManagerModelView(ModelView):
    # idも表示させるようにする
    column_display_pk = True    
    
    # password列を非表示に
    column_exclude_list = ["password_hash"]
    
    form_create_rules = (
        "name",
        "email",
        "password_hash",
        "role"
    )
    form_edit_rules = (
        "name",
        "email",
        "role"
    )

    
    def on_model_change(self, form, model, is_created):
        if(is_created):    
            if form.password_hash.data:
                model.set_password(form.password_hash.data) 
                       
        print(current_user.is_authenticated)
    
    
    
    
    @property
    def can_edit(self):
        return current_user.role>=3
    @property
    def can_create(self):
        return current_user.role>=3
    @property
    def can_delete(self):
        return current_user.role>=3
    
    
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.login_view', next=request.url))