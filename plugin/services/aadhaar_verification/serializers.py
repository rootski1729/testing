from rest_framework import serializers


class AadhaarOTPGenerateRequestSerializer(serializers.Serializer):
    aadhaar_number = serializers.CharField(
        min_length=12, max_length=12, required=True, help_text="12-digit Aadhaar number"
    )
    purpose = serializers.CharField(
        default="ForKYC", help_text="Purpose of verification"
    )


class AadhaarOTPGenerateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(required=False)
    message = serializers.CharField(required=False)
    code = serializers.CharField(required=False)

    reference_id = serializers.CharField(required=False, allow_null=True)
    transaction_id = serializers.CharField(required=False, allow_null=True)
    sub_code = serializers.CharField(required=False, allow_null=True)


class AadhaarOTPVerifyRequestSerializer(serializers.Serializer):
    otp = serializers.CharField(
        min_length=6,
        max_length=6,
        required=True,
        help_text="6-digit OTP received on mobile",
    )
    reference_id = serializers.CharField(
        required=True, help_text="Reference ID from generate OTP step"
    )
    mobile_number = serializers.CharField(
        min_length=10, max_length=10, required=True, help_text="10-digit mobile number"
    )
    generate_pdf = serializers.BooleanField(
        default=False, help_text="Generate PDF document"
    )


class AadhaarVerificationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(required=False)
    message = serializers.CharField(required=False)
    code = serializers.CharField(required=False)

    aadhaar_number = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    masked_number = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date_of_birth = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    gender = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    email = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    address = serializers.JSONField(required=False, allow_null=True)

    photo = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )  # Base64 encoded
    document_pdf = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )  # Base64 encoded PDF
    aadhaar_linked_mobile_match = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )  # Yes/No

    transaction_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    sub_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
