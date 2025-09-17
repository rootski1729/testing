import re
import unicodedata
from typing import Optional, Union
from email.utils import parseaddr

from models import FuelType, Insurer, ProductSubType, ProductCategory

# ====================== STATE MAPPING ======================

STATE_CODE_MAP = {
    "ANDHRA PRADESH": "Andhra Pradesh", "AP": "Andhra Pradesh",
    "ARUNACHAL PRADESH": "Arunachal Pradesh", "AR": "Arunachal Pradesh",
    "ASSAM": "Assam", "AS": "Assam",
    "BIHAR": "Bihar", "BR": "Bihar",
    "CHHATTISGARH": "Chhattisgarh", "CG": "Chhattisgarh",
    "GOA": "Goa", "GA": "Goa",
    "GUJARAT": "Gujarat", "GJ": "Gujarat",
    "HARYANA": "Haryana", "HR": "Haryana",
    "HIMACHAL PRADESH": "Himachal Pradesh", "HP": "Himachal Pradesh",
    "JHARKHAND": "Jharkhand", "JH": "Jharkhand",
    "KARNATAKA": "Karnataka", "KA": "Karnataka",
    "KERALA": "Kerala", "KL": "Kerala",
    "MADHYA PRADESH": "Madhya Pradesh", "MP": "Madhya Pradesh",
    "MAHARASHTRA": "Maharashtra", "MH": "Maharashtra",
    "MANIPUR": "Manipur", "MN": "Manipur",
    "MEGHALAYA": "Meghalaya", "ML": "Meghalaya",
    "MIZORAM": "Mizoram", "MZ": "Mizoram",
    "NAGALAND": "Nagaland", "NL": "Nagaland",
    "ODISHA": "Odisha", "OR": "Odisha", "ORISSA": "Odisha",
    "PUNJAB": "Punjab", "PB": "Punjab",
    "RAJASTHAN": "Rajasthan", "RJ": "Rajasthan",
    "SIKKIM": "Sikkim", "SK": "Sikkim",
    "TAMIL NADU": "Tamil Nadu", "TN": "Tamil Nadu",
    "TELANGANA": "Telangana", "TS": "Telangana", "TG": "Telangana",
    "TRIPURA": "Tripura", "TR": "Tripura",
    "UTTAR PRADESH": "Uttar Pradesh", "UP": "Uttar Pradesh",
    "UTTARAKHAND": "Uttarakhand", "UR": "Uttarakhand", "UK": "Uttarakhand",
    "WEST BENGAL": "West Bengal", "WB": "West Bengal",
    # Union Territories
    "ANDAMAN AND NICOBAR ISLANDS": "Andaman and Nicobar Islands", "AN": "Andaman and Nicobar Islands",
    "CHANDIGARH": "Chandigarh", "CH": "Chandigarh",
    "DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "Dadra and Nagar Haveli and Daman and Diu",
    "DADRA AND NAGAR HAVELI": "Dadra and Nagar Haveli and Daman and Diu",
    "DAMAN AND DIU": "Dadra and Nagar Haveli and Daman and Diu",
    "DN": "Dadra and Nagar Haveli and Daman and Diu", "DD": "Dadra and Nagar Haveli and Daman and Diu",
    "DELHI": "Delhi", "DL": "Delhi",
    "JAMMU AND KASHMIR": "Jammu and Kashmir", "JK": "Jammu and Kashmir",
    "LADAKH": "Ladakh", "LA": "Ladakh",
    "LAKSHADWEEP": "Lakshadweep", "LD": "Lakshadweep",
    "PUDUCHERRY": "Puducherry", "PONDICHERRY": "Puducherry", "PY": "Puducherry",
}

def state_code_to_state(state_code: str) -> Optional[str]:
    """Convert state code to full state name"""
    state_code = state_code.upper()
    return STATE_CODE_MAP.get(state_code)

# ====================== VEHICLE NUMBER PROCESSING ======================

