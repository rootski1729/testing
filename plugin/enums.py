from enum import StrEnum, auto


class PluginProvider(StrEnum):
    NSDL = auto()
    UNISEN = auto()
    DEEPVUE = auto()
    CELL24X7 = auto()


class PluginService(StrEnum):
    PAN_VALIDATION = auto()
    PAN_ELIGIBILITY = auto()
    AADHAAR_VERIFICATION = auto()
    DRIVING_LICENSE_VERIFICATION = auto()
    VEHICLE_RC_VERIFICATION = auto()
    MOBILE_TO_VEHICLE_RC = auto()
    BANK_ACCOUNT_VERIFICATION = auto()
    IFSC_LOOKUP = auto()
    SMS_NOTIFICATION = auto()