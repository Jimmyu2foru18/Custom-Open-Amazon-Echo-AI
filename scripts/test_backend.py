#!/usr/bin/env python3
import argparse
import json

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description='Quick local test for Echo Agent backend.')
    parser.add_argument('text', help='Prompt text')
    parser.add_argument('--url', default='http://localhost:5000/v1/chat', help='Backend chat endpoint URL')
    args = parser.parse_args()

    response = requests.post(args.url, json={'text': args.text}, timeout=60)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))


if __name__ == '__main__':
    main()
