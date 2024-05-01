import base64
from io import BytesIO
import json
from typing import Optional

from asgiref.sync import sync_to_async

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import PermissionDenied

from ninja import ModelSchema, Schema
from ninja.errors import HttpError
from ninja_extra import ControllerBase
from ninja_extra.controllers import api_controller, route

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from martor.utils import markdownify
from pydantic import TypeAdapter

from careernavigator.util.api import MentorPermission
from core.models import Company, Tip, User

class EducationItem(Schema):
    institution: str
    duration: str
    degree: str

class WorkExperienceItem(Schema):
    company: str
    position: str
    duration: str

class ContactItem(Schema):
    email: str
    phone: str
    address: str

class UserSchema(ModelSchema):
    class Meta:
        model = get_user_model()
        exclude = ('password', )

class ProfileSchema(Schema):
    username: str
    email: str
    last_name: str
    first_name: str
    is_mentor: bool

    @classmethod
    def from_user(cls, user: User) -> "ProfileSchema":
        return cls(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_mentor=user.is_mentor,
        )

class GoalSchema(Schema):
    short_goal: str
    long_goal: str
    motivation1: str
    motivation2: str
    motivation3: str

    @classmethod
    def from_user(cls, user: User) -> "GoalSchema":
        return cls(
            short_goal=user.short_goal,
            long_goal=user.long_goal,
            motivation1=user.motivation1,
            motivation2=user.motivation2,
            motivation3=user.motivation3,
        )

class JobSchema(Schema):
    job_name: str
    personality_type: list[str]
    holland_code: list[str]
    degree: bool
    education_one: str
    education_two: str
    education_three: str

class TipSchema(ModelSchema):
    class Meta:
        model = Tip
        fields= '__all__'

class CompanySchema(ModelSchema):
    class Meta:
        model = Company
        fields = '__all__'

_Education = TypeAdapter(list[EducationItem])
_WorkExperience = TypeAdapter(list[WorkExperienceItem])
_Contact = TypeAdapter(list[ContactItem])

class PlainStringPayload(Schema):
    content: str

@api_controller('/mentor', tags=['Account'])
class MentorCountroller(ControllerBase):
    @route.get('/mymentor', operation_id="get_montor")
    async def get_mentor(self, request: HttpRequest) -> Optional[UserSchema]:
        """Get the assigned mentor for the current user

        :param request: The original HTTP request
        :return: the mentor
        """
        return await User.objects.filter(id=request.user.mentor_id).afirst()
    
    @route.get('/mentees', operation_id='get_mentees')
    async def get_mentees(self, request) -> list[UserSchema]:
        """List all the mentees for the current user

        :param request: The original HTTP request
        :return: a list of mentees
        """
        return get_user_model().objects.filter(mentor__id=request.user.id)

    @route.get('/nomentor', operation_id='nomemtor')
    async def get_empty(self) -> list[UserSchema]:
        """Get a list of users that are wanting for a mentor

        :return: list of users wanting a mentor
        """
        return get_user_model().objects.filter(mentor__isnull=True, is_jobseeker=True, complete_question=True)

    @route.post('/accept', operation_id='accept')
    async def accept(self, request, username: str) -> UserSchema:
        """Accept a user as a mentor

        :param request: The original HTTP request
        :param username: the username of the user to accept
        :return: a full instance of the accepted user
        """
        user = await get_user_model().objects.aget(username=username)
        user.mentor = request.user
        await user.asave()
        return user
    
    @route.post('/goalMotivation', operation_id='goal')
    async def goal(
            self,
            request: HttpRequest,
            short_goal: str,
            long_goal: str,
            motivation1: str,
            motivation2: str,
            motivation3: str) -> UserSchema:
        """Update the goals for the currently logged in user

        :param request: The original HTTP request
        :param short_goal: The short-term goal of this user
        :param long_goal: The long-term goal of this user
        :param motivation1: The contents of the first motivation field
        :param motivation2: The contents of the second motivation field
        :param motivation3: The contents of the third motivation field
        :return: The new user
        """

        user = request.user
        user.short_goal = short_goal
        user.long_goal = long_goal
        user.motivation1 = motivation1
        user.motivation2 = motivation2
        user.motivation3 = motivation3

        await user.asave()
        return user

