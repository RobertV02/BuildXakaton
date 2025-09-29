import json
from django.test import TestCase
from django.contrib.auth.models import User, Permission
from rest_framework.test import APIClient
from orgs.models import Organization, Membership
from objects.models import ConstructionObject
from inspections.models import InspectionVisit

class IsOnSitePermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='inspector', password='pass123')
        self.org = Organization.objects.create(name='GeoOrg')
        Membership.objects.create(user=self.user, org=self.org, role='INSPECTOR')
        self.client.login(username='inspector', password='pass123')
        self.polygon = {"type": "Polygon", "coordinates": [[[30.0,50.0],[30.0,50.01],[30.01,50.01],[30.01,50.0],[30.0,50.0]]]}  # tiny square
        self.obj = ConstructionObject.objects.create(org=self.org, name='GeoObj', polygon=self.polygon)

    def _create_visit(self, lon, lat):
        return InspectionVisit.objects.create(object=self.obj, inspector=self.user, longitude=lon, latitude=lat)

    def test_point_inside_polygon(self):
        self._create_visit(30.005, 50.005)
        # Dummy protected endpoint: use object detail (permission will run object-level) if attached later; here we just assert method
        from core.permissions import IsOnSite
        perm = IsOnSite()
        class DummyView: pass
        allowed = perm.has_object_permission(self._dummy_request(), DummyView(), self.obj)
        self.assertTrue(allowed)

    def test_point_outside_polygon(self):
        self._create_visit(31.0, 51.0)
        from core.permissions import IsOnSite
        perm = IsOnSite()
        class DummyView: pass
        allowed = perm.has_object_permission(self._dummy_request(), DummyView(), self.obj)
        self.assertFalse(allowed)

    def _dummy_request(self):
        from types import SimpleNamespace
        return SimpleNamespace(user=self.user)
