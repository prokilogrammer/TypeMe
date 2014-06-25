import json

from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
import urllib, urlparse
import twilio # FIXME: Move this to smsclient module

from main.models import Request
from main.sms import SmsClient

# FIXME: Grab this location from the urls.py
RESPONSE_LOCATION = "/main/response"

def index(request):
  return render_to_response('main/index.html', {}, RequestContext(request))

def submitRequest(request):
  context = RequestContext(request)

  fieldsWithValues = dict()

  # Parse the parameters
  for key, vallist in request.GET.iterlists():
    fieldsWithValues[key] = vallist

  print fieldsWithValues

  # Grab list of field names requested by the user
  # This comes as a GET parameter "fieldName". There will be many parameters
  # with the same key and hence a list
  fieldNamesList = fieldsWithValues['fieldName'] if fieldsWithValues.has_key('fieldName') else None
  toPhoneNumberList = fieldsWithValues['phone'] if fieldsWithValues.has_key('phone') else None
  toEmailList = fieldsWithValues['email'] if fieldsWithValues.has_key('email') else None

  # There should be at least one email or phone.
  if ((toPhoneNumberList is not None and len(toPhoneNumberList) == 0) or
     (toEmailList is not None and len(toEmailList) == 0) or
     (toPhoneNumberList is None and toEmailList is None)):
    response = HttpResponse(status=400)
    response.body("Please enter at least one email or phone number")  # FIXME: Fixthis
    return response

  toPhoneNumber =  toPhoneNumberList[0] if toPhoneNumberList is not None and len(toPhoneNumberList) > 0 else None
  toEmail = toEmailList[0] if toEmailList is not None and len(toEmailList) > 0 else None

  # Create an object to store the field names and save it in JSON format
  requestData = {'fields': fieldNamesList}
  requestDataJson = json.dumps(requestData)
  requestObj = Request(phone=toPhoneNumber, email=toEmail, requestData=requestDataJson)
  requestObj.save()  # Save it to generate an ID

  # Get absolute base URL for this service and build response Url
  # Ex: http://www.example.com/response
  baseUrl = request.build_absolute_uri();
  responseUrlBase = urlparse.urljoin(baseUrl, RESPONSE_LOCATION)

  # Generate a URL with requestObj Id to post the Response
  # Ex: http://www.example.com/response?id=1
  params = urllib.urlencode({'id': requestObj.id})
  responseUrl = responseUrlBase + "?" + params

  # Save url in obj (don't save it yet)
  requestObj.url_short = shorten(responseUrl)
  requestObj.url_full = responseUrl

  print responseUrl

  # Now send the URLs out
  notificationSuccess = False
  notificationError = "Unable to send email or sms. Please try again later. "

  if toPhoneNumber is not None:
    print "Trying to send sms"
    smsClient = SmsClient();
    result = None
    try:
      result = smsClient.send(toPhoneNumber, requestObj.url_short)
      notificationSuccess = True
    except twilio.TwilioRestException as e:
      print e
      notificationError = notificationError + "\r\n" + str(e);
      notificationSuccess = False

  if toEmail is not None:
    # FIXME: Send out emails
    print "Trying to send email"
    notificationSuccess = False

  viewContextDict = {'error': None}
  if not notificationSuccess:
    # We did not notify the user about this request. No use in storing request obj
    requestObj.delete()
    viewContextDict['error'] = notificationError
  else:
    # Successful notification. Go ahead and save the urls in db
    requestObj.save()
    viewContextDict['id'] = requestObj.id

  return render_to_response('main/request.html', viewContextDict, context)


def refresh(request):
  context = RequestContext(request)
  viewContextDict = {'error' : None}

  requestId = request.GET.get('id', None)
  if requestId is None:
    print "Reqest Id is required"
    return HttpResponse(status=400)

  requestObj = Request.objects.get(pk=int(requestId))

  if requestObj is None:
    print "No request object found for key: " + requestId
    return HttpResponse(status=400)

  if requestObj.responseData is None:
    viewContextDict['error'] = "Response not yet received. Please try again later"
  else:
    viewContextDict['response'] = json.loads(requestObj.responseData)

  return render_to_response('main/refresh.html', viewContextDict, context)

def response(request):
  context = RequestContext(request)

  # Get ID parameter
  requestId = request.GET.get('id', None)
  if requestId is None:
    return HttpResponse(status=400) # bad request

  print "PROCESSING REQUST: " + `requestId`

  # Fetch request model
  requestModel = Request.objects.get(pk=int(requestId))

  if requestModel.requestData is None:
    return HttpResponse(status=400)

  requestData = json.loads(requestModel.requestData)

  contextDict = dict()
  contextDict['requestId'] = int(requestId)
  contextDict['fields'] = requestData['fields']

  return render_to_response('main/response.html', contextDict, context)


def submitResponse(request):
  context = RequestContext(request)
  fieldsWithValues = dict()

  # Parse the parameters
  # There should be unique keys in GET request. So no need to use request.GET.iterlist()
  for key, val in request.GET.iteritems():
    if key == 'requestId':
      requestId = val
    else:
      fieldsWithValues[key] = val

  if requestId is None or len(fieldsWithValues) == 0:
    return HttpResponse(status=400)

  # Retrieve the model and save the response
  requestId = int(requestId)
  requestModel = Request.objects.get(pk=requestId)
  requestModel.responseData = json.dumps(fieldsWithValues)
  requestModel.save()

  return render_to_response('main/submitResponse.html', {}, context)


#### Utilities #####

# FIXME: Implement this function
def shorten(longUrl):
  return longUrl
