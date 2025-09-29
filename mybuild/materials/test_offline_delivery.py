import json
from django.test import TestCase
from django.contrib.auth.models import User, Permission
from rest_framework.test import APIClient
from orgs.models import Organization, Membership
from materials.models import Delivery, MaterialType
from objects.models import ConstructionObject
from django.utils import timezone
from audit.models import AuditLog
from notifications.models import Notification

class OfflineDeliveryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(name="Org Offline")
        self.user = User.objects.create_user(username="u1", password="pass123")
        # perms for delivery (assuming view/add/change exist if model registered)
        for c in ["view_delivery", "add_delivery", "change_delivery"]:
            try:
                self.user.user_permissions.add(Permission.objects.get(codename=c))
            except Permission.DoesNotExist:
                pass
        Membership.objects.create(user=self.user, org=self.org, role="FOREMAN")
        self.client.login(username="u1", password="pass123")

    def test_idempotent_offline_creation(self):
        material = MaterialType.objects.create(name="Песок", unit="т")
        obj = ConstructionObject.objects.create(org=self.org, name="Obj1", polygon={"type":"Polygon","coordinates":[[[0,0],[0,1],[1,1],[1,0],[0,0]]]})
        base_payload = {
            "object": str(obj.id),
            "material": str(material.id),
            "quantity": "10.500",
            "delivered_at": timezone.now().isoformat().replace('+00:00','Z'),
            "offline_batch_id": "batch-123",
            "was_offline": True,
        }
        r1 = self.client.post("/api/deliveries/", data=json.dumps(base_payload), content_type="application/json")
        self.assertEqual(r1.status_code, 201, r1.content)
        first_id = r1.json()["id"]
        count_after_first = Delivery.objects.count()
        # After first create: one audit with create_delivery, one notification delivery.created
        self.assertTrue(AuditLog.objects.filter(action='create_delivery', model='materials.delivery', object_id=str(first_id)).exists())
        self.assertTrue(Notification.objects.filter(user=self.user, kind__icontains='delivery').exists())
        # Replay identical
        r2 = self.client.post("/api/deliveries/", data=json.dumps(base_payload), content_type="application/json")
        self.assertIn(r2.status_code, (200, 201))
        self.assertEqual(Delivery.objects.count(), count_after_first)
        second_id = r2.json()["id"]
        self.assertEqual(first_id, second_id, "Idempotent replay should return same object id")
        # Second call should log replay_delivery
        self.assertTrue(AuditLog.objects.filter(action='replay_delivery', model='materials.delivery', object_id=str(first_id)).exists())
        # Total audit entries for this delivery should be 2
        self.assertEqual(AuditLog.objects.filter(model='materials.delivery', object_id=str(first_id)).count(), 2)

    def test_offline_same_batch_different_users(self):
        material = MaterialType.objects.create(name="Щебень", unit="т")
        obj = ConstructionObject.objects.create(org=self.org, name="Obj2", polygon={"type":"Polygon","coordinates":[[[0,0],[0,1],[1,1],[1,0],[0,0]]]})
        payload = {
            "object": str(obj.id),
            "material": str(material.id),
            "quantity": "5.000",
            "delivered_at": timezone.now().isoformat().replace('+00:00','Z'),
            "offline_batch_id": "shared-batch-1",
            "was_offline": True,
        }
        # First user creates
        r1 = self.client.post("/api/deliveries/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(r1.status_code, 201, r1.content)
        first_id = r1.json()["id"]
        # Second user in same org with same batch id -> should create new Delivery (different id)
        user2 = User.objects.create_user(username="u2", password="pass123")
        for c in ["view_delivery", "add_delivery", "change_delivery"]:
            try:
                user2.user_permissions.add(Permission.objects.get(codename=c))
            except Permission.DoesNotExist:
                pass
        Membership.objects.create(user=user2, org=self.org, role="FOREMAN")
        self.client.logout()
        self.client.login(username="u2", password="pass123")
        r2 = self.client.post("/api/deliveries/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(r2.status_code, 201, r2.content)
        second_id = r2.json()["id"]
        self.assertNotEqual(first_id, second_id, "Different users must not collide on offline_batch_id")
        # Ensure two distinct deliveries exist
        self.assertEqual(Delivery.objects.filter(offline_batch_id="shared-batch-1").count(), 2)
