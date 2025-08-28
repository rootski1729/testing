# serializers.py

from rest_framework import serializers
from .models import Plugin
from .enums import PluginProvider, PluginService
from .utils.plugin_factory import PluginFactory


class PluginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plugin
        fields = [
            "uid",
            "provider",
            "service",
            "username",
            "password",
            "api_key",
            "client_id",
            "client_secret",
        ]
        read_only_fields = ["uid"]

    def validate(self, data):
        provider = data.get("provider")
        service = data.get("service")

        # 1. Validate provider-service combination exists
        try:
            PluginFactory.get_provider_class(provider, service)
        except ValueError:
            raise serializers.ValidationError(
                {"service": f"{provider} does not support {service}."}
            )

        # 2. Validate correct credentials based on provider
        if provider == PluginProvider.DEEPVUE:
            if not data.get("client_id") or not data.get("client_secret"):
                raise serializers.ValidationError(
                    "Deepvue requires client_id and client_secret."
                )
        elif provider == PluginProvider.NSDL:
            if not (data.get("username") and data.get("password")):
                raise serializers.ValidationError(
                    "NSDL requires username and password."
                )
        elif provider == PluginProvider.UNISEN:
            if not data.get("api_key"):
                raise serializers.ValidationError("Unisen requires api_key.")

        return data


class PANVerificationRequestSerializer(serializers.Serializer):
    pan_number = serializers.CharField(
        min_length=10, max_length=10, help_text="10-character PAN number"
    )


class PANVerificationResponseSerializer(serializers.Serializer):
    pan_number = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    full_name_split = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    category = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    dob = serializers.CharField(required=False)
    address = serializers.DictField(required=False)
    email = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    masked_aadhaar = serializers.CharField(required=False)
    aadhaar_linked = serializers.BooleanField(required=False)
    transaction_id = serializers.CharField(required=False)
    sub_code = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    father_name = serializers.CharField(required=False)
    status = serializers.CharField(required=False)

