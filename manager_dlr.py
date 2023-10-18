from py4web import action, request
from .common import db, session, auth, flash, jasmin
from pydal.validators import *
from .utils import cols_split
from .user_manager import list_groups
from .route_manager import mt_routes
from .filter_manager import list_filters
import requests

def log(sec, uuid, code):
    from datetime import datetime

    if sec == "api1":
        db.api_dlr_log.insert(uuid=uuid, code=code, date=datetime.now().isoformat(), sec=sec)
    elif sec == "api2":
        db.api_dlr_log.insert(uuid=uuid, code=code, date=datetime.now().isoformat(), sec=sec)
    elif sec == "web1":
        db.dlr_log.insert(uuid=uuid, code=code, date=datetime.now().isoformat(), sec=sec)
    elif sec == "web2":
        db.dlr_log.insert(uuid=uuid, code=code, date=datetime.now().isoformat(), sec=sec)

def dlr_1(sec, id, data):
    if sec == "web":
        have_one = db(db.dlr_1.uuid == data['id']).select().first()
        if not have_one:
            db.dlr_1.insert(message_id=id, uuid=data['id'], connector=data['connector'], level=data['level'], message_status=data['message_status'], send=0)    
        elif have_one.send != "0":
            return 'ACK/Jasmin'
        
        r = requests.post("https://fastermessage.com/app2/sms/batch/dlr/1/"+sec+"/"+data["id"], data={}, headers={})
    else:
        have_one = db(db.api_dlr_1.uuid == data['id']).select().first()
        if not have_one:
            db.api_dlr_1.insert(message_id=id, uuid=data['id'], connector=data['connector'], level=data['level'], message_status=data['message_status'], send=0)    
        elif have_one.send != "0":
            return 'ACK/Jasmin'
    
        r = requests.post("https://fastermessage.com/app2/sms/batch/dlr/1/"+sec+"/"+data["id"], data={}, headers={})

    log(sec+1, data["id"], r.status_code)

    if r.status_code == 200:
        if sec == "web":
            db.dlr_1.update(db.dlr_1.uuid == data['id'], send=1)
        else:
            db.api_dlr_1.update(db.api_dlr_1.uuid == data['id'], send=1)
        return 'ACK/Jasmin'
    else:
        return r.status_code

def dlr_2(sec, id, data):
    if sec == "web":
        have_one = db(db.dlr_2.uuid == data['id']).select().first()
        if not have_one:
            db.dlr_2.insert(message_id=id, uuid=data['id'], level=data['level'], message_status=data['message_status'], send=0)    
        elif have_one.send != "0":
            return 'ACK/Jasmin'
        
        r = requests.post("https://fastermessage.com/app2/sms/batch/dlr/2/"+sec+"/"+data["id"], data={}, headers={})
    else:
        have_one = db(db.api_dlr_2.uuid == data['id']).select().first()
        if not have_one:
            db.api_dlr_2.insert(message_id=id, uuid=data['id'], level=data['level'], message_status=data['message_status'], send=0)    
        elif have_one.send != "0":
            return 'ACK/Jasmin'
        
        r = requests.post("https://fastermessage.com/app2/sms/batch/dlr/2/"+sec+"/"+data["id"], data={}, headers={})

    log(sec+2, data["id"], r.status_code)

    if r.status_code == 200:
        if sec == "web":
            db.dlr_2.update(db.dlr_2.uuid == data['id'], send=1)
        else:
            db.api_dlr_2.update(db.api_dlr_2.uuid == data['id'], send=1)
        return 'ACK/Jasmin'
    else:
        return r.status_code
    
@action('callback/<sec>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def callback(sec="web"):
    data = request.GET

    try:
        statusText = data["statusText"]
        r = str.split(statusText, '"')
        data['id'] = r[1]
        data['batchId'] = data['batchId']
        data['to'] = data['to']
        data['status'] = data['status']
    except Exception as e:
        return str(e)
    
    if sec == "web":
        db.callback.update_or_insert(db.callback.uuid == data['id'], uuid=data['id'], batchuuid=data['batchId'], status=data['status'], to=data['to'])
    else:
        db.api_callback.update_or_insert(db.api_callback.uuid == data['id'], uuid=data['id'], batchuuid=data['batchId'], status=data['status'], to=data['to'])

    return 'ACK/Jasmin'

@action('dlr/<sec>/<id>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def dlr(sec="web", id=None):
    data = request.POST

    try:
        data['id'] = data['id']
        data['level'] = data['level']
        data['message_status'] = data['message_status']
    except Exception as e:
        log(sec, id, str(e))
        return str(e)
    
    if data["level"] == 1:
        return dlr_1(sec, id, data)
    else:
        return dlr_2(sec, id, data)

@action('dlr/data/<niv>/<sec>/<uuid>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def data_dlr(niv="1", sec="web", uuid=None):
    callback = None
    data_dlr = None
    connector = None
    
    if sec+niv == "web1":
        callback = db(db.callback.uuid == uuid).select().first()
        data_dlr = db(db.dlr_1.uuid == uuid).select().first()
        if data_dlr: connector = data_dlr.connector
    elif sec+niv == "web2":
        callback = db(db.callback.uuid == uuid).select().first()
        data_dlr = db(db.dlr_2.uuid == uuid).select().first()
    elif sec+niv == "api1":
        callback = db(db.api_callback.uuid == uuid).select().first()
        data_dlr = db(db.api_dlr_1.uuid == uuid).select().first()
        if data_dlr: connector = data_dlr.connector
    elif sec+niv == "api2":
        callback = db(db.api_callback.uuid == uuid).select().first()
        data_dlr = db(db.api_dlr_2.uuid == uuid).select().first()
    
    if callback == None or data_dlr == None:
        return dict({})
    
    return dict({'connector':connector, 'messageId':data_dlr.message_id, 'id':data_dlr.uuid, 'level':data_dlr.level, 'message_status':data_dlr.message_status, 'batchId':callback.batchuuid, 'status':callback.status, 'to':callback.to})
