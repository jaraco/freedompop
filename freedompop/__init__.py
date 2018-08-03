import os
import datetime

import jaraco.functools
from tempora import utc
from requests_toolbelt import sessions


class Error(Exception):
	@classmethod
	def raise_for_resp(cls, resp):
		resp.raise_for_status()
		data = resp.json()
		if 'error' in data:
			raise cls(data['error_description'])
		return data


class Client:

	@classmethod
	def from_env(cls):
		api_cred = (
			os.environ['FREEDOMPOP_API_USERNAME'],
			os.environ['FREEDOMPOP_API_PASSWORD'],
		)
		user_cred = (
			os.environ['FREEDOMPOP_USERNAME'],
			os.environ['FREEDOMPOP_PASSWORD'],
		)
		app_version = os.environ['FREEDOMPOP_APP_VERSION']
		device_info = dict(
			deviceId=os.environ.get('FREEDOMPOP_DEVICE_ID'),
			deviceSid=os.environ.get('FREEDOMPOP_DEVICE_SID'),
			deviceType=os.environ.get('FREEDOMPOP_DEVICE_TYPE'),
			radioType=os.environ.get('FREEDOMPOP_RADIO_TYPE'),
			pushToken=os.environ.get('FREEDOMPOP_PUSH_TOKEN'),
		)
		return cls(api_cred, user_cred, app_version, device_info)

	def __init__(self, api_cred, user_cred, app_version, device_info=None):
		self.session = self._build_session()
		self.session.params.update(appIdVersion=app_version)
		self.session.auth = api_cred
		self.user_cred = user_cred

	@staticmethod
	def _build_session():
		session = sessions.BaseUrlSession('https://api.freedompop.com')
		session.headers['User-Agent'] = (
			'Dalvik/2.1.0 (Linux; U; Android 7.1.1; Nokia 2 Build/NMF26F)'
		)
		return session

	def _update_token(self):
		if self._token_current():
			return

		vars(self).update(
			Error.raise_for_resp(self._refresh_token() or self._acquire_token()))
		self.session.params.update(accessToken=self.access_token)
		self.token_acquired = utc.now()

	def _token_current(self):
		if 'access_token' not in vars(self):
			return
		duration = datetime.timedelta(seconds=int(self.expires_in))
		expiration = self.token_acquired + duration
		return utc.now() < expiration

	def _refresh_token(self):
		if 'refresh_token' not in vars(self):
			return
		params = dict(
			grant_type='refresh_token',
			refresh_token=self.refresh_token,
		)
		return self.session.post('/auth/token', params=params)

	def _acquire_token(self):
		username, password = self.user_cred
		params = dict(
			grant_type='password',
			username=username,
			password=password,
		)
		return self.session.post('/auth/token', params=params)

	def _register_push_token(self):
		self.get('/phone/push/register/token', params=self.device_info),

	def __getattr__(self, name):
		"""
		Delegate to the session object, wrapped to first update the
		token and to check the response for errors and parse to
		JSON.
		"""
		method = getattr(self.session, name)
		return jaraco.functools.compose(
			Error.raise_for_resp,
			jaraco.functools.first_invoke(self._update_token, method),
		)

	def get_phone_account_info(self):
		return self.get('phone/account/info')

	def get_user_info(self):
		return self.get('user/info')

	def get_balance(self):
		return self.get('phone/balance')

	def list_sms(self):
		return self.get('phone/listsms')
