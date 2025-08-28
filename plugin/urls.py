from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (MobileToVehicleRCViewSet, PluginViewSet, 
                    VehicleRCVerificationView,
                    AadhaarVerificationViewSet,
                    DrivingLicenseVerificationViewSet,
                    PANVerificationViewSet,
                    BankAccountVerificationViewSet,
                    IfscLookUpViewSet)

router = DefaultRouter()
router.register(r'plugins', PluginViewSet, basename='plugin')

urlpatterns = [

    path(
        '<str:uid>/vehicle-rc-verification/',
        VehicleRCVerificationView.as_view({'post': 'create'}),
        name='plugin-vehicle-rc-verification',
    ),
    path(
        '<str:uid>/aadhaar/generate-otp/',
        AadhaarVerificationViewSet.as_view({'post': 'generate_otp'}),
        name='plugin-aadhaar-generate-otp',
    ),
    path(
        '<str:uid>/aadhaar/verify-otp/',
        AadhaarVerificationViewSet.as_view({'post': 'verify_otp'}),
        name='plugin-aadhaar-verify-otp',
    ),
    path(
        '<str:uid>/driving-license/verification/',
        DrivingLicenseVerificationViewSet.as_view({'post': 'verify_driving_license'}),
        name='plugin-driving-license-verification',
    ),
    path(
        '<str:uid>/pan/verify/',
        PANVerificationViewSet.as_view({'post': 'verify_pan'}),
        name='plugin-pan-verification',
    ),
    path(
        '<str:uid>/mobile-to-vehicle-rc/',
        MobileToVehicleRCViewSet.as_view({'post': 'fetch_vehicle_rc'}),
        name='plugin-mobile-to-vehicle-rc',
    ),
    path(
        '<str:uid>/bank-account/verification/',
        BankAccountVerificationViewSet.as_view({'post': 'verify_bank_account'}),
        name='plugin-bank-account-verification',
    ),
    path(
        '<str:uid>/ifsc-lookup/',
        IfscLookUpViewSet.as_view({'post': 'verify_ifsc'}),
        name='plugin-ifsc-lookup',
    ),
    path('', include(router.urls)),
]