def break_vehicle_number(vehicle_number: str) -> Optional[tuple[str, str, str, str]]:
    """Break vehicle number into components (state, rto, series, number)"""
    s = re.sub(r"[^A-Za-z0-9]", "", (vehicle_number or "")).upper()
    s = re.sub(r"^IND(?=[A-Z0-9])", "", s)
    m = re.fullmatch(r"(\d{2})BH(\d{4})([A-Z]{1,2})", s)
    if m:
        return m.group(1), "BH", m.group(2), m.group(3)
    m = re.fullmatch(r"([A-Z]{2})(\d{2})([A-Z]{1,3})(\d{4})", s)
    return m.groups() if m else None

def vehicle_number_to_state(vehicle_number: str) -> Optional[str]:
    """Extract state from vehicle number"""
    r1, r2, r3, r4 = break_vehicle_number(vehicle_number) or (None, None, None, None)
    if r2 == "BH":  # Bharat Series
        return None
    state_code = r1
    return state_code_to_state(state_code)

def vehicle_number_to_rta(vehicle_number: str, rto_code: str) -> Optional[str]:
    """Extract RTA (Regional Transport Authority) from vehicle number"""
    try:
        r1, r2, r3, r4 = break_vehicle_number(vehicle_number) or (None, None, None, None)
    except Exception:
        r1 = r2 = None

    # Bharat Series: derive state+RTO from provided rto_code like "RJ14"
    if r2 and r2.upper() == "BH":
        if not rto_code:
            return None
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

# ====================== CONTACT INFORMATION CLEANING ======================

def clean_phone(s: str, default_cc: str = "91") -> str:
    """Clean and format phone number"""
    if not s:
        return None
    d = re.sub(r"\D+", "", s or "")
    d = re.sub(r"^00", "", d)
    if len(d) < 10:
        return None
    sub = d[-10:]
    cc = d[:-10].lstrip("0") or default_cc
    return f"+{cc} {sub}"

EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$"
)

def clean_email(s: str | None) -> str | None:
    """Clean and validate email address"""
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

# ====================== AMOUNT CLEANING ======================

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
    "k": 1_000, "thousand": 1_000,
    "l": 100_000, "lac": 100_000, "lacs": 100_000, "lakh": 100_000, "lakhs": 100_000,
    "cr": 10_000_000, "crore": 10_000_000, "crores": 10_000_000,
    "m": 1_000_000, "mn": 1_000_000, "million": 1_000_000,
    "b": 1_000_000_000, "bn": 1_000_000_000, "billion": 1_000_000_000,
}

def clean_amount(s: Optional[str]) -> Optional[float]:
    """
    Parse messy amounts like:
      '₹4,50,000', '₹ 50 000', '₹ 50_000', 'IDV 3.2 lakh', '0.45 cr', '50k', 'Rs 12,34,567/-', '10L'
    Return float INR or None.
    """
    if not s:
        return None
    if isinstance(s, (int, float)):
        return s

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

# ====================== NCB CLEANING ======================

_WORD_MAP = {
    "nil": 0, "none": 0, "zero": 0,
    "twenty": 20, "twenty five": 25, "twenty-five": 25,
    "thirty five": 35, "thirty-five": 35,
    "forty five": 45, "forty-five": 45,
    "fifty": 50,
}

def clean_ncb(x: Union[int, float, str, None]) -> Optional[int]:
    """Clean No Claim Bonus (NCB) percentage"""
    if x is None:
        return None

    if isinstance(x, (int, float)):
        v = float(x)
        v = v * 100 if 0 < v <= 1 else v
        v = round(v)
        return int(v) if 0 <= v <= 100 else None

    s = str(x).strip().lower()
    if not s:
        return None

    s_norm = re.sub(r"[\s\-]+", " ", s)
    for phrase, val in _WORD_MAP.items():
        if phrase in s_norm:
            return val

    nums = []
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(%)?", s):
        n = float(m.group(1))
        has_pct = bool(m.group(2))
        v = n if has_pct or n >= 1 else n * 100
        if 0 <= v <= 100:
            nums.append(round(v))

    return int(max(nums)) if nums else None

