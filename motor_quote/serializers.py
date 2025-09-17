from rest_framework import serializers
from motor_quote.enums import (
    MotorQuoteCoverType,
    MotorQuoteTaxType,
    Product,
    ProductType,
    ProductSubType,
    ProductCategory,
    PolicyCategory,
    PolicyType,
    TaskStatus,
    Transmission,
    BusinessType,
    FuelType,
    InsuredType,
    InsuredTitle,
    State,
    HypothecatedType,
    EngineGearboxProtect,
    InsuredOccupation,
    Relation,
    Insurer,
    TaskMonitorErrorCode,
    TaskReturnCode,
    TaskSystemErrorCode,
)
from motor_quote.models import MotorQuoteRequest
from drf_yasg.utils import swagger_serializer_method


class MotorQuoteRequestBasicDetailsSerializer(serializers.Serializer):
    product = serializers.ChoiceField(
        choices=Product.choices(),
        help_text="Product for which the policy is requested",
    )
    product_type = serializers.ChoiceField(
        choices=ProductType.choices(),
        help_text="Type of the product for which the policy is requested",
    )
    product_sub_type = serializers.ChoiceField(
        choices=ProductSubType.choices(),
        help_text="Sub-type of the product for which the policy is requested",
    )
    product_category = serializers.ChoiceField(
        choices=ProductCategory.choices(),
        help_text="Category of the product for which the policy is requested",
    )
    policy_category = serializers.ChoiceField(
        choices=PolicyCategory.choices(),
        help_text="Category of the policy for which the request is made",
    )
    policy_type = serializers.ChoiceField(
        choices=PolicyType.choices(),
        help_text="Type of the policy for which the request is made",
    )
    make = serializers.CharField(help_text="Make of the vehicle")
    model = serializers.CharField(help_text="Model of the vehicle")
    variant = serializers.CharField(help_text="Variant of the vehicle", allow_blank=True)
    transmission = serializers.ChoiceField(
        choices=Transmission.choices(), help_text="Transmission type of the vehicle"
    )
    policy_start_date = serializers.DateField(
        help_text="Start date of the policy in YYYY-MM-DD format"
    )
    policy_expiry_date = serializers.DateField(
        help_text="Expiry date of the policy in YYYY-MM-DD format"
    )
    business_type = serializers.ChoiceField(
        choices=BusinessType.choices(),
        help_text="Type of business for which the policy is requested",
    )
    registration_number_1 = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="First part of the vehicle's registration number",
    )
    registration_number_2 = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Second part of the vehicle's registration number",
    )
    registration_number_3 = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Third part of the vehicle's registration number",
    )
    registration_number_4 = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Fourth part of the vehicle's registration number",
    )
    make_month = serializers.IntegerField(
        min_value=1, max_value=12, help_text="Month of the vehicle's make (1-12)"
    )
    make_year = serializers.IntegerField(
        min_value=1900,
        max_value=2100,
        help_text="Year of the vehicle's make (e.g., 2023)",
    )
    vehicle_fuel_type = serializers.ChoiceField(
        choices=FuelType.choices(), help_text="Fuel type of the vehicle"
    )
    vehicle_engine_number = serializers.CharField(
        help_text="Engine number of the vehicle"
    )
    vehicle_chassis_number = serializers.CharField(
        help_text="Chassis number of the vehicle"
    )

