from rest_framework import serializers


class VehicleRCVerificationRequestSerializer(serializers.Serializer):
    rc_number = serializers.CharField(
        help_text="RC number for advanced verification"
    )


class VehicleRCVerificationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(required=False)
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    transaction_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    sub_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    registration_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vehicle_registration_date = serializers.DateTimeField(required=False, allow_null=True)
    user = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    father_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    present_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    permanent_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mobile_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vehicle_category = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vehicle_chassis_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vehicle_engine_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    maker_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    model = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    body_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vehicle_fuel_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vehicle_color = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    norms_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fit_up_to = serializers.DateTimeField(required=False, allow_null=True)
    financer = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    insurance_company = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_policy_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    insurance_upto = serializers.DateTimeField(required=False, allow_null=True)
    manufactured_month_year = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    registered_at = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    latest_by = serializers.CharField(required=False, allow_blank=True, allow_null=True)


    less_info = serializers.BooleanField(required=False, allow_null=True)

    noc_details = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    owner_sr = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    permit_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    permit_issue_date = serializers.DateTimeField(required=False, allow_null=True)
    permit_valid_from = serializers.DateTimeField(required=False, allow_null=True)
    permit_valid_upto = serializers.DateTimeField(required=False, allow_null=True)
    permit_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    national_permit_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    national_permit_issued_by = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    national_permit_valid_from = serializers.DateTimeField(required=False, allow_null=True)
    national_permit_valid_upto = serializers.DateTimeField(required=False, allow_null=True)

    blacklist_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    rc_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    puc_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    puc_valid_upto = serializers.DateTimeField(required=False, allow_null=True)
    masked_aadhaar_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    masked_mobile_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)