import re
from dateutil import parser as dateparser

def normalize_date(date_str):
    if not date_str:
        return None

    s = date_str.strip()

    if re.fullmatch(r"\d{4}", s):
        return f"{s}.??.??"

    if re.fullmatch(r"\d{4}[-/.]\d{1,2}", s):
        year, month = re.split(r"[-/.]", s)
        return f"{int(year):04d}.{int(month):02d}.??"

    dt = dateparser.parse(s)
    return dt.strftime("%Y.%m.%d")
