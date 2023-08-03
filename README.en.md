# WB price parser
## Изменить язык: [Русский](README.md)
***
Telegram bot to detect WB advertising rates in maps and search. Implemented a subscription system with auto-renewal, a bonus system.
## [LIVE](https://t.me/WildBoost_bot)
## [DEMO](README.demo.md)
## Functionality:
1. Determines the bids for WB advertising in the search
2. Determines the rates for WB advertising in the card
3. Connected bonus system
4. Generates a referral QR code
5. Subscription payment
6. Automatic renewal of subscription
7. Uploading data from the database to google table
## Commands:
**For convenience, it is recommended to add these commands to the side menu of the bot using [BotFather](https://t.me/BotFather).**
- referral - get referral link and qr-code
- profile - open profile
- help - help

**Commands available:**
- users - upload information about users to google table
- payments - uploading information about payments to google table

## Installation and use:
- Logging when accounting for money in the py_log.log file
- Install dependency:
```sh
pip install -r requirements.txt
```
- in the .env file specify:
    - Bot telegram token: **TELEGRAM_TOKEN**=TOKEN
    - Bot ID: **BOT_ID**=ID (first digits from bot token, to :)
    - Manager ID: **MANAGER_ID**=MANAGER_ID; will have the right to execute the /update command, settings will be sent - to get the appearance, you need to activate the bot from your account (click the "start" button)
    > To determine the user ID, send any message to the following [bot](https://t.me/getmyid_bot) with the correct account. The value contained in **Your User ID** - User ID
    - Manager username - on the specified profile will enter the "manager" button in the menu: **MANAGER_USERNAME**=example (specified without @)
    - **ACCOUNT_ID** - Yookassa store number
    - **SECRET_KEY** - Yookassa secret key
    - **SPREAD_NAME** - table name in Google sheets where to upload data about new requests
    - **USERS_LIST_NAME** - sheet name in the table where user data will be found
    - **PAYMENTS_LIST_NAME** - sheet name in the table where payment data will be uploaded
-get a file with credentials (connection parameters):\
https://console.cloud.google.com/ \
https://www.youtube.com/watch?v=bu5wXjz2KvU - contents from 00:00 to 02:35\
The resulting save file at the root of the project, named **service_account.json**
- it is recommended that the service email address access the table (instruction in the video at the link above)
- game project:
```sh
python3 main.py
```