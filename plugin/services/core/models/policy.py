from datetime import date
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class Insurer(StrEnum):
    UIIC = "UIIC"  # United India Insurance Company
    NIC = "NIC"  # National Insurance Company
    TNI = "TNI"  # The New India Assurance Company
    SBI = "SBI"  # State Bank of India
    KTKM = "KTKM"  # Kotak Mahindra General Insurance
    HDFC = "HDFC"  # HDFC ERGO General Insurance
    ICICI = "ICICI"  # ICICI Lombard General Insurance
    GO = "GO"  # Go Digit General Insurance
    RGCL = "RGCL"  # Reliance General Insurance
    TATA = "TATA"  # TATA AIG General Insurance
    FUTURE = "FUTURE"  # Future Generali India Insurance
    ROYAL = "ROYAL"  # Royal Sundaram General Insurance
    BAJAJ = "BAJAJ"  # Bajaj Allianz General Insurance
    OR = "OR"  # Oriental Insurance Company
    LIB = "LIB"  # Liberty General Insurance
    USGI = "USGI"  # Universal Sompo General Insurance
    CHOLA = "CHOLA"  # Cholamandalam MS General Insurance
    MAGMA = "MAGMA"  # Magma General Insurance
    SHRIRAM = "SHRIRAM"  # Shriram General Insurance


class Product(StrEnum):
    MOTOR = "Motor"  # Motor Insurance
    HEALTH = "Health"  # Health Insurance


class ProductType(StrEnum):
    PRIVATE = "Private"  # Private Vehicle Insurance
    COMMERCIAL = "Commercial"  # Commercial Vehicle Insurance


class ProductSubType(StrEnum):
    GCV = "GCV"  # Goods Carrying Vehicle
    PCV = "PCV"  # Passenger Carrying Vehicle
    TW = "TW"  # Two Wheeler
    PC = "PC"  # Private Car
    MISC = "MISC"  # Miscellaneous Vehicle


class ProductCategory(StrEnum):
    DUO = "2W"  # Two Wheeler
    TRI = "3W"  # Three Wheeler
    QUAD = "4W"  # Four Wheeler
    HEX = "6W"  # Six Wheeler
    OCTA = "8W"  # Eight Wheeler
    DEC = "10W"  # Ten Wheeler
    DUODEC = "12W"  # Twelve Wheeler


class PolicyCategory(StrEnum):
    PACKAGE_1_1 = "1+1"  # Package Policy (1+1)
    PACKAGE_1_3 = "1+3"  # Package Policy (1+3)
    PACKAGE_1_5 = "1+5"  # Package Policy (1+5)
    PACKAGE_3_3 = "3+3"  # Package Policy (3+3)
    PACKAGE_5_5 = "5+5"  # Package Policy (5+5)
    SAOD_1 = "1+0"  # Standalone Own Damage
    SAOD_2 = "2+0"  # Standalone Own Damage (2 + 0)
    SAOD_3 = "3+0"  # Standalone Own Damage (3 + 0)
    SATP_1 = "0+1"  # Standalone Third Party (0 + 1)
    SATP_3 = "0+3"  # Standalone Third Party (0 + 3)


class PolicyType(StrEnum):
    PACKAGE = "Package"  # Package Policy
    OD = "OD"  # Own Damage Policy
    TP = "TP"  # Third Party Policy
    BUNDLED = "Bundled"  # Bundled Policy


class Transmission(StrEnum):
    MANUAL = "Manual"  # Manual Transmission
    AUTOMATIC = "Automatic"  # Automatic Transmission


class BusinessType(StrEnum):
    NEW = "New"  # New Business
    RENEWAL = "Renewal"  # Renewal Business


class FuelType(StrEnum):
    PETROL = "Petrol"  # Petrol
    DIESEL = "Diesel"  # Diesel
    CNG = "CNG"  # Compressed Natural Gas
    LPG = "LPG"  # Liquefied Petroleum Gas
    ELECTRIC = "Electric"  # Electric
    HYBRID_ELECTRIC = "Hybrid Electric"  # Hybrid Electric
    HYDROGEN = "Hydrogen"  # Hydrogen


class InsuredType(StrEnum):
    INDIVIDUAL = "Individual"  # Individual
    CORPORATE = "Corporate"  # Corporate


class InsuredTitle(StrEnum):
    MR = "Mr"  # Mister
    MRS = "Mrs"  # Misses
    MS = "Ms"  # Miss
    MISS = "Miss"  # Miss
    OTHER = "Other"  # Other


