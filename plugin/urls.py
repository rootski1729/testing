from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AadhaarVerificationViewSet,
    BankAccountVerificationViewSet,
    DrivingLicenseVerificationViewSet,
    IfscLookUpViewSet,
    MobileToVehicleRCViewSet,
    PANVerificationViewSet,
    PluginViewSet,
    SMSViewSet,
    VehicleRCVerificationView,
    PANEligibilityViewSet
)


router = DefaultRouter()
router.register(r"", PluginViewSet, basename="plugin")
# router.register(r'services', PluginServiceListViewSet, basename='plugin-services')

urlpatterns = [
    # path(
    #     '<str:uid>/vehicle-rc-verification/',
    #     VehicleRCVerificationView.as_view({'post': 'create'}),
    #     name='plugin-vehicle-rc-verification',
    # ),
    # path(
    #     '<str:uid>/aadhaar/generate-otp/',
    #     AadhaarVerificationViewSet.as_view({'post': 'generate_otp'}),
    #     name='plugin-aadhaar-generate-otp',
    # ),
    # path(
    #     '<str:uid>/aadhaar/verify-otp/',
    #     AadhaarVerificationViewSet.as_view({'post': 'verify_otp'}),
    #     name='plugin-aadhaar-verify-otp',
    # ),
    # path(
    #     '<str:uid>/driving-license/verification/',
    #     DrivingLicenseVerificationViewSet.as_view({'post': 'verify_driving_license'}),
    #     name='plugin-driving-license-verification',
    # ),
    # path(
    #     '<str:uid>/pan/verify/',
    #     PANVerificationViewSet.as_view({'post': 'verify_pan'}),
    #     name='plugin-pan-verification',
    # ),
    # path(
    #     '<str:uid>/mobile-to-vehicle-rc/',
    #     MobileToVehicleRCViewSet.as_view({'post': 'fetch_vehicle_rc'}),
    #     name='plugin-mobile-to-vehicle-rc',
    # ),
    # path(
    #     '<str:uid>/bank-account/verification/',
    #     BankAccountVerificationViewSet.as_view({'post': 'verify_bank_account'}),
    #     name='plugin-bank-account-verification',
    # ),
    # path(
    #     '<str:uid>/ifsc-lookup/',
    #     IfscLookUpViewSet.as_view({'post': 'verify_ifsc'}),
    #     name='plugin-ifsc-lookup',
    # ),
    # path(
    #     'sms/',
    #     SMSViewSet.as_view({'post': 'send_sms'}),
    #     name='plugin-sms',
    # ),
    # path('email/', EmailViewSet.as_view({'post': 'send_email'}), name='plugin-email'),
    path('pan-eligibility/', PANEligibilityViewSet.as_view({'post': 'check_pan_eligibility'}), name='plugin-pan-eligibility'),
    path('', include(router.urls)),
]