class MotorQuoteRequestDetailsSerializer(MotorQuoteRequestBasicDetailsSerializer):
    vehicle_transfer_of_ownership = serializers.BooleanField(
        help_text="Indicates if the vehicle's ownership transferred"
    )
    vehicle_registration_state = serializers.ChoiceField(
        choices=State.choices(), help_text="State where the vehicle is registered"
    )
    body_type = serializers.CharField(help_text="Body type of the vehicle")
    vehicle_registration_date = serializers.DateField(
        help_text="Date of vehicle registration in YYYY-MM-DD format"
    )
    vehicle_seating_capacity = serializers.IntegerField(
        min_value=1, help_text="Seating capacity of the vehicle"
    )
    vehicle_cc = serializers.IntegerField(
        help_text="Cubic capacity of the vehicle's engine"
    )
    vehicle_puc_available = serializers.BooleanField(
        help_text="Indicates if the vehicle has a valid PUC certificate"
    )
    transfer_vehicle_ncb = serializers.BooleanField(
        default=False,
        help_text="Indicates if the vehicle's NCB (No Claim Bonus) is transferred"
    )
    insured_type = serializers.ChoiceField(
        choices=InsuredType.choices(),
        help_text="Type of the insured person (individual, company, etc.)",
    )
    insured_title = serializers.ChoiceField(
        required=False,
        allow_null=True,
        choices=InsuredTitle.choices(),
        help_text="Title of the insured person (Mr., Mrs., etc.)",
    )
    insured_name = serializers.CharField(
        required=False, allow_null=True, help_text="Full name of the insured person"
    )
    insured_address = serializers.CharField(
        required=False, allow_null=True, help_text="Address of the insured person"
    )
    insured_pincode = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Pincode of the insured person's address",
    )
    insured_state = serializers.ChoiceField(
        required=False,
        allow_null=True,
        choices=State.choices(),
        help_text="State of the insured person's address",
    )
    insured_district = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="District of the insured person's address",
    )
    gstin = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="GSTIN of the insured person (if applicable)",
    )
    ckyc_number = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="CKYC number of the insured person (if applicable)",
    )
    insured_mobile = serializers.CharField(
        required=False, allow_null=True, help_text="Mobile number of the insured person"
    )
    insured_email = serializers.EmailField(
        required=False, allow_null=True, help_text="Email address of the insured person"
    )
    insured_dob = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Date of birth of the insured person in YYYY-MM-DD format",
    )
    insured_occupation = serializers.ChoiceField(
        required=False,
        allow_null=True,
        choices=InsuredOccupation.choices(),
        help_text="Occupation of the insured person",
    )
    insured_aadhar_no = serializers.RegexField(
        required=False,
        allow_null=True,
        regex=r"^\d{12}$",
        help_text="Aadhar number of the insured person (if applicable)",
    )
    insured_pan_no = serializers.RegexField(
        required=False,
        allow_null=True,
        regex=r"^[A-Z]{3}[PCHAFGLJT][A-Z][1-9][0-9]{3}[A-Z]$",
        help_text="PAN number of the insured person (if applicable)",
    )
    vehicle_rta = serializers.CharField(
        help_text="RTA (Regional Transport Authority) of the vehicle"
    )
    vehicle_fuel_outbuild = serializers.BooleanField(
        required=False,
        allow_null=True,
        help_text="Indicates if the vehicle has an outbuilding for fuel"
    )
    vehicle_fuel_outbuild_cost = serializers.IntegerField(
        min_value=0, help_text="Cost of the vehicle's outbuilding for fuel", required=False, allow_null=True
    )
    vehicle_hypothecated = serializers.BooleanField(
        required=False,
        allow_null=True,
        help_text="Indicates if the vehicle is hypothecated"
    )
    hypothecated_type = serializers.ChoiceField(
        choices=HypothecatedType.choices(),
        required=False,
        allow_null=True,
        help_text="Type of hypothecation for the vehicle",
    )
    hypothecated_with = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Name of the entity with which the vehicle is hypothecated",
    )
    hypothecated_state = serializers.ChoiceField(
        choices=State.choices(),
        required=False,
        allow_null=True,
        help_text="State where the vehicle is hypothecated",
    )
    hypothecated_district = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="District where the vehicle is hypothecated",
    )
    limit_tppd = serializers.BooleanField(
        help_text="Indicates if there is a limit on Third Party Property Damage (TPPD)"
    )
    legal_libility_to_paid_driver = serializers.IntegerField(
        min_value=0, help_text="Legal liability amount to be paid to the driver"
    )
    pa_cover_unnammed_person_count = serializers.IntegerField(
        min_value=0,
        help_text="Count of unnamed persons covered under PA (Personal Accident)",
    )
    pa_cover_unnammed_person = serializers.IntegerField(
        help_text="Sum insured for Personal Accident (PA) cover for unnamed persons"
    )
    pa_cover_driver_count = serializers.IntegerField(
        min_value=0, help_text="Count of drivers covered under PA (Personal Accident)"
    )
    pa_cover_driver = serializers.IntegerField(
        help_text="Sum insured for Personal Accident (PA) cover for the driver"
    )
    nfpp_cover = serializers.BooleanField(
        help_text="Indicates if Non-Fare Paying Passengers (NFPP) cover is included"
    )
    cpa_optout = serializers.BooleanField(
        help_text="Indicates if the customer has opted out of the Compulsory Personal Accident (CPA) cover"
    )
    cpa_cover_period = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Period for which the Compulsory Personal Accident (CPA) cover is applicable",
    )
    cpa_has_valid_dl = serializers.BooleanField(
        required=False,
        allow_null=True,
        help_text="Indicates if the customer has a valid driving license for the CPA cover"
    )
    cpa_insurer = serializers.ChoiceField(
        choices=Insurer.choices(),
        required=False,
        allow_null=True,
        help_text="Insurer for the Compulsory Personal Accident (CPA) cover",
    )
    cpa_policy_number = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Policy number for the Compulsory Personal Accident (CPA) cover",
    )
    cpa_policy_from = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Start date of the Compulsory Personal Accident (CPA) cover in YYYY-MM-DD format",
    )
    cpa_policy_to = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="End date of the Compulsory Personal Accident (CPA) cover in YYYY-MM-DD format",
    )
    nominiee_name = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Name of the nominee for the Compulsory Personal Accident (CPA) cover",
    )
    nominiee_relation = serializers.ChoiceField(
        choices=Relation.choices(),
        required=False,
        allow_null=True,
        help_text="Relation of the nominee to the insured person",
    )
    nominiee_age = serializers.IntegerField(
        required=False, allow_null=True, min_value=0, help_text="Age of the nominee"
    )
    appointee_name = serializers.CharField(
        required=False, allow_null=True, help_text="Name of the appointee"
    )
    appointee_relation = serializers.ChoiceField(
        choices=Relation.choices(),
        required=False,
        allow_null=True,
        help_text="Relation of the appointee to the insured person",
    )
    addon_roadside_assistance = serializers.BooleanField(
        default=False,
        help_text="Indicates if roadside assistance is included as an addon",
    )
    addon_nil_depreciation_cover = serializers.BooleanField(
        default=False,
        help_text="Indicates if nil depreciation cover is included as an addon",
    )
    addon_key_cover = serializers.BooleanField(
        default=False, help_text="Indicates if key cover is included as an addon"
    )
    addon_key_cover_sum = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Sum insured for key cover addon",
    )
    addon_personal_belongings = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Sum insured for personal belongings addon",
    )
    addon_consumable_cover = serializers.BooleanField(
        default=False, help_text="Indicates if consumable cover is included as an addon"
    )
    addon_return_to_invoice = serializers.BooleanField(
        default=False,
        help_text="Indicates if return to invoice cover is included as an addon",
    )
    addon_inconvenience_allowance = serializers.BooleanField(
        default=False,
        help_text="Indicates if inconvenience allowance is included as an addon",
    )
    addon_tyre_cover = serializers.BooleanField(
        default=False, help_text="Indicates if tyre cover is included as an addon"
    )
    addon_tyre_cover_sum = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Sum insured for tyre cover addon",
    )
    addon_ncb_protection = serializers.BooleanField(
        default=False,
        help_text="Indicates if NCB (No Claim Bonus) protection is included",
    )
    addon_rim_damage_cover = serializers.BooleanField(
        default=False, help_text="Indicates if rim damage cover is included as an addon"
    )
    addon_rim_damage_cover_sum = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Sum insured for rim damage cover addon",
    )
    addon_engine_protect = serializers.BooleanField(
        default=False,
        help_text="Indicates if engine protection is included as an addon",
    )
    addon_engine_gearbox_protect = serializers.ChoiceField(
        choices=EngineGearboxProtect.choices(),
        required=False,
        allow_null=True,
        help_text="Indicates if engine and gearbox protection is included as an addon",
    )
    addon_road_tax_and_registration_charges = serializers.BooleanField(
        default=False,
        help_text="Indicates if road tax and registration charges are included as an addon",
    )
    addon_road_tax_and_registration_charges_sum = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Sum insured for road tax and registration charges addon",
    )
    addon_overnight_stay = serializers.BooleanField(
        default=False,
        help_text="Indicates if overnight stay cover is included as an addon",
    )
    addon_pay_as_you_go = serializers.BooleanField(
        default=False,
        help_text="Indicates if pay-as-you-go cover is included as an addon",
    )
    addon_imt23 = serializers.BooleanField(
        default=False, help_text="Indicates if IMT 23 cover is included as an addon"
    )
    addon_imt47 = serializers.BooleanField(
        default=False, help_text="Indicates if IMT 47 cover is included as an addon"
    )
    addon_courtesy_car = serializers.BooleanField(
        default=False,
        help_text="Indicates if courtesy car cover is included as an addon",
    )
    addon_courtesy_car_days = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Number of days for which courtesy car is provided as an addon",
    )
    addon_indemnity_cover = serializers.BooleanField(
        default=False, help_text="Indicates if indemnity cover is included as an addon"
    )
    last_policy_available = serializers.BooleanField(
        default=False, help_text="Indicates if the last policy details are available"
    )
    last_insurer = serializers.ChoiceField(
        choices=Insurer.choices(),
        required=False,
        allow_null=True,
        help_text="Insurer of the last policy",
    )
    last_policy_number = serializers.CharField(
        required=False, allow_null=True, help_text="Policy number of the last policy"
    )
    last_policy_from = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Start date of the last policy in YYYY-MM-DD format",
    )
    last_policy_to = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="End date of the last policy in YYYY-MM-DD format",
    )
    last_policy_ncb_percent = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=100,
        help_text="No Claim Bonus (NCB) percentage of the last policy",
    )
    last_policy_claim = serializers.BooleanField(
        required=False,
        allow_null=True,
        help_text="Indicates if there were any claims in the last policy",
    )
    last_policy_claim_count = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Count of claims in the last policy",
    )
    last_policy_type = serializers.ChoiceField(
        choices=PolicyType.choices(),
        required=False,
        allow_null=True,
        help_text="Type of the last policy",
    )
    last_policy_category = serializers.ChoiceField(
        choices=PolicyCategory.choices(),
        required=False,
        allow_null=True,
        help_text="Category of the last policy",
    )
    vehicle_gvw = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Gross Vehicle Weight (GVW) of the vehicle in kilograms",
    )
    customer_id = serializers.CharField(
        required=False, allow_null=True, help_text="Unique identifier for the customer"
    )
    misc_vehicle_class = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Miscellaneous vehicle class if applicable",
    )


