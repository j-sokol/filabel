import filabel
import os
import pytest
import betamax
import pathlib
import atexit

from click.testing import CliRunner

from helper import * 


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(filabel.cli, ['--help'])
    assert result.exit_code == 0
    assert 'CLI tool for filename-pattern-based labeling of GitHub PRs.' in result.output

def test_cli_config_not_specified():
    runner = CliRunner()
    config_auth = './test/fixtures/auth.fff.cfg'

    result = runner.invoke(filabel.cli, ['--config-auth', config_auth])
    assert 'Labels configuration not supplied' in result.output

def test_cli_invalid_config():
    runner = CliRunner()
    result = runner.invoke(filabel.cli, ['--config-labels', 'test'])
    assert result.exit_code == 2
    assert 'Invalid value' in result.output

def test_cli_invalid_reposlug():
    runner = CliRunner()
    config_labels = './test/fixtures/labels.abc.cfg'
    config_auth = './test/fixtures/auth.fff.cfg'
    slug = 'foobar'

    result = runner.invoke(filabel.cli, ['--config-labels', config_labels, '--config-auth', config_auth, slug])
    assert 'Reposlug {} not valid'.format(slug) in result.output

def test_cli_invalid_second_reposlug():
    runner = CliRunner()
    config_labels = './test/fixtures/labels.abc.cfg'
    config_auth = './test/fixtures/auth.fff.cfg'
    slug1 = 'abc/cdf'
    slug2 = 'foobar'

    result = runner.invoke(filabel.cli, ['--config-labels', config_labels, '--config-auth', config_auth, slug1, slug2])
    assert 'Reposlug {} not valid'.format(slug2) in result.output


def test_cli_post_pr(betamax_session):
    runner = CliRunner()
    config_labels = './test/fixtures/labels.abc.cfg'
    config_auth = './test/fixtures/auth.real.cfg'
    slug = f'{user}/mi-pyt-test-repo'

    filabel.config.session = betamax_session
    result = runner.invoke(filabel.cli, ['--config-labels', config_labels, '--config-auth', config_auth, slug])
    assert '= abc' in result.output or '+ abc' in result.output
    # assert '= abc' in result.output or '+ abc' in result.output
