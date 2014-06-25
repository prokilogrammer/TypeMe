from twilio.rest import TwilioRestClient
from typeme import config

class SmsClient(object):

  def __init__(self):
    self.client = TwilioRestClient(config.Twilio.account_sid, config.Twilio.auth_token)
    self.fromPhoneNumber = config.Twilio.fromPhoneNumber

  def send(self, toPhoneNumber, text):
    message = self.client.messages.create(body=text, to=toPhoneNumber, from_=self.fromPhoneNumber)
    print message.sid
    return message.sid

