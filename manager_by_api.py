from py4web import action, request
from .common import db, session, auth, flash, jasmin
from pydal.validators import *
from .utils import cols_split
from .user_manager import list_groups

def api_resp(items=[], code=200):
    if code == 200:
        status="success"
    else:
        status="fail"

    return dict(api_version="",timestamp=datetime(),code=code,status=status, items=items)

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

def new_user():
    data = request.POST

    try:
        data["uid"]=data["uid"]
        data["username"]=data["username"]
        data["password"]=data["password"]
        data["group"]=data["group"]
    except Exception as e:
        flash.set(str(e), "danger")
        return api_resp(dict(data), 403)
    
    ret=jasmin.users(['create_user',data['uid'],data['username'], data['password'], data['group']])

    if ret:
        flash.set(ret, "danger")
        return api_resp(dict(data), 400)
    else:
        flash.set('Added user %s' %data['username'], "success")

    return api_resp(dict(data))

def refill_user(data):
    user = data["uid"]

    try:
        add_balance = data["balance"]
        query = db.j_user_cred.juser == user
        juser = db(query).select().first()
        default_src_addr = juser.default_src_addr
        quota_http_throughput = juser.quota_http_throughput
        quota_balance = juser.quota_balance
        quota_smpps_throughput = juser.quota_smpps_throughput
        quota_sms_count = juser.quota_sms_count
        quota_early_percent = juser.quota_early_percent
        value_priority = juser.value_priority
        value_content = juser.value_content
        value_src_addr = juser.value_src_addr
        value_dst_addr = juser.value_dst_addr
        value_validity_period = juser.value_validity_period
        author_http_send = juser.author_http_send
        author_http_dlr_method = juser.author_http_dlr_method
        author_http_balance = juser.author_http_balance
        author_smpps_send = juser.author_smpps_send
        author_priority = juser.author_priority
        author_http_long_content = juser.author_http_long_content
        author_src_addr = juser.author_src_addr
        author_dlr_level = juser.author_dlr_level
        author_http_rate = juser.author_http_rate
        author_validity_period = juser.author_validity_period
        author_http_bulk = juser.author_http_bulk
    except Exception as e:
        flash.set(str(e), "danger")
        return api_resp(dict(data), 403)
    
    if juser:
        db.j_user_cred.juser.readable = db.j_user_cred.juser.writable = False
        db.j_user_cred.juser.default = user
        db.j_user_cred.id.readable = db.j_user_cred.id.writable = False
        
        flash.set('Please refer to the Jamsin user manual when updating values')

        if not add_balance == "ND" and not quota_balance == "ND":
            quota_balance += add_balance
        else:
            quota_balance = add_balance

        ret = jasmin.users(['update', user, \
            default_src_addr,quota_http_throughput,quota_balance,quota_smpps_throughput,\
            quota_sms_count,quota_early_percent,value_priority,value_content,value_src_addr,\
            value_dst_addr,value_validity_period,author_http_send,author_http_dlr_method,\
            author_http_balance,author_smpps_send,author_priority,author_http_long_content,author_src_addr,\
            author_dlr_level,author_http_rate,author_validity_period,author_http_bulk])
        
        if not ret:
            flash.set('User credentials updated', "success")
        else:
            flash.set('Unable to update credentials', "warning")
            return api_resp(dict(data), 400)
    else:
        flash.set("User '%s' could not be found" % (user), "danger")
        return api_resp(dict(data), 404)

    data["new_balance"] = quota_balance
    return api_resp(dict(data))

@action('api/groups/get', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def groups():
    data = request.GET
    
    return api_resp(list_groups())

@action('api/users/<action>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def user_cred(action=None):
    data = request.POST

    if action == "refill":
        return refill_user(data)
    else:
        if action == "add":
            return new_user()
        
    flash.set('Undefined action', "danger")

    return api_resp(dict(data), 400) 
    
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