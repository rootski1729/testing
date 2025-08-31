# serializers.py

from rest_framework import serializers

from .enums import PluginProvider, PluginService
from .models import Plugin
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

        # 2. Validate correct credentials based on provider using enum properties
        if provider:
            provider_enum = PluginProvider(provider)
            required_fields = provider_enum.required_auth_fields

            # Check if all required fields are present and non-empty
            missing_fields = []
            for field in required_fields:
                if not data.get(field):
                    missing_fields.append(field)

            if missing_fields:
                raise serializers.ValidationError(
                    f"{provider_enum.auth_description}. Missing: {', '.join(missing_fields)}"
                )

        return data


class PluginUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plugin
        fields = [
            "uid",
            "provider",
            "username",
            "password",
            "api_key",
            "client_id",
            "client_secret",
        ]
        read_only_fields = ["uid"]

    def validate(self, data):
        # Determine target provider and service (service not updatable here)
        target_provider = data.get("provider") or (
            self.instance.provider if self.instance else None
        )
        target_service = self.instance.service if self.instance else None

        # Validate provider-service combination exists
        if target_provider and target_service:
            try:
                PluginFactory.get_provider_class(target_provider, target_service)
            except ValueError:
                raise serializers.ValidationError(
                    {"service": f"{target_provider} does not support {target_service}."}
                )

        # Validate correct credentials based on target provider using enum properties
        if target_provider:
            provider_enum = PluginProvider(target_provider)
            required_fields = provider_enum.required_auth_fields

            # For partial updates, consider existing instance values when fields not provided
            missing_fields = []
            for field in required_fields:
                incoming = data.get(field)
                existing = (
                    getattr(self.instance, field, None) if self.instance else None
                )
                if not incoming and not existing:
                    missing_fields.append(field)

            if missing_fields:
                raise serializers.ValidationError(
                    f"{provider_enum.auth_description}. Missing: {', '.join(missing_fields)}"
                )

        return data


class PluginServiceSerializer(serializers.Serializer):
    service = serializers.ChoiceField(
        choices=[(s.value, s.value) for s in PluginService],
    )
    display_name = serializers.CharField(help_text="User-friendly display name")
    lucid_icon = serializers.CharField(help_text="Lucid React icon name")
    configured = serializers.BooleanField(
        help_text="Whether company has configured this service"
    )
    provider = serializers.ChoiceField(
        choices=[(p.value, p.value) for p in PluginProvider],
        allow_null=True,
        required=False,
        help_text="Provider enum value if configured",
    )
    plugin_uid = serializers.CharField(
        allow_null=True, required=False, help_text="Plugin UID if configured"
    )


class ProviderConfigSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(
        choices=[(p.value, p.value) for p in PluginProvider],
        help_text="Provider enum value",
    )
    display_name = serializers.CharField(help_text="User-friendly provider name")
    auth_fields = serializers.ListField(
        child=serializers.CharField(), help_text="Required authentication fields"
    )
    auth_description = serializers.CharField(
        help_text="Authentication requirements description"
    )


class PluginMaskedSerializer(serializers.ModelSerializer):
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
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Mask sensitive fields: show only last 4 chars with fixed prefix
        def mask_tail(value: str, visible: int = 4) -> str:
            if not value:
                return value
            s = str(value)
            tail = s[-visible:] if len(s) >= 1 else ""
            return "****" + tail

        if data.get("username"):
            data["username"] = mask_tail(data.get("username"))
        if data.get("password"):
            data["password"] = mask_tail(data.get("password"))
        if data.get("api_key"):
            data["api_key"] = mask_tail(data.get("api_key"))
        if data.get("client_secret"):
            data["client_secret"] = mask_tail(data.get("client_secret"))
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
