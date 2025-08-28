from rest_framework import serializers



class IFSCVerificationRequestSerializer(serializers.Serializer):
    ifsc = serializers.CharField(required=True, max_length=11)

    

class IFSCVerificationResponseSerializer(serializers.Serializer):
    message = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    code = serializers.IntegerField(required=False, allow_null=True)
    sub_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    transaction_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    MICR = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    BRANCH = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    ADDRESS = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    STATE = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    CONTACT = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    UPI = serializers.BooleanField(required=False, allow_null=True)
    RTGS = serializers.BooleanField(required=False, allow_null=True)
    CITY = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    CENTRE = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    DISTRICT = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    NEFT = serializers.BooleanField(required=False, allow_null=True)
    IMPS = serializers.BooleanField(required=False, allow_null=True)
    SWIFT = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    ISO3166 = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    BANK = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    BANKCODE = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    IFSC = serializers.CharField(required=False, allow_null=True, allow_blank=True)

