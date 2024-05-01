from django.http import HttpRequest
from ninja import ModelSchema, Schema
from ninja_extra import ControllerBase, api_controller, route

from .models import QuestionResult


class QuestionItem(ModelSchema):
    class Meta:
        model = QuestionResult
        fields = '__all__'

@api_controller('/results', tags=['Question'])
class QuestionResults(ControllerBase):
    @route.post('/result', operation_id='questionResult')
    async def result(
            self,
            request: HttpRequest,
            MbtiType: str,
            codeOne: str,
            codeTwo: str,
            category_one: str,
            category_two: str,
            category_three: str):
        """Post the results of the questionnaire

        :param request: The original HTTP requests
        :param MbtiType: The determined MBTI type
        :param codeOne: The first Holland Code
        :param codeTwo: The second Holland Code
        :param category_one: The first interest category
        :param category_two: The second interest category
        :param category_three: The third interes tcategory
        """

        user = request.user
        await QuestionResult.objects.acreate(
            user=user,
            MbtiType=MbtiType,
            codeOne=codeOne,
            codeTwo=codeTwo,
            category_one=category_one,
            category_two=category_two,
            category_three=category_three,
        )
        user.complete_question = True
        await user.asave()
