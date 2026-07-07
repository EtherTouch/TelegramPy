# TelegramPy

TelegramPy enables running Python scripts through Telegram and updating messages to users via a Flask API.

## Why?

Often, when working with microcontrollers (which control or communicate with a Raspberry Pi), the primary need is to
execute specific Python functions. Using TelegramPy provides a convenient way to trigger these functions remotely.

## Configuration

Python scripts intended for execution are stored separately in `./user_data/tasks` folder. Configuration details are
stored in `./user_data/config.json5`, which includes:

- **users**: Defines different users by their `chat_id`. Only messages received from these `chat_id` will be
  executed. Each user object contains `chat_id`, `task` (a list of tasks available to the user; if set to "all", all
  Python scripts can be run by the user), and `admin` (to identify if the user is an admin). Admins receive messages
  when unauthorized users send messages to the bot or when Flask API receives data without metadata.

- **flask_api_address**: Specifies the address where the Flask server will run.

- **bot_token**: Token for the Telegram bot.

- **chat_style**: Specifies the interface style (`"ikm"` for inline keyboard markup interface or `"rkm"` for reply
  keyboard markup interface).

- **greeting**: Greeting messages displayed when starting a chat.

- **tasks**: Contains a dictionary object where each key is the Python object name. Optionally, descriptions can be
  added
  under `"desc"`. `"alias"` provides an alternative name for the object when chatting. `"singleton"` indicates whether
  only one instance of the object should exist (`true`) or if each `chat_id` should have its own
  instance (`false`). `"functions"` lists all callable functions of the Python class, where aliases can also be used to
  call functions instead of using function names directly.

## How to Run

1. Clone the repository:

2. Update the `bot_token` in `config.json5` with your Telegram bot token.

3. Add your `chat_id` to the `users` section in `config.json5`.

4. Install dependencies listed in `requirements.txt`.

5. Run `main.py`:

## Starting the app

```bash
cd ./TelegramPy
virtualenv env
source env/bin/activate # Activate virtual environment
pip3 install -r requirements.txt
# python3 main.py
# alternatively
chmod +x run_main.sh
./run_main.sh

# For more detail refer examples in ./user_data/tasks/
```
