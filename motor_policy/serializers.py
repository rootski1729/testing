from motor_quote.serializers import (
    MotorQuoteRequestDetailsSerializer,
)
from rest_framework import serializers
from .models import MotorPolicy
from drf_yasg.utils import swagger_serializer_method
from motor_quote.enums import Insurer, Product, ProductType, ProductSubType, ProductCategory, PolicyCategory, PolicyType, State
from authentication.models import CaliberUser
from authentication.serializers import NanoUserSerializer
from motor_quote.enums import PluginStatus

class NullableFieldsMixin:
    """
    Make all writable fields optional and nullable.
    Works with Serializer and ModelSerializer.
    """

    def get_fields(self):
        fields = super().get_fields()

        def relax(field):
            if getattr(field, "read_only", False):
                return field

            field.required = False
            if hasattr(field, "allow_null"):
                field.allow_null = True
            if hasattr(field, "allow_blank"):
                field.allow_blank = True
            if hasattr(field, "allow_empty"):
                field.allow_empty = True

            child = getattr(field, "child", None)
            if child is not None:
                relax(child)
            child_rel = getattr(field, "child_relation", None)
            if child_rel is not None:
                relax(child_rel)

            return field

        for name, f in fields.items():
            fields[name] = relax(f)
        return fields


def as_nullable(serializer_cls, *, ref_name=None):
    """
    Create a subclass that DRF sees as a different component in Swagger.
    For drf-yasg, Meta.ref_name avoids name clashes.
    """
    name = f"Nullable{serializer_cls.__name__}"
    attrs = {}

    if ref_name is None:
        ref_name = name
    attrs["Meta"] = type("Meta", (), {"ref_name": ref_name})
    return type(name, (NullableFieldsMixin, serializer_cls), attrs)

def as_ref(serializer_cls, *, ref_name=None):
    name = ref_name or f"Ref{serializer_cls.__name__}"
    # No mixin here
    return type(name, (serializer_cls,), {
        "Meta": type("Meta", (), {"ref_name": name})
    })

RefMotorQuote = as_ref(MotorQuoteRequestDetailsSerializer, ref_name="MotorQuoteBaseRef")

class MotorPolicySerializer(
    NullableFieldsMixin, RefMotorQuote
):
    insurer = serializers.ChoiceField(required=True, choices=Insurer.choices())

    vehicle_idv = serializers.FloatField(required=False, allow_null=True)
    
    policy_number = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    issue_date = serializers.DateField(required=False, allow_null=True)

    od_start_date = serializers.DateField(required=False, allow_null=True)

    od_end_date = serializers.DateField(required=False, allow_null=True)

    tp_start_date = serializers.DateField(required=False, allow_null=True)

    tp_end_date = serializers.DateField(required=False, allow_null=True)

    sum_insured = serializers.FloatField(required=False, allow_null=True)

    basic_od_premium = serializers.FloatField(
        required=False, allow_null=True
    )

    total_od_premium = serializers.FloatField(
        required=False, allow_null=True
    )

    total_od_add_on_premium = serializers.FloatField(
        required=False, allow_null=True
    )

    basic_tp_premium = serializers.FloatField(
        required=False, allow_null=True
    )

    total_tp_premium = serializers.FloatField(
        required=False, allow_null=True
    )
    total_tp_add_on_premium = serializers.FloatField(
        required=False, allow_null=True
    )

    net_premium = serializers.FloatField(required=False, allow_null=True)

    taxes = serializers.FloatField(required=False, allow_null=True)
    taxes_rate = serializers.FloatField(required=False, allow_null=True)

    gross_discount = serializers.FloatField(
        required=False, allow_null=True
    )

    total_premium = serializers.FloatField(required=False, allow_null=True)

    ncb = serializers.FloatField(required=False, allow_null=True)

    broker_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    broker_email = serializers.EmailField(
        required=False, allow_null=True, allow_blank=True
    )
    broker_code = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

class MetaSerializer(serializers.Serializer):
    file_url = serializers.URLField()
    file_name = serializers.CharField(allow_blank=True, allow_null=True)
    created_by = NanoUserSerializer()
    status = serializers.ChoiceField(
        choices=PluginStatus.choices(),
    )


class MotorPolicyResponseSerializer(serializers.Serializer):
    uid = serializers.CharField()
    meta = MetaSerializer()
    details = MotorPolicySerializer(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()    

class MotorPolicyExtractionRequest(serializers.Serializer):
    pdf_url = serializers.URLField(required=True)


class PolicyPresignedURLRequestSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=100)
    content_type = serializers.ChoiceField(
        choices=[
            "image/jpeg",
            "image/png",
            "application/pdf",
            "application/zip"
        ],
    )

    def get_extension(self):
        content_type = self.validated_data.get("content_type")
        if content_type:
            return content_type.split("/")[-1]
        return None
    
class PolicyPresignedURLResponseSerializer(serializers.Serializer):
    upload_url = serializers.URLField()
    file_url = serializers.URLField()

class PolicyUploadSerializer(serializers.Serializer):
    url = serializers.URLField()
    file_name = serializers.CharField(required=False, allow_blank=True)


