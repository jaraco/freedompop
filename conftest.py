import os


def pytest_configure():
	os.environ.update(
		FREEDOMPOP_API_USERNAME='',
		FREEDOMPOP_API_PASSWORD='',
		FREEDOMPOP_APP_VERSION='',
	)
