# Grade notification script for the University of Ulm

This script pulls grades from campusonline.uni-ulm.de and notifies users via telegram if any new grades are found. Due to its modular design, this script can easily be adapted to other courses even though it is currently designed for BSc Informatik.

## Getting Started
The following environment variables must be set:
```
USERNAME = username
PASSWORD = password
URL = login url
GRADE_URL = url to the grades
BOT_TOKEN = Telegram bot token
CHAT_ID = Telegram chat id
```
### Telegram bot
* Create a bot using [https://t.me/botfather](https://t.me/botfather)
* Write your bot a message
* Get your chat id by using `https://api.telegram.org/botXXX:YYY/getUpdates`. XXX:YYY is yout BOT_TOKEN
