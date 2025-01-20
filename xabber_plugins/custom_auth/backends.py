from xabber_plugins.custom_auth.models import Developer


class CustomAuthBackend:

    def authenticate(self, request, email, password, **kwargs):

        try:
            user = Developer.objects.get(
                email__email=email,
            )
        except:
            return None

        # check permissions
        if user.is_active:
            if user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        try:
            user = Developer.objects.get(id=user_id)
        except Developer.DoesNotExist:
            return None
        return user