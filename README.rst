.. image:: https://img.shields.io/pypi/v/freedompop.svg
   :target: https://pypi.org/project/freedompop

.. image:: https://img.shields.io/pypi/pyversions/freedompop.svg

.. image:: https://img.shields.io/travis/jaraco/freedompop/master.svg
   :target: https://travis-ci.org/jaraco/freedompop

.. .. image:: https://img.shields.io/appveyor/ci/jaraco/freedompop/master.svg
..    :target: https://ci.appveyor.com/project/jaraco/freedompop/branch/master

.. .. image:: https://readthedocs.org/projects/freedompop/badge/?version=latest
..    :target: https://freedompop.readthedocs.io/en/latest/?badge=latest


Unofficial FreedomPop Client library, inspired by
`freedompop-telegram <https://github.com/freedompop-telegram>`_.

This library provides a simple Pythonic API to a selection of calls available
through the undocumented and unsupported FreedomPop API.

Configuration
=============

All configuration is solicited through various environment variables.

App Credentials:

- FREEDOMPOP_API_USERNAME
- FREEDOMPOP_API_PASSWORD
- FREEDOMPOP_APP_VERSION

For these, you may extract them from an APK or re-use ones such as
`those published here
<https://github.com/wodim/freedompop-telegram/blob/master/config.py.example>`_.

Account Credentials:

- FREEDOMPOP_USERNAME
- FREEDOMPOP_PASSWORD

These are the e-mail address and password used to authenticate to the
FreedomPop web site.

Other variables that may be used:

- FREEDOMPOP_DEVICE_ID
- FREEDOMPOP_DEVICE_SID
- FREEDOMPOP_DEVICE_TYPE
- FREEDOMPOP_RADIO_TYPE
- FREEDOMPOP_PUSH_TOKEN

Usage
=====

Command-Line
------------

Once installed, the package provides a command-line client. For any of
the API methods that require no parameters, you may invoke it from
the command line and see the JSON response. For example::

    $ python -m freedompop 'get phone account info'
    {'accountExternalId': None,
     'accountExternalRefId': '...',
     'accountId': '...',
     ...

The command invoked can use space-separated, dash-separated, or
underscore-separated names.

Programmatic
------------

For other applications, it's possible to construct and invoke the API
programmatically::

    >>> import freedompop
    >>> client = freedompop.Client()
    >>> client.get_phone_account_info()
    {...}

Read the docs or review the source for the methods available.
