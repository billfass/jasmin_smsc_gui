from py4web import action, request
from .common import db, session, auth, flash, jasmin, api_resp, api_id
from pydal.validators import *
from .utils import cols_split
from .user_manager import list_users, list_groups
from .api_groups import new_group
from .api_refill import getCreds, refill
from .api_filters import new_filter
from .super_admin import api_popualate_database

def new_user(data):
    try:
        data["balance"]=data["balance"]
        
        create = True
        for grp in list_groups():
            if grp["gid"] == data["group"]:
                create = False

        if create:
            ret = new_group(dict(gid=data["group"]))
            if not ret["code"] == 200:
                return ret

        creds = getCreds(data['uid'])
        balance = "ND"
        
        if not creds == {}:
            balance = creds['quota_balance']
            jasmin.users(['remove_user', data['uid']])

        ret = jasmin.users(['create_user', data['uid'], data['username'], data['password'], data['group']])
        if ret:
            return dict(code=400, message=ret)
        
        if not data["balance"] == "ND" and not balance == "ND":
            ret = refill(dict(uid=data["uid"], balance=balance))
            if not ret["code"] == 200:
                return ret
            
        if creds == {}:
            new_filter(dict(fid=data['uid'], ftype="UserFilter", fvalue=data['uid']))
        
        ret = refill(data)
        if not ret["code"] == 200:
            return ret
    except Exception as e:
        return dict(code=403, message=str(e))
    
    return dict(code=200, balance=ret["balance"], message='Added user %s' %data['username'])

@action('api/users/<action>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def users_manage(action=None):
    ret = api_id(request)
    if ret:
        return api_resp(dict(), 400, ret)
    
    data = request.POST

    for grp in list_groups():
        return api_resp(grp["gid"], 200, "Users")

    try:
        if action == "create":
            ret = new_user(data)
        elif action == "list":
            return api_resp(list_users(), 200, "Users")
        else:
            return api_resp(dict(data), 400, 'Undefined action')
    except Exception as e:
        return api_resp(dict(request.POST), 400, str(e))

    try:
        api_popualate_database()
    except Exception as e:
        message=str(e)

    return api_resp(dict(data), ret["code"], ret["message"])
