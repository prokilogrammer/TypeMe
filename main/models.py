from django.db import models


class Request(models.Model):
  # FIXME: Validate that one of email or phone is not null before saving
  phone = models.CharField(max_length=40, null=True)
  email = models.EmailField(max_length=256, null=True)
  time = models.DateField(auto_now_add=True)
  url_full  = models.URLField(max_length=1024, null=False)
  url_short = models.URLField(max_length=100, null=False)
  requestData = models.TextField(null=False)
  responseData = models.TextField(null=True)

  def __unicode__(self):
    return self.phone + " @ " + str(self.time) + "\n----\nRequest: " + str(self.requestData) + "\n----\nResponse: " + str(self.responseData)
