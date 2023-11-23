from py4web import action, request
from .common import db, session, auth, flash, jasmin
from pydal.validators import *
from .utils import cols_split
from datetime import datetime
import requests, time

def log(sec, lev, uuid, code):
    db.dlr_log.insert(uuid=uuid, code=code, date=datetime.now().isoformat(), sec=sec+lev)

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
    
    db.callback.update_or_insert(db.callback.uuid == data['id'], uuid=data['id'], batchuuid=data['batchId'], status=data['status'], to=data['to'], date=datetime.now().isoformat())

    return 'ACK/Jasmin'

@action('errback/<sec>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def errback(sec="web"):
    data = request.GET

    try:
        data["statusText"] = data["statusText"]
        data['batchId'] = data['batchId']
        data['to'] = data['to']
        data['status'] = data['status']
    except Exception as e:
        return str(e)
    
    if sec == "web":
        r = requests.get("https://fastermessage.com/app/sms/errbatch/dlr/"+data['batchId']+"/"+data["to"]+"?batchId="+data["batchId"]+"&to="+data["to"]+"&statusText="+data["statusText"]+"&status="+data['status'], data={}, headers={})
    else:
        r = requests.get("https://api.fastermessage.com/v1/sms/errbatch/dlr/"+data['batchId']+"/"+data["to"]+"?batchId="+data["batchId"]+"&to="+data["to"]+"&statusText="+data["statusText"]+"&status="+data['status'], data={}, headers={})

    r.close()

    if r.status_code == 200:
        return 'ACK/Jasmin'
    
    return 'NOACK/Jasmin'

@action('dlr/<sec>/<id>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def dlr(sec="web", id=None):
    data = request.POST
    cpt = 0

    try:
        data['messageId'] = id
        data['id'] = data['id']
        data['level'] = data['level']
        data['message_status'] = data['message_status']

        callback = None
        while not callback and cpt < 5:
            cpt += 1
            callback = db(db.callback.uuid == data['id']).select().first()
            time.sleep(1)
        if not callback:
            return 'ACK/Jasmin'
        data['batchId'] = callback.batchuuid
        data['to'] = callback.to
        data['status'] = callback.status
    except Exception as e:
        # log(sec, 0, id, str(e))
        return str(e)
    
    try:
        if sec == "web":
            r = requests.post("https://fastermessage.com/app/sms/batch/dlr/"+data['level']+"/"+data["id"], data=dict(data), headers={})
        else:
            r = requests.post("https://api.fastermessage.com/v1/sms/batch/dlr/"+data['level']+"/"+data["id"], data=dict(data), headers={})
        
        r.close()
        
        # log(sec, data["level"], data["id"], r.status_code)
        
        if r.status_code == 200:
            db(db.callback.uuid == data['id']).delete()
            return 'ACK/Jasmin'
    except Exception as e:
        return str(e)
    
    return 'NOACK/Jasmin'

@action('callback/sms', method=['GET'])
@action.uses(db, session, auth, flash)
def send():
    data = request.GET
    dataCallback = []

    try:
        callbacks = db(db.callback.batchuuid == data["batchId"]).select()
    except Exception as e:
        callbacks = db(db.callback).select()
    
    for c in callbacks:
        dataCallback.append(dict(id=c.uuid,batchid=c.batchuuid,to=c.to,status=c.status))
    
    return dataCallback

@action('send/sms', method=['GET'])
@action.uses(db, session, auth, flash)
def send():
    phs = ["22967754089","22994551975","22966851608","22951578457","22964082731"]

    base = "x-api-key=08df092126a78b7382036efe152888507eea3c3689d6da17e91b6a4b1cd0525e&from=FASTERMSG&to=_1_&text=Ceci est un test de Fastermessage sur le _1_, merci de ne pas en tenir compte."
    
    rsp = {}

    for p in phs:
        t=base.replace("_1_", p)
        
        r = requests.get("https://api.fastermessage.com/v1/sms/send?"+t, data={}, headers={})
        r.close()
        
        rsp[p] = dict(code=r.status_code, response=r.text)

    return rsp

@action('callback/clear', method=['GET'])
@action.uses(db, session, auth, flash)
def clear():
    rows = db(db.callback).select()

    data = []

    try:
        for row in rows:
            # Accédez aux colonnes de chaque ligne en utilisant la notation point
            data.append(dict(id=row.uuid,batchId=row.batchuuid,to=row.to,date=row.date))
            db(db.callback.uuid == row.uuid).delete()
            
    except Exception as e:
        return str(e)

    return data
