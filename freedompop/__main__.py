import pprint

import autocommand

import freedompop


@autocommand.autocommand(__name__)
def main(command):
	method_name = command.replace('-', '_').replace(' ', '_')
	client = freedompop.Client()
	method = getattr(client, method_name)
	pprint.pprint(method())
