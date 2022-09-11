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
import os.path

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
#
import click

from dialpad_contact_uploader.contacts import update_contact_list
from dialpad_contact_uploader.spreadsheet import import_contacts, export_contacts


@click.command()
@click.option("--upload/--no-upload", default=False)
@click.option("--export/--no-export", default=False)
@click.option("--account", default="")
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
def dialpad_contact_uploader(upload: bool, export: bool, account: str, path: str):
    contacts = import_contacts(path)
    if export:
        name, extension = os.path.splitext(path)
        export_path = name + ".export" + extension
        export_contacts(contacts, export_path, True)
    if upload:
        update_contact_list(contacts, account, True)


if __name__ == "__main__":
    dialpad_contact_uploader()