class MotorQuoteRequestInsurerSerializer(serializers.Serializer):
    insurer = serializers.ChoiceField(choices=Insurer.choices())
    od_discount_percent = serializers.IntegerField(
        help_text="OD (Own Damage) discount percentage"
    )
    vehicle_idv = serializers.IntegerField(
        min_value=0, help_text="Insured Declared Value (IDV) of the vehicle"
    )


class MotorQuoteRequestCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, help_text="Name of the quote request")
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    insurers = MotorQuoteRequestInsurerSerializer(many=True)
    details = MotorQuoteRequestDetailsSerializer()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("insurers"):
            raise serializers.ValidationError("At least one insurer must be provided.")
        return attrs
    

class TaskBasicSerializer(serializers.Serializer):
    id = serializers.CharField()
    insurer = serializers.ChoiceField(choices=Insurer.choices())
    status = serializers.ChoiceField(choices=TaskStatus.choices())


class MotorQuoteRequestBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotorQuoteRequest
        fields = (
            "uid",
            "name",
            "description",
            "created_at",
            "updated_at",
        )

        
class MotorQuoteRequestSerializer(MotorQuoteRequestBasicSerializer):
    tasks = serializers.SerializerMethodField(method_name="get_tasks")
    details = serializers.SerializerMethodField(method_name="get_details")

    class Meta:
        model = MotorQuoteRequest
        fields = (
            "uid",
            "name",
            "description",
            "tasks",
            "details",
            "created_at",
            "updated_at",
        )

    @swagger_serializer_method(serializer_or_field=TaskBasicSerializer(many=True))
    def get_tasks(self, obj):
        docs = self.context["tasks"]
        try:
            data = docs[obj.mongo_id]
        except KeyError:
            return []
        else:
            serializer = TaskBasicSerializer(data=data, context=self.context, many=True)
            serializer.is_valid(raise_exception=True)
            return serializer.data

    @swagger_serializer_method(serializer_or_field=MotorQuoteRequestBasicDetailsSerializer())
    def get_details(self, obj):
        docs = self.context["details"]
        data = docs[obj.mongo_id]
        serializer = MotorQuoteRequestBasicDetailsSerializer(data=data["details"], context=self.context)
        serializer.is_valid(raise_exception=True)
        return serializer.data