class PolicyListResponseSerializer(serializers.Serializer):
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = serializers.SerializerMethodField(method_name="get_results")

    @swagger_serializer_method(serializer_or_field=MotorPolicyResponseSerializer(many=True))
    def get_results(self, obj):
        results = self.context.get("details", [])
        return MotorPolicyResponseSerializer(results, many=True, context=self.context).data


class PolicyExportSerializer(serializers.Serializer):
    """Serializer for policy export filters"""
    insurer = serializers.ChoiceField(choices=Insurer.choices(), required=False, allow_null=True)
    product = serializers.ChoiceField(choices=Product.choices(), required=False, allow_null=True)
    product_type = serializers.ChoiceField(choices=ProductType.choices(), required=False, allow_null=True)
    product_sub_type = serializers.ChoiceField(choices=ProductSubType.choices(), required=False, allow_null=True)
    product_category = serializers.ChoiceField(choices=ProductCategory.choices(), required=False, allow_null=True)
    policy_category = serializers.ChoiceField(choices=PolicyCategory.choices(), required=False, allow_null=True)
    policy_type = serializers.ChoiceField(choices=PolicyType.choices(), required=False, allow_null=True)
    issue_date = serializers.DateField(required=False, allow_null=True)
    issue_date_from = serializers.DateField(required=False, allow_null=True)
    issue_date_to = serializers.DateField(required=False, allow_null=True)
    created_at_from = serializers.DateTimeField(required=False, allow_null=True)
    created_at_to = serializers.DateTimeField(required=False, allow_null=True)
    posp = serializers.SlugRelatedField(
        queryset=CaliberUser.objects.all(),
        slug_field="uid",
        required=False,
        allow_null=True
    )
    rm = serializers.SlugRelatedField(
        queryset=CaliberUser.objects.all(),
        slug_field="uid",
        required=False,
        allow_null=True
    )
    posp_city = serializers.CharField(max_length=100, required=False, allow_null=True)
    posp_state = serializers.ChoiceField(choices=State.choices(), required=False, allow_null=True)

class PolicyExportResponseSerializer(serializers.Serializer):
    """Serializer for policy export response"""
    count = serializers.IntegerField()
    results = serializers.SerializerMethodField(method_name="get_results")

    @swagger_serializer_method(serializer_or_field=MotorPolicyResponseSerializer(many=True))
    def get_results(self, obj):
        results = self.context.get("results", [])
        return MotorPolicyResponseSerializer(results, many=True, context=self.context).data


class AggregatedPolicyFiltersResponseSerializer(serializers.Serializer):
    insurer = serializers.ListField(child=serializers.CharField(), required=True)
    product = serializers.ListField(child=serializers.CharField(), required=True)
    product_type = serializers.ListField(child=serializers.CharField(), required=True)
    product_sub_type = serializers.ListField(child=serializers.CharField(), required=True)
    product_category = serializers.ListField(child=serializers.CharField(), required=True)
    policy_category = serializers.ListField(child=serializers.CharField(), required=True)
    policy_type = serializers.ListField(child=serializers.CharField(), required=True)
    issue_date_range = serializers.DictField(child=serializers.DateField(), required=True)
    created_at_range = serializers.DictField(child=serializers.DateTimeField(), required=False)




class PolicyBulkUploadSerializer(serializers.Serializer):
    files = PolicyUploadSerializer(many=True)

class BulkPolicyPresignedURLRequestSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        help_text="List of files with file_name and content_type",
    )

    def validate_files(self, value):
        allowed_types = ["image/jpeg", "image/png", "application/pdf"]
        for f in value:
            if "file_name" not in f or "content_type" not in f:
                raise serializers.ValidationError("Each file must have file_name and content_type")
            if f["content_type"] not in allowed_types:
                raise serializers.ValidationError(f"Invalid content_type {f['content_type']}")
        return value

class BulkPolicyPresignedURLResponseSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.DictField(child=serializers.URLField())
    )

class PolicyBulkUploadResponseSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )
    
    
#Zip file upload

class ZipUploadSerializer(serializers.Serializer):
    url = serializers.URLField()  # S3 file URL
    file_name = serializers.CharField(required=False, allow_blank=True)
    
    def validate_url(self, value):
        if not value.startswith('https://'):
            raise serializers.ValidationError("Must be a valid HTTPS URL")
        if '.zip' not in value:
            raise serializers.ValidationError("URL must point to a ZIP file")
        return value

class ZipUploadResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    status = serializers.CharField()  # PROCESSING, COMPLETED, FAILED
    job_id = serializers.CharField()
    estimated_completion = serializers.CharField()
    check_status_url = serializers.URLField()

class ZipStatusResponseSerializer(serializers.Serializer):
    job_id = serializers.CharField()
    status = serializers.CharField()
    progress = serializers.CharField()
    files_processed = serializers.IntegerField(required=False)
    processed_files = serializers.ListField(required=False)

class ZipUploadErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    error_code = serializers.CharField(required=False)

class FileAccessRequestSerializer(serializers.Serializer):
    file_url = serializers.URLField()
    
    def validate_file_url(self, value):
        if not value.startswith('https://'):
            raise serializers.ValidationError("Must be a valid HTTPS URL")
        return value

class FileAccessResponseSerializer(serializers.Serializer):
    presigned_url = serializers.URLField()
    expiration = serializers.IntegerField()  # seconds until expiration