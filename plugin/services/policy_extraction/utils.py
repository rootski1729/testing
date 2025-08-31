import re
from typing import Optional

STATE_CODE_MAP = {
    "ANDHRA PRADESH": "Andhra Pradesh",
    "AP": "Andhra Pradesh",
    "ARUNACHAL PRADESH": "Arunachal Pradesh",
    "AR": "Arunachal Pradesh",
    "ASSAM": "Assam",
    "AS": "Assam",
    "BIHAR": "Bihar",
    "BR": "Bihar",
    "CHHATTISGARH": "Chhattisgarh",
    "CG": "Chhattisgarh",
    "GOA": "Goa",
    "GA": "Goa",
    "GUJARAT": "Gujarat",
    "GJ": "Gujarat",
    "HARYANA": "Haryana",
    "HR": "Haryana",
    "HIMACHAL PRADESH": "Himachal Pradesh",
    "HP": "Himachal Pradesh",
    "JHARKHAND": "Jharkhand",
    "JH": "Jharkhand",
    "KARNATAKA": "Karnataka",
    "KA": "Karnataka",
    "KERALA": "Kerala",
    "KL": "Kerala",
    "MADHYA PRADESH": "Madhya Pradesh",
    "MP": "Madhya Pradesh",
    "MAHARASHTRA": "Maharashtra",
    "MH": "Maharashtra",
    "MANIPUR": "Manipur",
    "MN": "Manipur",
    "MEGHALAYA": "Meghalaya",
    "ML": "Meghalaya",
    "MIZORAM": "Mizoram",
    "MZ": "Mizoram",
    "NAGALAND": "Nagaland",
    "NL": "Nagaland",
    "ODISHA": "Odisha",
    "OR": "Odisha",
    "ORISSA": "Odisha",  # Old name
    "PUNJAB": "Punjab",
    "PB": "Punjab",
    "RAJASTHAN": "Rajasthan",
    "RJ": "Rajasthan",
    "SIKKIM": "Sikkim",
    "SK": "Sikkim",
    "TAMIL NADU": "Tamil Nadu",
    "TN": "Tamil Nadu",
    "TELANGANA": "Telangana",
    "TS": "Telangana",
    "TG": "Telangana",
    "TRIPURA": "Tripura",
    "TR": "Tripura",
    "UTTAR PRADESH": "Uttar Pradesh",
    "UP": "Uttar Pradesh",
    "UTTARAKHAND": "Uttarakhand",
    "UR": "Uttarakhand",
    "UK": "Uttarakhand",
    "WEST BENGAL": "West Bengal",
    "WB": "West Bengal",
    # Union Territories
    "ANDAMAN AND NICOBAR ISLANDS": "Andaman and Nicobar Islands",
    "AN": "Andaman and Nicobar Islands",
    "CHANDIGARH": "Chandigarh",
    "CH": "Chandigarh",
    "DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "Dadra and Nagar Haveli and Daman and Diu",
    "DADRA AND NAGAR HAVELI": "Dadra and Nagar Haveli and Daman and Diu",
    "DAMAN AND DIU": "Dadra and Nagar Haveli and Daman and Diu",
    "DN": "Dadra and Nagar Haveli and Daman and Diu",
    "DD": "Dadra and Nagar Haveli and Daman and Diu",
    "DELHI": "Delhi",
    "DL": "Delhi",
    "JAMMU AND KASHMIR": "Jammu and Kashmir",
    "JK": "Jammu and Kashmir",
    "LADAKH": "Ladakh",
    "LA": "Ladakh",
    "LAKSHADWEEP": "Lakshadweep",
    "LD": "Lakshadweep",
    "PUDUCHERRY": "Puducherry",
    "PONDICHERRY": "Puducherry",  # Old name
    "PY": "Puducherry",
}


def state_code_to_state(state_code: str) -> Optional[str]:
    state_code = state_code.upper()
    return STATE_CODE_MAP.get(state_code)


def vehicle_number_to_state(vehicle_number: str) -> Optional[str]:
    # Extract the state code from the vehicle number
    # Assuming the state code is the first two characters of the vehicle number

    # remove space and uppercase and special chars
    r1, r2, r3, r4 = break_vehicle_number(vehicle_number) or (None, None, None, None)

    if r2 == "BH":  # Bharat Series
        return None

    state_code = r1
    return state_code_to_state(state_code)


def break_vehicle_number(vehicle_number: str) -> Optional[tuple[str, str, str, str]]:
    s = re.sub(r"[^A-Za-z0-9]", "", (vehicle_number or "")).upper()
    s = re.sub(r"^IND(?=[A-Z0-9])", "", s)
    m = re.fullmatch(r"(\d{2})BH(\d{4})([A-Z]{1,2})", s)
    if m:
        return m.group(1), "BH", m.group(2), m.group(3)
    m = re.fullmatch(r"([A-Z]{2})(\d{2})([A-Z]{1,3})(\d{4})", s)
    return m.groups() if m else None


