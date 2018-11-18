import filabel
import os
import pytest
import betamax


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
        token = 'false_token'
        # Do not attempt to record sessions with bad fake token
        betamax_config.default_cassette_options['record_mode'] = 'none'

    if 'GH_USER' not in os.environ:
        user = 'placeholder_user'


    # Hide the token in the cassettes
    betamax_config.define_cassette_placeholder('<TOKEN>', token)
    betamax_config.define_cassette_placeholder('<USER>', user)


@pytest.fixture
def testapp(betamax_parametrized_session):
    from filabel import app
    filabel.app.config['TESTING'] = True
    filabel.app.config['BETAMAX_SESSION'] = betamax_parametrized_session
    return app.test_client()

def test_flask_mainpage(testapp):
    assert "GitHub" in testapp.get('/').get_data(as_text=True)

