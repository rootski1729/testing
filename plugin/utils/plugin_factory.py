from plugin.enums import PluginProvider, PluginService
from plugin.services.pan_validation import providers as PANValidationProviders
from plugin.services.pan_eligibility import providers as PANElegibilityProviders
from plugin.services.aadhaar_verification import providers as AadhaarProviders
from plugin.services.vechile_rc_validation import providers as VehicleRCProviders
from plugin.services.driving_license import providers as DrivingLicenseProviders
from plugin.services.mobile_to_vehicle_rc import providers as MobileToVehicleRCProviders
from plugin.services.bankaccount_verification import providers as BankAccountVerificationProviders
from plugin.services.ifsc_lookup import providers as IFSCProviders

from plugin.services.sms_notification import providers as SMSProviders


class PluginFactory:
    _registry = {
        (PluginProvider.NSDL, PluginService.PAN_VALIDATION): PANValidationProviders.NSDL,
        (PluginProvider.UNISEN, PluginService.PAN_ELIGIBILITY): PANElegibilityProviders.Unisen,
        (PluginProvider.DEEPVUE, PluginService.PAN_VALIDATION): PANValidationProviders.DEEPVUE,
        (PluginProvider.DEEPVUE, PluginService.AADHAAR_VERIFICATION): AadhaarProviders.DEEPVUE,
        (PluginProvider.DEEPVUE, PluginService.VEHICLE_RC_VERIFICATION): VehicleRCProviders.DEEPVUE,
        (PluginProvider.DEEPVUE, PluginService.DRIVING_LICENSE_VERIFICATION): DrivingLicenseProviders.DEEPVUE,
        (PluginProvider.DEEPVUE, PluginService.MOBILE_TO_VEHICLE_RC): MobileToVehicleRCProviders.DEEPVUE,
        (PluginProvider.DEEPVUE, PluginService.BANK_ACCOUNT_VERIFICATION): BankAccountVerificationProviders.DEEPVUE,
        (PluginProvider.DEEPVUE, PluginService.IFSC_LOOKUP): IFSCProviders.DEEPVUE,

        (PluginProvider.CELL24X7, PluginService.SMS_NOTIFICATION): SMSProviders.Cell,
        # … add more
    }

    @classmethod
    def get_provider_class(cls, provider: PluginProvider | str, service: PluginService | str):
        try:
            if isinstance(provider, str):
                provider = PluginProvider(provider)
            if isinstance(service, str):
                service = PluginService(service)
            return cls._registry[(provider, service)]
        except KeyError:
            raise ValueError(f"No provider found for {provider} + {service}")
