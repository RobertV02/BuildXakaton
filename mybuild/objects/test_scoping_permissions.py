import json
from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase
from rest_framework.test import APIClient

from orgs.models import Organization, Membership
from objects.models import ConstructionObject


class ObjectScopingPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create two users and two orgs
        self.org_a = Organization.objects.create(name="Org A")
        self.org_b = Organization.objects.create(name="Org B")
        self.user_a = User.objects.create_user(username="user_a", password="pass123")
        self.user_b = User.objects.create_user(username="user_b", password="pass123")
        # Memberships
        Membership.objects.create(user=self.user_a, org=self.org_a, role="FOREMAN")
        Membership.objects.create(user=self.user_b, org=self.org_b, role="FOREMAN")
        # Create objects in each org
        base_polygon = {"type": "Polygon", "coordinates": [[[0,0],[0,1],[1,1],[1,0],[0,0]]]}  # minimal valid polygon
        self.obj_a1 = ConstructionObject.objects.create(name="Obj A1", org=self.org_a, polygon=base_polygon)
        self.obj_b1 = ConstructionObject.objects.create(name="Obj B1", org=self.org_b, polygon=base_polygon)
        # Grant basic view permission group to both users (simulate init command output)
        view_perm = Permission.objects.get(codename="view_constructionobject")
        grp_view = Group.objects.create(name="VIEWERS")
        grp_view.permissions.add(view_perm)
        self.user_a.groups.add(grp_view)
        self.user_b.groups.add(grp_view)

    def test_user_sees_only_own_org_objects(self):
        self.client.login(username="user_a", password="pass123")
        resp = self.client.get("/api/objects/")
        self.assertEqual(resp.status_code, 200)
        ids = {o['id'] for o in resp.json()}
        self.assertIn(str(self.obj_a1.id), ids)
        self.assertNotIn(str(self.obj_b1.id), ids)

    def test_user_cannot_create_without_add_permission(self):
        self.client.login(username="user_a", password="pass123")
        payload = {"name": "New Obj", "org": str(self.org_a.id), "polygon": {"type": "Polygon", "coordinates": [[[0,0],[0,1],[1,1],[1,0],[0,0]]]}}
        resp = self.client.post("/api/objects/", data=json.dumps(payload), content_type="application/json")
        self.assertIn(resp.status_code, (401, 403))
        self.assertFalse(ConstructionObject.objects.filter(name="New Obj").exists())

    def test_user_with_add_permission_can_create(self):
        add_perm = Permission.objects.get(codename="add_constructionobject")
        grp_edit = Group.objects.create(name="EDITORS")
        grp_edit.permissions.add(add_perm, Permission.objects.get(codename="view_constructionobject"))
        self.user_a.groups.add(grp_edit)
        self.client.login(username="user_a", password="pass123")
        payload = {"name": "Creatable", "org": str(self.org_a.id), "polygon": {"type": "Polygon", "coordinates": [[[0,0],[0,1],[1,1],[1,0],[0,0]]]}}
        resp = self.client.post("/api/objects/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertTrue(ConstructionObject.objects.filter(name="Creatable").exists())

    def test_cross_org_create_forbidden_even_with_permission(self):
        # Give add permission but attempt to create object in foreign org
        add_perm = Permission.objects.get(codename="add_constructionobject")
        grp_edit = Group.objects.create(name="EDITORS2")
        grp_edit.permissions.add(add_perm, Permission.objects.get(codename="view_constructionobject"))
        self.user_a.groups.add(grp_edit)
        self.client.login(username="user_a", password="pass123")
        payload = {"name": "Bad Obj", "org": str(self.org_b.id), "polygon": {"type": "Polygon", "coordinates": [[[0,0],[0,1],[1,1],[1,0],[0,0]]]}}
        resp = self.client.post("/api/objects/", data=json.dumps(payload), content_type="application/json")
        # Should be forbidden by scoping/permission logic
        self.assertIn(resp.status_code, (401, 403))
        self.assertFalse(ConstructionObject.objects.filter(name="Bad Obj").exists())
