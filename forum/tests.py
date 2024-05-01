from django.test import Client, TestCase
from ninja_jwt.tokens import RefreshToken

from careernavigator.util.test import seed_database


class VulgarityTestCase(TestCase):
    def setUp(self):
        self.settings(PASSWORD_HASHERS=[
            "django.contrib.auth.hashers.MD5PasswordHasher",
        ])
        self.db_seed = seed_database()

    def test_all_kinds_of_vulgar_shit(self):
        client = Client()
        ret = RefreshToken.for_user(self.db_seed.superuser)

        def do_test(title, body, vulgar=True):
            response = client.post(f'/api/forum/categories/{self.db_seed.category.id}/pages', data={
                "description": body,
                "title": title,
            }, content_type='application/json', headers={'Authorization': f'Bearer {ret.access_token}'})
            if vulgar:
                self.assertEqual(response.status_code, 403, "Submitted vulgar text, but was not caught")
            else:
                self.assertEqual(response.status_code, 200, "Benign text was recognized as vulgar")
            
        
        do_test(title="Fuck you", body="Benign text")
        do_test(title="Benign question", body="Shit!")
