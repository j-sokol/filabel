import configparser
import fnmatch
import json
import re
import sys

from flask import Flask, request, abort, Blueprint, render_template
import os
import hmac
import hashlib

import click
import requests

from ..github.github import get_prs, label_prs
from ..config.config import config, config_labels_parsed, github_url, github_api_url


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


app = Flask(__name__)
app.debug = os.environ.get('DEBUG') == 'true'

@app.before_first_request
def load_config():
    """
    Loads configuration for Flask App

    """

    app.config['FILABEL_CONFIG'] = os.environ.get('FILABEL_CONFIG', '').split(':')
    
    config['github'] = {'token': os.environ.get('GH_TOKEN', ''),
                        'secret': os.environ.get('GH_SECRET', '')}

    for config_file in app.config['FILABEL_CONFIG']:
            config.read(os.path.join(__location__, config_file))
            print(os.path.join(__location__, config_file))
    try:
        print(app.config['FILABEL_CONFIG'])
        for config_file in app.config['FILABEL_CONFIG']:
            print(os.path.join(__location__, config_file))
            config.read(os.path.join(__location__, config_file))


        if config['github']['token'] == None:
            raise Exception('Token variable not provided.')

        if config['labels'] == None:
            raise Exception('Label variables not provided.')
            
        # Parse labels from string to readable format
        for config_key in config['labels']:
            config_labels_parsed[config_key] = list(filter(None,config['labels'][config_key].splitlines()))

    except:
        print ("Configuration files not usable!", file=sys.stderr)
        sys.exit(1)


@app.route("/", methods=['GET', 'POST'])
def index():
    """
    Web application index page

    """
    head = {'Authorization': 'token {}'.format(config['github']['token'])}
    if request.method == 'GET':
        response = requests.get("{0}/user".format(github_api_url), headers=head)
        if response.status_code != 200:
            print('Fetching user data failed.', response.status_code)


        user_data = json.loads(response.text)


        return render_template("template.html", user=user_data, config_labels_parsed=config_labels_parsed)
    elif request.method == 'POST':

        # Enforce secret
        header_signature = request.headers.get('X-Hub-Signature')
        if header_signature is None:
            abort(403)

        # Only SHA1 is supported
        sha_name, signature = header_signature.split('=')
        if sha_name != 'sha1':
            abort(501)

        github_secret = bytes(config['github']['secret'], 'UTF-8')
        mac = hmac.new(github_secret, msg=request.data, digestmod=hashlib.sha1)
        if not hmac.compare_digest('sha1=' + mac.hexdigest(), header_signature):
            abort(403)


        if request.headers.get('X-GitHub-Event') == "ping":
            return json.dumps({'msg': 'pong'})
        if request.headers.get('X-GitHub-Event') != "pull_request":
            return json.dumps({'msg': "wrong event type"})


        payload = json.loads(request.data)

        # Define variables
        pull_request = {}
        slug = re.search(r"(?<=github.com/).*?(?=/pull/)", payload['pull_request']['html_url']).group(0)
        pull_request['number'] = payload['pull_request']['number']
        head = {'Authorization': 'token {}'.format(config['github']['token'])}

        try:
            label_prs(pull_request, slug, head)
        except Exception as e: print(e)
    return '', 204