class MotorQuoteRequestListResponseSerializer(serializers.Serializer):
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = serializers.SerializerMethodField(method_name="get_results")

    @swagger_serializer_method(serializer_or_field=MotorQuoteRequestSerializer(many=True))
    def get_results(self, obj):
        results = self.context.get("results", [])
        return MotorQuoteRequestSerializer(results, many=True, context=self.context).data


class CoverDetailSerializer(serializers.Serializer):
    """Serializer for individual cover details"""

    cover_name = serializers.CharField(
        required=True,
        help_text="Name of the cover"
    )
    cover_type = serializers.ChoiceField(
        choices=MotorQuoteCoverType.choices(),
        help_text="Type of the cover"
    )
    sum_insured = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Sum insured amount"
    )
    premium = serializers.FloatField(
        required=True,
        help_text="Premium amount for this cover"
    )
    is_addon = serializers.BooleanField(
        default=False,
        help_text="Whether this is an addon cover"
    )
    is_discount = serializers.BooleanField(
        default=False,
        help_text="Whether this is a discount (negative premium)"
    )


class TaxDetailSerializer(serializers.Serializer):
    """Serializer for tax details"""

    tax_type = serializers.ChoiceField(
        choices=MotorQuoteTaxType.choices(),
        required=True,
        help_text="Type of tax"
    )
    tax_description = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Description of the tax"
    )
    rate_percent = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Tax rate percentage"
    )
    amount = serializers.FloatField(
        required=True,
        help_text="Tax amount"
    )