class State(StrEnum):
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
    DADRA_AND_NAGAR_HAVELI_AND_DAMAN_AND_DIU = (
        "Dadra and Nagar Haveli and Daman and Diu"
    )
    DELHI = "Delhi"
    JAMMU_AND_KASHMIR = "Jammu and Kashmir"
    LADAKH = "Ladakh"
    LAKSHADWEEP = "Lakshadweep"
    PUDUCHERRY = "Puducherry"


class HypothecatedType(StrEnum):
    HIRE_PURCHASE = "Hire Purchase"  # Hire Purchase
    LEASE_AGREEMENT = "Lease Agreement"  # Lease Agreement
    HYPOTHECATION = "Hypothecation"  # Hypothecation


class EngineGearboxProtect(StrEnum):
    LOW = "Low"  # Low Engine and Gearbox Protection
    MEDIUM = "Medium"  # Medium Engine and Gearbox Protection
    HIGH = "High"  # High Engine and Gearbox Protection


class InsuredOccupation(StrEnum):
    ADVOCATE = "Advocate"  # Advocate
    AGRICULTURE = "Agriculture"  # Agriculture
    BUSINESSMAN_LARGE = "Businessman (Large)"  # Businessman (Large)
    BUSINESSMAN_MEDIUM = "Businessman (Medium)"  # Businessman (Medium)
    BUSINESSMAN_SMALL = "Businessman (Small)"  # Businessman (Small)
    CA = "CA"  # Chartered Accountant
    CLERICAL = "Clerical"  # Clerical
    EXECUTIVE_SENIOR = "Executive (Senior)"  # Executive (Senior)
    EXECUTIVE_MIDDLE = "Executive (Middle)"  # Executive (Middle)
    EXECUTIVE_JUNIOR = "Executive (Junior)"  # Executive (Junior)
    HOUSEWIFE = "Housewife"  # Housewife
    LABOUR = "Labour"  # Labour
    NOT_WORKING = "Not Working"  # Not Working
    RETIRED = "Retired"  # Retired
    SALES = "Sales"  # Sales
    SELF_EMPLOYED = "Self Employed"  # Self Employed
    SHOP_OWNER = "Shop Owner"  # Shop Owner
    SOFTWARE_PROFESSIONAL = "Software Professional"  # Software Professional
    SERVICE = "Service"  # Service
    STUDENT = "Student"  # Student
    SUPERVISOR = "Supervisor"  # Supervisor
    MEDICAL_PROFESSIONAL = "Medical Professional"  # Medical Professional
    EDUCATION_PROFESSIONAL = "Education Professional"  # Education Professional
    SECURITY_PERSONNEL = "Security Personnel"  # Security Personnel
    OTHERS = "Others"  # Others


class Relation(StrEnum):
    AUNTY = "Aunty"  # Aunty
    BROTHER = "Brother"  # Brother
    DAUGHTER = "Daughter"  # Daughter
    EMPLOYER = "Employer"  # Employer
    FATHER = "Father"  # Father
    MOTHER = "Mother"  # Mother
    HUSBAND = "Husband"  # Husband
    WIFE = "Wife"  # Wife
    SON = "Son"  # Son
    SISTER = "Sister"  # Sister
    SPOUSE = "Spouse"  # Spouse
    NIECE = "Niece"  # Niece
    NEPHEW = "Nephew"  # Nephew
    GRANDSON = "Grandson"  # Grandson
    GRANDDAUGHTER = "Granddaughter"  # Granddaughter
    UNCLE = "Uncle"  # Uncle
    OTHER = "Other"  # Other


