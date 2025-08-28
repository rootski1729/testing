from rest_framework import serializers


class DrivingLicenseVerificationRequestSerializer(serializers.Serializer):
    dl_number = serializers.CharField(max_length=50)
    dob = serializers.DateField()  # format YYYY-MM-DD


class DrivingLicenseVerificationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    provider = serializers.CharField(default="deepvue")
    request_id = serializers.CharField(required=False, allow_null=True)

    # DL Details
    id_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    name = serializers.CharField(required=False, allow_null=True,allow_blank = True)
    dob = serializers.CharField(required=False, allow_null=True)
    relatives_name = serializers.CharField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_null=True)
    issuing_rto_name = serializers.CharField(required=False, allow_null=True)
    date_of_issue = serializers.CharField(required=False, allow_null=True)
    dl_status = serializers.CharField(required=False, allow_null=True)
    nt_validity_from = serializers.CharField(required=False, allow_null=True)
    nt_validity_to = serializers.CharField(required=False, allow_null=True)
    t_validity_from = serializers.CharField(required=False, allow_null=True)
    t_validity_to = serializers.CharField(required=False, allow_null=True)

    cov_details = serializers.ListField(
        child=serializers.DictField(), required=False, allow_null=True
    )
