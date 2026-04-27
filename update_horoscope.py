#!/usr/bin/env python3
"""
Generates horoscopes for all zodiac signs using Groq and saves to horoscope.json.
- Daily: regenerated every run
- Monthly: regenerated when the month changes
- Yearly: regenerated when the year changes
- Yesterday: today's daily is rotated to yesterday before overwriting
"""

import json
import os
from datetime import datetime
from horoscope import HoroscopeGenerator


def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("  [OK] Saved " + path)


def needs_monthly_update(existing_data):
    current_period = datetime.now().strftime('%B %Y')
    for sign_data in existing_data.values():
        monthly = sign_data.get('monthly', {})
        if monthly.get('period') != current_period:
            return True
    return False


def needs_yearly_update(existing_data):
    current_year = datetime.now().strftime('%Y')
    for sign_data in existing_data.values():
        yearly = sign_data.get('yearly', {})
        if yearly.get('year') != current_year:
            return True
    return False


def main():
    print("=" * 60)
    print("Signs By Numbers — Horoscope Generator")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    today_path     = os.path.join(base_dir, 'horoscope.json')
    yesterday_path = os.path.join(base_dir, 'horoscope_yesterday.json')

    existing = load_json(today_path)
    regenerate_monthly = needs_monthly_update(existing) or not existing
    regenerate_yearly  = needs_yearly_update(existing)  or not existing

    # --- rotate today's daily -> horoscope_yesterday.json BEFORE overwriting ---
    if existing:
        yesterday = {}
        for sign, sign_data in existing.items():
            if sign_data.get('daily'):
                yesterday[sign] = {
                    'summary': sign_data['daily']['summary'],
                    'date':    sign_data['daily']['date'],
                }
        if yesterday:
            save_json(yesterday_path, yesterday)
            print(f"\nRotated daily readings -> {yesterday_path}")

    generator = HoroscopeGenerator()
    combined  = {}

    for sign in generator.SIGNS:
        print(f"\nProcessing {sign.upper()}...")
        sign_data = existing.get(sign, {})

        # daily — always fresh
        print(f"  Generating daily...")
        daily = generator.generate_daily(sign)
        if daily:
            sign_data['daily'] = daily

        # monthly — only if month changed
        if regenerate_monthly:
            print(f"  Generating monthly...")
            monthly = generator.generate_monthly(sign)
            if monthly:
                sign_data['monthly'] = monthly

        # yearly — only if year changed
        if regenerate_yearly:
            print(f"  Generating yearly...")
            yearly = generator.generate_yearly(sign)
            if yearly:
                sign_data['yearly'] = yearly

        # do NOT store 'yesterday' inside horoscope.json
        sign_data.pop('yesterday', None)
        combined[sign] = sign_data

    save_json(today_path, combined)
    print(f"\nDone! Processed {len(combined)} signs.")


if __name__ == "__main__":
    main()

# def main():
#     print("=" * 60)
#     print("Signs By Numbers — Horoscope Generator")
#     print("=" * 60)

#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     today_path = os.path.join(base_dir, 'horoscope.json')

#     existing = load_json(today_path)
#     regenerate_monthly = needs_monthly_update(existing) or not existing
#     regenerate_yearly = needs_yearly_update(existing) or not existing

#     print(f"\nRegenerate monthly: {regenerate_monthly}")
#     print(f"Regenerate yearly:  {regenerate_yearly}")

#     generator = HoroscopeGenerator()
#     combined = {}

#     for sign in generator.SIGNS:
#         print(f"\nProcessing {sign.upper()}...")
#         sign_data = existing.get(sign, {})

#         # rotate today's daily -> yesterday
#         if sign_data.get('daily'):
#             sign_data['yesterday'] = sign_data['daily']
#             print(f"  Rotated daily -> yesterday")

#         # always generate fresh daily
#         print(f"  Generating daily...")
#         daily = generator.generate_daily(sign)
#         if daily:
#             sign_data['daily'] = daily

#         # generate monthly only if month changed
#         if regenerate_monthly:
#             print(f"  Generating monthly...")
#             monthly = generator.generate_monthly(sign)
#             if monthly:
#                 sign_data['monthly'] = monthly

#         # generate yearly only if year changed
#         if regenerate_yearly:
#             print(f"  Generating yearly...")
#             yearly = generator.generate_yearly(sign)
#             if yearly:
#                 sign_data['yearly'] = yearly

#         combined[sign] = sign_data

#     save_json(today_path, combined)
#     print(f"\nDone! Processed {len(combined)} signs.")
#     print(f"Output: {today_path}")


# if __name__ == "__main__":
#     main()
