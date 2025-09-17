from core.enums import BaseStrEnum

class Insurer(BaseStrEnum):
    # Public sector
    UIIC = "UIIC"           # United India Insurance Company
    NIC = "NIC"             # National Insurance Company
    TNI = "TNI"             # The New India Assurance Company
    OR = "OR"               # The Oriental Insurance Company
    GIC = "GIC"             # General Insurance Corporation of India (reinsurer)

    # Large private
    SBI = "SBI"             # SBI General Insurance
    HDFC = "HDFC"           # HDFC ERGO General Insurance
    ICICI = "ICICI"         # ICICI Lombard General Insurance
    BAJAJ = "BAJAJ"         # Bajaj Allianz General Insurance
    RGCL = "RGCL"           # Reliance General Insurance
    TATA = "TATA"           # TATA AIG General Insurance

    # Private - established
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
    BHARTIAXA = "BHARTIAXA"   # Bharti AXA General Insurance

    # Private - digital and newer
    ACKO = "ACKO"           # ACKO General Insurance
    NAVI = "NAVI"           # Navi General Insurance
    ZUNO = "ZUNO"           # Zuno General Insurance (formerly Edelweiss General)
    RAHEJAQBE = "RAHEJAQBE" # Raheja QBE General Insurance
    KSHEMA = "KSHEMA"       # Kshema General Insurance

    # Brand update for Future Generali
    FUTURE = "FUTURE"                 # Legacy alias - Future Generali India Insurance
    GENERALI_CENTRAL = "GENERALI_CENTRAL"  # Generali Central Insurance (rebrand per your label)
    
    @staticmethod
    def full_names() -> dict["Insurer", str]:
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


class Product(BaseStrEnum):
    MOTOR = "Motor" # Motor Insurance
    HEALTH = "Health" # Health Insurance
    LIFE = "Life" # Life Insurance
    NON_MOTOR = "Non-Motor" # Non-Motor Insurance
    PERSONAL_ACCIDENT = "Personal Accident" # Personal Accident Insurance
    TRAVEL = "Travel" # Travel Insurance

class ProductType(BaseStrEnum):
    PRIVATE = "Private" # Private Vehicle Insurance
    COMMERCIAL = "Commercial" # Commercial Vehicle Insurance

class ProductSubType(BaseStrEnum):
    GCV = "GCV" # Goods Carrying Vehicle
    PCV = "PCV" # Passenger Carrying Vehicle
    TW = "TW" # Two Wheeler
    PC = "PC" # Private Car
    MISC = "MISC" # Miscellaneous Vehicle

class ProductCategory(BaseStrEnum):
    DUO = "2W" # Two Wheeler
    TRI = "3W" # Three Wheeler
    QUAD = "4W" # Four Wheeler
    HEX = "6W" # Six Wheeler
    OCTA = "8W" # Eight Wheeler
    DEC = "10W" # Ten Wheeler
    DUODEC = "12W" # Twelve Wheeler


class PolicyCategory(BaseStrEnum):
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

class PolicyType(BaseStrEnum):
    PACKAGE = "Package" # Package Policy
    OD = "OD" # Own Damage Policy
    TP = "TP" # Third Party Policy
    BUNDLED = "Bundled" # Bundled Policy

class Transmission(BaseStrEnum):
    MANUAL = "Manual" # Manual Transmission
    AUTOMATIC = "Automatic" # Automatic Transmission


class BusinessType(BaseStrEnum):
    NEW = "New" # New Business
    RENEWAL = "Renewal" # Renewal Business

class FuelType(BaseStrEnum):
    PETROL = "Petrol" # Petrol
    DIESEL = "Diesel" # Diesel
    CNG = "CNG" # Compressed Natural Gas
    LPG = "LPG" # Liquefied Petroleum Gas
    ELECTRIC = "Electric" # Electric
    HYBRID_ELECTRIC = "Hybrid Electric" # Hybrid Electric
    HYDROGEN = "Hydrogen" # Hydrogen

class InsuredType(BaseStrEnum):
    INDIVIDUAL = "Individual" # Individual
    CORPORATE = "Corporate" # Corporate

