from rest_framework import serializers


class PANVerificationRequestSerializer(serializers.Serializer):
    pan_number = serializers.CharField(
        max_length=10, min_length=10, help_text="10-character PAN number"
    )


class PANVerificationResponseSerializer(serializers.Serializer):
    # Meta fields
    success = serializers.BooleanField(default=False)
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    provider = serializers.CharField(default="deepvue")
    request_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    # API response fields
    pan_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    full_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    full_name_split = serializers.ListField(
        child=serializers.CharField(allow_blank=True), required=False, allow_null=True
    )
    category = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    gender = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dob = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    masked_aadhaar = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    aadhaar_linked = serializers.BooleanField(required=False, allow_null=True)

    transaction_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    sub_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
