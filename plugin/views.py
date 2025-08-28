# views.py

from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from core.views import PermissionScopedViewSet, module_permission
from permission.enums import Module, Operation
from .models import Plugin
from .serializers import PluginSerializer

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from pydantic import ValidationError
from plugin.utils.plugin_factory import PluginFactory

from django.db import IntegrityError
from plugin.services.vechile_rc_validation.vechile_rc_serializer import (VehicleRCVerificationRequestSerializer,
                                                                        VehicleRCVerificationResponseSerializer)

from plugin.services.aadhaar_verification.serializers import (AadhaarOTPGenerateRequestSerializer,
                                                            AadhaarOTPGenerateResponseSerializer,
                                                            AadhaarOTPVerifyRequestSerializer,
                                                            AadhaarVerificationResponseSerializer)

from plugin.services.driving_license.serializers import(DrivingLicenseVerificationRequestSerializer,
                                                        DrivingLicenseVerificationResponseSerializer)

from plugin.services.pan_validation.serializers import (PANVerificationRequestSerializer,
                                                    PANVerificationResponseSerializer)

from plugin.services.mobile_to_vehicle_rc.serializers import (MobileToVehicleRCRequestSerializer,
                                                            MobileToVehicleRCResponseSerializer)

from plugin.services.bankaccount_verification.serializers import (BankAccountVerificationRequestSerializer,
                                                                BankAccountVerificationResponseSerializer)

from plugin.services.ifsc_lookup.serializers import (IFSCVerificationRequestSerializer,
                                                    IFSCVerificationResponseSerializer)
class PluginViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()


    @swagger_auto_schema(
        operation_summary="List Plugins",
        operation_description="Retrieve a list of registered plugins.",
        responses={200: PluginSerializer(many=True), 404: "Not Found"},
    )
    
    def list(self, request, *args, **kwargs):
        plugins = self.get_queryset()
        serializer = PluginSerializer(plugins, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new Plugin",
        operation_description="Register a new plugin with provider + service credentials.",
        request_body=PluginSerializer,
        responses={201: PluginSerializer, 400: "Bad Request"},
    )


    def create(self, request, *args, **kwargs):
        serializer = PluginSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        try:
            plugin = serializer.save(
                access_level=request.user.role.access_level,
                access_department=request.user.department,
                access_location=request.user.location,
                company=request.user.company
            )
        except IntegrityError:
            return Response(
                {"error": "Plugin with this provider and service already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            PluginSerializer(plugin).data, status=status.HTTP_201_CREATED
        )



class VehicleRCVerificationView(PermissionScopedViewSet):
    modules = [Module.PLUGIN] 
    permission_classes = [AllowAny]
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
            plugin = Plugin.objects.get(uid=kwargs.get('uid'))
            req_serializer = VehicleRCVerificationRequestSerializer(data=request.data)
            req_serializer.is_valid(raise_exception=True)

    
            provider_class = PluginFactory.get_provider_class(plugin.provider, plugin.service)
            provider = provider_class(plugin.client_id, plugin.client_secret)


            resp_data = provider.verify_rc(plugin, req_serializer)


            resp_serializer = VehicleRCVerificationResponseSerializer(data=resp_data)
            resp_serializer.is_valid(raise_exception=True)

            return Response(resp_serializer.data, status=status.HTTP_200_OK)

        except Plugin.DoesNotExist:
            return Response(
                {"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            


class AadhaarVerificationViewSet(PermissionScopedViewSet):
    modules = [Module.PLUGIN]
    queryset = Plugin.objects.all()
    lookup_field = "uid"

    @swagger_auto_schema(
        operation_summary="Generate Aadhaar OTP",
        operation_description="Step 1 - Generate OTP for Aadhaar verification.",
        request_body=AadhaarOTPGenerateRequestSerializer,
        responses={200: AadhaarOTPGenerateResponseSerializer, 400: "Bad Request", 404: "Plugin not found"},
    )
    
    #@module_permission(op=Operation.CREATE)
    @action(detail=True, methods=["post"], url_path="generate-otp", url_name="generate-otp")
    def generate_otp(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()
            serializer = AadhaarOTPGenerateRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            provider_class = PluginFactory.get_provider_class(plugin.provider, plugin.service)
        
            
            provider = provider_class(plugin.client_id, plugin.client_secret)
            
            
            # Check if method exists
            resp_data = provider.generate_otp(plugin, serializer.validated_data)
            response_serializer = AadhaarOTPGenerateResponseSerializer(data=resp_data)
            response_serializer.is_valid(raise_exception=True)

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Plugin.DoesNotExist:
            return Response({"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Verify Aadhaar OTP",
        operation_description="Step 2 - Verify OTP and fetch Aadhaar KYC details.",
        request_body=AadhaarOTPVerifyRequestSerializer,
        responses={200: AadhaarVerificationResponseSerializer, 400: "Bad Request", 404: "Plugin not found"},
    )
    #@module_permission(op=Operation.CREATE)
    @action(detail=True, methods=["post"], url_path="verify-otp", url_name="verify-otp")
    def verify_otp(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()
            serializer = AadhaarOTPVerifyRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            provider_class = PluginFactory.get_provider_class(plugin.provider, plugin.service)
            provider = provider_class(plugin.client_id, plugin.client_secret)

            resp_data = provider.verify_otp(plugin, serializer.validated_data)

            response_serializer = AadhaarVerificationResponseSerializer(data=resp_data)
            response_serializer.is_valid(raise_exception=True)

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Plugin.DoesNotExist:
            return Response({"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
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
            serializer = DrivingLicenseVerificationRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            provider_class = PluginFactory.get_provider_class(plugin.provider, plugin.service)
            provider = provider_class(plugin.client_id, plugin.client_secret)

            
            resp_data = provider.verify_driving_license(plugin, serializer)

            return Response(resp_data, status=status.HTTP_200_OK)

        except Plugin.DoesNotExist:
            return Response({"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
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
            404: "Plugin not found"
        },
    )
    # @module_permission(op=Operation.CREATE)
    @action(detail=True, methods=["post"], url_path="pan/verify", url_name="verify-pan")
    def verify_pan(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()

            serializer = PANVerificationRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            provider_class = PluginFactory.get_provider_class(plugin.provider, plugin.service)
            provider = provider_class(plugin.client_id, plugin.client_secret)

        
            resp_data = provider.validate_pan(plugin, serializer)

            return Response(resp_data, status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Plugin.DoesNotExist:
            return Response({"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        


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
    @action(detail=True, methods=["post"], url_path="mobile-to-vehicle-rc", url_name="mobile-to-vehicle-rc")
    def fetch_vehicle_rc(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()

            serializer = MobileToVehicleRCRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            provider_class = PluginFactory.get_provider_class(plugin.provider, plugin.service)
            provider = provider_class(plugin.client_id, plugin.client_secret)

            resp_data = provider.fetch_vehicle_rc(plugin, serializer)

            return Response(resp_data, status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Plugin.DoesNotExist:
            return Response({"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    @action(detail=True, methods=["post"], url_path="bank-account-verification", url_name="bank-account-verification")
    def verify_bank_account(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()

            serializer = BankAccountVerificationRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            provider_class = PluginFactory.get_provider_class(plugin.provider, plugin.service)
            provider = provider_class(plugin.client_id, plugin.client_secret)

            resp_data = provider.verify_bank_account(plugin, serializer)

            return Response(resp_data, status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Plugin.DoesNotExist:
            return Response({"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
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
    @action(detail=True, methods=["post"], url_path="ifsc-lookup", url_name="ifsc-lookup")
    def verify_ifsc(self, request, *args, **kwargs):
        try:
            plugin = self.get_object()

            serializer = IFSCVerificationRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)


            provider_class = PluginFactory.get_provider_class(plugin.provider, plugin.service)
            provider = provider_class(plugin.client_id, plugin.client_secret)

            resp_data = provider.verify_ifsc(plugin, serializer)

            return Response(resp_data, status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Plugin.DoesNotExist:
            return Response({"error": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
