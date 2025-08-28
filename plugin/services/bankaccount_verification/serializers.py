from rest_framework import serializers


class BankAccountVerificationRequestSerializer(serializers.Serializer):
    account_number = serializers.CharField(required=True, max_length=20)
    ifsc = serializers.CharField(required=True, max_length=11)
    name = serializers.CharField(required=True, max_length=255)


class BankAccountVerificationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    provider = serializers.CharField(default="deepvue")

    code = serializers.IntegerField(required=False, allow_null=True)
    timestamp = serializers.IntegerField(required=False, allow_null=True)
    transaction_id = serializers.CharField(required=False, allow_blank=True)

    account_exists = serializers.BooleanField(required=False, allow_null=True)
    name_at_bank = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utr = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    amount_deposited = serializers.IntegerField(required=False, allow_null=True)

    # Nested
    name_information = serializers.DictField(required=False, allow_null=True)
