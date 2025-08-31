from datetime import date
from typing import TYPE_CHECKING, Optional

import httpx
from pydantic import BaseModel, ConfigDict, EmailStr

from plugin.utils.cache_decorator import auto_cached_provider_method

from ...core.models.policy import (
    FuelType,
    InsuredType,
    Insurer,
    PolicyCategory,
    PolicyType,
    Product,
    ProductCategory,
    ProductSubType,
    ProductType,
)
from ..models import (
    PolicyExtractionObject,
    PolicyExtractionRequest,
    PolicyExtractionResponse,
)
from .abc import AbstractPolicyExtractionProvider

if TYPE_CHECKING:
    from plugin.models import Plugin

from datetime import date
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field

from ..utils import (
    break_vehicle_number,
    clean_amount,
    clean_email,
    clean_ncb,
    clean_phone,
    clean_vehicle_gvw,
    vehicle_number_to_rta,
    vehicle_number_to_state,
)

PROVIDER_MAP = {
    "68678b51df5a5abb9e504573": {
        "insurer": Insurer.CHOLA,
        "product": Product.MOTOR,
        "product_type": ProductType.COMMERCIAL,
        "product_sub_type": None,
        "policy_type": PolicyType.TP,
    },
    "68678aab8d822bc79808357e": {
        "insurer": Insurer.MAGMA,
        "product": Product.MOTOR,
        "product_type": ProductType.COMMERCIAL,
        "product_sub_type": ProductSubType.GCV,
        "policy_type": PolicyType.PACKAGE,
    },
    "68678af2df5a5abb9e504569": {
        "insurer": Insurer.SHRIRAM,
        "product": Product.MOTOR,
        "product_type": ProductType.COMMERCIAL,
        "product_sub_type": None,
        "policy_type": None,
    },
    "68676ee08d822bc79808354b": {
        "insurer": Insurer.TATA,
        "product": Product.MOTOR,
        "product_type": None,
        "product_sub_type": None,
        "policy_type": None,
    },
    "68678ac18d822bc798083584": {
        "insurer": Insurer.UIIC,
        "product": Product.MOTOR,
        "product_type": ProductType.COMMERCIAL,
        "product_sub_type": ProductSubType.GCV,
        "policy_type": PolicyType.PACKAGE,
    },
    "68678ae18d822bc79808358a": {
        "insurer": Insurer.BAJAJ,
        "product": Product.HEALTH,
        "product_type": None,
        "product_sub_type": None,
        "policy_type": None,
    },
    "68678a5d8d822bc798083570": {
        "insurer": Insurer.NIC,
        "product": Product.MOTOR,
        "product_type": ProductType.PRIVATE,
        "product_sub_type": ProductSubType.PC,
        "policy_type": PolicyType.TP,
    },
    "68678a7ddf5a5abb9e504561": {
        "insurer": Insurer.GO,
        "product": Product.MOTOR,
        "product_type": ProductType.PRIVATE,
        "product_sub_type": ProductSubType.TW,
        "policy_type": PolicyType.PACKAGE,
    },
    "68678a4bdf5a5abb9e50455b": {
        "insurer": Insurer.ICICI,
        "product": Product.MOTOR,
        "product_type": ProductType.PRIVATE,
        "product_sub_type": ProductSubType.PC,
        "policy_type": PolicyType.PACKAGE,
    },
    "68678a99df5a5abb9e504565": {
        "insurer": Insurer.SBI,
        "product": Product.MOTOR,
        "product_type": ProductType.PRIVATE,
        "product_sub_type": ProductSubType.PC,
        "policy_type": PolicyType.TP,
    },
    "68678b1adf5a5abb9e50456d": {
        "insurer": Insurer.USGI,
        "product": Product.MOTOR,
        "product_type": None,
        "product_sub_type": ProductSubType.MISC,
        "policy_type": None,
    },
    "68678b028d822bc798083592": {
        "insurer": Insurer.KTKM,
        "product": Product.MOTOR,
        "product_type": ProductType.PRIVATE,
        "product_sub_type": ProductSubType.PC,
        "policy_type": PolicyType.TP,
    },
}


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
        od_premium_fields = (
            "basic_od_premium",
            "total_od_premium",
            "total_od_add_on_premium",
        )
        return any(
            self.get(field) not in (None, 0, "0", "0.0", "0.00")
            for field in od_premium_fields
        )

    @property
    def has_tp_premium(self) -> bool:
        tp_premium_fields = (
            "basic_tp_premium",
            "total_tp_premium",
            "total_tp_add_on_premium",
        )
        return any(
            self.get(field) not in (None, 0, "0", "0.0", "0.00")
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
    def calc_vehicle_fuel_type(self) -> FuelType:
        fuel_type = self.fuel_type.lower() if self.fuel_type else None
        # return FuelType(fuel_type) if fuel_type and fuel_type is supported
        if fuel_type in FuelType.__members__:
            return FuelType[fuel_type]
        return FuelType.UNKNOWN

    @property
    def product_category(self) -> ProductCategory:
        # ProductCategory: "2W", "3W", "4W", "6W"
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
        if self.policy_type.lower() == "third party":
            policy_type = PolicyType.TP

        elif self.policy_type.lower() == "package":
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
        s = (self.fuel_type or "").strip()
        if not s:
            return None

        # Try by enum name (case and space insensitive)
        name_key = s.upper().replace(" ", "_")
        if name_key in FuelType.__members__:
            return FuelType[name_key]

        # Try by enum value (case insensitive)
        s_lower = s.lower()
        for m in FuelType:
            if m.value.lower() == s_lower:
                return m

        # Normalize and map common aliases
        s_norm = "".join(ch for ch in s_lower if ch.isalnum())
        alias_map = {
            "petrol": FuelType.PETROL,
            "gasoline": FuelType.PETROL,
            "diesel": FuelType.DIESEL,
            "cng": FuelType.CNG,
            "lpg": FuelType.LPG,
            "ev": FuelType.ELECTRIC,
            "electric": FuelType.ELECTRIC,
            "bev": FuelType.ELECTRIC,
            "phev": FuelType.HYBRID_ELECTRIC,
            "hybrid": FuelType.HYBRID_ELECTRIC,
            "hybridelectric": FuelType.HYBRID_ELECTRIC,
            "h2": FuelType.HYDROGEN,
            "hydrogen": FuelType.HYDROGEN,
        }
        return alias_map.get(s_norm, None)

    @property
    def last_policy_available(self) -> bool:
        # Check if the last policy is available
        return (
            self.previous_insurer_name is not None
            or self.previous_policy_number is not None
        )


class Novoup(AbstractPolicyExtractionProvider):
    URL = "https://coral-app-aqae8.ondigitalocean.app/api/providers/extract"

    def __init__(self, plugin: "Plugin"):
        super().__init__(plugin)

    @auto_cached_provider_method()
    def run(
        self, plugin: "Plugin", request: PolicyExtractionRequest
    ) -> PolicyExtractionResponse:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                self.URL,
                files={"pdf": request.file},
            )
            response.raise_for_status()

        provider_id = response.json()["providerID"]
        extracted_data = response.json().get("extractedData", {})
        extract = NovoupExtractionResponse(**extracted_data)
        provider_info = PROVIDER_MAP.get(provider_id, {})

        obj = PolicyExtractionObject(
            insurer=provider_info.get("insurer"),
            product=provider_info.get("product"),
            product_type=(
                ProductType.PRIVATE
                if provider_info.get("product_sub_type")
                in [ProductSubType.PC, ProductSubType.TW]
                else ProductType.COMMERCIAL
            ),
            product_sub_type=provider_info.get("product_sub_type"),
            product_category=extract.product_category,
            policy_category=extract.calc_policy_category(provider_info),
            policy_type=extract.calc_policy_type(provider_info),
            vehicle_transfer_of_ownership=None,
            vehicle_registration_state=vehicle_number_to_state(extract.vehicle_number),
            make=extract.make,
            model=extract.model,
            variant=None,
            transmission=None,
            policy_start_date=extract.start_date,
            policy_expiry_date=extract.end_date,
            business_type=None,
            body_type=None,
            registration_number_1=break_vehicle_number(extract.vehicle_number)[0],
            registration_number_2=break_vehicle_number(extract.vehicle_number)[1],
            registration_number_3=break_vehicle_number(extract.vehicle_number)[2],
            registration_number_4=break_vehicle_number(extract.vehicle_number)[3],
            vehicle_registration_date=extract.registration_date,
            make_month=None,
            make_year=extract.manufacturing_year,
            vehicle_fuel_type=extract.vehicle_fuel_type,
            vehicle_engine_number=extract.engine_number,
            vehicle_chassis_number=extract.chassis_number,
            vehicle_seating_capacity=extract.seating_capacity,
            vehicle_cc=extract.engine_capacity_cc,
            vehicle_puc_available=True,
            transfer_vehicle_ncb=None,
            insured_type=(
                InsuredType.INDIVIDUAL
                if extract.business_type
                and extract.business_type.lower() == "individual"
                else None
            ),
            insured_title=None,
            insured_name=extract.customer_name,
            insured_address=extract.customer_address,
            insured_pincode=None,
            insured_state=None,
            insured_district=None,
            gstin=None,
            ckyc_number=None,
            insured_mobile=clean_phone(extract.customer_phone),
            insured_email=clean_email(extract.customer_email),
            insured_dob=None,
            insured_occupation=None,
            insured_aadhar_no=None,
            insured_pan_no=None,
            vehicle_rta=vehicle_number_to_rta(extract.vehicle_number, extract.rto_code),
            vehicle_idv=clean_amount(extract.vehicle_idv),
            vehicle_fuel_outbuild=None,
            vehicle_fuel_outbuild_cost=None,
            vehicle_hypothecated=None,
            hypothecated_type=None,
            hypothecated_with=None,
            hypothecated_state=None,
            hypothecated_district=None,
            od_discount_percent=None,
            limit_tppd=None,
            legal_libility_to_paid_driver=None,
            pa_cover_unnammed_person_count=None,
            pa_cover_unnammed_person=None,
            pa_cover_driver_count=None,
            pa_cover_driver=None,
            nfpp_cover=None,
            cpa_optout=None,
            cpa_cover_period=None,
            cpa_has_valid_dl=None,
            cpa_insurer=None,
            cpa_policy_number=None,
            cpa_policy_from=None,
            cpa_policy_to=None,
            nominiee_name=None,
            nominiee_relation=None,
            nominiee_age=None,
            appointee_name=None,
            appointee_relation=None,
            # No Addons Available
            last_policy_available=extract.last_policy_available,
            last_insurer=None,  # TODO map extract.previous_insurer_name to Enum
            last_policy_number=extract.previous_policy_number,
            last_policy_from=None,
            last_policy_to=extract.previous_policy_end_date
            or extract.prev_policy_expiry,
            last_policy_ncb_percent=clean_ncb(extract.previous_ncb),
            last_policy_claim=None,
            last_policy_claim_count=None,
            last_policy_type=None,
            last_policy_category=None,
            vehicle_gvw=clean_vehicle_gvw(extract.gross_vehicle_weight),
            misc_vehicle_class=None,
            # policy only details
            policy_number=extract.policy_number,
            issue_date=extract.issue_date,
            od_start_date=extract.od_start_date,
            od_end_date=extract.od_end_date,
            tp_start_date=extract.tp_start_date,
            tp_end_date=extract.tp_end_date,
            sum_insured=clean_amount(extract.sum_insured),
            basic_od_premium=clean_amount(extract.basic_od_premium),
            total_od_premium=clean_amount(extract.total_od_premium),
            total_od_add_on_premium=clean_amount(extract.total_od_add_on_premium),
            basic_tp_premium=clean_amount(extract.basic_tp_premium),
            total_tp_premium=clean_amount(extract.total_tp_premium),
            total_tp_add_on_premium=clean_amount(extract.total_tp_add_on_premium),
            net_premium=clean_amount(extract.net_premium),
            taxes=clean_amount(extract.taxes),
            taxes_rate=clean_ncb(extract.taxes_rate),
            gross_discount=clean_amount(extract.gross_discount),
            total_premium=clean_amount(extract.total_premium),
            ncb=clean_ncb(extract.ncb),
            broker_name=extract.broker_name,
            broker_email=clean_email(extract.broker_email),
            broker_code=extract.broker_code,
        )
        return PolicyExtractionResponse(
            is_success=True,
            message="Policy extracted successfully",
            response=obj
        )
