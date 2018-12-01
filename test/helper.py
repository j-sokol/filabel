import os
import pytest
import betamax
import pathlib
import atexit
import json
import hmac
import hashlib

from click.testing import CliRunner

def config(name):
    return pathlib.Path(__file__).parent / 'fixtures' / name


try:
    user = os.environ['GH_USER']
    token = os.environ['GH_TOKEN']
    filabel_config = os.environ['FILABEL_CONFIG']
except KeyError:
    # raise RuntimeError('You must set GH_USER and GH_TOKEN environ vars')
    os.environ["FILABEL_CONFIG"] = "../test/fixtures/labels.abc.cfg"

with betamax.Betamax.configure() as betamax_config:
    # tell Betamax where to find the cassettes
    # make sure to create the directory
    betamax_config.cassette_library_dir = 'test/fixtures/cassettes'

    if 'GH_TOKEN' in os.environ:
        # If the tests are invoked with an AUTH_FILE environ variable
        token = os.environ['GH_TOKEN']
        # Always re-record the cassetes
        # https://betamax.readthedocs.io/en/latest/record_modes.html
        betamax_config.default_cassette_options['record_mode'] = 'all'
    else:
        token = 'False_token'
        # Do not attempt to record sessions with bad fake token
        betamax_config.default_cassette_options['record_mode'] = 'none'

    if 'GH_USER' not in os.environ:
        user = 'placeholder_user'


    # Hide the token in the cassettes
    betamax_config.define_cassette_placeholder('<TOKEN>', token)
    betamax_config.define_cassette_placeholder('<USER>', user)


config('auth.real.cfg').write_text(
    config('auth.fff.cfg').read_text().replace(40 * 'f', token)
)
atexit.register(config('auth.real.cfg').unlink)


def generate_sha_hash(github_secret, request_data):
    github_secret_bytes = bytes(github_secret, 'UTF-8')
    request_data_bytes = bytes(json.dumps(request_data), 'UTF-8')
    print (request_data_bytes)
    mac = hmac.new(github_secret_bytes, msg=request_data_bytes, digestmod=hashlib.sha1)
    return mac.hexdigest()


PING = {
    'zen': 'Approachable is better than simple.',
    'hook_id': 123456,
    'hook': {
        'type': 'Repository',
        'id': 55866886,
        'name': 'web',
        'active': True,
        'events': [
            'pull_request',
        ],
        'config': {
            'content_type': 'json',
            'insecure_ssl': '0',
            'secret': '********',
        },
    },
    'repository': {
        'id': 123456,
        'name': 'filabel-testrepo-everybody',
        'full_name': 'hroncok/filabel-testrepo-everybody',
        'private': False,
    },
    'sender': {
        'login': 'user',
    },
}

PULL_REQUEST = {
  "action": "closed",
  "number": 1,
  "pull_request": {
    "html_url": f'https://github.com/{user}/mi-pyt-test-repo/pull/5',
    "id": 191568743,
    "node_id": "MDExOlB1bGxSZXF1ZXN0MTkxNTY4NzQz",
    "number": 5,

    "url": f'https://api.github.com/repos/{user}/mi-pyt-test-repo/pulls/5',
  }
}

github_secret = "tajneheslo"
