import filabel
import os
import pytest
import betamax

from helper import *

@pytest.fixture
def testapp(betamax_session):
    os.environ["GH_SECRET"] = "tajneheslo" 
    from filabel import app
    filabel.app.config['TESTING'] = True
    filabel.app.config['BETAMAX_SESSION'] = betamax_session
    return app.test_client()

def test_flask_mainpage(testapp):
    assert "GitHub" in testapp.get('/').get_data(as_text=True)

def test_flask_pingpong(testapp):
    assert 200 == testapp.post('/', json=PING, headers={
            'X-Hub-Signature': 'sha1=7528bd9a5b9d6546b0c221cacacc4207bdd4a51a',
            'X-GitHub-Event': 'ping'}).status_code

def test_flask_bad_pingpong(testapp):
    assert 403 == testapp.post('/', json=PING, headers={
            'X-Hub-Signature': 'sha1=aaa8bd9a5b9d6546b0c221cacacc4207bdd4a51a',
            'X-GitHub-Event': 'ping'}).status_code

def test_flask_label_pr(testapp, capfd):
# def test_flask_label_pr(testapp, capsys):
    sha_hash = generate_sha_hash(github_secret, PULL_REQUEST)
    ret = testapp.post('/', json=PULL_REQUEST, headers={
            'X-Hub-Signature': f'sha1={sha_hash}',
            'X-GitHub-Event': 'pull_request'})
    out, err = capfd.readouterr()
    assert "= abc" in out
    assert 204 == ret.status_code

