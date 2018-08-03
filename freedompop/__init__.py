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
	_session = sessions.BaseUrlSession('https://api.freedompop.com')
	username = os.environ['FREEDOMPOP_API_USERNAME']
	password = os.environ['FREEDOMPOP_API_PASSWORD']
	_session.auth = username, password
	_session.params = dict(appIdVersion=os.environ['FREEDOMPOP_APP_VERSION'])
	_session.headers['User-Agent'] = (
		'Dalvik/2.1.0 (Linux; U; Android 7.1.1; Nokia 2 Build/NMF26F)'
	)

	def _update_token(self):
		if self._token_current():
			return

		vars(self).update(
			Error.raise_for_resp(self._refresh_token() or self._acquire_token()))
		self._session.params = dict(accessToken=self.access_token)
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
		return self._session.post('/auth/token', params=params)

	def _acquire_token(self):
		params = dict(
			grant_type='password',
			username=os.environ['FREEDOMPOP_USERNAME'],
			password=os.environ['FREEDOMPOP_PASSWORD'],
		)
		return self._session.post('/auth/token', params=params)

	@jaraco.functools.method_cache
	def _register_push_token(self):
		params = dict(
			deviceId='1234567899',
			deviceSid='8144701821',
			deviceType='FPOP_BYOD',
			radioType='PHONE_TYPE_GSM',
			pushToken='1234567890',
			accessToken=self.access_token,
		)
		return Error.raise_for_resp(
			self._session.get('/phone/push/register/token', params=params),
		)

	@property
	def session(self):
		self._update_token()
		# self._register_push_token()
		return self._session

	def get_phone_account_info(self):
		return Error.raise_for_resp(self.session.get('/phone/account/info'))

	def get_user_info(self):
		return Error.raise_for_resp(self.session.get('/user/info'))
