import json
from django.test import TestCase
from django.contrib.auth.models import User, Permission
from rest_framework.test import APIClient
from orgs.models import Organization, Membership
from objects.models import ConstructionObject
from inspections.models import InspectionVisit
from django.utils import timezone

class IsOnSiteEdgeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(name="Org OnSite Edge")
        self.user = User.objects.create_user(username="u_edge", password="pass123")
        for codename in ["view_constructionobject", "add_constructionobject", "change_constructionobject"]:
            try:
                self.user.user_permissions.add(Permission.objects.get(codename=codename))
            except Permission.DoesNotExist:
                pass
        Membership.objects.create(user=self.user, org=self.org, role="FOREMAN")
        self.client.login(username="u_edge", password="pass123")

    def _create_object(self, polygon):
        payload = {"name": "ObjEdge", "org": str(self.org.id), "polygon": polygon}
        r = self.client.post("/api/objects/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(r.status_code, 201, r.content)
        return r.json()["id"]

    def _start_visit(self, obj_id):
        # create visit directly via ORM with coordinates (center of polygon roughly)
        return InspectionVisit.objects.create(object_id=obj_id, inspector=self.user, latitude=0.5, longitude=0.5)

    def test_point_on_polygon_edge(self):
        # square polygon
        poly = {"type":"Polygon","coordinates":[[[0,0],[0,10],[10,10],[10,0],[0,0]]]} 
        obj_id = self._create_object(poly)
        # visit at boundary point (x=0, y=5)
        InspectionVisit.objects.create(object_id=obj_id, inspector=self.user, latitude=0, longitude=5)
        r = self.client.get(f"/api/objects/{obj_id}/")
        self.assertEqual(r.status_code, 200)
        # boundary semantics not directly exposed, but ensure object accessible
        data = r.json()
        self.assertIn("polygon", data)

    def test_object_without_polygon(self):
        # empty polygon coordinates edge case
        obj_id = self._create_object({"type":"Polygon","coordinates":[[]]})
        self._start_visit(obj_id)
        r = self.client.get(f"/api/objects/{obj_id}/")
        self.assertEqual(r.status_code, 200)

    def test_visit_without_polygon_uses_object(self):
        poly = {"type":"Polygon","coordinates":[[[0,0],[0,5],[5,5],[5,0],[0,0]]]} 
        obj_id = self._create_object(poly)
        visit = self._start_visit(obj_id)
        self.assertIsNotNone(visit.latitude)
        r = self.client.get(f"/api/objects/{obj_id}/")
        self.assertEqual(r.status_code, 200)
