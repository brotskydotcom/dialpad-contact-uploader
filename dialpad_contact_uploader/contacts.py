#  MIT License
#
#  Copyright (c) 2022 Daniel Brotsky
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
import os
import pprint
import sys
import time
import urllib.parse
import uuid
from datetime import datetime

import requests

API_BASE = "https://dialpad.com/api/v2"
API_KEY = os.getenv("DIALPAD_API_KEY") or "set the DIALPAD_API_KEY environment var"
_api_session: requests.Session | None = None

TEST_CONTACT = {
    "phones": ["+18005551212"],
    "first_name": "Test",
    "last_name": "Contact",
}

contact_map: dict[str, list[dict]] = {}


def get_session() -> requests.Session:
    global _api_session
    if _api_session is None:
        _api_session = requests.session()
        _api_session.headers = {
            "Authorization": "Bearer " + API_KEY,
            "Accept": "application/json",
        }
    return _api_session


class RateLimiter:
    def __init__(
        self, per_second: float = 15, per_minute: float = 0, verbose: bool = False
    ):
        self.timestamp: float = 0
        delay_seconds: float = 1.0 / per_second  # spacing based on max per second
        delay_minutes: float = 0.0
        if per_minute > 0:
            delay_minutes = 60.0 / per_minute  # spacing based on max per 60 seconds
        self.delay: float = max(delay_seconds, delay_minutes)
        self.back_off = 30  # how long to delay if rate limit exceeded
        self.verbose = verbose

    def prepare_call(self):
        spacing: float = time.time() - self.timestamp
        if spacing < self.delay:
            time.sleep(spacing)
        self.timestamp = time.time()

    def retry_call(self, response: requests.Response) -> bool:
        if response.status_code == 400:
            body = response.json()
            errors: list = body.get("errors", [])
            message: str = body.get("message", "")
            if message.find("rate") >= 0:
                if self.verbose:
                    print(f"{message}: backing off {self.back_off} seconds")
                time.sleep(self.back_off)
                return True
            print(f"Bad request: {message}", file=sys.stderr)
            print(f"Detailed errors: {errors}", file=sys.stderr)
        response.raise_for_status()
        return False


def get_all_contacts(account: str = None, verbose: bool = True) -> list[dict]:
    result: list[dict] = []
    limit = 1000
    cursor = ""
    name = f"account {account}" if account else "company account"
    if verbose:
        print(f"{datetime.now()}: Fetching batches of {limit} contacts from {name}...")
    limiter = RateLimiter(verbose=verbose)
    while True:
        params = dict(limit=limit, cursor=cursor)
        if account:
            params.update(owner_id=account)
        query = urllib.parse.urlencode(params)
        url = API_BASE + f"/contacts?{query}"
        session = get_session()
        limiter.prepare_call()
        response = session.get(url)
        if limiter.retry_call(response):
            continue
        body = response.json()
        items = body.get("items", [])
        if verbose:
            batch_modifier = "next" if cursor else "first"
            print(f"{datetime.now()}: Fetched {batch_modifier} {len(items)}...")
        cursor = body.get("cursor", "")
        result += items
        if len(items) < limit or not cursor:
            break
    if verbose:
        print(f"Fetched {len(result)} contact(s) from {name}.")
    return result


def insert_contact(limiter: RateLimiter, data: dict, account: str = None) -> dict:
    if account:
        data = data.copy()
        data.update(owner_id=account)
    url = API_BASE + "/contacts"
    session = get_session()
    response = session.post(url, json=data)
    if limiter.retry_call(response):
        response = session.post(url, json=data)
    response.raise_for_status()
    return response.json()


def test_insert_contact(template: dict) -> tuple[dict, dict]:
    sent = (template or TEST_CONTACT).copy()
    if "id" in sent:
        del sent["id"]
    uid = str(uuid.uuid4())
    sent.update(uid=uid)
    sent.update(emails=[f"{uid}@oasislegalservices.org"])
    limiter = RateLimiter(per_minute=100, verbose=True)
    result = update_contact(limiter, sent)
    return sent, result


