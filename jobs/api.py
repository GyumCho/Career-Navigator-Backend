from typing import Optional, Type
from datetime import datetime
from django.http import HttpRequest
from django.utils.text import slugify
from ninja import ModelSchema, Schema
from ninja.orm import create_schema
from ninja_extra import ControllerBase, api_controller, ModelConfig, \
    paginate, route
from ninja_extra.schemas import NinjaPaginationResponseSchema
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from careernavigator.util.api import MentorPermission
from core.models import Company, User
from questionnaire.models import QuestionResult
 
from .models import Job, JobApplication, JobBookmark

JobSchema: Type[ModelSchema] = create_schema(Job, depth=1)

class JobApplicationCreateSchema(ModelSchema):
    class Meta:
        model=JobApplication
        fields = ['job']

class JobCreateSchema(ModelSchema):
    company_name: str
    company_description: str

    class Meta:
        model=Job
        fields = '__all__'
        exclude = ['company', 'id']

class BookmarkSchema(ModelSchema):
    #user: UserSchema
    job: JobSchema # type: ignore

    class Meta:
        model = JobBookmark
        fields = "__all__"

class ApplicationOut(Schema):
    applied_date: datetime
    organization: str
    location: str
    position: str
    image: str
    keywords : str
    sent: bool
    processed: bool
    interviewed: bool
    tested: bool
    feedback: str

class JobApplicationSchema(ModelSchema):
    job: JobSchema

    class Meta:
        model = JobApplication
        fields = "__all__"

class FeedbackRequestSchema(ModelSchema):
    class Meta:
        model = JobApplication
        fields = (
            "sent",
            "processed",
            "interviewed",
            "tested",
            "feedback",
        )

@api_controller('/jobs/applications', tags='Application')
class JobApplicationController(ControllerBase):
    @route.get('', response=NinjaPaginationResponseSchema[ApplicationOut], operation_id='list_applications')
    @paginate(page_size=50)
    async def list_applications(self, request: HttpRequest):
        """List all applications for the current user

        :param request: The original HTTP request
        :return: All the applications done by the current user
        """
        return [
            ApplicationOut(
                applied_date=application.applied_date,
                organization=application.job.company.name,
                position=application.job.title,
                location=application.job.location,
                image=application.job.image,
                keywords=application.job.keywords,
                sent=application.sent,
                processed=application.processed,
                interviewed=application.interviewed,
                tested=application.tested,
                feedback=application.feedback,
            )
            async for application in JobApplication.objects.filter(user=request.user).select_related('job', 'job__company').aiterator()
        ]
    
    @route.post('/', operation_id='create_application')
    async def create(self, request: HttpRequest, application: JobApplicationCreateSchema) -> JobApplicationSchema:
        """Apply to a job

        :param request: The original HTTP request
        :param application: The details for the application
        :return: The created application
        """
        await JobApplication.objects.acreate(
            user=request.user,
            job=Job(id=application.job),
        )

        return await JobApplication.objects.filter(user=request.user, job=Job(id=application.job)).select_related('job').afirst()

    @route.get('get-by-username/{username}', operation_id='get_applications')
    async def get_applications(self, request: HttpRequest, username: str) -> list[JobApplicationSchema]:
        """List all applications that the given user has done

        You can only fetch the list of applications of a user if you are their
        mentor, or if you are fetching your own applications.

        :param username: The user to request the applications for
        :raises PermissionDenied: When you try to get the applications for someone who is not yourself or your mentee
        :return: a list of applications
        """
        mentee = await User.objects.aget(username=username)
        if not (request.user.is_mentor and mentee.mentor_id == request.user.id) and request.user != mentee:
            raise PermissionDenied("Can only fetch applications for mentees or yourself")

        return JobApplication.objects.filter(user=mentee).select_related('job')
    
    @route.get('get-by-id/{id}', operation_id='get_application')
    async def get_application(self, request: HttpRequest, id: int) -> Optional[JobApplicationSchema]:
        """Get a job application by id

        :param request: The original HTTP request
        :param id: the ID of the job application
        :raises PermissionDenied: When you attempt to get an application for someone who is not yourself or your mentor
        :return: the job application
        """
        application = await JobApplication.objects.aget(id=id)
        if application.user_id == request.user.id:
            return application
        
        if await User.objects.filter(mentor=request.user, id=application.user_id).aexists():
            return application
        
        raise PermissionDenied("Cannot get an application if you are not the mentor of that user, or the user that is applying")
    
    @route.post('set-feedback/{id}', operation_id='set_feedback')
    async def update_progress(self, request: HttpRequest, id: int, feedback: FeedbackRequestSchema) -> JobApplicationSchema:
        """Update the feedback for a job application

        :param request: The original HTTP request
        :param id: The ID of the application
        :param feedback: The new feedback information
        :raises PermissionDenied: When you try to change feedback for someone who is not your mentee
        :return: The new job application
        """
        application: JobApplication = await JobApplication.objects.select_related('user', 'user__mentor').aget(pk=id)
        if application.user.mentor.id != request.user.id:
            raise PermissionDenied("Cannot feed back on applications for users which are not your mentees")

        application.sent = feedback.sent
        application.processed = feedback.processed
        application.interviewed = feedback.interviewed
        application.tested = feedback.tested
        application.feedback = feedback.feedback

        await application.asave()
        return application

