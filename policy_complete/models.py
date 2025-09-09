from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Tuple, Union
from datetime import date
from enum import StrEnum

# ====================== ENUMS ======================

class FuelType(StrEnum):
    PETROL = "Petrol" # Petrol
    DIESEL = "Diesel" # Diesel
    CNG = "CNG" # Compressed Natural Gas
    LPG = "LPG" # Liquefied Petroleum Gas
    ELECTRIC = "Electric" # Electric
    HYBRID_ELECTRIC = "Hybrid Electric" # Hybrid Electric
    HYDROGEN = "Hydrogen" # Hydrogen


class Insurer(StrEnum):
    # Public sector
    UIIC = "UIIC"           # United India Insurance Company
    NIC = "NIC"             # National Insurance Company
    TNI = "TNI"             # The New India Assurance Company
    OR = "OR"               # The Oriental Insurance Company
    
    # Large private
    SBI = "SBI"             # SBI General Insurance
    HDFC = "HDFC"           # HDFC ERGO General Insurance
    ICICI = "ICICI"         # ICICI Lombard General Insurance
    BAJAJ = "BAJAJ"         # Bajaj Allianz General Insurance
    RGCL = "RGCL"           # Reliance General Insurance
    TATA = "TATA"           # TATA AIG General Insurance
    
    KTKM = "KTKM"           # Kotak Mahindra General Insurance - legacy code
    ZURICHKOTAK = "ZURICHKOTAK"  # Zurich Kotak General Insurance
    IFFCO = "IFFCO"         # IFFCO Tokio General Insurance
    ROYAL = "ROYAL"         # Royal Sundaram General Insurance
    CHOLA = "CHOLA"         # Cholamandalam MS General Insurance
    MAGMA = "MAGMA"         # Magma HDI General Insurance
    LIB = "LIB"             # Liberty General Insurance
    USGI = "USGI"           # Universal Sompo General Insurance
    GO = "GO"               # Go Digit General Insurance
    SHRIRAM = "SHRIRAM"     # Shriram General Insurance

    # Private - digital and newer
    ACKO = "ACKO"           # ACKO General Insurance
    NAVI = "NAVI"           # Navi General Insurance
    ZUNO = "ZUNO"           # Zuno General Insurance (formerly Edelweiss General)
    RAHEJAQBE = "RAHEJAQBE" # Raheja QBE General Insurance
    KSHEMA = "KSHEMA"       # Kshema General Insurance

    # Brand update for Future Generali
    FUTURE = "FUTURE"                 # Legacy alias - Future Generali India Insurance
    GENERALI_CENTRAL = "GENERALI_CENTRAL"  # Generali Central Insurance (rebrand per your label)
    
    @property
    def full_names(self) -> dict["Insurer", str]:
        return {
            # Public sector
            Insurer.UIIC: "United India Insurance Co. Ltd.",
            Insurer.NIC: "National Insurance Co. Ltd.",
            Insurer.TNI: "The New India Assurance Co. Ltd.",
            Insurer.OR: "The Oriental Insurance Co. Ltd.",

            # Large private
            Insurer.SBI: "SBI General Insurance Co. Ltd.",
            Insurer.HDFC: "HDFC ERGO General Insurance Co. Ltd.",
            Insurer.ICICI: "ICICI Lombard General Insurance Co. Ltd.",
            Insurer.BAJAJ: "Bajaj Allianz General Insurance Co. Ltd.",
            Insurer.RGCL: "Reliance General Insurance Co. Ltd.",
            Insurer.TATA: "Tata AIG General Insurance Co. Ltd.",

            # Private - established
            Insurer.KTKM: "Kotak Mahindra General Insurance Co. Ltd.",
            Insurer.ZURICHKOTAK: "Zurich Kotak General Insurance Co. Ltd.",
            Insurer.IFFCO: "IFFCO Tokio General Insurance Co. Ltd.",
            Insurer.ROYAL: "Royal Sundaram General Insurance Co. Ltd.",
            Insurer.CHOLA: "Cholamandalam MS General Insurance Co. Ltd.",
            Insurer.MAGMA: "Magma HDI General Insurance Co. Ltd.",
            Insurer.LIB: "Liberty General Insurance Ltd.",
            Insurer.USGI: "Universal Sompo General Insurance Co. Ltd.",
            Insurer.GO: "Go Digit General Insurance Ltd.",
            Insurer.SHRIRAM: "Shriram General Insurance Co. Ltd.",

            # Private - digital and newer
            Insurer.ACKO: "Acko General Insurance Ltd.",
            Insurer.NAVI: "Navi General Insurance Ltd.",
            Insurer.ZUNO: "Zuno General Insurance Ltd.",
            Insurer.RAHEJAQBE: "Raheja QBE General Insurance Co. Ltd.",
            Insurer.KSHEMA: "Kshema General Insurance Ltd.",

            # Brand update and alias
            Insurer.FUTURE: "Future Generali India Insurance Co. Ltd.",
            Insurer.GENERALI_CENTRAL: "Generali Central Insurance Co. Ltd.",
        }


