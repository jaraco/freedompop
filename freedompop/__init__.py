import os
import datetime

from tempora import utc
from requests_toolbelt import sessions


class Error(Exception):
	@classmethod
	def raise_for_resp(cls, data):
		if 'error' in data:
			raise cls(data['error_description'])
		return data


class Client:
	_session = sessions.BaseUrlSession('https://api.freedompop.com')
	username = os.environ['FREEDOMPOP_API_USERNAME']
	password = os.environ['FREEDOMPOP_API_PASSWORD']
	_session.auth = username, password

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
		return self._session.post('/auth/token', params=params).json()

	def _acquire_token(self):
		params = dict(
			grant_type='password',
			username=os.environ['FREEDOMPOP_USERNAME'],
			password=os.environ['FREEDOMPOP_PASSWORD'],
		)
		return self._session.post('/auth/token', params=params).json()

	@property
	def session(self):
		self._update_token()
		return self._session

	def get_phone_account_info(self):
		return self.session.get('/phone/account/info').json()
