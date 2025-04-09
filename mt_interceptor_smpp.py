import requests

# Tu peux définir ici une correspondance username => password
USER_CREDENTIALS = {
    'Urban002': 'Urban002',
    #'user2': 'pass2',
    #'smppuser': 'smpppass',
    # Ajoute tous tes utilisateurs ici
}

def mt_interceptor_smpp(message):
    if message.status == 'ERROR/ESME_RSUBMITFAIL':
        message.log.info(f"[Interceptor] ESME_RSUBMITFAIL - triggering resend.")
    
        try:
            # Récupération des infos du message
            to = message.destination_addr
            sender = message.source_addr
            content = message.short_message.decode('utf-8')
            username = message.user.username
            password = USER_CREDENTIALS.get(username)
            dlr_url = getattr(message, 'dlr_url', None)

            if not password:
                message.log.error(f"[Interceptor] No password found for user: {username}, skipping resend.")
                return message

            # Requête vers /send
            data = {
                "username": username,
                "password": password,
                "to": to,
                "from": sender,
                "text": content,
                "messageId": message.message_id,
                "resend": true
            }
            
            if dlr_url:
                data["dlr-url"] = dlr_url
        
            response = requests.post(
                "https://api.fastermessage.com/sms/send",
                data=data,
                timeout=5
            )
            message.log.info(f"[Interceptor] Resend done: {response.status_code} {response.text}")
        except Exception as e:
            message.log.error(f"[Interceptor] Resend failed: {e}")

        message.retry = False  # On évite que Jasmin retry lui-même

    return message
