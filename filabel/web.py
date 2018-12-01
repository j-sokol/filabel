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

from .github import GitHub
from .config import config, config_labels_parsed, github_url, github_api_url


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

app = Flask(__name__)
app.debug = os.environ.get('DEBUG') == 'true'

def test_hmac_signature(header_signature, github_secret, request_data):
    if header_signature is None:
        return 403

    # Only SHA1 is supported
    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        return 501

    github_secret_bytes = bytes(github_secret, 'UTF-8')
    mac = hmac.new(github_secret_bytes, msg=request_data, digestmod=hashlib.sha1)

    print("Req:")
    print(request_data)
    print ("Generated hmac:", mac.hexdigest())
    print ("from sig:", header_signature)
    if not hmac.compare_digest('sha1=' + mac.hexdigest(), header_signature):
        return 403

    return 200


@app.before_first_request
def load_config(config_path=None):
    """
    Loads configuration for Flask App

    """
    try:
        app.config['FILABEL_CONFIG'] = os.environ.get('FILABEL_CONFIG', config_path).split(':')
    
        config['github'] = {'token': os.environ.get('GH_TOKEN', ''),
                            'secret': os.environ.get('GH_SECRET', '')}
    except KeyError:
        raise RuntimeError('You must set FILABEL_CONFIG, GH_USER and GH_TOKEN environ vars')



    for config_file in app.config['FILABEL_CONFIG']:
            config.read(os.path.join(__location__, config_file))
    try:
        print(app.config['FILABEL_CONFIG'])
        for config_file in app.config['FILABEL_CONFIG']:
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

    print (config['labels'])


@app.route("/", methods=['GET', 'POST'])
def index():
    """
    Web application index page

    """
    if app.config['TESTING']:
        github = GitHub(config['github']['token'], app.config['BETAMAX_SESSION'])
    else:
        github = GitHub(config['github']['token'])


    if request.method == 'GET':
        user_data = github.get_user()
        return render_template("template.html", user=user_data, config_labels_parsed=config_labels_parsed)

    elif request.method == 'POST':

        # Enforce secret
        header_signature = request.headers.get('X-Hub-Signature')

        # print (request.data)
        ret = test_hmac_signature(header_signature, config['github']['secret'], request.data)
        if ret != 200:
            abort(ret)

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
            github.label_pr(slug, pull_request)
        except Exception as e: print(e)
    return '', 204