class PremiumBreakdownSerializer(serializers.Serializer):
    """Serializer for premium breakdown"""

    od_premium = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Own Damage premium"
    )
    tp_premium = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Third Party premium"
    )
    basic_od_rate = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Basic OD rate percentage"
    )
    net_premium = serializers.FloatField(
        required=True,
        help_text="Net premium before taxes"
    )
    taxes = serializers.ListField(
        child=TaxDetailSerializer(),
        default=list,
        help_text="List of taxes applied on the premium"
    )
    total_tax_amount = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Total tax amount"
    )
    stamp_duty = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Stamp duty amount"
    )
    total_premium = serializers.FloatField(
        required=True,
        help_text="Total premium including taxes"
    )


class AdditionalProductSerializer(serializers.Serializer):
    """Serializer for additional products like IPA"""

    product_name = serializers.CharField(
        required=True,
        help_text="Name of the additional product"
    )
    sum_insured = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Sum insured for the additional product"
    )
    basic_premium = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Basic premium for the additional product"
    )
    medical_expenses = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Medical expenses covered by the additional product"
    )
    taxes = serializers.ListField(
        child=TaxDetailSerializer(),
        default=list,
        help_text="List of taxes applied on the additional product"
    )
    net_premium = serializers.FloatField(
        required=True,
        help_text="Net premium for the additional product"
    )
    total_premium = serializers.FloatField(
        required=True,
        help_text="Total premium for the additional product"
    )


