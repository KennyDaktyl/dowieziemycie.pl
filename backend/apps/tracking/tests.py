from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.fleet.models import Driver

from .consumers import DriverTrackConsumer, LiveMapConsumer


class DriverTrackConsumerTests(TestCase):
    async def _connect_driver(self, token):
        communicator = WebsocketCommunicator(DriverTrackConsumer.as_asgi(), f"/ws/driver/track/?token={token}")
        connected, _ = await communicator.connect()
        return communicator, connected

    async def test_rejects_missing_token(self):
        communicator, connected = await self._connect_driver("")
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_rejects_invalid_token(self):
        communicator, connected = await self._connect_driver("not-a-real-token")
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_accepts_valid_token_updates_position_and_broadcasts(self):
        user = await User.objects.acreate(username="driver1")
        driver = await Driver.objects.acreate(user=user, name="Jan Testowy", status=Driver.Status.DOSTEPNY)
        token = str(RefreshToken.for_user(driver).access_token)

        driver_socket, connected = await self._connect_driver(token)
        self.assertTrue(connected)

        map_socket = WebsocketCommunicator(LiveMapConsumer.as_asgi(), "/ws/live-map/")
        map_connected, _ = await map_socket.connect()
        self.assertTrue(map_connected)

        # Initial snapshot on connect — driver has no position yet, so empty.
        snapshot = await map_socket.receive_json_from()
        self.assertEqual(snapshot["type"], "snapshot")
        self.assertEqual(snapshot["drivers"], [])

        await driver_socket.send_json_to({"lat": 50.0614, "lng": 19.9366, "status": "W_KURSIE"})

        update = await map_socket.receive_json_from()
        self.assertEqual(update["type"], "update")
        self.assertEqual(update["driver"]["id"], driver.id)
        self.assertEqual(update["driver"]["status"], "W_KURSIE")
        self.assertEqual(update["driver"]["current_lat"], "50.061400")

        await driver.arefresh_from_db()
        self.assertEqual(driver.status, Driver.Status.W_KURSIE)
        self.assertIsNotNone(driver.location_updated_at)

        await driver_socket.disconnect()
        await map_socket.disconnect()

    async def test_ignores_malformed_payload(self):
        user = await User.objects.acreate(username="driver2")
        driver = await Driver.objects.acreate(user=user, name="Ewa Testowa")
        token = str(RefreshToken.for_user(driver).access_token)

        communicator, connected = await self._connect_driver(token)
        self.assertTrue(connected)

        await communicator.send_json_to({"lat": "not-a-number", "lng": 19.9})
        # Should not raise and should not close the connection.
        self.assertTrue(await communicator.receive_nothing())

        await driver.arefresh_from_db()
        self.assertIsNone(driver.current_lat)

        await communicator.disconnect()


class LiveMapConsumerTests(TestCase):
    async def test_snapshot_excludes_offline_and_positionless_drivers(self):
        user1 = await User.objects.acreate(username="visible")
        await Driver.objects.acreate(
            user=user1, name="Widoczny", status=Driver.Status.DOSTEPNY, current_lat=50.06, current_lng=19.93,
        )
        user2 = await User.objects.acreate(username="offline")
        await Driver.objects.acreate(
            user=user2, name="Offline", status=Driver.Status.OFFLINE, current_lat=50.06, current_lng=19.93,
        )
        user3 = await User.objects.acreate(username="no-position")
        await Driver.objects.acreate(user=user3, name="Bez pozycji", status=Driver.Status.DOSTEPNY)

        communicator = WebsocketCommunicator(LiveMapConsumer.as_asgi(), "/ws/live-map/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        snapshot = await communicator.receive_json_from()
        self.assertEqual(len(snapshot["drivers"]), 1)
        self.assertEqual(snapshot["drivers"][0]["name"], "Widoczny")

        await communicator.disconnect()
