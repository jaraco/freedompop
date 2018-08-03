import pprint

import autocommand

import freedompop


@autocommand.autocommand(__name__)
def main(command):
	import logging
	logging.basicConfig(level=logging.DEBUG)
	pprint.pprint(freedompop.Client().get_user_info())
