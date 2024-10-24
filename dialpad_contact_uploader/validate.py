#  MIT License
#
#  Copyright (c) 2022-2024 Daniel C. Brotsky
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
import re
from functools import reduce
from operator import add

from dateutil.parser import parse as parse_time
from email_validator import validate_email, EmailNotValidError

PERSONAL_AREA_CODES = {
    "500",
    "521",
    "522",
    "523",
    "524",
    "525",
    "526",
    "527",
    "528",
    "529",
    "533",
    "544",
    "566",
    "577",
    "588",
}
AMBIGUOUS_AREA_CODES = {"664"}


def parse_phones(value: str) -> (list[str], list[str]):
    candidates = re.split(r"[/|]", value)
    phones = []
    errors = []
    for candidate in candidates:
        candidate = candidate.strip()
        if not candidate:
            continue
        digits = reduce(add, re.split(r"[^+0-9]", candidate))
        if digits.startswith("+"):
            phones.append(digits)
        elif digits.find("+") >= 0:
            errors.append(f"+ not at front of phone: {candidate}")
        elif digits.startswith("011"):
            phones.append("+" + digits[3:])
        elif len(digits) < 10:
            errors.append(f"Not enough digits: {candidate}")
        elif len(digits) > 10:
            phones.append("+" + digits)
        elif digits[3:4] in ["0", "1"]:
            errors.append(
                f"Invalid prefix after area code (starts with 0 or 1): {candidate}"
            )
        elif digits[0:3] in PERSONAL_AREA_CODES:
            errors.append(f"Personal/Text-service area code: {candidate}")
        elif digits[0:3] in AMBIGUOUS_AREA_CODES:
            errors.append(f"Area code in more than one country: {candidate}")
        else:
            phones.append("+1" + digits)
    return phones, errors


def parse_emails(value: str) -> (list[str], list[str]):
    candidates = re.split(r"[,;|/]", value)
    emails = []
    errors = []
    for candidate in candidates:
        try:
            candidate = candidate.strip()
            if not candidate or candidate.lower() == "none":
                continue
            email = validate_email(candidate, check_deliverability=False)
            emails.append(email.ascii_email)
        except EmailNotValidError as exc:
            errors.append(f"'{candidate}': {exc}")
    return emails, errors


def parse_name(value: str, if_missing: str = None) -> str:
    candidate = value.strip()
    if len(candidate) > 0:
        return candidate
    elif if_missing:
        return if_missing
    raise ValueError("Invalid (empty) name")


def parse_uid(value: str) -> str:
    try:
        timestamp = parse_time(value.strip())
        return timestamp.strftime("%s")
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"Invalid timestamp ({exc}): {value.strip()}")