class Product(StrEnum):
    MOTOR = "Motor" # Motor Insurance
    HEALTH = "Health" # Health Insurance
    LIFE = "Life" # Life Insurance
    NON_MOTOR = "Non-Motor" # Non-Motor Insurance
    PERSONAL_ACCIDENT = "Personal Accident" # Personal Accident Insurance
    TRAVEL = "Travel" # Travel Insurance

class ProductType(StrEnum):
    PRIVATE = "Private"
    COMMERCIAL = "Commercial"

class ProductSubType(StrEnum):
    PC = "PC"
    TW = "TW"
    GCV = "GCV"
    PCV = "PCV"
    MISC = "MISC"

class ProductCategory(StrEnum):
    DUO = "2W"
    TRI = "3W"
    QUAD = "4W"
    HEXA = "6W"

class PolicyType(StrEnum):
    PACKAGE = "Package" # Package Policy
    OD = "OD" # Own Damage Policy
    TP = "TP" # Third Party Policy
    BUNDLED = "Bundled" # Bundled Policy

class PolicyCategory(StrEnum):
    PACKAGE_1_1 = "1+1" # Package Policy (1+1)
    PACKAGE_1_3 = "1+3" # Package Policy (1+3)
    PACKAGE_1_5 = "1+5" # Package Policy (1+5)
    PACKAGE_3_3 = "3+3" # Package Policy (3+3)
    PACKAGE_5_5 = "5+5" # Package Policy (5+5)
    SAOD_1 = "1+0" # Standalone Own Damage
    SAOD_2 = "2+0" # Standalone Own Damage (2 + 0)
    SAOD_3 = "3+0" # Standalone Own Damage (3 + 0)
    SATP_1 = "0+1" # Standalone Third Party (0 + 1)
    SATP_3 = "0+3" # Standalone Third Party (0 + 3)

class InsuredType(StrEnum):
    INDIVIDUAL = "Individual"
    CORPORATE = "Corporate"

# ====================== BASE MODELS ======================

class BasePluginResponse(BaseModel):
    is_success: bool
    message: str

# ====================== REQUEST/RESPONSE MODELS ======================

class StartCompanyProcessingRequest(BaseModel):
    company_id: str
    django_base_url: str
    jwt_token: Optional[str] = None 

class PendingFileResponse(BaseModel):
    mongo_id: str
    file_url: str
    file_name: str

class UpdateFileStatusRequest(BaseModel):
    mongo_id: str
    success: bool
    extracted_data: Optional[dict] = None
    error: Optional[str] = None

class PolicyExtractionRequest(BaseModel):
    file: Tuple[str, bytes, str]

