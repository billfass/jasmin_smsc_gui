#!/usr/bin/env python

import sys
import json
import requests

# API HTTP externe (URL et API Key)
EXTERNAL_API_URL = "https://edok-api.kingsmspro.com/api/v1/sms/send"
API_KEY = 'NgDnKzjDpv3EndwGiOrVBBLHDivERcZt'  # clé API
CLIENT_ID = "2839"  #  client ID

def send_sms_via_api(from_, to, message, type_, dlr):
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
        response = requests.post(EXTERNAL_API_URL, data=sms_data, headers=headers)

        # Vérification du statut de la réponse
        if response.status_code == 200:
            return True, response.json()  # Réponse OK
        else:
            sys.stderr.write(f"Erreur d'envoi : {response.status_code} - {response.text}\n")
            return False, response.text  # Réponse en erreur
    except Exception as e:
        sys.stderr.write(f"Erreur d'envoi de l'API : {str(e)}\n")
        return False, str(e)

def intercept_sms(message):
    """Intercepte et traite le message SMS."""
    try:
        # Récupération des informations du message intercepté (Jasmin envoie les données via stdin)
        message_data = json.loads(message)

        to = message_data['to']
        sender = message_data['from']
        content = message_data['content']
        message_type = message_data.get('type', 'text')  # Type de message (par défaut 'text')
        dlr = message_data.get('dlr', '1')  # DLR (par défaut 1 pour accusé de réception)

        # Envoi du SMS via l'API HTTP externe
        success, api_response = send_sms_via_api(sender, to, content, message_type, dlr)

        if success:
            return True, "Message envoyé avec succès via l'API."
        else:
            sys.stderr.write(f"Échec de l'envoi via l'API : {api_response}\n")
            return False, api_response  # Échec de l'envoi

    except Exception as e:
        sys.stderr.write(f"Erreur : {str(e)}\n")
        return False, str(e)

if __name__ == "__main__":
    # Lire le message depuis stdin (transmis par Jasmin)
    message = sys.stdin.read()

    # Appeler la fonction pour traiter le message
    success, result = intercept_sms(message)

    if success:
        sys.stdout.write(json.dumps({"status": 200, "message": result}))
    else:
        sys.stdout.write(json.dumps({"status": 500, "message": result}))
