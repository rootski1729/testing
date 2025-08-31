# plugin/services/sms_notification/serializers.py

from rest_framework import serializers


class SMSNotificationRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField(
        max_length=10,
        min_length=10,
        required=True,
        help_text="10-digit mobile number (without +91 prefix)",
    )
    text = serializers.CharField(
        max_length=2000,
        required=True,
        help_text="Message content (max 2000 characters)",
    )
    sender_name = serializers.CharField(
        max_length=6,
        min_length=6,
        required=True,
        help_text="6-character sender ID approved on DLT",
    )
    message_type = serializers.ChoiceField(
        choices=[(0, "English"), (1, "Flash"), (2, "Unicode")],
        default=0,
        help_text="Message type: 0-English, 1-Flash, 2-Unicode",
    )
    shorten_url = serializers.BooleanField(
        default=False, help_text="Whether to shorten URLs in message"
    )

    def validate_mobile(self, value):
        """Validate mobile number format"""
        if not value.isdigit():
            raise serializers.ValidationError("Mobile number must contain only digits")
        return value

    def validate_sender_name(self, value):
        """Validate sender name format"""
        if not value.isalnum():
            raise serializers.ValidationError(
                "Sender name must be 6 alphanumeric characters"
            )
        return value.upper()


class SMSNotificationResponseSerializer(serializers.Serializer):
    # Meta fields
    success = serializers.BooleanField(default=False)
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    provider = serializers.CharField(default="cell24x7")

    # API response fields
    response_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    error_code = serializers.IntegerField(required=False, allow_null=True)
    error_description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    # Request tracking fields
    mobile_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    message_content = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    sender_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Status tracking
    delivery_status = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    sent_at = serializers.DateTimeField(required=False, allow_null=True)

    # Raw API response for debugging
    raw_response = serializers.DictField(required=False, allow_null=True)