@api_controller('/tip', tags=['Tip'])
class TipController(ControllerBase):
    @route.get('/newTip', operation_id='tip_new', permissions=[MentorPermission()])
    async def newtip(self, description: str, url: str) -> TipSchema:
        """Create a new tip

        :param description: The description of the new tip
        :param url: The URL associated with the new tip
        :return: The complete created tip instance
        """
        return await Tip.objects.acreate(description=description, url=url)

    @route.delete('/deleteTip/{tip_id}', operation_id='tip_delete', permissions=[MentorPermission()])
    async def delete_tip(self, tip_id: int) -> None:
        """Delete a tip

        :param tip_id: The ID of the tip to delete
        """
        try:
            tip = await Tip.objects.aget(id=tip_id)
            await tip.adelete()
        except Tip.DoesNotExist:
            pass
    
    @route.put('/editTip/{tip_id}', operation_id='tip_edit', permissions=[MentorPermission()])
    async def edit_tip(self, tip_id: int, description: str, url: str) -> TipSchema:
        """Edit a tip

        :param tip_id: The ID of the tip to edit
        :param description: The new description
        :param url: The new URL
        :return: The updated Tip
        """
        try:
            tip = Tip.objects.aget(id=tip_id)
            tip.description = description
            tip.url = url
            await tip.asave()
            return tip
        except Tip.DoesNotExist:
            return None
    
    @route.get('/allTips', operation_id='tip_all')
    async def all_tips(self) -> list[TipSchema]:
        """List all tips

        :return: All tips
        """
        return Tip.objects

@api_controller('/account', tags=['Account'])
class AccountController(ControllerBase):
    @route.get('/new', operation_id='account_new', auth=None)
    async def new(self, username: str, password: str, email: str, last_name: str, first_name: str) -> ProfileSchema:
        """Create a new user

        :param username: The username of the new user
        :param password: The password of the new user
        :param email: The email address of the new user
        :param last_name: The last name of the new user
        :param first_name: The first name of the new user
        :return: The newly created user
        """
        user = await sync_to_async(get_user_model().objects.create_user)(username=username, password=password, email=email, last_name=last_name, first_name=first_name, is_mentor=False, is_jobseeker=True)

        return ProfileSchema.from_user(user)

    @route.get('/by-username/{user}', operation_id='account_profile')
    async def profile(self, user: str|int) -> ProfileSchema:
        """Return the profile of the passed user

        :param user: Either the username or the primary key of the user
        :return: The user instance
        """
        if isinstance(user, int) or user.isdigit():
            user_obj = await get_user_model().objects.aget(pk=int(user))
        else:
            user_obj = await get_user_model().objects.aget(username=user)

        return ProfileSchema.from_user(user_obj)

    @route.get('/by-username/{user}/goals', operation_id='get_user_goals')
    async def goals(self, request: HttpRequest, user: str | int) -> GoalSchema:
        """List the goals of the user

        :param user: The username or the id of the user
        :raises PermissionDeneid: When the requested user is not yourself or one of your mentees
        :return: The goals of the user
        """
        if isinstance(user, str) and user.isdigit():
            user_obj = await get_user_model().objects.aget(pk=int(user))
        else:
            user_obj = await get_user_model().objects.aget(username=user)

        if request.user != user_obj and request.user.id != user_obj.mentor_id:
            raise PermissionDenied("Cannot list goals of a user that is not yourself or one of your mentees")
        
        return GoalSchema.from_user(user_obj)

    @route.post('/update', operation_id='account_update')
    async def update(self,
                     request: HttpRequest,
                     education: list[EducationItem], 
                     work_experience: list[WorkExperienceItem], 
                     contact: list[ContactItem], 
                     interest: str, 
                     skill: str, 
                     others: str) -> UserSchema:
        """Update your own background details

        :param request: The original HTTP request
        :param education: Your education details
        :param work_experience: Your work experience details
        :param contact: Your contact info
        :param interest: Your interests
        :param skill: Your skills
        :param others: Other information
        :return: Your updated user object
        """
        education = education[1:]
        work_experience = work_experience[1:]
        contact = contact[1:]
        
        user = request.user
        user.education = _Education.dump_python(education)
        user.work_experience = _WorkExperience.dump_python(work_experience)
        user.contact = _Contact.dump_python(contact)
        user.interest = interest
        user.skill = skill
        user.others = others
        await sync_to_async(user.resume_pdf.delete)(save=True)
        await user.asave()
        return user

