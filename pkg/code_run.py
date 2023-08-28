import logging

import requests
from plugins.QChatCodeRunner.config.coderun_config import Config
from urllib.parse import quote

_config = Config()


def code_runner(code: str, language: str):
    code_runner_url = f"{_config.domain}/run_code"
    headers = {"Referer": "https://code-runner-plugin.vercel.app"}
    session = requests.session()
    res = session.post(
        url=code_runner_url,
        json={
            "code": code,
            "language": language,
            "input": 50,
            "compileOnly": "false",
        },
        headers=headers,
        proxies=_config.proxy,
    )
    if res.status_code != 200:
        result = {"output": f"error:{res.text} with status code {res.status_code}"}
        logging.error(f"error:{res.text} with status code {res.status_code}")
    else:
        result = res.json()
        logging.debug(result)
    return result


def graph_generation(chart_type: str, labels: str, datasets: list):
    code_runner_url = f"{_config.domain}/quick_chart"
    headers = {"Referer": "https://code-runner-plugin.vercel.app"}
    session = requests.session()
    res = session.post(
        url=code_runner_url,
        json={"chart_type": chart_type, "labels": labels, "datasets": datasets},
        headers=headers,
    )
    if res.status_code != 200:
        result = {"output": f"error:{res.text} with status code {res.status_code}"}
        logging.error(f"error:{res.text} with status code {res.status_code}")
    else:
        result = res.json()
        logging.debug(result)
    return result


def save_code(filename: str, code: str):
    code_runner_url = f"{_config.domain}/save_code"
    headers = {"Referer": "https://code-runner-plugin.vercel.app"}
    session = requests.session()
    res = session.post(
        url=code_runner_url,
        json={"filename": filename, "code": code},
        headers=headers,
    )
    if res.status_code != 200:
        result = {"output": f"error:{res.text} with status code {res.status_code}"}
        logging.error(f"error:{res.text} with status code {res.status_code}")
    else:
        result = res.json()
        logging.debug(result)
    return result


def show_snippet(
    code: str,
    language: str,
    title: str,
    theme: str,
    showNums: str,
    opacity: str,
    blurLines: str,
):
    code_runner_url = f"{_config.domain}/show_snippet"
    headers = {"Referer": "https://code-runner-plugin.vercel.app"}
    session = requests.session()
    data = {
        "code": code,
        "language": language,
        "title": title,
        "theme": theme,
        "showNums": showNums,
        "opacity": opacity,
        "blurLines": blurLines,
    }
    res = session.get(
        url=code_runner_url,
        params=data,
        headers=headers,
    )
    if res.status_code != 200:
        result = {"output": f"error:{res.text} with status code {res.status_code}"}
        logging.error(f"error:{res.text} with status code {res.status_code}")
    else:
        result = res.json()
        logging.debug(result)
    return result
