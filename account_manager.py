from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash

from py4web import action, request, response, abort, redirect, URL
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

@action('auth/accounts', method=['GET'])
@action.uses(db, auth.user, "accounts.html", T)
def index():

    user    = auth.get_user()
   
    rows    = db(db.auth_user).select()

    return dict(rows=rows,user=user)

@action('auth/add_user', method=['GET', 'POST'])
@action.uses(db, session, auth.user, "add_user.html", T)
def add_user():
    user = auth.get_user()
    form = Form(db.auth_user,csrf_session=session,formstyle=FormStyleBulma)

    if form.accepted:
        redirect(URL('auth/accounts'))

    return dict(form=form,user=user)

@action('auth/edit_user/<user_id:int>',method=['GET', 'POST'])
@action.uses(db, session, auth.user, "edit_user.html", T)
def edit_user(user_id=None):

    assert user_id is not None
    u = db.auth_user[user_id]
    user = auth.get_user()

    if u is None:
        redirect(URL('auth/accounts'))

    form = Form(db.auth_user,record=u, deletable=False,csrf_session=session,formstyle=FormStyleBulma)
    auth.db.auth_user.id.readable = False
    auth.db.auth_user.id.writable = False
    if form.accepted:
       redirect(URL('auth/accounts'))

    return dict(form=form,user=user)


@action('auth/actif_user/<user_id:int>')
@action.uses(db,session,auth.user, T)
def actif_user(user_id=None):

    assert user_id is not None
   
    db(db.auth_user.id == user_id).update(action_token="")

    redirect(URL('auth/accounts'))

@action('auth/delete_user/<user_id:int>')
@action.uses(db,session,auth.user, T)
def delete_user(user_id=None):

    assert user_id is not None
    
    db(db.auth_user.id==user_id).delete()

    redirect(URL('auth/accounts'))
