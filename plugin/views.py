# views.py

from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from pydantic import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.views import PermissionScopedViewSet, module_permission
from permission.enums import Module, Operation
from plugin.enums import PluginProvider, PluginService
from plugin.services.aadhaar_verification.models import (
    AadhaarOTPGenerateRequest,
    AadhaarOTPGenerateResponse,
    AadhaarOTPVerifyRequest,
    AadhaarVerificationResponse,
)
from plugin.services.aadhaar_verification.serializers import (
    AadhaarOTPGenerateRequestSerializer,
    AadhaarOTPGenerateResponseSerializer,
    AadhaarOTPVerifyRequestSerializer,
    AadhaarVerificationResponseSerializer,
)
from plugin.services.bankaccount_verification.models import (
    BankAccountVerificationRequest,
    BankAccountVerificationResponse,
)
from plugin.services.bankaccount_verification.serializers import (
    BankAccountVerificationRequestSerializer,
    BankAccountVerificationResponseSerializer,
)
from plugin.services.driving_license.models import (
    DrivingLicenseVerificationRequest,
    DrivingLicenseVerificationResponse,
)
from plugin.services.driving_license.serializers import (
    DrivingLicenseVerificationRequestSerializer,
    DrivingLicenseVerificationResponseSerializer,
)
from plugin.services.ifsc_lookup.models import (
    IFSCVerificationRequest,
    IFSCVerificationResponse,
)
from plugin.services.ifsc_lookup.serializers import (
    IFSCVerificationRequestSerializer,
    IFSCVerificationResponseSerializer,
)
from plugin.services.mobile_to_vehicle_rc.models import (
    MobileToVehicleRCRequest,
    MobileToVehicleRCResponse,
)
from plugin.services.mobile_to_vehicle_rc.serializers import (
    MobileToVehicleRCRequestSerializer,
    MobileToVehicleRCResponseSerializer,
)
from plugin.services.pan_validation.models import (
    PANVerificationRequest,
    PANVerificationResponse,
)
from plugin.services.pan_validation.serializers import (
    PANVerificationRequestSerializer,
    PANVerificationResponseSerializer,
)
from plugin.services.sms_notification.models import SMSRequest, SMSResponse
from plugin.services.sms_notification.serializers import (
    SMSNotificationRequestSerializer,
    SMSNotificationResponseSerializer,
)
from plugin.services.vechile_rc_validation.models import (
    VehicleRCVerificationRequest,
    VehicleRCVerificationResponse,
)
from plugin.services.vechile_rc_validation.serializers import (
    VehicleRCVerificationRequestSerializer,
    VehicleRCVerificationResponseSerializer,
)

from plugin.services.pan_eligibility.models import (
    PANEligibilityRequest,
    PANEligibilityResponse,
)
from plugin.services.pan_eligibility.serializers import (
    PANEligibilityRequestSerializer,
    PANEligibilityResponseSerializer,
)

from plugin.utils.plugin_factory import PluginFactory

from .models import Plugin
from .serializers import (
    PluginMaskedSerializer,
    PluginSerializer,
    PluginServiceSerializer,
    PluginUpdateSerializer,
    ProviderConfigSerializer,
)
from plugin.services.email_notification.serializers import (
    EmailNotificationRequestSerializer,
    EmailNotificationResponseSerializer
)

from plugin.services.email_notification.models import EmailRequest, EmailResponse


# class PluginServiceListViewSet(PermissionScopedViewSet):
#     modules = [Module.PLUGIN]

#     @swagger_auto_schema(
#         operation_summary="List Plugin Services",
#         operation_description="Get all available plugin service types with configuration status",
#         responses={200: PluginServiceSerializer(many=True)},
#     )
#     @module_permission(op=Operation.READ)
#     def list(self, request, *args, **kwargs):
#         company = request.user.company if request.user.is_authenticated else None
#         services = []

#         # Single query to get all configured plugins for the company
#         configured_plugins = {}
#         if company:
#             plugins = Plugin.objects.filter(company=company).values('service', 'provider')
#             configured_plugins = {plugin['service']: plugin['provider'] for plugin in plugins}

#         for service in PluginService:
#             service_data = {
#                 "slug": service.value,
#                 "display_name": service.display_name,
#                 "lucid_icon": service.lucid_icon,
#                 "configured": service.value in configured_plugins,
#                 "provider": configured_plugins.get(service.value)
#             }
#             services.append(service_data)

