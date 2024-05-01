from datetime import datetime
import json

from django.http import HttpRequest
from django.test import Client, TestCase as DjangoTestCase

from unittest import TestCase as UnittestTestCase

from careernavigator.util.api import JobseekerPermission, MentorPermission, SuperuserPermission
from careernavigator.util.test import seed_database
from core.models import FailedLogin, User


class RendererRendersUrl(UnittestTestCase):
    def test_render_renders_url(self):
        from .api import Renderer
        renderer = Renderer()
        rendered = renderer.render(HttpRequest(), datetime(year=2020, month=11, day=7, hour=15, minute=31, second=2), response_status=200)
        self.assertEqual(rendered, '"2020-11-07T15:31:02"')


class LoginTestCase(DjangoTestCase):
    def setUp(self):
        self.settings(PASSWORD_HASHERS=[
            "django.contrib.auth.hashers.MD5PasswordHasher",
        ])
        self.db_seed = seed_database()

    def test_login_works(self):
        client = Client()
        login_response = client.post("/api/token/pair", data={
            "username": self.db_seed.superuser.username,
            "password": "iamasuperuser",
        }, content_type="application/json")
        self.assertEqual(login_response.status_code, 200)
        pair = json.loads(login_response.content)
        self.assertEqual(pair["username"], self.db_seed.superuser.username)
        
        verify_response = client.post("/api/token/verify", data={
            "token": pair["access"],
        }, content_type="application/json")
        self.assertEqual(verify_response.status_code, 200)

        refresh_response = client.post("/api/token/refresh", data={
            "refresh": pair["refresh"],
        }, content_type="application/json")
        self.assertEqual(refresh_response.status_code, 200)

    def test_login_blcoked_after_10_tries(self):
        client = Client()

        for i in range(11):
            FailedLogin.objects.all().delete()
            for _ in range(i):
                client.post("/api/token/pair", data={
                    "username": self.db_seed.superuser.username,
                    "password": "wrong",
                }, content_type="application/json")
            response = client.post("/api/token/pair", data={
                "username": self.db_seed.superuser.username,
                "password": "iamasuperuser",
            }, content_type="application/json")

            if i <= 10:
                self.assertEqual(response.status_code, 200)
            else:
                self.assertEqual(response.status_code, 401)



class PermissionsWork(DjangoTestCase):
    def setUp(self) -> None:
        self.settings(PASSWORD_HASHERS=[
            "django.contrib.auth.hashers.MD5PasswordHasher",
        ])
        self.db_seed = seed_database()
    
    def _make_request(self, user: User):
        request = HttpRequest()
        request.user = user
        request.path = '/test'

        return request
    
    def test_superuser_permissions(self):
        p = SuperuserPermission()
        self.assertTrue( p.has_permission(self._make_request(self.db_seed.superuser), None))
        self.assertFalse(p.has_permission(self._make_request(self.db_seed.jobseeker), None))
        self.assertFalse(p.has_permission(self._make_request(self.db_seed.mentor), None))
        self.assertFalse(p.has_permission(self._make_request(self.db_seed.noone), None))
    
    def test_jobseeker_permissions(self):
        p = JobseekerPermission()
        self.assertTrue( p.has_permission(self._make_request(self.db_seed.superuser), None))
        self.assertTrue( p.has_permission(self._make_request(self.db_seed.jobseeker), None))
        self.assertFalse(p.has_permission(self._make_request(self.db_seed.mentor), None))
        self.assertFalse(p.has_permission(self._make_request(self.db_seed.noone), None))
    
    def test_mentor_permissions(self):
        p = MentorPermission()
        self.assertTrue( p.has_permission(self._make_request(self.db_seed.superuser), None))
        self.assertFalse(p.has_permission(self._make_request(self.db_seed.jobseeker), None))
        self.assertTrue( p.has_permission(self._make_request(self.db_seed.mentor), None))
        self.assertFalse(p.has_permission(self._make_request(self.db_seed.noone), None))