class InsuredTitle(BaseStrEnum):
    MR = "Mr" # Mister
    MRS = "Mrs" # Misses
    MS = "Ms" # Miss
    MISS = "Miss" # Miss
    OTHER = "Other" # Other

class State(BaseStrEnum):
    # States of India
    ANDHRA_PRADESH = "Andhra Pradesh"
    ARUNACHAL_PRADESH = "Arunachal Pradesh"
    ASSAM = "Assam"
    BIHAR = "Bihar"
    CHHATTISGARH = "Chhattisgarh"
    GOA = "Goa"
    GUJARAT = "Gujarat"
    HARYANA = "Haryana"
    HIMACHAL_PRADESH = "Himachal Pradesh"
    JHARKHAND = "Jharkhand"
    KARNATAKA = "Karnataka"
    KERALA = "Kerala"
    MADHYA_PRADESH = "Madhya Pradesh"
    MAHARASHTRA = "Maharashtra"
    MANIPUR = "Manipur"
    MEGHALAYA = "Meghalaya"
    MIZORAM = "Mizoram"
    NAGALAND = "Nagaland"
    ODISHA = "Odisha"
    PUNJAB = "Punjab"
    RAJASTHAN = "Rajasthan"
    SIKKIM = "Sikkim"
    TAMIL_NADU = "Tamil Nadu"
    TELANGANA = "Telangana"
    TRIPURA = "Tripura"
    UTTAR_PRADESH = "Uttar Pradesh"
    UTTARAKHAND = "Uttarakhand"
    WEST_BENGAL = "West Bengal"

    # Union Territories of India
    ANDAMAN_AND_NICOBAR_ISLANDS = "Andaman and Nicobar Islands"
    CHANDIGARH = "Chandigarh"
    DADRA_AND_NAGAR_HAVELI_AND_DAMAN_AND_DIU = "Dadra and Nagar Haveli and Daman and Diu"
    DELHI = "Delhi"
    JAMMU_AND_KASHMIR = "Jammu and Kashmir"
    LADAKH = "Ladakh"
    LAKSHADWEEP = "Lakshadweep"
    PUDUCHERRY = "Puducherry"


class HypothecatedType(BaseStrEnum):
    HIRE_PURCHASE = "Hire Purchase" # Hire Purchase
    LEASE_AGREEMENT = "Lease Agreement" # Lease Agreement
    HYPOTHECATION = "Hypothecation" # Hypothecation

class EngineGearboxProtect(BaseStrEnum):
    LOW = "Low" # Low Engine and Gearbox Protection
    MEDIUM = "Medium" # Medium Engine and Gearbox Protection
    HIGH = "High" # High Engine and Gearbox Protection


class InsuredOccupation(BaseStrEnum):
    ADVOCATE = "Advocate" # Advocate
    AGRICULTURE = "Agriculture" # Agriculture
    BUSINESSMAN_LARGE = "Businessman (Large)" # Businessman (Large)
    BUSINESSMAN_MEDIUM = "Businessman (Medium)" # Businessman (Medium)
    BUSINESSMAN_SMALL = "Businessman (Small)" # Businessman (Small)
    CA = "CA" # Chartered Accountant
    CLERICAL = "Clerical" # Clerical
    EXECUTIVE_SENIOR = "Executive (Senior)" # Executive (Senior)
    EXECUTIVE_MIDDLE = "Executive (Middle)" # Executive (Middle)
    EXECUTIVE_JUNIOR = "Executive (Junior)" # Executive (Junior)
    HOUSEWIFE = "Housewife" # Housewife
    LABOUR = "Labour" # Labour
    NOT_WORKING = "Not Working" # Not Working
    RETIRED = "Retired" # Retired
    SALES = "Sales" # Sales
    SELF_EMPLOYED = "Self Employed" # Self Employed
    SHOP_OWNER = "Shop Owner" # Shop Owner
    SOFTWARE_PROFESSIONAL = "Software Professional" # Software Professional
    SERVICE = "Service" # Service
    STUDENT = "Student" # Student
    SUPERVISOR = "Supervisor" # Supervisor
    MEDICAL_PROFESSIONAL = "Medical Professional" # Medical Professional
    EDUCATION_PROFESSIONAL = "Education Professional" # Education Professional
    SECURITY_PERSONNEL = "Security Personnel" # Security Personnel
    OTHERS = "Others" # Others

