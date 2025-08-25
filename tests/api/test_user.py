class TestUser:

    def test_create_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data,
        expected_status=201).json()

        assert response.get('id') and response['id'] != '', "ID должен быть не пустым"
        assert response.get('email') == creation_user_data['email']
        assert response.get('fullName') == creation_user_data['fullName']
        assert "roles" in response
        assert "USER" in response["roles"]
        assert response.get('verified') is True

        super_admin.api.user_api.delete_user(response['id'])


    def test_get_user_by_locator(self, super_admin, created_user):
        created, payload = created_user

        response_by_id = super_admin.api.user_api.get_user(created['id']).json()
        response_by_email = super_admin.api.user_api.get_user(payload['email']).json()

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.get('id') and response_by_id['id'] != '', "ID должен быть не пустым"
        assert response_by_id.get('email') == payload['email']
        assert response_by_id.get('fullName') == payload['fullName']
        assert "USER" in response_by_id.get("roles", [])
        assert response_by_id.get('verified') is True

    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user(common_user.email, expected_status=403)
