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
    
def array_comp(fi=[], ty=3, dd=[]):
    sy = False
    if fi == []:
        sy = True

    if ty==0:
        for f in fi:
            if f in dd:
                sy = True
                break
    
    elif ty==1 or ty == 2:
        l = 0
        for f in fi:
            if f in dd:
                l += 1
        
        if ty == 2 and l == len(fi) and l == len(dd):
            sy = True
        elif ty==1 and l == len(fi):
            sy = True
        
    return sy

def string_comp(fi=None, dd=''):
    if fi == None:
        return True

    if str(fi) == dd:
        return True
    
    return False

def setting_route(setting=None, route=None):
    if setting['con'] == None:
        setting['con'] = route['connectors']

    if setting['fil'] == None:
        setting['fil'] = route['filters']

    if setting['rat'] == None:
        setting['rat'] = route['rate']

    order = route['order']
    type = route['type']
    rate = str(setting['rat'])

    cons = ''
    for c in setting['con']:
        if not cons == '':
            cons += ';'
        cons = 'smppc('+c+')'

    filters = ''
    for f in setting['fil']:
        filters += f+';'

    if not order == '' and not type == '' and not rate == '' and not cons == '' and not filters == '':
        try:
            jasmin.mtrouter(['remove', order])
            new_mtrouter(dict(type=type, order=order, rate=rate, connector=cons, filters=filters))
        except Exception as e:
            message=str(e)

def switch(data):
    try:
        iv = dict(cn=False, ft = False, od = False, tp = False)

        if not "c_type" in data["query"]:
            c_type = 3
        else:
            c_type = int(data["c_type"])

        if not "f_type" in data["query"]:
            f_type = 3
        else:
            f_type = int(data["f_type"])

        if "connectors" in data["query"]:
            q_connectors = data["query"]["connectors"]
        else:
            q_connectors = []
            iv['cn'] = True

        if "filters" in data["query"]:
            q_filters = data["query"]["filters"]
        else:
            q_filters = []
            iv['ft'] = True

        if "order" in data["query"]:
            q_order = data["query"]["order"]
        else:
            q_order = None
            iv['od'] = True

        if "type" in data["query"]:
            q_type = data["query"]["type"]
        else:
            q_type = None
            iv['tp'] = True

        if iv['cn'] and iv['ft'] and iv['od']:
            return dict(code=400, data=data, message="Query syntaxe error")
        
        stt = dict()

        if "connectors" in data["set"]:
            stt['con'] = data["set"]["connectors"]
        else:
            stt['con'] = None

        if "filters" in data["set"]:
            stt['fil'] = data["set"]["filters"]
        else:
            stt['fil'] = None

        if "rate" in data["set"]:
            stt['rat'] = data["set"]["rate"]
        else:
            stt['rat'] = None

        if stt['con'] == None and stt['fil'] == None and stt['rat'] == None:
            return dict(code=400, data=data, message="Setting syntaxe error")
        
        matchs = []
        for route in list_mtroutes():
            vv = iv
            vv['cn'] = array_comp(q_connectors, c_type, route['connectors'])
            vv['ft'] = array_comp(q_filters, f_type, route['q_filters'])
            vv['od'] = string_comp(q_order, route['order'])
            vv['tp'] = string_comp(q_type, route['type'])

            if vv['cn'] and vv['ft'] and vv['od'] and vv['tp']:
                matchs.append(route['order'])
                setting_route(stt, route)
                        
        data['match'] = matchs
    except Exception as e:
        return dict(code=400, data=data, message=str(e))

    return dict(code=200, data=data, message="Successfull switched")

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

