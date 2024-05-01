import json
from typing import Optional
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import PermissionDenied, BadRequest
from django.db.models import Count, F

from ninja import ModelSchema, Schema
from ninja_extra import ControllerBase, api_controller, route, paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema
from martor.utils import markdownify
from profanity_check import predict

from core.api import UserSchema

from .models import Category, Page, Comment


class CategorySchema(ModelSchema):
    class Meta:
        model = Category
        fields = "__all__"


class CategoryCreateSchema(Schema):
    name: str


class PageSchema(ModelSchema):
    class Meta:
        model = Page
        fields = "__all__"


class PageListEntryScema(ModelSchema):
    num_comments: int
    owner: UserSchema

    class Meta:
        model = Page
        fields = "__all__"


class PageCreateSchema(Schema):
    description: str
    title: str


class PageUpdateSchema(Schema):
    description: Optional[str]
    title: Optional[str]


class CommentSchema(ModelSchema):
    class Meta:
        model = Comment
        fields = "__all__"


class CommentListEntrySchema(ModelSchema):
    owner: UserSchema

    class Meta:
        model = Comment
        fields = '__all__'


class CommentCreateSchema(Schema):
    description: str


class CommentUpdateSchema(Schema):
    description: Optional[str]


@api_controller('/forum', tags=['Forum'])
class ForumController(ControllerBase):
    ...


@api_controller('/forum/categories', tags=['Forum.Category'])
class CategoryController(ControllerBase):
    @route.get('', response=NinjaPaginationResponseSchema[CategorySchema], operation_id='category_list')
    @paginate(page_size=50)
    async def list(self):
        return Category.objects.all()

    @route.post('', operation_id='category_new')
    async def post(self, request: HttpRequest, category: CategoryCreateSchema) -> CategorySchema:
        user_obj = request.user
        if not user_obj.is_staff:
            raise PermissionDenied()

        category = Category(
            name=category.name,
        )

        await category.save()

        return category
    
    @route.get('/{int:category}', operation_id='category_detail')
    async def detail(self, category: int) -> CategorySchema:
        return await Category.objects.aget(pk=category)


@api_controller('/forum/categories/{int:category}/pages', tags=['Forum.Page'])
class PageController(ControllerBase):
    @route.get('', response=NinjaPaginationResponseSchema[PageListEntryScema], operation_id='page_list')
    @paginate(page_size=50)
    async def list(self, category: int) -> list[int]:
        return Page.objects.filter(category__pk=category)\
            .annotate(num_comments=Count('comment'))\
            .select_related('owner')
    
    @route.post('', operation_id='page_new')
    async def post(self, request: HttpRequest, page: PageCreateSchema, category: int) -> PageSchema:
        category_obj = await Category.objects.aget(pk=category)

        scores = predict([page.description, page.title])

        if any(scores):
            raise PermissionDenied("You cannot use profanity")

        page = Page(
            category=category_obj,
            title=page.title,
            description=page.description,
            owner=request.user,
        )

        await page.asave()

        return page

    @route.get('/{int:page}', operation_id='page_detail')
    async def detail(self, category: int, page: int) -> PageListEntryScema:
        return await Page.objects\
            .annotate(num_comments=Count('comment'))\
            .select_related('owner')\
            .aget(pk=page)
    
    @route.get('/{int:page}/html', openapi_extra={"responses": {
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
    }}, operation_id='page_html')
    async def html(self, request: HttpRequest, category: int, page: int):
        page_obj = await Page.objects.aget(pk=page)

        result = markdownify(page_obj.description)

        if request.accepts("text/html"):
            return HttpResponse(content=result, content_type="text/html")
        elif request.accepts("application/json"):
            return HttpResponse(content=json.dumps(result), content_type="application/json")
        else:
            raise BadRequest()
    
    @route.patch('/{int:page}', operation_id='page_update')
    async def update(self, request: HttpRequest, update: PageUpdateSchema, category: int, page: int) -> None:
        page_obj: Page = await Page.objects.select_related("owner").aget(pk=page)
        if page_obj.owner.pk != request.user.pk:
            raise PermissionDenied()
        should_save = False
        if update.title is not None:
            if predict([update.title])[0]:
                raise PermissionDenied("You cannot use profanity")
            page_obj.title = update.title
            should_save = True
        if update.description is not None:
            if predict([update.description])[0]:
                raise PermissionDenied("You cannot use profanity")
            page_obj.description = update.description
            should_save = True
        if should_save:
            await page_obj.asave()
    
    @route.delete("/{int:page}", operation_id='page_delete')
    async def delete(self, request: HttpRequest, category: int, page: int) -> None:
        page_obj: Page = await Page.objects.select_related("owner").aget(pk=page)
        if page_obj.owner.pk != request.user.pk:
            raise PermissionDenied()
        await page_obj.adelete()


@api_controller('/forum/categories/{int:category}/pages/{int:page}/comments', tags=['Forum.Comment'])
class CommentController(ControllerBase):
    @route.get('', response=NinjaPaginationResponseSchema[CommentListEntrySchema], operation_id='comment_list')
    @paginate(page_size=50)
    async def list(self, category: int, page: int):
        return Comment.objects.filter(page__pk=page)\
            .annotate(owner_email=F('owner__email'))\
            .annotate(owner_firstname=F('owner__first_name'))\
            .annotate(owner_lastname=F('owner__last_name'))
    
    @route.post('', operation_id='comment_new')
    async def post(self, request: HttpRequest, comment: CommentCreateSchema, category: int, page: int) -> CommentSchema:
        page_obj = await Page.objects.aget(pk=page)

        if predict([comment.description])[0]:
            raise PermissionDenied("You cannot use profanity")

        comment = Comment(
            owner=request.user,
            description=comment.description,
            page=page_obj,
        )

        await comment.asave()

        return comment

    @route.get('/{int:comment}', operation_id='comment_detail')
    async def detail(self, category: int, page: int, comment: int) -> CommentListEntrySchema:
        return await Comment.objects\
            .annotate(owner_email=F('owner__email'))\
            .annotate(owner_firstname=F('owner__first_name'))\
            .annotate(owner_lastname=F('owner__last_name'))\
            .aget(pk=comment)
    
    @route.get('/{int:comment}/html', openapi_extra={"responses": {
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
    }}, operation_id='comment_html')
    async def html(self, request: HttpRequest, category: int, page: int, comment: int):
        comment_obj = await Comment.objects.aget(pk=comment)

        result = markdownify(comment_obj.description)

        if request.accepts("text/html"):
            return HttpResponse(content=result, content_type="text/html")
        elif request.accepts("application/json"):
            return HttpResponse(content=json.dumps(result), content_type="application/json")
        else:
            raise BadRequest()

    @route.patch('/{int:comment}', operation_id='comment_update')
    async def update(self, request: HttpRequest, update: CommentUpdateSchema, category: int, page: int, comment: int) -> None:
        comment_obj = await Comment.objects.select_related("owner").aget(pk=comment)
        if comment_obj.owner.pk != request.user.pk:
            raise PermissionDenied()
        
        if update.description is not None:
            if predict([update.description])[0]:
                raise PermissionDenied("You cannot use profanity")
            comment_obj.description = update.description
            await comment_obj.asave()
    
    @route.delete("/{int:comment}", operation_id='comment_delete')
    async def delete(self, request: HttpRequest, category: int, page: int, comment: int) -> None:
        comment_obj: Comment = await Comment.objects.select_related("owner").aget(pk=comment)
        if comment_obj.owner.pk != request.user.pk:
            raise PermissionDenied("Only the owner of a comment may delete it")
        
        await comment_obj.adelete()
