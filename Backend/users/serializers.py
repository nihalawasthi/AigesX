from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "profile_picture",
            "display_mode",
            "preferred_language",
            "notify_job_complete",
            "notify_critical_only",
            "two_factor_enabled",
            "session_alerts",
            "default_timeout_seconds",
            "default_memory_limit_mb",
            "default_cpu_limit",
        ]

    def validate_default_timeout_seconds(self, value):
        return max(1, value)

    def validate_default_memory_limit_mb(self, value):
        return max(64, value)

    def validate_default_cpu_limit(self, value):
        return max(0.1, value)


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, trim_whitespace=False)
    confirm_password = serializers.CharField(required=True, trim_whitespace=False)

    def validate(self, attrs):
        user = self.context["request"].user

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "New password and confirm password do not match."})

        validate_password(attrs["new_password"], user=user)
        return attrs

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        token["preferred_language"] = user.preferred_language
        return token
