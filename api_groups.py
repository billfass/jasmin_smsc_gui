from py4web import action, request
from .common import db, session, auth, flash, jasmin, api_resp, api_id
from pydal.validators import *
from .utils import cols_split
from .user_manager import list_groups, remove_group
from .api_filters import new_filter
from .api_mtrouters import bj_routers_by_group
from .super_admin import api_popualate_database
import json

def new_group(data):
    try:
        ret=jasmin.users(['create_group', data["gid"]])
        if ret:
            return dict(code=400, message=ret)
        
        ret = new_filter(dict(fid=data["gid"], ftype="GroupFilter", fvalue=data["gid"]))
        if not ret["code"] == 200:
            return ret
        
        bj_routers_by_group(data)
    except Exception as e:
        return dict(code=403, message=str(e))
    
    return dict(code=200, message='Added group %s' %data)

def restore_group(data):
    try:
        return dict(code=400, message='here')
        for grp in list_groups():
            remove_group(grp["gid"])

        for grp in data:
            ret=jasmin.users(['create_group', grp["gid"]])
            if ret:
                return dict(code=400, message=ret)

    except Exception as e:
        return dict(code=403, message=str(e))
    
    return dict(code=200, message='Restore groups %s' %data)

@action('api/groups/<action>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def groups_manage(action=None):
    ret = api_id(request)
    if ret:
        return api_resp(dict(), 400, ret)
    
    try:
        if action == "create":
            data = request.POST
            ret = new_group(data)
        elif action == "restore":
            data = request.json
            try:
                # Lire le contenu brut du body (sinon, request.json ne fonctionnera pas après)
                raw_body = request.body.read().decode("utf-8")  

                # Re-parsing du JSON (car après .read(), request.json sera None)
                parsed_json = json.loads(raw_body) if raw_body else None  

                # Retourner les informations en JSON
                return {
                    "status": "success",
                    # "data": dict(data),
                    "headers": dict(request.headers),  # Convertir les headers en dictionnaire
                    "raw_body": raw_body,
                    "parsed_json": parsed_json
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}
            for grp in data:
                return dict()
            ret = restore_group(data)
        elif action == "list":
            return api_resp(list_groups(), 200, "Group's user")
        else:
            return api_resp(dict(), 400, 'Undefined action')
    except Exception as e:
        return api_resp(dict(request.POST), 400, str(e))

    try:
        api_popualate_database()
    except Exception as e:
        message=str(e)

    return api_resp(dict(), ret["code"], ret["message"])

