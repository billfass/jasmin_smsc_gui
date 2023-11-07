from py4web import action, request
from .common import db, session, auth, flash, jasmin, api_resp, api_id
from pydal.validators import *
from .utils import cols_split
from .route_manager import mt_routes
from .filter_manager import list_filters
from .super_admin import api_popualate_database

def list_mtroutes():
    import re
    con_regex = '.*\((.*?)\).*'
    fil_regex = '.*\<(.*?)\>.*'

    routers = []
    filters = {}

    for f in list_filters():
        idx = str(f["filter_type"])+str(f["description"])
        filters[idx] = f["filter_id"]
    
    for route in mt_routes():
        cids = []
        fids = []
        
        c_split = route['r_connectors'].split()
        for con in c_split:
            matches = re.search(con_regex, con)
            connector = matches.group(1)
            if 'smpp' in con:
                cids.append(connector)
            else:
                print('MT ROUTES RE HTTP CONNECTORS', con, connector)

        f_split = route['r_filters'].split(', ')
        for f in f_split:
            f_type = ''
            f_val = ''
            if '<DA' in f:
                f_type = 'DestinationAddrFilter'
                matches = re.search(fil_regex, f)
                if matches:
                    line = matches.group(1)
                    f_val = line.split('=')[1]
                    if(line[-1] == ")"):
                        f_val = f_val[:-1]
            elif '<U' in f:
                f_type = 'UserFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]
            elif 'SA' in f:
                f_type = 'SourceAddrFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]
            elif 'SM' in f:
                f_type = 'ShortMessageFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]    
            elif 'DI' in f:
                f_type = 'DateIntervalFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line
            elif 'TI' in f:
                f_type = 'TimeIntervalFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line
            elif 'TG' in f:
                f_type = 'TagFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]

            elif 'G' in f:    
                f_type = 'GroupFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]
            
            elif '<T>' in f:
                f_type = 'TransparentFilter'
            else:    
                continue 

            if f_type+f_val in filters:
                fids.append(filters[f_type+f_val])
        
        routers.append(dict(order=route['r_order'], type=route['r_type'], connectors=cids, filters=fids, rate=route['r_rate']))

    return routers
    

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

    return list_mtroutes()

    try:
        if action == "create":
            ret = new_mtrouter(data)
            data = ret['data']
        elif action == "switch":
            ret = switch(data)
        elif action == "list":
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

