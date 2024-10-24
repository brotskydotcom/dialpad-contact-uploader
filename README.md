# dialpad-contact-uploader

A merging uploader/maintainer for Dialpad company contacts

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
    cd ~/Downloads/dialpad-contact-uploader-main
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
    DIALPAD_API_KEY=yourApiKeyGoesHere
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
