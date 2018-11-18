import filabel
import os
import pytest
import betamax
from click.testing import CliRunner


@pytest.fixture
def testapp():
    from filabel import app
    app.config['TESTING'] = True
    return app.test_client()

def test_flask_mainpage(testapp):
    assert "GitHub" in testapp.get('/').get_data(as_text=True)