# ====================== VEHICLE GVW CLEANING ======================

_NUM = r"(?:(?:\d{1,3}(?:[,\s_]\d{3})+|\d+)(?:\.\d+)?|\.\d+)"
_UNIT = r"(kg|kgs?|kilograms?|kilogram|t|tonnes?|tons?|mt|metric\s*tons?|lb|lbs|pounds?|pound|q|quintals?|quintal)"
_RE_NUM_UNIT = re.compile(rf"(?P<num>{_NUM})\s*(?P<unit>{_UNIT})", re.I)
_RE_UNIT_NUM = re.compile(rf"(?P<unit>{_UNIT})\s*(?P<num>{_NUM})", re.I)
_RE_PLAIN_INT = re.compile(r"(?<![\w.])(\d{3,})(?![\w.])")

_SCALE_KG = {
    "kg": 1, "kgs": 1, "kilogram": 1, "kilograms": 1,
    "t": 1000, "ton": 1000, "tons": 1000, "tonne": 1000, "tonnes": 1000, "mt": 1000, "metrictons": 1000,
    "lb": 0.45359237, "lbs": 0.45359237, "pound": 0.45359237, "pounds": 0.45359237,
    "q": 100, "quintal": 100, "quintals": 100,
}

def _to_float(num_s: str) -> Optional[float]:
    """Convert number string to float"""
    num_s = re.sub(r"[,\s_]", "", num_s)
    if num_s.startswith("."):
        num_s = "0" + num_s
    try:
        return float(num_s)
    except ValueError:
        return None