@api_controller('/jobs', tags='Job')
class JobController(ControllerBase):
    @route.get('/by-id/{id}', operation_id='find_one')
    async def find_one(self, id: int) -> JobSchema: # type: ignore
        """Find a job by its ID

        :param id: The ID of the job
        :return: The actual job
        """
        return await Job.objects.select_related('company').aget(pk=id)

    @route.get('', response=NinjaPaginationResponseSchema[JobSchema], operation_id='list')
    @paginate(page_size=50)
    async def list_jobs(self) -> list[Job]:
        """Return all jobs

        :return: All jobs
        """
        return Job.objects.select_related('company')
    
    @route.get('/recommended', operation_id='recommended', response=Optional[list[JobSchema]])
    async def get_recommended(self, request: HttpRequest):
        """Get recommended jobs for the current uesr

        :param request: The original HTTP request
        :return: All recommended jobs for the current user
        """
        qs = await QuestionResult.objects.filter(user=request.user).afirst()
        if (qs != None):
            codeOne = qs.codeOne
            codeTwo = qs.codeTwo
            mbti = qs.MbtiType
            c1 = qs.category_one
            c2 = qs.category_two
            c3 = qs.category_three
            return Job.objects\
                .select_related('company')\
                .filter(Q(mbti__contains=mbti) | Q(holland__contains=codeOne) | Q(holland__contains=codeTwo)
                        | Q(job_fields__contains=c1) | Q(job_fields__contains=c2) | Q(job_fields__contains=c3))
        else:
            return


    @route.get('/search', response=list[JobSchema], operation_id='search_jobs')
    async def get_jobs(self, search: str, company: str = ""):
        """Return jobs by search string

        :param search: The search string
        :param company: The company that should be filtered on, defaults to ""
        :return: All jobs that have been found
        """
        jobs = Job.objects\
            .select_related('company')\
            .filter(Q(title__contains=search) | Q(description__contains=search) | Q(keywords__contains=search) | Q(company__name__contains=search))
        if company != "":
            jobs = jobs.filter(company_name__contains=search)
        return jobs


@api_controller('/jobs/manage', tags='Job', permissions=[MentorPermission()])
class JobCreateController(ControllerBase):
    model_config = ModelConfig(
        model=Job,
        async_routes=True,
        allowed_routes=[
            "update",
            "patch",
            "delete",
        ],
        update_route_info = {"operation_id": "update_job"},
        patch_route_info = {"operation_id": "patch_job"},
        delete_route_info = {"operation_id": "delete_job"},
    )

    @route.post('/', operation_id='create_job')
    async def create(self, job: JobCreateSchema):
        """Create a job

        :param job: Data for the job to create
        """
        try:
            company = await Company.objects.aget(name=job.company_name)
        except Company.DoesNotExist:
            company = Company(name=job.company_name, 
                              slug=slugify(job.company_name))
 
            
        print(job.company_description)
        if job.company_description != "":
            company.description = job.company_description
            await company.asave()

        await Job.objects.acreate(
            title=job.title,
            company=company,
            location=job.location,
            description=job.description,
            requirements=job.requirements,
            salary=job.salary,
            instructions=job.instructions,
            deadline=job.deadline,
            keywords=job.keywords,
            image=job.image,
            contact_info=job.contact_info,
            mbti=job.mbti,
            job_fields=job.job_fields,
            holland=job.holland,
            additional=job.additional
        )

@api_controller('/bookmark', tags='Bookmark')
class BookmarkController(ControllerBase): 
    @route.get('', response=NinjaPaginationResponseSchema[JobSchema], operation_id='get_bookmarks')
    @paginate(page_size=50)   
    async def get_bookmarks(self, request: HttpRequest):
        """List all bookmarks for the currently logged in user

        :param request: The original HTTP request
        :return: All bookmarked jobs
        """
        return Job.objects.filter(jobbookmark__user=request.user)

    @route.post('', operation_id='bookmark_job') 
    async def bookmark_job(self, request: HttpRequest, jobid: int) -> BookmarkSchema:
        """Bookmark a job

        :param request: The original HTTP request
        :param jobid: The ID of the job to bookmark
        :return: The final bookmark
        """
        return await JobBookmark.objects.acreate(user=request.user, job_id=jobid)

    @route.delete('', operation_id='delete_bookmark')
    async def delete_bookmark(self, request: HttpRequest, job_id: int) -> None:
        """Delete a bookmark by the ID of the job

        :param request: The original HTTP request
        :param job_id: The ID of the job for which we'll delete the bookmark
        """
        await JobBookmark.objects.filter(user=request.user, job__id=job_id).adelete()
