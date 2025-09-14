from constants import Roles
from models.errors_model import ForbiddenResponse
from models.user_create_models import CreateUserRequest, CreateUserResponse, \
    GetUserResponse


class TestUser:

    def test_create_user(self, super_admin, creation_user_data: CreateUserRequest):
        response = super_admin.api.user_api.create_user(creation_user_data,
        expected_status=201).json()

        user_model = CreateUserResponse(**response)

        assert user_model.id, "ID должен быть не пустым"
        assert user_model.email == creation_user_data.email
        assert user_model.fullName == creation_user_data.fullName
        assert Roles.USER in user_model.roles  # Enum(str) — сравнение с самим Roles.USER ок
        assert user_model.verified is True
        assert user_model.banned is False

        # teardown
        super_admin.api.user_api.delete_user(user_model.id)


    def test_get_user_by_locator(self, super_admin, created_user):
        '''
        created: dict
        payload: модель CreateUserRequest
        '''
        created, payload = created_user

        response_by_id = super_admin.api.user_api.get_user(created['id']).json()
        user_model_by_id = GetUserResponse(**response_by_id)

        response_by_email = super_admin.api.user_api.get_user(payload.email).json()
        user_model_by_email = GetUserResponse(**response_by_email)

        # Оба ответа должны описывать одного и того же пользователя
        assert user_model_by_id.id == user_model_by_email.id
        assert user_model_by_id.email == user_model_by_email.email
        assert user_model_by_id.fullName == user_model_by_email.fullName
        assert user_model_by_id.roles == user_model_by_email.roles
        assert user_model_by_id.verified == user_model_by_email.verified
        assert user_model_by_id.banned == user_model_by_email.banned

        # Сверки с исходным payload создания
        assert user_model_by_id.id  # не пустой
        assert user_model_by_id.email == payload.email
        assert user_model_by_id.fullName == payload.fullName
        assert Roles.USER in user_model_by_id.roles
        assert user_model_by_id.verified is True

    def test_get_user_by_email_common_user(self, common_user):
        # обычный пользователь не имеет права читать других пользователей
        response = common_user.api.user_api.get_user(common_user.email,
                                                  expected_status=403)
        error_model = ForbiddenResponse(**response.json())
        assert error_model.statusCode == 403
        assert error_model.error == "Forbidden"
        assert error_model.message == "Forbidden resource"  # если бек стабилен по тексту
