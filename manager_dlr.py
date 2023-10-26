from py4web import action, request
from .common import db, session, auth, flash, jasmin
from pydal.validators import *
from .utils import cols_split
from .user_manager import list_groups
from .route_manager import mt_routes
from .filter_manager import list_filters
import requests, time

def log(sec, lev, uuid, code):
    from datetime import datetime
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
    
    db.callback.update_or_insert(db.callback.uuid == data['id'], uuid=data['id'], batchuuid=data['batchId'], status=data['status'], to=data['to'])

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
        requests.get("https://fastermessage.com/app2/sms/errbatch/dlr/"+data['batchId']+"/"+data["to"]+"?statusText="+data["statusText"]+"&status="+data['status'], data={}, headers={})
    else:
        requests.get("https://api.fastermessage.com/v2/sms/errbatch/dlr/"+data['batchId']+"/"+data["to"]+"?statusText="+data["statusText"]+"&status="+data['status'], data={}, headers={})

    return 'ACK/Jasmin'

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
        log(sec, 0, id, str(e))
        return str(e)
    
    if sec == "web":
        r = requests.post("https://fastermessage.com/app2/sms/batch/dlr/"+data['level']+"/"+data["id"], data=dict(data), headers={})
    else:
        r = requests.post("https://api.fastermessage.com/v2/sms/batch/dlr/"+data['level']+"/"+data["id"], data=dict(data), headers={})

    log(sec, data["level"], data["id"], r.status_code)

    if r.status_code == 200:
        return 'ACK/Jasmin'
    elif r.status_code == 202:
        db(db.callback.uuid == data['id']).delete()
        return 'ACK/Jasmin'
    
    return 'NOACK/Jasmin'    

@action('callback/clear', method=['GET'])
@action.uses(db, session, auth, flash)
def clear():
    rows = db().select(db.callback.ALL)

    data = []

    for row in rows:
        # Accédez aux colonnes de chaque ligne en utilisant la notation point
        uuid = row.uuid
        batchuuid = row.batchuuid
        if(row.status):
            status = row.status
        else:
            status = ""
        if(row.to):
            to = row.to
        else:
            to = ""
        if(row.date):
            date = row.date
        else:
            date = ""
        
        # Effectuez les opérations nécessaires avec les données
        data.append("UUID: "+uuid+", BatchUUID: "+batchuuid+", Status: "+status+", To: "+to+", Date: "+date)
        # print(f"UUID: {uuid}, BatchUUID: {batchuuid}, Status: {status}, To: {to}, Date: {date}")

    return dict(data)