def update_contact(limiter: RateLimiter, data: dict, account: str = None) -> dict:
    if "uid" not in data:
        raise ValueError(f"Can't update a contact with no uid: {data}")
    if "id" in data:
        raise ValueError(f"Source contacts should not have id field: {data}")
    if account:
        data = data.copy()
        data.update(owner_id=account)
    url = API_BASE + "/contacts"
    session = get_session()
    limiter.prepare_call()
    response = session.put(url, json=data)
    if limiter.retry_call(response):
        response = session.put(url, json=data)
    response.raise_for_status()
    return response.json()


def update_contact_list(
    contacts: list[dict], account: str = None, verbose: bool = True
):
    count, total = 0, len(contacts)
    name = f"account {account}" if account else "company account"
    if verbose:
        print(f"{datetime.now()}: Updating {total} contact(s) in {name}...")
    limiter = RateLimiter(per_minute=100, verbose=verbose)
    for contact in contacts:
        limiter.prepare_call()
        try:
            update_contact(limiter, contact, account)
            count += 1
        except requests.HTTPError:
            print(f"Skipping contact due to errors: {contact}")
        if verbose and count < total and count % 100 == 0:
            print(f"{datetime.now()}: Updated {count}/{total}...")
    print(f"{datetime.now()}: Updated {count} contact(s) in {name}.")


def test_update_contact(data: dict):
    if "id" in data:
        raise ValueError(f"Not a source contact record with uid intact: {data}")
    sent = data.copy()
    new_uid = str(uuid.uuid4())
    if "uid" not in sent:
        sent.update(uid=new_uid)
    sent.update(emails=[f"{new_uid}@test.com"])
    limiter = RateLimiter(per_minute=100, verbose=True)
    result = update_contact(limiter, sent)
    return sent, result


def delete_contact_by_id(limiter: RateLimiter, contact_id: str):
    url = API_BASE + f"/contacts/{contact_id}"
    session = get_session()
    limiter.prepare_call()
    response = session.delete(url)
    if limiter.retry_call(response):
        response = session.delete(url)
    response.raise_for_status()


def delete_contact(limiter: RateLimiter, data: dict):
    if "id" not in data:
        raise ValueError(f"Can't delete a contact with no id: {data}")
    delete_contact_by_id(limiter, data["id"])


def delete_all_contacts(account: str = None, verbose: bool = True):
    contacts = get_all_contacts(account, verbose)
    count, total = 0, len(contacts)
    name = f"account {account}" if account else "company account"
    if verbose:
        print(f"{datetime.now()}: Deleting {total} contact(s) in {name}...")
    limiter = RateLimiter(per_minute=100, verbose=verbose)
    for contact in contacts:
        limiter.prepare_call()
        try:
            delete_contact(limiter, contact)
            count += 1
        except requests.HTTPError:
            print(f"Skipping contact due to errors: {contact}")
        if verbose and count < total and count % 100 == 0:
            print(f"{datetime.now()}: Deleted {count}/{total}...")
    if verbose:
        print(f"{datetime.now()}: Deleted {count} contact(s) in {name}.")


def print_all_contacts(account: str = None):
    if account:
        pprint.pp({account: contact_map.get(account, [])})
    else:
        pprint.pp(contact_map)


def fetch_all_contacts(account: str = None):
    key = account if account else "company"
    contact_map[key] = get_all_contacts(account)
    print(f"Fetched {len(contact_map[key])} contact(s)")


# if __name__ == "__main__":
#     delete_all_contacts()
#     s0, r0 = test_update_contact(TEST_CONTACT)
#     s1, r1 = test_update_contact(s0)
#     s2, r2 = test_update_contact(s1)
#     print_all_contacts()
