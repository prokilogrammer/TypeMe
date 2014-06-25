from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import Authorization
import urllib
import urlparse

from main.models import Request
from main.sms import SmsClient

RESPONSE_LOCATION = "/main/response"

# Wrapper to make models sent by Tastypie to be compatible with Backbone.js
# REF: http://paltman.com/2012/04/30/integration-backbonejs-tastypie/
class BackboneCompatibleResource(ModelResource):
  class Meta:
    always_return_data = True


class RequestResource(BackboneCompatibleResource):
  class Meta:
    # FIXME: Need to prevent API that would return all request objects
    # Allow only GET/POST with explicit API IDs
    # Have an expiry timer for the POST. If request wasn't responded within 15mins, it POST will be rejected
    queryset = Request.objects.all()
    authorization = Authorization();

  # Send SMS before creating the object
  def obj_create(self, bundle, **kwargs):
    request = bundle.request

    # Save the object to get a ID
    bundle = super(RequestResource, self).obj_create(bundle);
    requestObj = bundle.obj

    # Add the URL to request object and save it again
    responseUrlBase = "http://localhost:8000/response"

    # Get absolute base URL for this service. Ex: http://www.typeme.in
    baseUrl = request.build_absolute_uri();
    responseUrlBase = urlparse.urljoin(baseUrl, RESPONSE_LOCATION)

    resourceUrl = super(RequestResource, self).get_resource_uri(bundle)
    params = urllib.urlencode({'id':requestObj.id, 'url':resourceUrl})
    responseUrl = responseUrlBase + "?" + params
    print responseUrl;

    requestObj.url_short = resourceUrl;
    requestObj.url_full = resourceUrl
    toPhoneNumber = requestObj.phone

    # Trigger sms
    smsClient = SmsClient()
    sid = "hi"
    # sid = smsClient.send(toPhoneNumber, resourceUrl)

    # Rollback the object if we cannot send an sms
    if sid is None:
      requestObj.delete()
      # FIXME: Need to aleter bundle response
    else:
      requestObj.save()

    return bundle


