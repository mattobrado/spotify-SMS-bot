from twilio.rest import Client

from my_secrets import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, MY_TWILIO_NUMBER, MY_PHONE_NUMBER

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

message = client.messages \
    .create(
         body='Hello, I have a texting robot',
         from_= MY_TWILIO_NUMBER,
         to= MY_PHONE_NUMBER
     )
     
print(message.sid)