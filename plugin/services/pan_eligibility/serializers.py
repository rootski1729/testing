from rest_framework import serializers


class PANEligibilityRequestSerializer(serializers.Serializer):
    plugin_uid = serializers.CharField()
    pan = serializers.CharField(max_length=10)
    mobile = serializers.CharField(max_length=10, required=False, allow_null=True)
    use_cache = serializers.BooleanField(default=True)
    cache_validity_minutes = serializers.IntegerField(default=10)


class PANEligibilityResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()

    verification_status = serializers.CharField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_null=True)
    verified_at = serializers.CharField(required=False, allow_null=True)

    agent_enum = serializers.CharField(required=False, allow_null=True)
    error_code = serializers.CharField(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_null=True)
    is_cached_response = serializers.BooleanField(required=False, allow_null=True)
