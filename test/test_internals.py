import filabel
import os
import pytest
import betamax

from helper import *

@pytest.mark.parametrize(
    ['header_signature', 'github_secret', 'ret_code'],
    [('sha=bad_prefix', github_secret, 501),
     ('sha1=bad_hash', github_secret, 403),
     ('sha1=1cacacc4207bdd4a51a7528bd9a5b9d6546b0c22', github_secret, 403),
     ('sha1=7528bd9a5b9d6546b0c221cacacc4207bdd4a51a', github_secret, 200),
    ])

def test_hmac_signature(header_signature, github_secret, ret_code):
    """Test hmac hash function"""
    data = b'{"hook": {"active": true, "config": {"content_type": "json", "insecure_ssl": "0", "secret": "********"}, "events": ["pull_request"], "id": 55866886, "name": "web", "type": "Repository"}, "hook_id": 123456, "repository": {"full_name": "hroncok/filabel-testrepo-everybody", "id": 123456, "name": "filabel-testrepo-everybody", "private": false}, "sender": {"login": "user"}, "zen": "Approachable is better than simple."}'

    hmac_ret = filabel.web.test_hmac_signature(header_signature, github_secret, data)
    assert ret_code == hmac_ret



@pytest.mark.parametrize(
    ['change_type'],
    ['+', '-', '='])
def test_reporter(change_type):
    """Test whether reporter outputs right values"""
    github = filabel.github.GitHub(token)

    labels_log = [(change_type, "testing_label")]

    ret = github.report_log(labels_log)

    assert change_type, "testing_label" in ret


def test_get_user(betamax_session):
    """Test whether API returns user"""
    github = filabel.github.GitHub(token, session=betamax_session)

    ret = github.get_user()
    assert user is not None

def test_get_all_prs(betamax_session):
    """Test whether API returns prs"""
    github = filabel.github.GitHub(token, session=betamax_session)

    slug = 'hroncok/filabel-testrepo-everybody'
    ret = github.get_all_prs(slug)
    assert 'id' in ret[0].keys()

def test_post_labels_exception(betamax_session):
    """Test whether filabel posts a label"""
    github = filabel.github.GitHub(token, session=betamax_session)

    slug = 'hroncok/filabel-testrepo-everybody'
    with pytest.raises(Exception):
	    ret = github.post_label(slug, '1', 'test_label')

def test_delete_labels_exception(betamax_session):
    """Test whether filabel posts a label"""
    github = filabel.github.GitHub(token, session=betamax_session)

    slug = 'hroncok/filabel-testrepo-everybody'
    with pytest.raises(Exception):
        ret = github.delete_label(slug, '1', 'test_label')


def test_post_labels(betamax_session):
    """Test whether filabel posts a label"""
    github = filabel.github.GitHub(token, session=betamax_session)

    slug = f'{user}/mi-pyt-test-repo'
    ret = github.post_label(slug, '5', 'ddd')
    print (ret)
    assert 0 == ret


def test_delete_labels(betamax_session):
    """Test whether filabel posts a label"""
    github = filabel.github.GitHub(token, session=betamax_session)

    slug = f'{user}/mi-pyt-test-repo'
    ret = github.delete_label(slug, '5', 'ddd')
    print (ret)
    assert 0 == ret

def test_web_config():
    """Test whether filabel posts a label"""
    filabel.web.load_config(config_path="../test/fixtures/labels.abc.cfg")
    assert filabel.config.config['labels'] is not None


def test_label_pr(betamax_session):
    """Test whether filabel posts a label"""
    filabel.web.load_config(config_path="../test/fixtures/labels.abc.cfg")

    github = filabel.github.GitHub(token, session=betamax_session)

    slug = f'{user}/mi-pyt-test-repo'
    pull_request = {'number': 5}

    github.label_pr(slug, pull_request)

    assert filabel.config.config['labels'] is not None