class PolicyRequest(BaseModel):
    insurer: Optional[Insurer] = Field(
        default=None,
        description="Insurer for which the policy is requested",
    )
    product: Optional[Product] = Field(
        default=None,
        description="Product for which the policy is requested",
    )
    product_type: Optional[ProductType] = Field(
        default=None,
        description="Type of the product for which the policy is requested",
    )
    product_sub_type: Optional[ProductSubType] = Field(
        default=None,
        description="Sub-type of the product for which the policy is requested",
    )
    product_category: Optional[ProductCategory] = Field(
        default=None,
        description="Category of the product for which the policy is requested",
    )
    policy_category: Optional[PolicyCategory] = Field(
        default=None,
        description="Category of the policy for which the request is made",
    )
    policy_type: Optional[PolicyType] = Field(
        default=None,
        description="Type of the policy for which the request is made",
    )
    vehicle_transfer_of_ownership: Optional[bool] = Field(
        default=None,
        description="Indicates if the vehicle's ownership transferred",
    )
    vehicle_registration_state: Optional[State] = Field(
        default=None,
        description="State where the vehicle is registered",
    )
    make: Optional[str] = Field(
        default=None,
        description="Make of the vehicle",
    )
    model: Optional[str] = Field(
        default=None,
        description="Model of the vehicle",
    )
    variant: Optional[str] = Field(
        default=None,
        description="Variant of the vehicle",
    )
    transmission: Optional[Transmission] = Field(
        default=None,
        description="Transmission type of the vehicle",
    )
    policy_start_date: Optional[date] = Field(
        default=None,
        description="Start date of the policy in YYYY-MM-DD format",
    )
    policy_expiry_date: Optional[date] = Field(
        default=None,
        description="Expiry date of the policy in YYYY-MM-DD format",
    )
    business_type: Optional[BusinessType] = Field(
        default=None,
        description="Type of business for which the policy is requested",
    )
    body_type: Optional[str] = Field(
        default=None,
        description="Body type of the vehicle",
    )
    registration_number_1: Optional[str] = Field(
        default=None,
        description="First part of the vehicle's registration number",
    )
    registration_number_2: Optional[str] = Field(
        default=None,
        description="Second part of the vehicle's registration number",
    )
    registration_number_3: Optional[str] = Field(
        default=None,
        description="Third part of the vehicle's registration number",
    )
    registration_number_4: Optional[str] = Field(
        default=None,
        description="Fourth part of the vehicle's registration number",
    )
    vehicle_registration_date: Optional[date] = Field(
        default=None,
        description="Date of vehicle registration in YYYY-MM-DD format",
    )
    make_month: Optional[int] = Field(
        default=None,
        ge=1,
        le=12,
        description="Month of the vehicle's make (1-12)",
    )
    make_year: Optional[int] = Field(
        default=None,
        ge=1900,
        le=2100,
        description="Year of the vehicle's make (e.g., 2023)",
    )
    vehicle_fuel_type: Optional[FuelType] = Field(
        default=None,
        description="Fuel type of the vehicle",
    )
    vehicle_engine_number: Optional[str] = Field(
        default=None,
        description="Engine number of the vehicle",
    )
    vehicle_chassis_number: Optional[str] = Field(
        default=None,
        description="Chassis number of the vehicle",
    )
    vehicle_seating_capacity: Optional[int] = Field(
        default=None,
        ge=1,
        description="Seating capacity of the vehicle",
    )
    vehicle_cc: Optional[int] = Field(
        default=None,
        description="Cubic capacity of the vehicle's engine",
    )
    vehicle_puc_available: Optional[bool] = Field(
        default=None,
        description="Indicates if the vehicle has a valid PUC certificate",
    )
    transfer_vehicle_ncb: Optional[bool] = Field(
        default=None,
        description="Indicates if the vehicle's NCB (No Claim Bonus) is transferred",
    )
    insured_type: Optional[InsuredType] = Field(
        default=None,
        description="Type of the insured person (individual, company, etc.)",
    )
    insured_title: Optional[InsuredTitle] = Field(
        default=None,
        description="Title of the insured person (Mr., Mrs., etc.)",
    )
    insured_name: Optional[str] = Field(
        default=None,
        description="Full name of the insured person",
    )
    insured_address: Optional[str] = Field(
        default=None,
        description="Address of the insured person",
    )
    insured_pincode: Optional[int] = Field(
        default=None,
        description="Pincode of the insured person's address",
    )
    insured_state: Optional[State] = Field(
        default=None,
        description="State of the insured person's address",
    )
    insured_district: Optional[str] = Field(
        default=None,
        description="District of the insured person's address",
    )
    gstin: Optional[str] = Field(
        default=None,
        description="GSTIN of the insured person (if applicable)",
    )
    ckyc_number: Optional[str] = Field(
        default=None,
        description="CKYC number of the insured person (if applicable)",
    )
    insured_mobile: Optional[str] = Field(
        default=None,
        description="Mobile number of the insured person",
    )
    insured_email: Optional[str] = Field(
        default=None,
        description="Email address of the insured person",
    )
    insured_dob: Optional[date] = Field(
        default=None,
        description="Date of birth of the insured person in YYYY-MM-DD format",
    )
    insured_occupation: Optional[InsuredOccupation] = Field(
        default=None,
        description="Occupation of the insured person",
    )
    insured_aadhar_no: Optional[str] = Field(
        default=None,
        pattern=r"^\d{12}$",
        description="Aadhar number of the insured person (if applicable)",
    )
    insured_pan_no: Optional[str] = Field(
        default=None,
        pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]$",
        description="PAN number of the insured person (if applicable)",
    )
    vehicle_rta: Optional[str] = Field(
        default=None,
        description="RTA (Regional Transport Authority) of the vehicle",
    )
    vehicle_idv: Optional[int] = Field(
        default=None,
        ge=0,
        description="Insured Declared Value (IDV) of the vehicle",
    )
    vehicle_fuel_outbuild: Optional[bool] = Field(
        default=None,
        description="Indicates if the vehicle has an outbuilding for fuel",
    )
    vehicle_fuel_outbuild_cost: Optional[int] = Field(
        default=None,
        ge=0,
        description="Cost of the vehicle's outbuilding for fuel",
    )
    vehicle_hypothecated: Optional[bool] = Field(
        default=None,
        description="Indicates if the vehicle is hypothecated",
    )
    hypothecated_type: Optional[HypothecatedType] = Field(
        default=None,
        description="Type of hypothecation for the vehicle",
    )
    hypothecated_with: Optional[str] = Field(
        default=None,
        description="Name of the entity with which the vehicle is hypothecated",
    )
    hypothecated_state: Optional[State] = Field(
        default=None,
        description="State where the vehicle is hypothecated",
    )
    hypothecated_district: Optional[str] = Field(
        default=None,
        description="District where the vehicle is hypothecated",
    )
    od_discount_percent: Optional[int] = Field(
        default=None,
        description="OD (Own Damage) discount percentage",
    )
    limit_tppd: Optional[bool] = Field(
        default=None,
        description="Indicates if there is a limit on Third Party Property Damage (TPPD)",
    )
    legal_libility_to_paid_driver: Optional[int] = Field(
        default=None,
        ge=0,
        description="Legal liability amount to be paid to the driver",
    )
    pa_cover_unnammed_person_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Count of unnamed persons covered under PA (Personal Accident)",
    )
    pa_cover_unnammed_person: Optional[int] = Field(
        default=None,
        description="Sum insured for Personal Accident (PA) cover for unnamed persons",
    )
    pa_cover_driver_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Count of drivers covered under PA (Personal Accident)",
    )
    pa_cover_driver: Optional[int] = Field(
        default=None,
        description="Sum insured for Personal Accident (PA) cover for the driver",
    )
    nfpp_cover: Optional[bool] = Field(
        default=None,
        description="Indicates if Non-Fare Paying Passengers (NFPP) cover is included",
    )
    cpa_optout: Optional[bool] = Field(
        default=None,
        description="Indicates if the customer has opted out of the Compulsory Personal Accident (CPA) cover",
    )
    cpa_cover_period: Optional[int] = Field(
        default=None,
        description="Period for which the Compulsory Personal Accident (CPA) cover is applicable in YYYY-MM-DD format",
    )
    cpa_has_valid_dl: Optional[bool] = Field(
        default=None,
        description="Indicates if the customer has a valid driving license for the CPA cover",
    )
    cpa_insurer: Optional[Insurer] = Field(
        default=None,
        description="Insurer for the Compulsory Personal Accident (CPA) cover",
    )
    cpa_policy_number: Optional[str] = Field(
        default=None,
        description="Policy number for the Compulsory Personal Accident (CPA) cover",
    )
    cpa_policy_from: Optional[date] = Field(
        default=None,
        description="Start date of the Compulsory Personal Accident (CPA) cover in YYYY-MM-DD format",
    )
    cpa_policy_to: Optional[date] = Field(
        default=None,
        description="End date of the Compulsory Personal Accident (CPA) cover in YYYY-MM-DD format",
    )
    nominiee_name: Optional[str] = Field(
        default=None,
        description="Name of the nominee for the Compulsory Personal Accident (CPA) cover",
    )
    nominiee_relation: Optional[Relation] = Field(
        default=None,
        description="Relation of the nominee to the insured person",
    )
    nominiee_age: Optional[int] = Field(
        default=None,
        ge=0,
        description="Age of the nominee",
    )
    appointee_name: Optional[str] = Field(
        default=None, description="Name of the appointee"
    )
    appointee_relation: Optional[Relation] = Field(
        default=None,
        description="Relation of the appointee to the insured person",
    )
    addon_roadside_assistance: Optional[bool] = Field(
        default=None,
        description="Indicates if roadside assistance is included as an addon",
    )
    addon_nil_depreciation_cover: Optional[bool] = Field(
        default=None,
        description="Indicates if nil depreciation cover is included as an addon",
    )
    addon_key_cover: Optional[bool] = Field(
        default=None,
        description="Indicates if key cover is included as an addon",
    )
    addon_key_cover_sum: Optional[int] = Field(
        default=None,
        ge=0,
        description="Sum insured for key cover addon",
    )
    addon_personal_belongings: Optional[int] = Field(
        default=None,
        ge=0,
        description="Sum insured for personal belongings addon",
    )
    addon_consumable_cover: Optional[bool] = Field(
        default=None,
        description="Indicates if consumable cover is included as an addon",
    )
    addon_return_to_invoice: Optional[bool] = Field(
        default=None,
        description="Indicates if return to invoice cover is included as an addon",
    )
    addon_inconvenience_allowance: Optional[bool] = Field(
        default=None,
        description="Indicates if inconvenience allowance is included as an addon",
    )
    addon_tyre_cover: Optional[bool] = Field(
        default=None,
        description="Indicates if tyre cover is included as an addon",
    )
    addon_tyre_cover_sum: Optional[int] = Field(
        default=None,
        ge=0,
        description="Sum insured for tyre cover addon",
    )
    addon_ncb_protection: Optional[bool] = Field(
        default=None,
        description="Indicates if NCB (No Claim Bonus) protection is included",
    )
    addon_rim_damage_cover: Optional[bool] = Field(
        default=None,
        description="Indicates if rim damage cover is included as an addon",
    )
    addon_rim_damage_cover_sum: Optional[int] = Field(
        default=None,
        ge=0,
        description="Sum insured for rim damage cover addon",
    )
    addon_roadside_assistance: Optional[bool] = Field(
        default=None,
        description="Indicates if roadside assistance is included as an addon",
    )
    addon_engine_protect: Optional[bool] = Field(
        default=None,
        description="Indicates if engine protection is included as an addon",
    )
    addon_engine_gearbox_protect: Optional[EngineGearboxProtect] = Field(
        default=None,
        description="Indicates if engine and gearbox protection is included as an addon",
    )
    addon_nil_depreciation_cover: Optional[bool] = Field(
        default=None,
        description="Indicates if nil depreciation cover is included as an addon",
    )
    addon_consumable_cover: Optional[bool] = Field(
        default=None,
        description="Indicates if consumable cover is included as an addon",
    )
    addon_road_tax_and_registration_charges: Optional[bool] = Field(
        default=None,
        description="Indicates if road tax and registration charges are included as an addon",
    )
    addon_road_tax_and_registration_charges_sum: Optional[int] = Field(
        default=None,
        ge=0,
        description="Sum insured for road tax and registration charges addon",
    )
    addon_overnight_stay: Optional[bool] = Field(
        default=None,
        description="Indicates if overnight stay cover is included as an addon",
    )
    addon_pay_as_you_go: Optional[bool] = Field(
        default=None,
        description="Indicates if pay-as-you-go cover is included as an addon",
    )
    addon_imt23: Optional[bool] = Field(
        default=None,
        description="Indicates if IMT 23 cover is included as an addon",
    )
    addon_imt47: Optional[bool] = Field(
        default=None,
        description="Indicates if IMT 47 cover is included as an addon",
    )
    addon_courtesy_car: Optional[bool] = Field(
        default=None,
        description="Indicates if courtesy car cover is included as an addon",
    )
    addon_courtesy_car_days: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of days for which courtesy car is provided as an addon",
    )
    addon_indemnity_cover: Optional[bool] = Field(
        default=None,
        description="Indicates if indemnity cover is included as an addon",
    )
    last_policy_available: Optional[bool] = Field(
        default=None,
        description="Indicates if the last policy details are available",
    )
    last_insurer: Optional[Insurer] = Field(
        default=None,
        description="Insurer of the last policy",
    )
    last_policy_number: Optional[str] = Field(
        default=None,
        description="Policy number of the last policy",
    )
    last_policy_from: Optional[date] = Field(
        default=None,
        description="Start date of the last policy in YYYY-MM-DD format",
    )
    last_policy_to: Optional[date] = Field(
        default=None,
        description="End date of the last policy in YYYY-MM-DD format",
    )
    last_policy_ncb_percent: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="No Claim Bonus (NCB) percentage of the last policy",
    )
    last_policy_claim: Optional[bool] = Field(
        default=None,
        description="Indicates if there were any claims in the last policy",
    )
    last_policy_claim_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Count of claims in the last policy",
    )
    last_policy_type: Optional[PolicyType] = Field(
        default=None,
        description="Type of the last policy",
    )
    last_policy_category: Optional[PolicyCategory] = Field(
        default=None,
        description="Category of the last policy",
    )
    vehicle_gvw: Optional[int] = Field(
        default=None,
        ge=0,
        description="Gross Vehicle Weight (GVW) of the vehicle in kilograms",
    )
    customer_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the customer",
    )
    misc_vehicle_class: Optional[str] = Field(
        default=None,
        description="Miscellaneous vehicle class if applicable",
    )
