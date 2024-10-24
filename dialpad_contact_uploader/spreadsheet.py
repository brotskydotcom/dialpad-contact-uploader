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
import csv
import sys

from .validate import parse_uid, parse_name, parse_phones, parse_emails


def import_contacts(path: str) -> list[dict]:
    contacts = []
    with open(path, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        for i, row in enumerate(reader, 2):  # row 1 is the header row
            try:
                uid = parse_uid(row["Creation Date"])
                first_name = parse_name(row["First_Name"])
                last_name = parse_name(row["Last_Name"], first_name)
                phones, errors = parse_phones(row["Phones"])
                if errors:
                    print(f"Line {i}: Invalid phones ignored:", file=sys.stderr)
                    for e in errors:
                        print(f"    {e}", file=sys.stderr)
                emails, errors = parse_emails(row["Email"])
                if errors:
                    print(f"Line {i}: Invalid emails ignored:", file=sys.stderr)
                    for e in errors:
                        print(f"    {e}", file=sys.stderr)
                contact = dict(
                    uid=uid,
                    first_name=first_name,
                    last_name=last_name,
                    phones=phones,
                    emails=emails,
                )
                # print(f"Row {i}: {contact}", file=sys.stderr)
                contacts.append(contact)
            except KeyError as exc:
                raise ValueError(f"Missing column on row {i}: {exc}")
            except ValueError as exc:
                print(f"Skipping row {i}: {exc}")
    return contacts


def export_contacts(contacts: list[dict], path: str, verbose=True):
    with open(path, "w") as outfile:
        print(f"UID,first_name,last_name,phones,emails", file=outfile)
        for contact in contacts:
            print(
                f"{contact['uid']},"
                f"{contact['first_name']},"
                f"{contact['last_name']},"
                f"{'|'.join(contact['phones'])},"
                f"{'|'.join(contact['emails'])}",
                file=outfile,
            )
    if verbose:
        print(f"Wrote {len(contacts)} row(s) to file: {path}")