class PolicyExtractionObject(BaseModel):
    # Core policy fields
    policy_number: Optional[str] = Field(default=None, description="Policy number of the issued policy")
    issue_date: Optional[date] = Field(default=None, description="Issue date of the issued policy in YYYY-MM-DD format")
    od_start_date: Optional[date] = Field(default=None, description="Start date of the OD cover in YYYY-MM-DD format")
    od_end_date: Optional[date] = Field(default=None, description="End date of the OD cover in YYYY-MM-DD format")
    tp_start_date: Optional[date] = Field(default=None, description="Start date of the TP cover in YYYY-MM-DD format")
    tp_end_date: Optional[date] = Field(default=None, description="End date of the TP cover in YYYY-MM-DD format")
    sum_insured: Optional[float] = Field(default=None, description="Sum insured amount in INR")
    
    # Premium fields
    basic_od_premium: Optional[float] = Field(default=None, description="Basic OD premium amount in INR")
    total_od_premium: Optional[float] = Field(default=None, description="Total OD premium amount in INR")
    total_od_add_on_premium: Optional[float] = Field(default=None, description="Total OD add-on premium amount in INR")
    basic_tp_premium: Optional[float] = Field(default=None, description="Basic TP premium amount in INR")
    total_tp_premium: Optional[float] = Field(default=None, description="Total TP premium amount in INR")
    total_tp_add_on_premium: Optional[float] = Field(default=None, description="Total TP add-on premium amount in INR")
    net_premium: Optional[float] = Field(default=None, description="Net premium amount in INR")
    taxes: Optional[float] = Field(default=None, description="Taxes amount in INR")
    taxes_rate: Optional[float] = Field(default=None, description="Taxes rate in percentage")
    gross_discount: Optional[float] = Field(default=None, description="Gross discount amount in INR")
    total_premium: Optional[float] = Field(default=None, description="Total premium amount in INR")
    ncb: Optional[float] = Field(default=None, description="No Claim Bonus (NCB) amount in INR")
    
    # Broker fields
    broker_name: Optional[str] = Field(default=None, description="Name of the broker")
    broker_email: Optional[str] = Field(default=None, description="Email of the broker")
    broker_code: Optional[str] = Field(default=None, description="Code of the broker")
    
    # Vehicle fields
    make: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    vehicle_registration_date: Optional[date] = None
    make_year: Optional[int] = None
    vehicle_fuel_type: Optional[FuelType] = None
    vehicle_engine_number: Optional[str] = None
    vehicle_chassis_number: Optional[str] = None
    vehicle_seating_capacity: Optional[int] = None
    vehicle_cc: Optional[int] = None
    vehicle_idv: Optional[float] = None
    vehicle_gvw: Optional[float] = None
    
    # Registration fields
    registration_number_1: Optional[str] = None
    registration_number_2: Optional[str] = None
    registration_number_3: Optional[str] = None
    registration_number_4: Optional[str] = None
    vehicle_registration_state: Optional[str] = None
    vehicle_rta: Optional[str] = None
    
    # Insured fields
    insured_name: Optional[str] = None
    insured_address: Optional[str] = None
    insured_mobile: Optional[str] = None
    insured_email: Optional[str] = None
    
    # Classification fields
    insurer: Optional[Insurer] = None
    product: Optional[Product] = None
    product_type: Optional[ProductType] = None
    product_sub_type: Optional[ProductSubType] = None
    product_category: Optional[ProductCategory] = None
    policy_category: Optional[PolicyCategory] = None
    policy_type: Optional[PolicyType] = None
    insured_type: Optional[InsuredType] = None
    
    # Previous policy fields
    last_policy_available: Optional[bool] = None
    last_insurer: Optional[Insurer] = None
    last_policy_number: Optional[str] = None
    last_policy_to: Optional[date] = None
    last_policy_ncb_percent: Optional[float] = None

class PolicyExtractionResponse(BasePluginResponse):
    response: PolicyExtractionObject

# ====================== NOVOUP SPECIFIC MODELS ======================

