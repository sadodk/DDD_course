from application.main import app

app.testing = True
client = app.test_client()


def test_index():
    response = client.get("/")
    assert b'{"status":"OK"}' in response.data
