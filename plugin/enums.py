from enum import StrEnum, auto


class PluginProvider(StrEnum):
    NSDL = auto()
    UNISEN = auto()
    DEEPVUE = auto()
    CELL24X7 = auto()
    NOVOUP = auto()
    RESEND = auto()

    @property
    def required_auth_fields(self):
        """Returns list of required authentication fields for each provider"""
        auth_requirements = {
            self.NSDL: ["username", "password"],
            self.UNISEN: ["api_key"],
            self.DEEPVUE: ["client_id", "client_secret"],
            self.CELL24X7: ["api_key"],
            self.NOVOUP: ["api_key"],  # No authentication required
            self.RESEND: ["api_key"],
        }
        return auth_requirements.get(self, [])

    @property
    def auth_description(self):
        """Returns human-readable description of authentication requirements"""
        descriptions = {
            self.NSDL: "Requires username and password",
            self.UNISEN: "Requires API key",
            self.DEEPVUE: "Requires client ID and client secret",
            self.CELL24X7: "Requires API key",
            self.NOVOUP: "No authentication required",
            self.RESEND: "Requires API key",
        }
        return descriptions.get(self, "Authentication requirements not specified")

    @property
    def display_name(self):
        """Returns user-friendly display name for the provider"""
        display_names = {
            self.NSDL: "NSDL",
            self.UNISEN: "Unisen",
            self.DEEPVUE: "DeepVue",
            self.CELL24X7: "Cell24x7",
            self.NOVOUP: "NovoUP",
            self.RESEND: "Resend",
        }
        return display_names.get(self, self.value.title())


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
    POLICY_EXTRACTION = auto()
    EMAIL_NOTIFICATION = auto()

    @property
    def display_name(self):
        display_names = {
            self.PAN_VALIDATION: "PAN Validation",
            self.PAN_ELIGIBILITY: "PAN Eligibility Check",
            self.AADHAAR_VERIFICATION: "Aadhaar Verification",
            self.DRIVING_LICENSE_VERIFICATION: "Driving License Verification",
            self.VEHICLE_RC_VERIFICATION: "Vehicle RC Verification",
            self.MOBILE_TO_VEHICLE_RC: "Mobile to Vehicle RC",
            self.BANK_ACCOUNT_VERIFICATION: "Bank Account Verification",
            self.IFSC_LOOKUP: "IFSC Code Lookup",
            self.SMS_NOTIFICATION: "SMS Notification",
            self.POLICY_EXTRACTION: "Policy Extraction",
            self.EMAIL_NOTIFICATION: "Email Notification",
        }
        return display_names.get(self, self.value)

    @property
    def lucid_icon(self):
        icons = {
            self.PAN_VALIDATION: "credit-card",
            self.PAN_ELIGIBILITY: "check-circle",
            self.AADHAAR_VERIFICATION: "user-check",
            self.DRIVING_LICENSE_VERIFICATION: "car",
            self.VEHICLE_RC_VERIFICATION: "truck",
            self.MOBILE_TO_VEHICLE_RC: "smartphone",
            self.BANK_ACCOUNT_VERIFICATION: "building-2",
            self.IFSC_LOOKUP: "search",
            self.SMS_NOTIFICATION: "message-square",
            self.POLICY_EXTRACTION: "file-text",
            self.EMAIL_NOTIFICATION: "mail",
        }
        return icons.get(self, "circle")
