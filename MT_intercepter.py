#!/usr/bin/env python

import json
import requests
from datetime import datetime

EXTERNAL_API_URL = "https://edok-api.kingsmspro.com/api/v1/sms/send"
API_KEY = 'NgDnKzjDpv3EndwGiOrVBBLHDivERcZt'  # clé API
CLIENT_ID = "2839"  #  client ID

def send_sms_via_fake(code = 201, text = "Test fake response"):
    """Méthode pour simuler un requests.Response"""
    import uuid

    try:
        id_uniq = uuid.uuid4()
        if text == "":
            text = str('{"messageId":"%s"}' % id_uniq)

        return code, {"messageId":id_uniq}, text
    except Exception as e:
        #sys.stderr.write(f"Erreur d'envoi de l'API : {str(e)}\n")
        return 400, {}, str(e)

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
        r = requests.post(EXTERNAL_API_URL, data=sms_data, headers=headers)

        return r.status_code, r.json, r.text
    except Exception as e:
        #sys.stderr.write(f"Erreur d'envoi de l'API : {str(e)}\n")
        return send_sms_via_fake(400, str(e))

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
    message_id = ""
    message_user = ""
    dateSend = datetime.now().isoformat() + 'Z'
    daySend = datetime.now().strftime('%Y%m%d%H')
    to = routable.pdu.params['destination_addr']
    sender = routable.pdu.params['source_addr']
    content = routable.pdu.params['short_message']

    # Envoi du SMS via l'API HTTP externe
    api_code, api_json, api_text = send_sms_via_fake()
    #api_code, api_json, api_text = send_sms_via_api(sender, to, content, type_, dlr, url)

    if api_code < 200 or api_code > 299:
        raise Exception("Fail sending SMS")

    message_id   = api_json["messageId"]
    message_user = routable.user #routable.pdu.params["sm_default_msg_id"]

    # smpp_status = 0
except Exception as e:
    api_text = str(e)
    # We got an error when calling for charging
    # Return ESME_RDELIVERYFAILURE
    # smpp_status = 254
    http_status = api_code
finally:
    log_file = "/var/log/jasmin/mt_interceptor/{0}.log".format(daySend)
    with open(log_file, "a") as file:
        file.write("{0} : send SMS from {1} to {2} ({3} - {4} {5})".format(dateSend, sender, to, api_code, api_text, message_id))
        file.write('\n')