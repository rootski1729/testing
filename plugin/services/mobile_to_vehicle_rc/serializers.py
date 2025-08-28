from rest_framework import serializers


class MobileToVehicleRCRequestSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(
        required=True, max_length=15, help_text="Mobile number to fetch Vehicle RC"
    )


class MobileToVehicleRCResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    provider = serializers.CharField()
    code = serializers.IntegerField(required=False)
    timestamp = serializers.IntegerField(required=False)
    transaction_id = serializers.CharField(required=False, allow_null=True)
    sub_code = serializers.CharField(required=False, allow_null=True)
    data = serializers.DictField(required=False, allow_null=True)