class NovoupExtractionResponse(BaseModel):
    policy_number: Optional[str] = None
    business_type: Optional[str] = None
    policy_type: Optional[str] = None
    seating_capacity: Optional[int] = None
    sum_insured: Optional[float] = None
    registration_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    issue_date: Optional[date] = None
    od_start_date: Optional[date] = None
    od_end_date: Optional[date] = None
    tp_start_date: Optional[date] = None
    tp_end_date: Optional[date] = None
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    manufacturing_year: Optional[int] = None
    vehicle_number: Optional[str] = None
    vehicle_idv: Optional[float] = None
    engine_number: Optional[str] = None
    chassis_number: Optional[str] = None
    rto_code: Optional[str] = None
    fuel_type: Optional[str] = None
    gross_vehicle_weight: Optional[float] = None
    engine_capacity_cc: Optional[int] = None
    basic_od_premium: Optional[float] = None
    total_od_premium: Optional[float] = None
    total_od_add_on_premium: Optional[float] = None
    basic_tp_premium: Optional[float] = None
    total_tp_premium: Optional[float] = None
    total_tp_add_on_premium: Optional[float] = None
    net_premium: Optional[float] = None
    taxes: Optional[float] = None
    taxes_rate: Optional[str] = None
    ncb: Optional[float] = None
    gross_discount: Optional[float] = None
    previous_ncb: Optional[float] = None
    prev_policy_expiry: Optional[date] = None
    total_premium: Optional[float] = None
    previous_insurer_name: Optional[str] = None
    previous_policy_number: Optional[str] = None
    previous_policy_end_date: Optional[date] = None
    broker_name: Optional[str] = None
    broker_email: Optional[EmailStr] = None
    broker_code: Optional[str] = None

    @property
    def od_duration_years(self) -> int:
        if self.od_end_date and self.od_start_date:
            return max(0, self.od_end_date.year - self.od_start_date.year)
        return 0

    @property
    def tp_duration_years(self) -> int:
        if self.tp_end_date and self.tp_start_date:
            return max(0, self.tp_end_date.year - self.tp_start_date.year)
        return 0

    @property
    def has_od_premium(self) -> bool:
        od_premium_fields = ("basic_od_premium", "total_od_premium", "total_od_add_on_premium")
        return any(
            getattr(self, field) not in (None, 0, "0", "0.0", "0.00")
            for field in od_premium_fields
        )

    @property
    def has_tp_premium(self) -> bool:
        tp_premium_fields = ("basic_tp_premium", "total_tp_premium", "total_tp_add_on_premium")
        return any(
            getattr(self, field) not in (None, 0, "0", "0.0", "0.00")
            for field in tp_premium_fields
        )

    def calc_policy_category(self, provider_info: dict) -> PolicyCategory:
        policy_type = self.calc_policy_type(provider_info)
        if policy_type == PolicyType.OD:
            if self.od_duration_years == 1:
                return PolicyCategory.SAOD_1
            elif self.od_duration_years == 2:
                return PolicyCategory.SAOD_2
            elif self.od_duration_years == 3:
                return PolicyCategory.SAOD_3
        elif policy_type == PolicyType.TP:
            if self.tp_duration_years == 1:
                return PolicyCategory.SATP_1
            elif self.tp_duration_years == 3:
                return PolicyCategory.SATP_3
        elif self.od_duration_years == 1 and self.tp_duration_years == 1:
            return PolicyCategory.PACKAGE_1_1
        elif self.od_duration_years == 1 and self.tp_duration_years == 3:
            return PolicyCategory.PACKAGE_1_3
        elif self.od_duration_years == 1 and self.tp_duration_years == 5:
            return PolicyCategory.PACKAGE_1_5
        elif self.od_duration_years == 3 and self.tp_duration_years == 3:
            return PolicyCategory.PACKAGE_3_3
        elif self.od_duration_years == 5 and self.tp_duration_years == 5:
            return PolicyCategory.PACKAGE_5_5

    @property
    def product_category(self) -> ProductCategory:
        if self.seating_capacity is None:
            return None
        
        if self.seating_capacity == 2:
            return ProductCategory.DUO
        elif self.seating_capacity == 3:
            return ProductCategory.TRI
        elif self.seating_capacity >= 4 and self.seating_capacity < 9:
            return ProductCategory.QUAD
        return None

    def calc_policy_type(self, provider_info: dict) -> PolicyType:
        policy_type = provider_info.get("policy_type")
        
        if self.policy_type and self.policy_type.lower() == "third party":
            policy_type = PolicyType.TP
        elif self.policy_type and self.policy_type.lower() == "package":
            if self.od_duration_years == self.tp_duration_years:
                policy_type = PolicyType.PACKAGE
            else:
                policy_type = PolicyType.BUNDLED
        elif self.has_od_premium and self.has_tp_premium:
            if self.od_duration_years == self.tp_duration_years:
                policy_type = PolicyType.PACKAGE
            else:
                policy_type = PolicyType.BUNDLED
        elif self.has_od_premium and not self.has_tp_premium:
            policy_type = PolicyType.OD
        elif self.has_tp_premium and not self.has_od_premium:
            policy_type = PolicyType.TP

        return policy_type

    @property
    def vehicle_fuel_type(self) -> FuelType:
        from utils import clean_fuel_type
        return clean_fuel_type(self.fuel_type)

    @property
    def last_policy_available(self) -> bool:
        return (
            self.previous_insurer_name is not None
            or self.previous_policy_number is not None
        )