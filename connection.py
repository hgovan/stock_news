import json
import requests
from datetime import datetime
import time


def web_requests_post(url: str, header: dict, payload: dict) -> dict or bool:
    try:
        r = requests.post(url, headers=header, json=payload)
        if r.ok:
            return r
        else:
            print(f"\n{r} failed to make proper connection to: {url}")
            error_logger(f"{r}: failed to make proper connection to: {url}")
            return False
    except:
        print(f"\nConnection not established to: {url}")
        error_logger(f"Connection not established to: {url}")
        return False


def web_requests_get(url: str, header: dict) -> dict or bool:
    try:
        r = requests.get(url, headers=header)
        if r.ok:
            return r
        else:
            print(f"\n{r} failed to connect to: {url}")
            error_logger(f"{r}: failed to make proper connection to: {url}")
            return False
    except:
        print(f"{r}\nConnection not established to: {url}")
        error_logger(f"Connection not established to: {url}")
        return False


def error_logger(text: str) -> None:
    today = datetime.today()
    with open("error_logger.txt", "a") as f:
        f.write(f"{today} --> {text}\n")


def read_json(file: str) -> None:
    with open(file, "r") as openfile:
        return json.load(openfile)


def write_json(file: str, data: dict) -> None:
    with open(file, 'w') as outfile:
        json.dump(data, outfile)


def progress_tracker(step: int, total: int) -> None:
    percent = (step+1) / total * 100
    print(f'\rProgress: [{"#" * int(percent): <99}] {percent:.1f}%', end='')
    time.sleep(0.001)
