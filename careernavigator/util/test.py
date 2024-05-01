from dataclasses import dataclass
from core.models import User
from forum.models import Category, Page


@dataclass
class DatabaseSeed:
    mentor: User
    jobseeker: User
    sad_jobseeker: User
    lazy_jobseeker: User
    superuser: User
    noone: User
    category: Category
    page: Page


def seed_database() -> DatabaseSeed:
    mentor = User.objects.create_user(
        username="mentor_test",
        password="iamamentor",
        email="mentor@test.com",
        last_name="Test",
        first_name="Mentor",
        is_mentor=True,
        is_jobseeker=False)
    jobseeker = User.objects.create_user(
        username="jobseeker_test",
        password="iamajobseeker",
        email="jobskeer@test.com",
        last_name="Test",
        first_name="Jobseker",
        is_mentor=False,
        mentor=mentor,
        is_jobseeker=True,
        complete_question=True)
    sad_jobseeker = User.objects.create_user(
        username="sad_jobseeker_test",
        password="iamasadjobseeker",
        email="sadjobskeer@test.com",
        last_name="Jobseeker",
        first_name="Sad",
        is_mentor=False,
        is_jobseeker=True,
        complete_question=True)
    lazy_jobseeker = User.objects.create_user(
        username="lazy_jobseeker_test",
        password="iamalazyjobseeker",
        email="sadjobskeer@test.com",
        last_name="Jobseeker",
        first_name="Lazy",
        is_mentor=False,
        is_jobseeker=True,
        complete_question=False)
    superuser = User.objects.create_user(
        username="superuser_test",
        password="iamasuperuser",
        email="superuser@test.com",
        last_name="Test",
        first_name="Superuser",
        is_mentor=False,
        is_jobseeker=False,
        is_superuser=True)
    noone = User.objects.create_user(
        username="noone_test",
        password="iamanoone",
        email="noone@test.com",
        last_name="Test",
        first_name="Noone",
        is_mentor=False,
        is_jobseeker=False)
    
    category = Category.objects.create(
        name="Test Category"
    )
    page = Page.objects.create(
        owner=superuser,
        category=category,
        title="Test Page",
        description="Test description",
    )
    
    return DatabaseSeed(
        mentor=mentor,
        jobseeker=jobseeker,
        sad_jobseeker=sad_jobseeker,
        lazy_jobseeker=lazy_jobseeker,
        superuser=superuser,
        noone=noone,
        category=category,
        page=page,
    )
