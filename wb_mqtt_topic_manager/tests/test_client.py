import pytest
from client import MQTTClient


@pytest.mark.skip
def test_connect_disconnect_with_context():
    with MQTTClient(
        broker_host='test.mosquitto.org', broker_port=1883, client_id='test_client'
    ) as client:
        assert client.connection_info == {
            'broker_host': 'test.mosquitto.org',
            'broker_port': 1883,
            'connected': True,
            'client_id': 'test_client',
        }

    assert not client.is_connected


@pytest.mark.skip
def test_connect_disconnect_with_try_finally():
    client = MQTTClient(
        broker_host='test.mosquitto.org', broker_port=1883, client_id='test_client'
    )

    if client.connect():
        try:
            assert client.connection_info == {
                'broker_host': 'test.mosquitto.org',
                'broker_port': 1883,
                'connected': True,
                'client_id': 'test_client',
            }
        finally:
            client.disconnect()

    assert not client.is_connected


@pytest.mark.skip
def test_client_from_fixture(test_client: MQTTClient):
    assert test_client.connection_info == {
        'broker_host': 'test.mosquitto.org',
        'broker_port': 1883,
        'connected': True,
        'client_id': 'test_client',
    }
