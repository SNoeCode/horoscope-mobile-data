#!/usr/bin/env python3
"""
Generates daily horoscopes for all zodiac signs using Groq
and saves to horoscope.json. Also rotates yesterday's horoscope
to horoscope_yesterday.json before overwriting.
"""

import json
import os
from horoscope import HoroscopeGenerator


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("  [OK] Saved " + path)


def main():
    print("=" * 60)
    print("Generating Daily Horoscopes with Groq")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    today_path = os.path.join(base_dir, 'horoscope.json')
    yesterday_path = os.path.join(base_dir, 'horoscope_yesterday.json')

    # rotate today -> yesterday before overwriting
    if os.path.exists(today_path):
        with open(today_path, 'r', encoding='utf-8') as f:
            yesterday_data = json.load(f)
        save_json(yesterday_path, yesterday_data)
        print("  [OK] Rotated horoscope.json -> horoscope_yesterday.json")

    generator = HoroscopeGenerator()
    combined = {}

    for sign in generator.SIGNS:
        print("\nGenerating " + sign.upper() + "...")
        daily = generator.generate_horoscope(sign)
        if daily:
            # wrap in 'daily' key so the mobile app can read it directly
            combined[sign] = {'daily': daily}

    save_json(today_path, combined)
    print("\nDone! Generated " + str(len(combined)) + " signs.")


if __name__ == "__main__":
    main()