class AdditionalProductPremiumSerializer(serializers.Serializer):
    key = serializers.CharField(
        required=True,
        help_text="Key for the additional product"
    )
    value = serializers.FloatField(
        required=True,
        help_text="Premium amount for the additional product"
    )


class BundleInfoSerializer(serializers.Serializer):
    """Serializer for bundle information when multiple products are bundled"""

    motor_premium = serializers.FloatField(
        required=True,
        help_text="Motor premium amount"
    )
    additional_products_premium = serializers.ListField(
        child=AdditionalProductPremiumSerializer(),
        default=list,
        help_text="List of additional products and their premiums"
    )
    bundle_premium = serializers.FloatField(
        required=True,
        help_text="Bundle premium amount"
    )
    bundle_discount = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Bundle discount amount"
    )


class QuoteMetadataSerializer(serializers.Serializer):
    """Quote-specific metadata serializer"""

    insurer = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Name of the insurer"
    )
    quote_id = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Unique identifier for the quote"
    )
    imt_clauses = serializers.ListField(
        child=serializers.CharField(),
        default=list,
        help_text="IMT clauses applied"
    )
    ncb_percent_applied = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="NCB percentage actually applied in quote"
    )
    idv = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="IDV used for this quote"
    )


class UWReferralSerializer(serializers.Serializer):
    """Underwriting referral information serializer"""

    is_referred = serializers.BooleanField(
        default=False,
        help_text="Whether the quote is referred to underwriting"
    )
    authority_code = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Authority code for the referral"
    )
    deviation_message = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Message explaining the deviation if referred"
    )
    error_messages = serializers.ListField(
        child=serializers.CharField(),
        default=list,
        help_text="List of error messages if any"
    )


class ExtraFieldSerializer(serializers.Serializer):
    key = serializers.CharField(
        required=True,
        help_text="Key for the extra field"
    )
    # Using JSONField to handle Union[str, float, int] types
    value = serializers.JSONField(
        default=None,
        help_text="Value can be string, float, or int"
    )
    info = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Additional information about the field"
    )

    def validate_value(self, value):
        """Custom validation to ensure value is str, float, or int"""
        if value is not None and not isinstance(value, (str, float, int)):
            raise serializers.ValidationError(
                "Value must be a string, float, or integer"
            )
        return value


class PolicyQuoteSerializer(serializers.Serializer):
    """Main serializer for policy quote from any insurer"""

    # Basic Information
    metadata = QuoteMetadataSerializer(
        required=True,
        help_text="Metadata related to the quote"
    )

    # Coverage Details
    covers = serializers.ListField(
        child=CoverDetailSerializer(),
        default=list,
        help_text="All covers including basic and addons"
    )

    # Premium Information
    premium_breakdown = PremiumBreakdownSerializer(
        required=True,
        help_text="Premium breakdown details"
    )

    # Additional Products (like IPA)
    additional_products = serializers.ListField(
        child=AdditionalProductSerializer(),
        default=list,
        help_text="List of additional products"
    )

    # Bundle Information (if applicable)
    bundle_info = BundleInfoSerializer(
        required=False,
        allow_null=True,
        help_text="Bundle information if multiple products are bundled"
    )

    # Underwriting Information
    uw_referral = UWReferralSerializer(
        required=False,
        allow_null=True,
        help_text="Underwriting referral information"
    )

    # Additional flexible storage for insurer-specific fields
    extra_fields = serializers.ListField(
        child=ExtraFieldSerializer(),
        default=list,
        help_text="List of extra fields for insurer-specific data"
    )

