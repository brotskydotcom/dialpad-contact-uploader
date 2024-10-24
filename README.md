# Dialpad Contact Uploader

This repo contains a python module (and command-line script) for uploading a CSV file of contacts to Dialpad.

## Usage

Steps 1-3 only have to be done once per machine. Step 4 only has to be done when a new version of the uploader is available. Steps 5 on have to be done every time you use the uploader.

These examples assume a macOS environment for steps 1, 2, 4, 5, and 8. You will have to adjust for other operating systems, and of course you can change what directory you use for your download. The other steps are independent of your operating system.

1. Install python 3.10 or higher.
    ```zsh
    brew install python3
    ```
2. Install pipx
    ```zsh
    brew install pipx
    ```
3. Install poetry with pipx
    ```zsh
    pipx install poetry
    ```
4. Get latest version from GitHub.
    ```zsh
    curl -L -o ~/Downloads/dialpad-contact-uploader-main.zip https://github.com/brotskydotcom/dialpad-contact-uploader/archive/refs/heads/main.zip
    unzip -d ~/Downloads ~/Downloads/dialpad-contact-uploader-main.zip
    ```
5. Change to download root directory.
    ```zsh
    cd ~/Downloads/dialpad-contact-uploader-main
    ```
6. Use poetry to create a python virtual environment with all the necessary dependencies installed.
    ```zsh
    poetry install
    ```
7. Get into a command environment that is using the poetry virtual environment
    ```zsh
    poetry shell
    ```
8. Export a DIALPAD_API_KEY environment variable whose value is the very-long-string-of-characters that is your account's Dialpad API key.
    ```zsh
    export DIALPAD_API_KEY=yourApiKeyGoesHere
    ```
9. In your current directory, create a CSV files named "contacts.csv" containing the data you want to upload.  It should have exactly four columns, with these labels in this order:
    ```
    First_Name,Last_Name,Phones,Email
    ```
10. Upload the file using this command:
    ```zsh
    python dialpad_uploader.py --upload contacts.csv 
    ```
 
The script will validate the entries in the spreadsheet, spitting out errors for lines it can't validate, and then attempt to upload the lines it could validate.  It will provide a progress report every 100 contacts (each group of 100 takes 60-90 seconds to upload), and it will provide error messages for each contact that Dialpad won't accept (typically because of issues with the phone number).

Running the script another time with some of the same contact information will replace information for those contacts, so you can just clean up any errors in your spreadsheet and then upload the whole thing again.

You can get the script to do validation only (with no upload) by using `--export` rather than `--upload` in step 10. When invoked this way, it will create a CSV file with validated data with the same name as the input file but with `.export.csv` as its suffix.

## Phone number validation

Dialpad does very careful phone number validation on every uploaded contact, and rejects any whose numbers are invalid.  Unfortunately, it doesn't give much information about why it has rejected the number. So this script does a bunch of validations before it even tries the upload, and rejects numbers that fail the validation.  Here are the validations performed by the script:

1. If a number starts with '+' or '011', it's assumed to be an international number and no more validation is done. (The 011 is replaced by '+', because Dialpad requires that.)
2. If a number has a '+' anywhere but at the front, it's rejected, because valid numbers can only have a '+' at the front.
3. If a number has fewer than 10 digits, it's rejected, because Dialpad requires area codes on all numbers.
4. If a number has more than 10 digits, it's assumed to be an international number so a '+' is prepended and no more validation is done.
5. If a number, after the area code, has a prefix starting with "0" or "1" (such as `510-123-4567`), it's rejected because North American prefixes can't start with either of those numbers. (This typically means it's an international number that has not been prefixed correctly with a '+'.)
6. If a number has one of the "non-geographic" (aka 5XX) area codes that are reserved for machine-to-machine communication, Dialpad will not call it, so it is rejected. 

Note: If you want to put more than one phone number in your "Phones" field, separate them with a forward slash `/` or a vertical bar `|`; any other characters except `+` and digits will be ignored.

## License

Everything in this repository is copyright 2022-2024 by Daniel C. Brotsky, and is available for use under the open-source [MIT License](LICENSE). Contributions are welcome and covered by the same license.