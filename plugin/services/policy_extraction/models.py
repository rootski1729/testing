from datetime import date
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

from ..core.models.base import BasePluginResponse
from ..core.models.policy import PolicyRequest


class PolicyExtractionRequest(BaseModel):
    # Tuple of (filename, bytes_content, content_type)
    file: Tuple[str, bytes, str]


class PolicyExtractionObject(PolicyRequest):
    policy_number: Optional[str] = Field(
        default=None,
        description="Policy number of the issued policy",
    )
    issue_date: Optional[date] = Field(
        default=None,
        description="Issue date of the issued policy in YYYY-MM-DD format",
    )
    od_start_date: Optional[date] = Field(
        default=None,
        description="Start date of the OD cover in YYYY-MM-DD format",
    )
    od_end_date: Optional[date] = Field(
        default=None,
        description="End date of the OD cover in YYYY-MM-DD format",
    )
    tp_start_date: Optional[date] = Field(
        default=None,
        description="Start date of the TP cover in YYYY-MM-DD format",
    )
    tp_end_date: Optional[date] = Field(
        default=None,
        description="End date of the TP cover in YYYY-MM-DD format",
    )
    sum_insured: Optional[float] = Field(
        default=None,
        description="Sum insured amount in INR",
    )
    basic_od_premium: Optional[float] = Field(
        default=None,
        description="Basic OD premium amount in INR",
    )
    total_od_premium: Optional[float] = Field(
        default=None,
        description="Total OD premium amount in INR",
    )
    total_od_add_on_premium: Optional[float] = Field(
        default=None,
        description="Total OD add-on premium amount in INR",
    )
    basic_tp_premium: Optional[float] = Field(
        default=None,
        description="Basic TP premium amount in INR",
    )
    total_tp_premium: Optional[float] = Field(
        default=None,
        description="Total TP premium amount in INR",
    )
    total_tp_add_on_premium: Optional[float] = Field(
        default=None,
        description="Total TP add-on premium amount in INR",
    )
    net_premium: Optional[float] = Field(
        default=None,
        description="Net premium amount in INR",
    )
    taxes: Optional[float] = Field(
        default=None,
        description="Taxes amount in INR",
    )
    taxes_rate: Optional[float] = Field(
        default=None,
        description="Taxes rate in percentage",
    )
    gross_discount: Optional[float] = Field(
    default=None,
    description="Gross discount amount in INR",
    )
    total_premium: Optional[float] = Field(
        default=None,
        description="Total premium amount in INR",
    )
    ncb: Optional[float] = Field(
        default=None,
        description="No Claim Bonus (NCB) amount in INR",
    )
    broker_name: Optional[str] = Field(
        default=None,
        description="Name of the broker",
    )
    broker_email: Optional[str] = Field(
        default=None,
        description="Email of the broker",
    )
    broker_code: Optional[str] = Field(
        default=None,
        description="Code of the broker",
    )


class PolicyExtractionResponse(BasePluginResponse):
    response: PolicyExtractionObject