@api_controller('/resume', tags=['Account'])
class ResumeController(ControllerBase):
    @route.get('/download/{username}', operation_id='generate_pdf', openapi_extra={"responses": {
        200: {
            "description": "OK",
            "content": {
                "application/pdf": {},
            },
        },
    }})
    async def download_pdf(self, request: HttpRequest, username: str) -> str:
        """Download the given user's resume

        :param request: The original HTTP request
        :param username: The user to download a resume for
        :raises PermissionDenied: if you are not a mentor and the given username is not your own
        :return: The resume as base64-encoded PDF
        """
        user = await get_user_model().objects.aget(username=username)

        if (not request.user.is_mentor) and user.id != request.user.id:
            raise PermissionDenied("You can only see resumes of other users as a mentor")

        pdf = BytesIO()

        if user.resume_pdf:
            text = base64.b64encode(user.resume_pdf.open('rb').read()).decode('utf-8')
            return text

        p = canvas.Canvas(pdf, pagesize=letter)

        p.setFont("Helvetica", 12)
        p.setStrokeColor(colors.black)

        p.setFont("Helvetica-Bold", 18)
        p.drawString(100, 750, "Curriculum Vitae")
        p.line(100, 740, 320, 740)

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 710, "Personal Information")
        p.setFont("Helvetica", 12)
        p.drawString(100, 690, f"Name: {user.get_full_name()}")
        p.linkURL(
            f"mailto:{user.email}",
            (
                100 + p.stringWidth("Name: ", "Helvetica", 12),
                685,
                100 + p.stringWidth(f"Name: {user.email}", "Helvetica", 12),
                665
            ), relative=1)
        p.drawString(100, 670, f"Email: {user.email}")

        y_position = 660

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 630, "Education")
        y_position = 610
        p.setFont("Helvetica", 12)
        for education in user.education:
            p.drawString(100, y_position, f"Institution: {education['institution']}")
            p.drawString(100, y_position - 20, f"Duration: {education['duration']}")
            p.drawString(100, y_position - 40, f"Degree: {education['degree']}")
            y_position -= 80

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, y_position - 40, "Work Experience")
        y_position -= 60
        p.setFont("Helvetica", 12)
        for experience in user.work_experience:
            p.drawString(100, y_position, f"Company: {experience['company']}")
            p.drawString(100, y_position - 20, f"Position: {experience['position']}")
            p.drawString(100, y_position - 40, f"Duration: {experience['duration']}")
            y_position -= 80

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, y_position - 40, "Interests")
        y_position -= 60
        p.setFont("Helvetica", 12)
        interest_text = p.beginText(100, y_position)
        for line in user.interest.splitlines(False):
            interest_text.textLine(line.rstrip())
        p.drawText(interest_text)
        y_position = interest_text.getY() - 20

        y_position -= 5
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, y_position, "Skills")
        y_position -= 20
        p.setFont("Helvetica", 12)
        skill_text = p.beginText(100, y_position)
        for line in user.skill.splitlines(False):
            skill_text.textLine(line.rstrip())
        p.drawText(skill_text)
        y_position = skill_text.getY() - 20

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, y_position, "Other")
        y_position -= 20
        p.setFont("Helvetica", 12)
        other_text = p.beginText(100, y_position)
        for line in user.others.splitlines(False):
            other_text.textLine(line.rstrip())
        p.drawText(other_text)
        y_position = other_text.getY() - 20

        p.showPage()
        p.save()

        text = base64.b64encode(pdf.getvalue()).decode('utf-8')
        return text

    @route.post("/upload", operation_id='upload_pdf')
    async def upload_pdf(self, request, file: PlainStringPayload):
        """Upload a new resume for yourself

        :param request: The original HTTP request
        :param file: The file to upload as base-64-encoded PDF
        """
        await sync_to_async(request.user.resume_pdf.save)("resume.pdf", ContentFile(base64.b64decode(file.content)), save=True)

@api_controller('/markdown', tags=['Markdown'])
class Markdown(ControllerBase):
    @route.post('/render', openapi_extra={"responses": {
            200: {
                "description": "OK",
                "content": {
                    "text/html": {},
                    "application/json": {
                        "schema": {
                            "type": "string",
                        },
                    },
                },
            },
        }}, operation_id='markdown_render')
    async def render_markdown(self, request: HttpRequest, markdown: PlainStringPayload):
        """Render the passed text as markdown

        :param request: The original HTTP reuqest
        :param markdown: The markdown that needs to be rendered
        :raises HttpError: If the request neither accepts HTML nor JSON. The status code is then 406 Not Acceptable.
        :return: The rendered markdown
        """
        result = markdownify(markdown.content)

        if request.accepts("text/html"):
            return HttpResponse(content=result, content_type="text/html")
        elif request.accepts("application/json"):
            return HttpResponse(content=json.dumps(result), content_type="application/json")
        else:
            raise HttpError(406, "The request must either accept `text/html` or `application/json`.")