class TaskSystemTimestampsSerializer(serializers.Serializer):
    picked = serializers.DateTimeField(
        required=False, 
        allow_null=True,
        help_text="Timestamp when the task was picked up"
    )
    completed = serializers.DateTimeField(
        required=False, 
        allow_null=True,
        help_text="Timestamp when the task was completed"
    )
    poll_time = serializers.DateTimeField(
        required=False, 
        allow_null=True,
        help_text="Timestamp when the task polled"
    )


class TaskFailedAttemptSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField(
        required=True,
        help_text="Timestamp of the failed attempt"
    )
    return_code = serializers.ChoiceField(
        choices=TaskReturnCode.choices(),
        help_text="Return code from the system for the failed attempt"
    )
    system_error_code = serializers.ChoiceField(
        choices=TaskSystemErrorCode.choices(),
        help_text="System error code for the failed attempt"
    )
    error_code = serializers.CharField(
        help_text="Error code associated with the failed attempt"
    )
    error_message = serializers.CharField(
        required=True,
        help_text="Error message associated with the failed attempt"
    )
    details = serializers.DictField(
        required=False,
        default=dict,
        help_text="Additional details about the failed attempt"
    )


class TaskFailureSerializer(serializers.Serializer):
    is_failed = serializers.BooleanField(
        default=False,
        help_text="Indicates if the task has failed"
    )
    reason = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Reason for the failure, if applicable"
    )
    attempts = TaskFailedAttemptSerializer(many=True)
    monitor_error_code = serializers.ChoiceField(
        choices=TaskMonitorErrorCode.choices(),
        required=False,
        allow_null=True,
        help_text="Monitor error code associated with the failure"
    )
    monitor_updated_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Timestamp when the monitor was updated the task"
    )


class TaskStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=TaskStatus.choices(),  # Assuming Status has choices
        required=True,
        help_text="Current status of the quote task request"
    )
    timestamps = TaskSystemTimestampsSerializer(
        required=False,
        allow_null=True,
        help_text="Timestamps related to the status of the quote task request"
    )
    failure = TaskFailureSerializer(
        required=False,
        allow_null=True,
        help_text="Failure information related to the status of the quote task request"
    )
    quote = PolicyQuoteSerializer(  # Assuming PolicyQuoteSerializer exists
        required=False,
        allow_null=True,
        help_text="Quote information related to the quote task, if available"
    )
    payment_url = serializers.URLField(
        required=False,
        allow_null=True,
        help_text="Payment URL for the quote, if available"
    )


class MotorQuoteTaskSerializer(serializers.Serializer):
    id = serializers.CharField()
    insurer = serializers.ChoiceField(choices=Insurer.choices())
    status = serializers.ChoiceField(choices=TaskStatus.choices())
    quote_status = TaskStatusSerializer(required=False, allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

class MotorQuoteRequestRetrieveSerializer(serializers.Serializer):
    request = serializers.SerializerMethodField(method_name="get_request")
    insurers = MotorQuoteRequestInsurerSerializer(many=True)
    details = MotorQuoteRequestDetailsSerializer()
    tasks = MotorQuoteTaskSerializer(many=True)

    @swagger_serializer_method(serializer_or_field=MotorQuoteRequestBasicSerializer())
    def get_request(self, data):
        return MotorQuoteRequestBasicSerializer(self.context["instance"]).data


class MotorQuoteRequestRecordingRequestSerializer(serializers.Serializer):
    insurer = serializers.ChoiceField(choices=Insurer.choices())

class MotorQuoteRequestRecordingResponseSerializer(serializers.Serializer):
    is_available = serializers.BooleanField()
    recording_url = serializers.URLField(allow_null=True, required=False)

class MotorQuoteRequestInsurerValidationResponseSerializer(serializers.Serializer):
    insurer = serializers.ChoiceField(choices=Insurer.choices())
    is_valid = serializers.BooleanField()
    error = serializers.CharField(allow_null=True, required=False)


class MotorQuoteRequestValidationResponseSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField()
    insurers = MotorQuoteRequestInsurerValidationResponseSerializer(many=True)
    error = serializers.CharField(allow_null=True, required=False)