def clean_vehicle_gvw(x: Union[str, int, float, None]) -> Optional[int]:
    """
    Clean Gross Vehicle Weight in kg.
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

    s = re.sub(r"[\u00A0\u2007\u202F]", " ", s)
    vals = []

    for m in _RE_NUM_UNIT.finditer(s):
        base = _to_float(m.group("num"))
        if base is None:
            continue
        unit_key = re.sub(r"\s+", "", m.group("unit").lower())
        mul = _SCALE_KG.get(unit_key)
        if mul:
            vals.append(base * mul)

    for m in _RE_UNIT_NUM.finditer(s):
        base = _to_float(m.group("num"))
        if base is None:
            continue
        unit_key = re.sub(r"\s+", "", m.group("unit").lower())
        mul = _SCALE_KG.get(unit_key)
        if mul:
            vals.append(base * mul)

    if not vals:
        for m in _RE_PLAIN_INT.finditer(s):
            v = _to_float(m.group(1))
            if v and v >= 500:
                vals.append(v)

    if not vals:
        return None

    return int(round(max(vals)))

# ====================== FUEL TYPE CLEANING ======================

def clean_fuel_type(fuel_type) -> FuelType:
    """Clean and standardize fuel type"""
    s = (fuel_type or "").strip()
    if not s:
        return None

    name_key = s.upper().replace(" ", "_")
    if name_key in FuelType.__members__:
        return FuelType[name_key]

    s_lower = s.lower()
    for m in FuelType:
        if m.value.lower() == s_lower:
            return m

    s_norm = "".join(ch for ch in s_lower if ch.isalnum())
    alias_map = {
        "petrol": FuelType.PETROL, "gasoline": FuelType.PETROL,
        "diesel": FuelType.DIESEL, "cng": FuelType.CNG, "lpg": FuelType.LPG,
        "ev": FuelType.ELECTRIC, "electric": FuelType.ELECTRIC, "bev": FuelType.ELECTRIC,
        "phev": FuelType.HYBRID_ELECTRIC, "hybrid": FuelType.HYBRID_ELECTRIC, "hybridelectric": FuelType.HYBRID_ELECTRIC,
        "h2": FuelType.HYDROGEN, "hydrogen": FuelType.HYDROGEN,
    }
    return alias_map.get(s_norm, None)

# ====================== INSURER CLEANING ======================

def _norm(s: str) -> str:
    """Normalize string for comparison"""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-zA-Z0-9]+", " ", s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s

def clean_insurer(insurer: str | None) -> Optional[Insurer]:
    """Clean and standardize insurer name"""
    s = (insurer or "").strip()
    if not s:
        return None

    up = s.upper()
    if up in Insurer.__members__:
        return Insurer[up]

    t = _norm(s)
    tight = t.replace(" ", "")

    checks = [
        (Insurer.BAJAJ, ["bajaj", "allianz"]),
        (Insurer.TATA, ["tata", "aig"]),
        (Insurer.ICICI, ["icici", "lombard"]),
        (Insurer.HDFC, ["hdfc", "ergo"]),
        (Insurer.RGCL, ["reliance", "general"]),
        (Insurer.IFFCO, ["iffco", "tokio"]),
        (Insurer.ROYAL, ["royal", "sundaram"]),
        (Insurer.CHOLA, ["chola", "ms"]),
        (Insurer.MAGMA, ["magma", "hdi"]),
        (Insurer.USGI, ["universal", "sompo"]),
        (Insurer.ZURICHKOTAK, ["zurich", "kotak"]),
        (Insurer.ZURICHKOTAK, ["zurich"]),
        (Insurer.ZURICHKOTAK, ["kotak", "general"]),
        (Insurer.KTKM, ["kotak", "mahindra"]),
        (Insurer.ZUNO, ["zuno"]),
        (Insurer.ZUNO, ["edelweiss"]),
        (Insurer.RAHEJAQBE, ["raheja", "qbe"]),
        (Insurer.RAHEJAQBE, ["qbe"]),
        (Insurer.SBI, ["sbi", "general"]),
        (Insurer.GO, ["digit"]),
        (Insurer.ACKO, ["acko"]),
        (Insurer.NAVI, ["navi"]),
        (Insurer.SHRIRAM, ["shriram"]),
        (Insurer.UIIC, ["united", "india"]),
        (Insurer.NIC, ["national", "insurance"]),
        (Insurer.TNI, ["new", "india"]),
        (Insurer.OR, ["oriental"]),
        (Insurer.FUTURE, ["future", "generali"]),
        (Insurer.GENERALI_CENTRAL, ["generali"]),
        (Insurer.LIB, ["liberty"]),
    ]
    
    for code, toks in checks:
        if all(tok in t for tok in toks) or all(tok.replace(" ", "") in tight for tok in toks):
            return code

    simple = {
        "bajaj": Insurer.BAJAJ, "tata": Insurer.TATA, "icici": Insurer.ICICI,
        "hdfc": Insurer.HDFC, "reliance": Insurer.RGCL, "iffco": Insurer.IFFCO,
        "sundaram": Insurer.ROYAL, "chola": Insurer.CHOLA, "liberty": Insurer.LIB,
        "sompo": Insurer.USGI, "digit": Insurer.GO, "shriram": Insurer.SHRIRAM,
        "sbi": Insurer.SBI, "acko": Insurer.ACKO, "navi": Insurer.NAVI,
        "zuno": Insurer.ZUNO, "edelweiss": Insurer.ZUNO, "qbe": Insurer.RAHEJAQBE,
        "generali": Insurer.GENERALI_CENTRAL, "kotak": Insurer.ZURICHKOTAK,
        "oriental": Insurer.OR, "united india": Insurer.UIIC, "national": Insurer.NIC,
        "new india": Insurer.TNI,
    }
    
    for key, val in simple.items():
        if key in t:
            return val

    return None

# ====================== PRODUCT CATEGORY MAPPING ======================

def sub_type_to_product_category(sub_type: ProductSubType) -> ProductCategory:
    """Map product sub type to product category"""
    if not sub_type:
        return None
    
    if sub_type == ProductSubType.TW:
        return ProductCategory.DUO
    elif sub_type == ProductSubType.PCV:
        return ProductCategory.QUAD

    return None