import json
import oauth2client.client
from Products.ERP5Security.ERP5ExternalOauth2ExtractionPlugin import getGoogleUserEntry
from zExceptions import Unauthorized


SCOPE_LIST = ['https://www.googleapis.com/auth/userinfo.profile',
              'https://www.googleapis.com/auth/userinfo.email']

def redirectToGoogleLoginPage(self):
  client_id, secret_key = self.ERP5Site_getGoogleClientIdAndSecretKey()
  flow = oauth2client.client.OAuth2WebServerFlow(
    client_id=client_id,
    client_secret=secret_key,
    scope=SCOPE_LIST,
    redirect_uri="{0}/ERP5Site_receiveGoogleCallback".format(self.absolute_url()),
    access_type="offline",
    prompt="consent",
    include_granted_scopes="true")
  self.REQUEST.RESPONSE.redirect(flow.step1_get_authorize_url())

def getAccessTokenFromCode(self, code, redirect_uri):
  portal = self.getPortalObject()
  client_id, secret_key = portal.ERP5Site_getGoogleClientIdAndSecretKey()
  flow = oauth2client.client.OAuth2WebServerFlow(
    client_id=client_id,
    client_secret=secret_key,
    scope=SCOPE_LIST,
    redirect_uri=redirect_uri,
    access_type="offline",
    include_granted_scopes="true")
  credential = flow.step2_exchange(code)
  credential_data = json.loads(credential.to_json())
  return credential_data

def unrestrictedSearchGoogleConnector(self):
  return self.getPortalObject().portal_catalog.unrestrictedSearchResults(
            portal_type="Google Connector",
            reference="default",
            validation_state="validated",
            limit=2)

def unrestrictedSearchGoogleLogin(self, login, REQUEST=None):
  if REQUEST is not None:
    raise Unauthorized

  return self.getPortalObject().portal_catalog.unrestrictedSearchResults(
    portal_type="Google Login",
    reference=login,
    validation_state="validated", limit=1)

def getUserEntry(access_token):
  return getGoogleUserEntry(access_token)