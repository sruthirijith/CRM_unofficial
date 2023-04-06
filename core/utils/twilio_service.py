# Download the helper library from https://www.twilio.com/docs/python/install
import os

from twilio.rest import Client

from config.base import settings

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

service = client.verify.v2.services(settings.TWILIO_SERVICE_ID)


def twilio_send_otp(phone_number, channel='sms'):
    response = service.verifications.create(to=phone_number, channel=channel)
    return response

def twilio_verify_otp(phone_number, code):
    response = service.verification_checks.create(to=phone_number, code=code)
    return response

