from unittest.mock import MagicMock, patch
import asyncio


from app.tests_pre_start import init, logger


def test_init_successful_connection() -> None:
    client_mock = MagicMock()
    admin_mock = MagicMock()
    command_mock = MagicMock()
    
    client_mock.admin = admin_mock
    admin_mock.command = command_mock
    command_mock.return_value = {"ok": 1}

    with (
        patch("motor.motor_asyncio.AsyncIOMotorClient", return_value=client_mock),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            asyncio.run(init())
            connection_successful = True
        except Exception:
            connection_successful = False

        assert (
            connection_successful
        ), "The database connection should be successful and not raise an exception."

        assert command_mock.called_once_with(
            'ping'
        ), "The client should execute a ping command once."