#         serializer = PluginServiceSerializer(services, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class PluginViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()
    lookup_field = "uid"

    @swagger_auto_schema(
        operation_summary="List Plugin Services",
        operation_description="Get all available plugin service types with configuration status",
        responses={200: PluginServiceSerializer(many=True)},
    )
    @module_permission(op=Operation.READ)
    def list(self, request, *args, **kwargs):
        company = request.user.company if request.user.is_authenticated else None
        services = []

        # Single query to get all configured plugins for the company
        configured_plugins = {}
        if company:
            plugins = Plugin.objects.filter(company=company).values(
                "service", "provider", "uid"
            )
            configured_plugins = {
                plugin["service"]: {
                    "provider": plugin["provider"],
                    "uid": plugin["uid"],
                }
                for plugin in plugins
            }

        for service in PluginService:
            plugin_config = configured_plugins.get(service.value)
            provider_name = None
            plugin_uid = None

            if plugin_config:
                provider_name = plugin_config["provider"]
                plugin_uid = plugin_config["uid"]

            service_data = {
                "service": service.value,
                "display_name": service.display_name,
                "lucid_icon": service.lucid_icon,
                "configured": service.value in configured_plugins,
                "provider": provider_name,
                "plugin_uid": plugin_uid,
            }
            services.append(service_data)

        serializer = PluginServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Get Available Providers for Service",
        operation_description="Get list of available providers and their auth requirements for a specific service",
        responses={200: ProviderConfigSerializer(many=True), 404: "Service not found"},
    )
    @action(
        detail=False, methods=["get"], url_path="services/(?P<service>[^/.]+)/providers"
    )
    @module_permission(op=Operation.READ)
    def service_providers(self, request, service=None, *args, **kwargs):
        try:
            service_enum = PluginService(service)
        except ValueError:
            return Response(
                {"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get all available providers for this service from PluginFactory registry
        available_providers = []
        for (provider_enum, svc_enum), _ in PluginFactory._registry.items():
            if svc_enum == service_enum:
                provider_data = {
                    "provider": provider_enum.name,
                    "display_name": provider_enum.display_name,
                    "auth_fields": provider_enum.required_auth_fields,
                    "auth_description": provider_enum.auth_description,
                }
                available_providers.append(provider_data)

        serializer = ProviderConfigSerializer(available_providers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Get Plugin with Masked Credentials",
        operation_description="Retrieve plugin configuration with sensitive fields masked for form prefilling",
        responses={200: PluginMaskedSerializer, 404: "Plugin not found"},
    )
    @module_permission(op=Operation.READ)
    def retrieve(self, request, *args, **kwargs):
        print("Getting object")
        instance = self.get_object()
        print("Got object", instance)
        serializer = PluginMaskedSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a new Plugin",
        operation_description="Register a new plugin with provider + service credentials.",
        request_body=PluginSerializer,
        responses={201: PluginSerializer, 400: "Bad Request"},
    )
    def create(self, request, *args, **kwargs):
        serializer = PluginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            plugin = serializer.save(
                access_level=request.user.role.access_level,
                access_department=request.user.department,
                access_location=request.user.location,
                company=request.user.company,
                owners=[request.user]
            )
        except IntegrityError:
            return Response(
                {"error": "Plugin with this provider and service already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(PluginSerializer(plugin).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Partially Update Plugin Configuration",
        operation_description="Partially update plugin credentials and configuration. Provider can be changed; service cannot.",
        request_body=PluginUpdateSerializer,
        responses={200: PluginSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    @module_permission(op=Operation.UPDATE)
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PluginUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            plugin = serializer.save()
        except IntegrityError:
            return Response(
                {"error": "Plugin with this provider and service already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(PluginSerializer(plugin).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Delete Plugin Configuration",
        operation_description="Remove plugin configuration and credentials",
        responses={204: "No Content", 404: "Plugin not found"},
    )
    @module_permission(op=Operation.DELETE)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VehicleRCVerificationView(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    permission_classes = [AllowAny]  # TODO
    queryset = Plugin.objects.all()
    lookup_field = "uid"

    @swagger_auto_schema(
        operation_summary="Verify Vehicle RC",
        operation_description="Verify the vehicle registration certificate (RC) using the provided RC number.",
        request_body=VehicleRCVerificationRequestSerializer,
        responses={
            200: VehicleRCVerificationResponseSerializer,
            400: "Bad Request",
            404: "Plugin not found",
            500: "Internal Server Error",
        },
    )
    def create(self, request, *args, **kwargs):
        try:
            plugin = Plugin.objects.get(uid=kwargs.get("uid"))
        except Plugin.DoesNotExist:
            return Response(
                {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:

            req = VehicleRCVerificationRequest(**request.data)
            provider_class = PluginFactory.get_provider_class(
                plugin.provider, plugin.service
            )
            provider = provider_class(plugin)

            resp = provider.run(plugin, req)

            return Response(resp.dict(), status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)


class AadhaarVerificationViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()
    lookup_field = "uid"

    @swagger_auto_schema(
        operation_summary="Generate Aadhaar OTP",
        operation_description="Step 1 - Generate OTP for Aadhaar verification.",
        request_body=AadhaarOTPGenerateRequestSerializer,
        responses={
            200: AadhaarOTPGenerateResponseSerializer,
            400: "Bad Request",
            404: "Plugin not found",
        },
    )

    # @module_permission(op=Operation.CREATE)
    @action(
        detail=True, methods=["post"], url_path="generate-otp", url_name="generate-otp"
    )
    def generate_otp(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()
        except Plugin.DoesNotExist:
            return Response(
                {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            req_model = AadhaarOTPGenerateRequest(**request.data)

            provider_class = PluginFactory.get_provider_class(
                plugin.provider, plugin.service
            )
            provider = provider_class(plugin)

            resp_model: AadhaarOTPGenerateResponse = provider.generate_otp(
                plugin, req_model
            )

            return Response(resp_model.dict(), status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.errors()}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Verify Aadhaar OTP",
        operation_description="Step 2 - Verify OTP and fetch Aadhaar KYC details.",
        request_body=AadhaarOTPVerifyRequestSerializer,
        responses={
            200: AadhaarVerificationResponseSerializer,
            400: "Bad Request",
            404: "Plugin not found",
        },
    )
    # @module_permission(op=Operation.CREATE)
    @action(detail=True, methods=["post"], url_path="verify-otp", url_name="verify-otp")
    def verify_otp(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()
        except Plugin.DoesNotExist:
            return Response(
                {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            req_model = AadhaarOTPVerifyRequest(**request.data)

            provider_class = PluginFactory.get_provider_class(
                plugin.provider, plugin.service
            )
            provider = provider_class(plugin)

            resp_model: AadhaarVerificationResponse = provider.verify_otp(
                plugin, req_model
            )

            return Response(resp_model.dict(), status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.errors()}, status=status.HTTP_400_BAD_REQUEST)


class DrivingLicenseVerificationViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()
    lookup_field = "uid"

    @swagger_auto_schema(
        operation_summary="Verify Driving License",
        operation_description="Submit DL number + DOB → internally calls POST (submit) + GET (details) and returns final DL details.",
        request_body=DrivingLicenseVerificationRequestSerializer,
        responses={
            200: DrivingLicenseVerificationResponseSerializer,
            400: "Bad Request",
            404: "Plugin not found",
        },
    )
    # @module_permission(op=Operation.CREATE)
    @action(detail=True, methods=["post"], url_path="verify", url_name="verify-dl")
    def verify_driving_license(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()
        except Plugin.DoesNotExist:
            return Response(
                {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            req = DrivingLicenseVerificationRequest(**request.data)

            provider_class = PluginFactory.get_provider_class(
                plugin.provider, plugin.service
            )
            provider = provider_class(plugin)

            resp = provider.run(plugin, req)

            return Response(resp.model_dump(), status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.errors()}, status=status.HTTP_400_BAD_REQUEST)


class PANVerificationViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()
    lookup_field = "uid"

    @swagger_auto_schema(
        operation_summary="Verify PAN",
        operation_description="Validate PAN number using Deepvue PAN+ API",
        request_body=PANVerificationRequestSerializer,
        responses={
            200: PANVerificationResponseSerializer,
            400: "Bad Request",
            404: "Plugin not found",
        },
    )
    # @module_permission(op=Operation.CREATE)
    @action(detail=True, methods=["post"], url_path="pan/verify", url_name="verify-pan")
    def verify_pan(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()
        except Plugin.DoesNotExist:
            return Response(
                {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            req = PANVerificationRequest(**request.data)

            provider_class = PluginFactory.get_provider_class(
                plugin.provider, plugin.service
            )
            provider = provider_class(plugin)

            resp = provider.run(plugin, req)

            return Response(resp.dict(), status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)


class MobileToVehicleRCViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()
    lookup_field = "uid"

    @swagger_auto_schema(
        operation_summary="Fetch Vehicle RC from Mobile Number",
        operation_description="Fetch the Vehicle RC numbers linked to a mobile number using Deepvue API",
        request_body=MobileToVehicleRCRequestSerializer,
        responses={200: MobileToVehicleRCResponseSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="mobile-to-vehicle-rc",
        url_name="mobile-to-vehicle-rc",
    )
    def fetch_vehicle_rc(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()

        except Plugin.DoesNotExist:
            return Response(
                {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:

            req = MobileToVehicleRCRequest(**request.data)

            provider_class = PluginFactory.get_provider_class(
                plugin.provider, plugin.service
            )
            provider = provider_class(plugin)

            resp = provider.run(plugin, req)

            return Response(resp.dict(), status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)


class BankAccountVerificationViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()
    lookup_field = "uid"

    @swagger_auto_schema(
        operation_summary="Bank Account Verification - Penny Drop",
        operation_description="Verify bank account & IFSC combination via penny drop check using Deepvue API.",
        request_body=BankAccountVerificationRequestSerializer,
        responses={200: BankAccountVerificationResponseSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="bank-account-verification",
        url_name="bank-account-verification",
    )
    def verify_bank_account(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()
        except Plugin.DoesNotExist:
            return Response(
                {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            req = BankAccountVerificationRequest(**request.data)

            provider_class = PluginFactory.get_provider_class(
                plugin.provider, plugin.service
            )
            provider = provider_class(plugin)

            resp = provider.run(plugin, req)

            return Response(resp.dict(), status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.errors()}, status=status.HTTP_400_BAD_REQUEST)


class IfscLookUpViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()
    lookup_field = "uid"

    @swagger_auto_schema(
        operation_summary="IFSC Code Verification",
        operation_description="Verify IFSC code using Deepvue API.",
        request_body=IFSCVerificationRequestSerializer,
        responses={200: IFSCVerificationResponseSerializer},
    )
    @action(
        detail=True, methods=["post"], url_path="ifsc-lookup", url_name="ifsc-lookup"
    )
    def verify_ifsc(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()
        except Plugin.DoesNotExist:
            return Response(
                {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            req = IFSCVerificationRequest(**request.data)

            provider_class = PluginFactory.get_provider_class(
                plugin.provider, plugin.service
            )
            provider = provider_class(plugin)

            resp = provider.run(plugin, req)

            return Response(resp.dict(), status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)


class SMSViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()

    @swagger_auto_schema(
        operation_summary="Send SMS using Cell24x7",
        operation_description="Send transactional or promotional SMS via Cell24x7 provider",
        request_body=SMSNotificationRequestSerializer,
        responses={
            200: SMSNotificationResponseSerializer,
            400: "Bad Request",
            404: "Plugin not found",
        },
    )
    @action(detail=True, methods=["post"], url_path="send-sms", url_name="send-sms")
    def send_sms(self, request, *args, **kwargs):
        try:
            req = SMSRequest(**request.data)

            try:
                plugin = Plugin.objects.get(uid=req.plugin_uid)
            except Plugin.DoesNotExist:
                return Response(
                    {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
                )
            provider_class = PluginFactory.get_provider_class(
                plugin.provider, plugin.service
            )
            provider = provider_class(plugin)

            resp = provider.run(plugin, req)
            return Response(resp.dict(), status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.errors()}, status=status.HTTP_400_BAD_REQUEST)



class EmailViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()

    @swagger_auto_schema(
        operation_summary="Send Email using Resend",
        operation_description="Send email via Resend provider",
        request_body=EmailNotificationRequestSerializer,
        responses={200: EmailNotificationResponseSerializer},
    )
    @action(detail=True, methods=["post"], url_path="send-email", url_name="send-email")
    def send_email(self, request, *args, **kwargs):
        try:
            req = EmailRequest(**request.data)
            try:
                plugin = Plugin.objects.get(uid=req.plugin_uid)
            except Plugin.DoesNotExist:
                return Response(
                    {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
                )

            provider_class = PluginFactory.get_provider_class(plugin.provider, plugin.service)
            provider = provider_class(plugin)

            resp = provider.run(plugin, req)
            return Response(resp.dict(), status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.errors()}, status=status.HTTP_400_BAD_REQUEST)
        

class PANEligibilityViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()

    @swagger_auto_schema(
        operation_summary="Check PAN eligibility using UNISEN",
        operation_description="Check PAN eligibility via UNISEN provider",
        request_body=PANEligibilityRequestSerializer,
        responses={200: PANEligibilityResponseSerializer},
    )
    @action(detail=True, methods=["post"], url_path="check-pan-eligibility", url_name="check-pan-eligibility")
    def check_pan_eligibility(self, request, *args, **kwargs):
        try:
            req = PANEligibilityRequest(**request.data)
            try:
                plugin = Plugin.objects.get(uid=req.plugin_uid)
            except Plugin.DoesNotExist:
                return Response(
                    {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
                )

            provider_class = PluginFactory.get_provider_class(plugin.provider, plugin.service)
            provider = provider_class(plugin)

            resp = provider.run(plugin, req)
            return Response(resp.dict(), status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.errors()}, status=status.HTTP_400_BAD_REQUEST)