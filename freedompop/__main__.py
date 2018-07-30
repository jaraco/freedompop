import pprint

import autocommand

import freedompop


@autocommand.autocommand(__name__)
def main(command):
	pprint.pprint(freedompop.Client().get_phone_account_info())