class Relation(BaseStrEnum):
    AUNTY = "Aunty" # Aunty
    BROTHER = "Brother" # Brother
    DAUGHTER = "Daughter" # Daughter
    EMPLOYER = "Employer" # Employer
    FATHER = "Father" # Father
    MOTHER = "Mother" # Mother
    HUSBAND = "Husband" # Husband
    WIFE = "Wife" # Wife
    SON = "Son" # Son
    SISTER = "Sister" # Sister
    SPOUSE = "Spouse" # Spouse
    NIECE = "Niece" # Niece
    NEPHEW = "Nephew" # Nephew
    GRANDSON = "Grandson" # Grandson
    GRANDDAUGHTER = "Granddaughter" # Granddaughter
    UNCLE = "Uncle" # Uncle
    OTHER = "Other" # Other


class TaskStatus(BaseStrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    UNKNOWN = "unknown"


class TaskReturnCode(BaseStrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"
    
class PluginStatus(BaseStrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"

class TaskSystemErrorCode(BaseStrEnum):
    AUTH_CHECK_FAILED = "auth_check_failed"
    AUTHENTICATION_FAILED = "authentication_failed"
    SITE_LAUNCH_FAILED = "site_launch_failed"
    MAIN_WORKFLOW_FAILED = "main_workflow_failed"
    SOMETHING_WENT_WRONG = "something_went_wrong"


class TaskMonitorErrorCode(BaseStrEnum):
    POLLING_THRESHOLD_CROSSED = "polling_threshold_crossed"
    RUNTIME_SLA_BREACH = "runtime_sla_breach"



class MotorQuoteCoverType(BaseStrEnum):
    """Enumeration for different types of insurance covers"""
    BASIC_OD = "basic_od"
    OD_INCLUSIVE = "od_inclusive_addons_and_covers"
    BASIC_LIABILITY = "basic_liability"
    LIABILITY_INCLUSIVE = "liability_inclusive_addons_and_covers"
    TPPD = "tppd"
    PA_OWNER_DRIVER = "pa_owner_driver"
    PA_UNNAMED_PASSENGER = "pa_unnamed_passenger"
    PA_DRIVER = "pa_driver"
    NCB = "ncb"
    LEGAL_LIABILITY_PAID_DRIVER = "legal_liability_paid_driver"
    NFPP = "nfpp"
    CPA = "cpa"

    # Addons
    ROADSIDE_ASSISTANCE = "roadside_assistance"
    NIL_DEPRECIATION = "nil_depreciation"
    KEY_COVER = "key_cover"
    PERSONAL_BELONGINGS = "personal_belongings"
    CONSUMABLE_COVER = "consumable_cover"
    RETURN_TO_INVOICE = "return_to_invoice"
    INCONVENIENCE_ALLOWANCE = "inconvenience_allowance"
    TYRE_COVER = "tyre_cover"
    NCB_PROTECTION = "ncb_protection"
    RIM_DAMAGE_COVER = "rim_damage_cover"
    ENGINE_PROTECT = "engine_protect"
    ENGINE_GEARBOX_PROTECT = "engine_gearbox_protect"
    ROAD_TAX_REGISTRATION = "road_tax_and_registration_charges"
    OVERNIGHT_STAY = "overnight_stay"
    PAY_AS_YOU_GO = "pay_as_you_go"
    IMT23 = "imt23"
    IMT47 = "imt47"
    COURTESY_CAR = "courtesy_car"
    INDEMNITY_COVER = "indemnity_cover"
    MEDICAL_EXPENSES = "medical_expenses"

    OTHERS = "others"


class MotorQuoteTaxType(BaseStrEnum):
    """Enumeration for different tax types"""
    IGST = "igst"
    CGST = "cgst"
    SGST = "sgst"
    SERVICE_TAX = "service_tax"
    GST = "gst"
    SWACHH_BHARAT = "swachh_bharat"
    KRISHI_KALYAN = "krishi_kalyan"
    SALES_TAX = "sales_tax"
