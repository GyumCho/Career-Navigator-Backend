from django.http import HttpRequest
from django.test import Client, TestCase as DjangoTestCase
from ninja_jwt.tokens import RefreshToken
from unittest import IsolatedAsyncioTestCase

from pydantic import TypeAdapter

from careernavigator.util.test import seed_database
from core.api import UserSchema
from core.models import User


class RenderMarkdownTest(IsolatedAsyncioTestCase):
    async def test_markdown_renders(self):
        from .api import Markdown, PlainStringPayload

        payload = PlainStringPayload(content="# Test")
        request = HttpRequest()
        request.path = '/markdown/render'
        request.content_type = 'application/json'
        request.headers = {'Accept': 'text/html'}
        request._body = payload.model_dump_json()
        self.assertEqual(
            (await Markdown().render_markdown(
                request=request,
                markdown=payload,
            )).content,
            b"<h1>Test</h1>"
        )


class TestMentors(DjangoTestCase):
    def setUp(self) -> None:
        self.db_seed = seed_database()
        self.client = Client()
    
    def test_get_mentor_works(self) -> None:
        ret = RefreshToken.for_user(self.db_seed.jobseeker)
        response = self.client.get('/api/mentor/mymentor', headers={'Authorization': f'Bearer {ret.access_token}'})
        mentor: User = UserSchema.model_validate_json(response.content)

        self.assertEqual(mentor.id, self.db_seed.mentor.id)

    def test_get_mentees_works(self) -> None:
        ret = RefreshToken.for_user(self.db_seed.mentor)
        response = self.client.get('/api/mentor/mentees', headers={'Authorization': f'Bearer {ret.access_token}'})
        mentees: list[User] = TypeAdapter(list[UserSchema]).validate_json(response.content)

        self.assertEqual(len(mentees), 1)
        self.assertEqual(mentees[0].id, self.db_seed.jobseeker.id)

    def test_get_empty_works(self) -> None:
        ret = RefreshToken.for_user(self.db_seed.mentor)
        response = self.client.get('/api/mentor/nomentor', headers={'Authorization': f'Bearer {ret.access_token}'})
        mentees: list[User] = TypeAdapter(list[UserSchema]).validate_json(response.content)

        self.assertEqual(len(mentees), 1)
        self.assertEqual(mentees[0].id, self.db_seed.sad_jobseeker.id)

    def test_accept_works(self) -> None:
        ret = RefreshToken.for_user(self.db_seed.mentor)
        response = self.client.post(f'/api/mentor/accept?username={self.db_seed.sad_jobseeker.username}', headers={'Authorization': f'Bearer {ret.access_token}'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/api/mentor/mentees', headers={'Authorization': f'Bearer {ret.access_token}'})
        mentees: list[User] = TypeAdapter(list[UserSchema]).validate_json(response.content)

        self.assertEqual(len(mentees), 2)
        self.assertEqual(len(list(filter(lambda mentee: mentee.id == self.db_seed.sad_jobseeker.id, mentees))), 1)
