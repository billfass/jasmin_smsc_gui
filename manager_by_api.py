from py4web import action, request
from .common import db, session, auth, flash, jasmin
from pydal.validators import *
from .utils import cols_split
from .user_manager import list_groups
from .route_manager import mt_routes
from .filter_manager import list_filters
from .super_admin import api_popualate_database, get_mtroutes

def api_resp(items=[], code=200, message=''):
    if code == 200:
        flash.set(message, "success")
        status="success"
    else:
        flash.set(message, "danger")
        status="fail"

    return dict(api_version="",timestamp=datetime(),code=code,status=status, items=items, message=message)

def datetime(date_string=None,date_format=None):
    from datetime import datetime

    # Obtenir la date et l'heure
    if not date_string or date_string.lower()=="now":
        current_datetime = datetime.now()
    else:
        # Définir un objet datetime à partir de la chaîne en spécifiant le format
       current_datetime = datetime.strptime(date_string, date_format)
    
    # Formater la date et l'heure au format ISO 8601
    iso8601_datetime = current_datetime.isoformat()
    return iso8601_datetime

def refill_user(data):
    try:
        user = data["uid"]
        balance = data["balance"]

        juser = jasmin.users(["get_creds", user])

        if not juser:
            return dict(code=404, message="User '%s' could not be found" % (user))

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

        if not balance == "ND" and not cred["quota_balance"] == "ND":
            cred["quota_balance"] = float(cred["quota_balance"]) + float(balance)
        else:
            cred["quota_balance"] = balance
            
        ret = jasmin.users(['update', user,
                            cred["default_src_addr"],
                            cred["quota_http_throughput"],
                            str(cred["quota_balance"]),
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
    
        return dict(code=200, balance=cred["quota_balance"], message='User credentials updated')
    except Exception as e:
        return dict(code=403, message=str(e))

def new_filter(data):
    try:
        data["fid"]=data["fid"]
        data["ftype"]=data["ftype"]
        data["fvalue"]=data["fvalue"]
    except Exception as e:
        return dict(code=403, message=str(e))
    
    ret=jasmin.filters(['create', data["fid"], data["ftype"], data["fvalue"]])

    if ret:
        return dict(code=400, message=ret)
    
    return dict(code=200, message='Added filter %s' %data)
        
def del_filter(fid):
    if not fid:
        flash.set('You need to select a filter to delet')

    res = jasmin.filters(['delete',  fid])
    
    flash.set('Removed Filter %s' % fid)
    
    query = db.mt_filter.fid == fid
    db(query).delete()

def new_user(data):
    try:
        data["uid"]=data["uid"]
        data["username"]=data["username"]
        data["password"]=data["password"]
        data["group"]=data["group"]
        data["balance"]=data["balance"]
    except Exception as e:
        return dict(code=403, message=str(e))
    
    ret = jasmin.users(['create_user', data['uid'], data['username'], data['password'], data['group']])

    if ret:
        return dict(code=400, message=ret)
    
    data["fid"] = data['uid']
    data["ftype"] = "UserFilter"
    data["fvalue"] = data['uid']
    ret = new_filter(data)
    if not ret["code"] == 200:
        return dict(code=ret["code"], message=ret["message"])
    
    ret = refill_user(data)
    if not ret["code"] == 200:
        return dict(code=ret["code"], message=ret["message"])

    return dict(code=200, balance=ret["balance"], message='Added user %s' %data['username'])

def mtrouter(data):
    return dict(code=200, id="", message='Added mtrouter')

@action('api/groups/get', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def groups():
    data = request.GET
    return api_resp(list_groups(), 200, "Group's user")

@action('api/filters/get', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def groups():
    data = request.GET
    return api_resp(list_filters(), 200, "Filters")

@action('api/users/<action>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def user_cred(action=None):
    data = request.POST

    if action == "add":
        ret = new_user(data)
    elif action == "refill":
        ret = refill_user(data)
    elif action == "mtrouter":
        ret = mtrouter(data)
    else:
        return api_resp(dict(data), 400, 'Undefined action')
    
    try:
        api_popualate_database()
    except Exception as e:
        message=str(e)
    
    return api_resp(dict(data), ret["code"], ret["message"])

@action('api/filters/<action>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def filters_manage(action=None):
    data = request.POST

    if action == "add":
        ret = new_filter(data)
    elif action == "update":
        del_filter(data["fid"])
        ret = new_filter(data)
    else:
        return api_resp(dict(data), 400, 'Undefined action')

    try:
        api_popualate_database()
    except Exception as e:
        message=str(e)
    
    return api_resp(dict(data), ret["code"], ret["message"])

@action('api/mt_routes/<usr>/<order>/<rate>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def filters_manage(usr=None,order=None,rate=None):
    if(not usr or not order or not rate):
        return api_resp(dict(user=usr, order=order, rate=rate), 404, "Invalid parameter")
    
    try:
        rate = float(rate)
        order = int(order)
        
        # resp = jasmin.mtrouter(['StaticMTRoute', order, 'smppc(bj_mtn)', usr+';bj;', rate])
        # if resp:
        #     return api_resp(dict(user=usr, order=order, rate=rate), 400, resp)
        
        order = order + 1
        resp = jasmin.mtrouter(['StaticMTRoute',order, 'smppc(bj_moov)', usr+';bj_moov;', rate])
        if resp:
            return api_resp(dict(user=usr, order=order, rate=rate), 400, resp)
        
        order = order + 1
        resp = jasmin.mtrouter(['StaticMTRoute',order, 'smppc(bj_moov)', usr+';bj_celtiis;', rate])
        if resp:
            return api_resp(dict(user=usr, order=order, rate=rate), 400, resp)
        
        try:
            api_popualate_database()
        except Exception as e:
            message=str(e)
    except Exception as e:
        return api_resp(dict(user=usr, order=order, rate=rate), 400, str(e))
    
    return api_resp(dict(user=usr, order=order, rate=rate), 200, "Adds mt routers")

@action('api/stats/<usr>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def user_stats(usr:None):
    tt = jasmin.stats(['user',usr])
    stats = []
    for t in tt[2:-1]:
        stat = []
        r = str.split(t)
        l = len(r)
        if l ==4:
            ite = r[0][1:]
            tpe = r[1]+r[2]
            val = r[3]
        else:
            ite = r[0][1:]
            tpe = r[1]+r[2]
            if r[0][1:4] == 'bou':
                val = r[3]+" "+r[4]+" "+r[5]+" "+r[6]+" "+r[7]+" "+r[8]
            else:
                val = r[3]+" "+r[4]
        # if tpe == "HTTPApi" :
        stat.append(ite)
        stat.append(tpe)
        stat.append(val)
        stats.append(stat)
    return api_resp(dict(stats))