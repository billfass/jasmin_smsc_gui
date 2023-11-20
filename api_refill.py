from py4web import action, request
from .common import db, session, auth, flash, jasmin, api_resp, api_id
from pydal.validators import *
from .utils import cols_split
from .super_admin import api_popualate_database

def getCreds(user):
    juser = jasmin.users(["get_creds", user])

    if not len(juser) > 4:
        return {}

    cred = {}

    for j in juser[2:-1]:
        r = str.split(j)

        if r[1] == "defaultvalue":
            cred["default_"+r[2]] = r[3]
        elif r[1] == "quota":
            cred["quota_"+r[2]] = r[3]
        elif r[1] == "valuefilter":
            cred["value_"+r[2]] = r[3]
        elif r[1] == "authorization":
            cred["author_"+r[2]] = r[3]

    return cred

def refill(data, cred=None):
    try:
        user = data["uid"]
        balance = data["balance"]

        if cred == None or cred == {}:
            cred = getCreds(user)

        if cred == {}:
            return dict(code=404, message="User not found")

        if not balance == None:
            if not balance == "ND" and not cred["quota_balance"] == "ND":
                cred["quota_balance"] = float(cred["quota_balance"]) + float(balance)
            else:
                cred["quota_balance"] = balance

        cred["quota_balance"] = str(cred["quota_balance"])
            
        ret = jasmin.users(['update', user,
            cred["default_src_addr"],
            cred["quota_http_throughput"],
            cred["quota_balance"],
            cred["quota_smpps_throughput"],
            cred["quota_sms_count"],
            cred["quota_early_percent"],
            cred["value_priority"],
            cred["value_content"],
            cred["value_src_addr"],
            cred["value_dst_addr"],
            cred["value_validity_period"],
            cred["author_http_send"],
            cred["author_http_dlr_method"],
            cred["author_http_balance"],
            cred["author_smpps_send"],
            cred["author_priority"],
            cred["author_http_long_content"],
            cred["author_src_addr"],
            cred["author_dlr_level"],
            cred["author_http_rate"],
            cred["author_validity_period"],
            cred["author_http_bulk"]])

        if ret:
            return dict(code=403, message=ret)
    except Exception as e:
        return dict(code=403, message=str(e))
    
    return dict(code=200, balance=cred["quota_balance"], message='User credentials updated')

def replace(data):
    try:
        user = data["uid"]
        balance = data["balance"]

        cred = getCreds(user)

        if cred == {}:
            return dict(code=404, message="User not found")

        if not balance == None:
            cred["quota_balance"] = balance
        
        cred["quota_balance"] = str(cred["quota_balance"])
            
        ret = jasmin.users(['update', user,
            cred["default_src_addr"],
            cred["quota_http_throughput"],
            cred["quota_balance"],
            cred["quota_smpps_throughput"],
            cred["quota_sms_count"],
            cred["quota_early_percent"],
            cred["value_priority"],
            cred["value_content"],
            cred["value_src_addr"],
            cred["value_dst_addr"],
            cred["value_validity_period"],
            cred["author_http_send"],
            cred["author_http_dlr_method"],
            cred["author_http_balance"],
            cred["author_smpps_send"],
            cred["author_priority"],
            cred["author_http_long_content"],
            cred["author_src_addr"],
            cred["author_dlr_level"],
            cred["author_http_rate"],
            cred["author_validity_period"],
            cred["author_http_bulk"]])

        if ret:
            return dict(code=403, message=ret)
    except Exception as e:
        return dict(code=403, message=str(e))
    
    return dict(code=200, balance=cred["quota_balance"], message='User credentials updated')

@action('api/refill/<action>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def refill_manage(action=None):
    ret = api_id(request)
    if ret:
        return api_resp(dict(), 400, ret)
    
    data = request.POST

    try:
        if action == "add":
            ret = refill(data)
        elif action == "replace":
            ret = replace(data)
    except Exception as e:
        return api_resp(dict(request.POST), 400, str(e))

    try:
        api_popualate_database()
    except Exception as e:
        message=str(e)

    return api_resp(dict(data), ret["code"], ret["message"])

