from twilio.rest import Client

from my_secrets import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

message = client.messages \
    .create(
         body='This is you Spotify SMS playlist number, send links to this number to add them to your playlist',
         from_='+12702900802',
         to='+17084207758'
     )

print(message.sid)