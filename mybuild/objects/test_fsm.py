import json
from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase
from rest_framework.test import APIClient
from orgs.models import Organization, Membership
from objects.models import ConstructionObject, ObjectStatus, OpeningChecklist, OpeningChecklistStatus
from notifications.models import Notification
from audit.models import AuditLog


class FSMTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(name="Org FSM")
        self.admin = User.objects.create_user(username="admin1", password="pass123")
        # Give model base perms
        for codename in [
            "view_constructionobject", "add_constructionobject", "change_constructionobject",
            "view_openingchecklist", "add_openingchecklist", "change_openingchecklist"
        ]:
            self.admin.user_permissions.add(Permission.objects.get(codename=codename))
        Membership.objects.create(user=self.admin, org=self.org, role="ADMIN")
        self.client.login(username="admin1", password="pass123")
        # create object
        payload = {"name": "FSM Obj", "org": str(self.org.id), "polygon": {"type": "Polygon", "coordinates": [[[0,0],[0,1],[1,1],[1,0],[0,0]]]}}
        r = self.client.post("/api/objects/", data=json.dumps(payload), content_type="application/json")
        assert r.status_code == 201, r.content
        self.obj_id = r.json()["id"]

    def test_object_plan_and_activation_flow(self):
        # initial status
        obj = ConstructionObject.objects.get(id=self.obj_id)
        self.assertEqual(obj.status, ObjectStatus.DRAFT)
        # plan
        r = self.client.post(f"/api/objects/{self.obj_id}/plan/")
        self.assertEqual(r.status_code, 200, r.content)
        obj.refresh_from_db()
        self.assertEqual(obj.status, ObjectStatus.PLANNED)
        # request activation
        r = self.client.post(f"/api/objects/{self.obj_id}/request_activation/")
        self.assertEqual(r.status_code, 200, r.content)
        obj.refresh_from_db()
        self.assertEqual(obj.status, ObjectStatus.ACTIVATION_PENDING)
        # activate
        r = self.client.post(f"/api/objects/{self.obj_id}/activate/")
        self.assertEqual(r.status_code, 200, r.content)
        obj.refresh_from_db()
        self.assertEqual(obj.status, ObjectStatus.ACTIVE)
        # audit entries present
        actions = list(AuditLog.objects.filter(model="objects.constructionobject").values_list("action", flat=True))
        self.assertIn("object_plan", actions)
        self.assertIn("object_request_activation", actions)
        self.assertIn("object_activate", actions)
        # notifications for last action
        self.assertTrue(Notification.objects.filter(kind="object.activated").exists())

    def test_checklist_submit_approve(self):
        obj = ConstructionObject.objects.get(id=self.obj_id)
        # Create checklist directly
        checklist = OpeningChecklist.objects.create(object=obj, data={"fields": []})
        self.assertEqual(checklist.status, OpeningChecklistStatus.DRAFT)
        # submit
        r = self.client.post(f"/api/opening-checklists/{checklist.id}/submit/")
        self.assertEqual(r.status_code, 200, r.content)
        checklist.refresh_from_db()
        self.assertEqual(checklist.status, OpeningChecklistStatus.SUBMITTED)
        # approve
        r = self.client.post(f"/api/opening-checklists/{checklist.id}/approve/")
        self.assertEqual(r.status_code, 200, r.content)
        checklist.refresh_from_db()
        self.assertEqual(checklist.status, OpeningChecklistStatus.APPROVED)
        actions = list(AuditLog.objects.filter(model="objects.openingchecklist").values_list("action", flat=True))
        self.assertIn("checklist_submit", actions)
        self.assertIn("checklist_approve", actions)
        self.assertTrue(Notification.objects.filter(kind="checklist.approved").exists())

    def test_checklist_reject_path(self):
        obj = ConstructionObject.objects.get(id=self.obj_id)
        checklist = OpeningChecklist.objects.create(object=obj, data={"fields": []})
        r = self.client.post(f"/api/opening-checklists/{checklist.id}/submit/")
        self.assertEqual(r.status_code, 200)
        r = self.client.post(f"/api/opening-checklists/{checklist.id}/reject/", data={"comment": "Не хватает данных"})
        self.assertEqual(r.status_code, 200, r.content)
        checklist.refresh_from_db()
        self.assertEqual(checklist.status, OpeningChecklistStatus.REJECTED)
        actions = list(AuditLog.objects.filter(model="objects.openingchecklist").values_list("action", flat=True))
        self.assertIn("checklist_reject", actions)
        self.assertTrue(Notification.objects.filter(kind="checklist.rejected").exists())

    # --- Negative FSM cases ---
    def test_object_activate_twice_fails(self):
        obj = ConstructionObject.objects.get(id=self.obj_id)
        # normal flow to ACTIVE
        self.client.post(f"/api/objects/{self.obj_id}/plan/")
        self.client.post(f"/api/objects/{self.obj_id}/request_activation/")
        r = self.client.post(f"/api/objects/{self.obj_id}/activate/")
        self.assertEqual(r.status_code, 200, r.content)
        obj.refresh_from_db()
        self.assertEqual(obj.status, ObjectStatus.ACTIVE)
        # second activate should 400 and not change status
        r2 = self.client.post(f"/api/objects/{self.obj_id}/activate/")
        self.assertEqual(r2.status_code, 400, r2.content)
        obj.refresh_from_db()
        self.assertEqual(obj.status, ObjectStatus.ACTIVE)

    def test_checklist_approve_from_draft_fails(self):
        obj = ConstructionObject.objects.get(id=self.obj_id)
        checklist = OpeningChecklist.objects.create(object=obj, data={"fields": []})
        self.assertEqual(checklist.status, OpeningChecklistStatus.DRAFT)
        r = self.client.post(f"/api/opening-checklists/{checklist.id}/approve/")
        self.assertEqual(r.status_code, 400, r.content)
        checklist.refresh_from_db()
        self.assertEqual(checklist.status, OpeningChecklistStatus.DRAFT)

    def test_checklist_reject_from_draft_fails(self):
        obj = ConstructionObject.objects.get(id=self.obj_id)
        checklist = OpeningChecklist.objects.create(object=obj, data={"fields": []})
        r = self.client.post(f"/api/opening-checklists/{checklist.id}/reject/", data={"comment": "Нет данных"})
        self.assertEqual(r.status_code, 400, r.content)
        checklist.refresh_from_db()
        self.assertEqual(checklist.status, OpeningChecklistStatus.DRAFT)