def clean_phone(s: str, default_cc: str = "91") -> str:
    if not s:
        return None
    d = re.sub(r"\D+", "", s or "")
    d = re.sub(r"^00", "", d)
    if len(d) < 10:
        return None
    sub = d[-10:]
    cc = d[:-10].lstrip("0") or default_cc
    return f"+{cc} {sub}"


import re
from email.utils import parseaddr

EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$"
)


def clean_email(s: str | None) -> str | None:
    if not s:
        return None
    a = parseaddr(s)[1] or s
    a = re.sub(r"[\u200B-\u200D\uFEFF\u2060]", "", a).strip()
    if "@" not in a:
        a = re.sub(r"\s*(?:\(|\[)?at(?:\)|\])\s*", "@", a, flags=re.I)
        a = re.sub(r"\s*(?:\(|\[)?dot(?:\)|\])\s*", ".", a, flags=re.I)
    if "@" not in a:
        return None
    try:
        local, domain = map(str.strip, a.rsplit("@", 1))
    except ValueError:
        return None
    local = re.sub(r"\s+", "", local)
    domain = domain.rstrip(".").lower()
    try:
        domain = domain.encode("idna").decode("ascii")
    except Exception:
        return None
    e = f"{local}@{domain}"
    return e if EMAIL_RE.fullmatch(e) else None


import re
from typing import Optional, Tuple


def vehicle_number_to_rta(vehicle_number: str, rto_code: str) -> Optional[str]:
    # Expect break_vehicle_number -> (state, rto, series, number)
    try:
        r1, r2, r3, r4 = break_vehicle_number(vehicle_number) or (
            None,
            None,
            None,
            None,
        )
    except Exception:
        r1 = r2 = None

    # Bharat Series: derive state+RTO from provided rto_code like "RJ14"
    if r2 and r2.upper() == "BH":
        code = re.sub(r"[^A-Za-z0-9]", "", rto_code or "").upper()[:4]
        if len(code) < 4:
            return None
        st, num = code[:2], code[2:4]
        return f"{st} {num}" if st.isalpha() and num.isdigit() else None

    # Normal case: use tokens from vehicle_number
    if r1 and r2:
        st = str(r1).upper()
        num = str(r2)
        if len(st) == 2 and st.isalpha() and len(num) == 2 and num.isdigit():
            return f"{st} {num}"

    return None


import re
from typing import Optional

_NUM_SCALE_RE = re.compile(
    r"""
    (?P<num>
        (?:(?:\d{1,3}(?:[,\s_]\d{2,3})+)(?:\.\d+)?)
        |
        (?:\d+(?:\.\d+)?)
        |
        (?:\.\d+)
    )
    \s*
    (?P<scale>
        cr(?:ores?)?|crore|
        l(?:akhs?|acs?)?|lac|lakh|
        k|thousand|
        m(?:n)?|million|
        b(?:n)?|billion
    )?
    \.?
""",
    re.IGNORECASE | re.VERBOSE,
)

_SCALE = {
    "k": 1_000,
    "thousand": 1_000,
    "l": 100_000,
    "lac": 100_000,
    "lacs": 100_000,
    "lakh": 100_000,
    "lakhs": 100_000,
    "cr": 10_000_000,
    "crore": 10_000_000,
    "crores": 10_000_000,
    "m": 1_000_000,
    "mn": 1_000_000,
    "million": 1_000_000,
    "b": 1_000_000_000,
    "bn": 1_000_000_000,
    "billion": 1_000_000_000,
}


def clean_amount(s: Optional[str]) -> Optional[float]:
    """
    Parse messy amounts like:
      '₹4,50,000', '₹ 50 000', '₹ 50_000', 'IDV 3.2 lakh', '0.45 cr', '50k', 'Rs 12,34,567/-', '10L'
    Return integer INR or None.
    """
    if not s:
        return None

    # if s is int or float type, return float
    if isinstance(s, (int, float)):
        return s

    # Normalize odd unicode spaces and drop common currency markers
    t = re.sub(r"[\u00A0\u2007\u202F]", " ", s)
    t = re.sub(r"(inr|rs\.?|rupees?|₹|/-)", "", t, flags=re.I)

    vals = []
    for m in _NUM_SCALE_RE.finditer(t):
        num_s = re.sub(r"[,\s_]", "", m.group("num"))
        if num_s.startswith("."):
            num_s = "0" + num_s
        try:
            base = float(num_s)
        except ValueError:
            continue
        scale_key = (m.group("scale") or "").lower().rstrip(".")
        mul = _SCALE.get(scale_key, 1)
        vals.append(base * mul)

    return round(max(vals), 2) if vals else None


