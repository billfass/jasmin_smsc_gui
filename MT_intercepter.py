#!/usr/bin/env python

import json
import requests
from datetime import datetime
import uuid

EXTERNAL_API_URL = "https://edok-api.kingsmspro.com/api/v1/sms/send"
API_KEY = 'NgDnKzjDpv3EndwGiOrVBBLHDivERcZt'  # clé API
CLIENT_ID = "2839"  #  client ID

def send_sms_via_fake():
    id_uniq = uuid.uuid4()
    return json.dumps({"status_code":201, "json":{"messageId":id_uniq}, "text":"{\"messageId\":\"%s\"}" % id_uniq})

def send_sms_via_api(from_, to, message, type_, dlr, url):
    """Envoie le SMS via l'API externe."""
    try:
        sms_data = {
            'from': from_,
            'to': to,
            'type': type_,
            'message': message,
            'dlr': dlr
        }

        headers = {
            "APIKEY": API_KEY,
            "CLIENTID": CLIENT_ID
        }

        # Envoi du SMS via l'API
        return requests.post(EXTERNAL_API_URL, data=sms_data, headers=headers)
    except Exception as e:
        #sys.stderr.write(f"Erreur d'envoi de l'API : {str(e)}\n")
        return 400, str(e)

globals()['json'] = json
globals()['requests'] = requests
globals()['EXTERNAL_API_URL'] = EXTERNAL_API_URL
globals()['API_KEY'] = API_KEY
globals()['CLIENT_ID'] = CLIENT_ID
try:
    type_ = 0  # Type de message (par défaut 0 : 'text', 1 : 'Flash')
    dlr = 0  # DLR (par défaut 1 pour accusé de réception)
    url = ''  # DLR URL
    api_code = 400
    api_text = "Fail"
    dateSend = datetime.now().isoformat() + 'Z'
    to = routable.pdu.params['destination_addr']
    sender = routable.pdu.params['source_addr']
    content = routable.pdu.params['short_message']

    # Envoi du SMS via l'API HTTP externe
    api_response = send_sms_via_fake()
    #api_response = send_sms_via_api(sender, to, content, type_, dlr, url)

    api_code = api_response.status_code
    api_text = api_response.text

    if api_code < 200 or api_code > 299:
        raise Exception("Fail sending SMS")
    
    routable.pdu.params["sm_default_msg_id"] = api_response.json["messageId"]
except Exception as e:
    # We got an error when calling for charging
    # Return ESME_RDELIVERYFAILURE
    # smpp_status = 254
    http_status = api_code
finally:
    log_file = "/var/log/jasmin/mt_interceptor.log"
    with open(log_file, "a") as file:
        file.write("{0} : send SMS from {1} to {2} ({3} - {4})".format(dateSend, sender, to, api_code, api_text))
        file.write('\n')