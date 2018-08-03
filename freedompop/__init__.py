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
	session = sessions.BaseUrlSession('https://api.freedompop.com')
	username = os.environ['FREEDOMPOP_API_USERNAME']
	password = os.environ['FREEDOMPOP_API_PASSWORD']
	session.auth = username, password
	session.headers['User-Agent'] = (
		'Dalvik/2.1.0 (Linux; U; Android 7.1.1; Nokia 2 Build/NMF26F)'
	)
	session.params.update(
		appIdVersion=os.environ['FREEDOMPOP_APP_VERSION'],
	)

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
		params = dict(
			grant_type='password',
			username=os.environ['FREEDOMPOP_USERNAME'],
			password=os.environ['FREEDOMPOP_PASSWORD'],
		)
		return self.session.post('/auth/token', params=params)

	@jaraco.functools.method_cache
	def _register_push_token(self):
		params = dict(
			deviceId='1234567899',
			deviceSid='8144701821',
			deviceType='FPOP_BYOD',
			radioType='PHONE_TYPE_GSM',
			pushToken='1234567890',
		)
		self.get('/phone/push/register/token', params=params),

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
