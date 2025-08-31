from rest_framework import serializers


class EmailNotificationRequestSerializer(serializers.Serializer):
    from_email = serializers.CharField(help_text="Sender email")
    to = serializers.ListField(
        child=serializers.EmailField(),
        help_text="List of recipient emails"
    )
    subject = serializers.CharField(help_text="Email subject")
    html = serializers.CharField(help_text="HTML content")


class EmailNotificationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