from typing import Optional, Union

_WORD_MAP = {
    "nil": 0,
    "none": 0,
    "zero": 0,
    "twenty": 20,
    "twenty five": 25,
    "twenty-five": 25,
    "thirty five": 35,
    "thirty-five": 35,
    "forty five": 45,
    "forty-five": 45,
    "fifty": 50,
}


def clean_ncb(x: Union[int, float, str, None]) -> Optional[int]:
    if x is None:
        return None

    # Numeric direct
    if isinstance(x, (int, float)):
        v = float(x)
        v = v * 100 if 0 < v <= 1 else v
        v = round(v)
        return int(v) if 0 <= v <= 100 else None

    s = str(x).strip().lower()
    if not s:
        return None

    # Try word phrases common in NCB slabs
    s_norm = re.sub(r"[\s\-]+", " ", s)
    for phrase, val in _WORD_MAP.items():
        if phrase in s_norm:
            return val

    # Extract numbers, with optional percent sign
    nums = []
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(%)?", s):
        n = float(m.group(1))
        has_pct = bool(m.group(2))
        v = n if has_pct or n >= 1 else n * 100
        if 0 <= v <= 100:
            nums.append(round(v))

    return int(max(nums)) if nums else None


import re
from typing import Optional, Union

# number with optional separators and optional decimal, including ".5"
_NUM = r"(?:(?:\d{1,3}(?:[,\s_]\d{3})+|\d+)(?:\.\d+)?|\.\d+)"

# units we recognize (tight or spaced, case-insensitive)
_UNIT = r"(kg|kgs?|kilograms?|kilogram|t|tonnes?|tons?|mt|metric\s*tons?|lb|lbs|pounds?|pound|q|quintals?|quintal)"

# num followed by unit, or unit followed by num
_RE_NUM_UNIT = re.compile(rf"(?P<num>{_NUM})\s*(?P<unit>{_UNIT})", re.I)
_RE_UNIT_NUM = re.compile(rf"(?P<unit>{_UNIT})\s*(?P<num>{_NUM})", re.I)

# plain integer numbers without units
_RE_PLAIN_INT = re.compile(r"(?<![\w.])(\d{3,})(?![\w.])")  # 3+ digits

_SCALE_KG = {
    "kg": 1,
    "kgs": 1,
    "kilogram": 1,
    "kilograms": 1,
    "t": 1000,
    "ton": 1000,
    "tons": 1000,
    "tonne": 1000,
    "tonnes": 1000,
    "mt": 1000,
    "metrictons": 1000,
    "lb": 0.45359237,
    "lbs": 0.45359237,
    "pound": 0.45359237,
    "pounds": 0.45359237,
    "q": 100,
    "quintal": 100,
    "quintals": 100,
}


def _to_float(num_s: str) -> Optional[float]:
    num_s = re.sub(r"[,\s_]", "", num_s)
    if num_s.startswith("."):
        num_s = "0" + num_s
    try:
        return float(num_s)
    except ValueError:
        return None


def clean_vehicle_gvw(x: Union[str, int, float, None]) -> Optional[int]:
    """
    Gross Vehicle Weight in kg.
    Examples:
      'GVW 3.5T' -> 3500
      'GVW 3500 kg' -> 3500
      '3,490kgs' -> 3490
      'GVW: 12T' -> 12000
      '9,500 lb' -> 4309
      'GVW 50_000' -> 50000
      3490 -> 3490
    """
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return int(round(x)) if x > 0 else None

    s = str(x)
    if not s.strip():
        return None

    # normalize odd spaces
    s = re.sub(r"[\u00A0\u2007\u202F]", " ", s)

    vals = []

    # matches like "3.5T" or "3500 kg"
    for m in _RE_NUM_UNIT.finditer(s):
        base = _to_float(m.group("num"))
        if base is None:
            continue
        unit_key = re.sub(r"\s+", "", m.group("unit").lower())
        mul = _SCALE_KG.get(unit_key)
        if mul:
            vals.append(base * mul)

    # matches like "T 3.5" or "kg 3500"
    for m in _RE_UNIT_NUM.finditer(s):
        base = _to_float(m.group("num"))
        if base is None:
            continue
        unit_key = re.sub(r"\s+", "", m.group("unit").lower())
        mul = _SCALE_KG.get(unit_key)
        if mul:
            vals.append(base * mul)

    # fallback for bare integers that look like kg values
    if not vals:
        for m in _RE_PLAIN_INT.finditer(s):
            v = _to_float(m.group(1))
            if v and v >= 500:  # treat 3+ digit numbers >= 500 as kg
                vals.append(v)

    if not vals:
        return None

    return int(round(max(vals)))
