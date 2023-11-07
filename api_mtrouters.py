from py4web import action, request
from .common import db, session, auth, flash, jasmin, api_resp, api_id
from pydal.validators import *
from .utils import cols_split
from .route_manager import mt_routes
from .super_admin import api_popualate_database

def switch(data):
    try:
        cnt = False
        for rt in mt_routes():
            if "connector" in data["query"] and rt :
                cnt = True
    except Exception as e:
        return str(e)

    return ""

def get_order():
    order = 0
    try:
        ods = []
        for r in mt_routes():
            ods.append(int(r["r_order"]))
        order = max(ods)+1
    except Exception as e:
        return 0
    return order

def new_mtrouter(data):
    try:
        if not "order" in data:
            data["order"] = get_order()

        resp = jasmin.mtrouter([str(data["type"]), str(data["order"]), str(data["connector"]), str(data["filters"]), str(data["rate"])])
        if resp:
            dict(code=400, data=data, message=resp)
    except Exception as e:
        dict(code=400, data=data, message=str(e))
    
    return dict(code=200, data=data, message='Added mtrouter')

@action('api/mtrouters/<action>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def groups_manage(action=None):
    ret = api_id(request)
    if ret:
        return api_resp(dict(), 400, ret)
    
    data = request.POST

    try:
        if action == "create":
            ret = new_mtrouter(data)
            data = ret['data']
        elif action == "switch":
            ret = switch(data)
        elif action == "get":
            return api_resp(mt_routes(), 200, "MT Routers")
        else:
            return api_resp(dict(data), 400, 'Undefined action')
    except Exception as e:
        return api_resp(dict(request.POST), 400, str(e))

    try:
        api_popualate_database()
    except Exception as e:
        message=str(e)

    return api_resp(dict(data), ret["code"], ret["message"])

