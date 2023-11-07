from py4web import action, request
from .common import db, session, auth, flash, jasmin, api_resp, api_id
from pydal.validators import *
from .utils import cols_split
from .filter_manager import list_filters
from .super_admin import api_popualate_database

def new_filter(data):
    try:
        ret=jasmin.filters(['create', data["fid"], data["ftype"], data["fvalue"]])
        if ret:
            return dict(code=400, message=ret)
    except Exception as e:
        return dict(code=403, message=str(e))
    
    return dict(code=200, message='Added filter %s' %data)

@action('api/filters/<action>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def filters_manage(action=None):
    ret = api_id(request)
    if ret:
        return api_resp(dict(), 400, ret)
    
    data = request.POST

    try:
        if action == "create":
            ret = new_filter(data)
        elif action == "list":
            return api_resp(list_filters(), 200, "Filters")
        else:
            return api_resp(dict(data), 400, 'Undefined action')
    except Exception as e:
        return api_resp(dict(request.POST), 400, str(e))

    try:
        api_popualate_database()
    except Exception as e:
        message=str(e)

    return api_resp(dict(data), ret["code"], ret["message"])

