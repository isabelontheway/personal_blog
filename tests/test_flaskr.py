import os
import pytest
from flaskr.factory import create_app
from flaskr.blueprints.flaskr import init_db
import tempfile


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    config = {
        'DATABASE': db_path,
        'TESTING': True
    }

    app = create_app(config=config)

    with app.app_context():
        init_db()
        yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


def test_empty_db(client):
    rv = client.get('/')
    assert b'No entries' in rv.data


def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_login_logout(client):
    rv = login(client, 'admin', 'default')
    assert b'You were logged in' in rv.data
    rv = logout(client, )
    assert b'You were logged out' in rv.data
    rv = login(client, 'adminx', 'default')
    assert b'Invalid username' in rv.data
    rv = login(client, 'admin', 'defaultx')
    assert b'Invalid password' in rv.data


def test_message(client):
    login(client, 'admin', 'default')
    rv = client.post('/add', data = dict(
        title='<Hello>',
        text='<strong>HTML</strong> allowed here'
    ), follow_redirects=True)
    assert b'No entries here so far' not in rv.data
    assert b'Hello' in rv.data
    assert b'<strong>HTML</strong> allowed here' in rv.data
