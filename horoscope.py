"""
Groq Horoscope Generator
Generates daily, monthly, and yearly horoscopes for all zodiac signs using the Groq API
"""

import requests
import os
import hashlib
import random
from datetime import datetime
import time


class HoroscopeGenerator:

    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"

    SIGNS = [
        'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
        'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'
    ]

    SIGN_TRAITS = {
        'aries': 'bold, energetic, and pioneering',
        'taurus': 'grounded, patient, and determined',
        'gemini': 'curious, adaptable, and communicative',
        'cancer': 'intuitive, nurturing, and emotional',
        'leo': 'confident, creative, and generous',
        'virgo': 'analytical, practical, and detail-oriented',
        'libra': 'balanced, diplomatic, and charming',
        'scorpio': 'intense, passionate, and transformative',
        'sagittarius': 'adventurous, optimistic, and philosophical',
        'capricorn': 'ambitious, disciplined, and persistent',
        'aquarius': 'innovative, independent, and humanitarian',
        'pisces': 'dreamy, empathetic, and artistic'
    }

    THEMES = [
        'communication and clarity', 'rest and reflection', 'bold action and risk-taking',
        'finances and practical decisions', 'relationships and emotional depth',
        'creativity and self-expression', 'ambition and career focus',
        'healing and letting go', 'new beginnings and fresh starts',
        'patience and steady progress', 'intuition and inner wisdom',
        'social connections and community'
    ]

    FOCUS_AREAS = [
        'romantic love', 'career advancement', 'personal finances',
        'physical health', 'personal growth', 'friendship and social life',
        'family dynamics', 'creative pursuits', 'mental health and stress',
        'long-term goals', 'daily habits and routines', 'self-confidence'
    ]

    STYLES = [
        'terse and punchy — short sharp sentences, no fluff, reads like a telegram',
        'warm and conversational — like advice from a close friend over coffee',
        'dramatic and cinematic — big stakes, vivid imagery, like a movie trailer voiceover',
        'blunt and direct — no softening, just the hard truth delivered plainly',
        'poetic and lyrical — metaphor-heavy, slower rhythm, almost song-like',
        'clinical and precise — structured, specific, reads like a smart newsletter',
        'urgent and pressured — there is a deadline, something must happen today',
        'gentle and reassuring — soft tone, steady encouragement, nothing is catastrophic',
        'mysterious and cryptic — holds something back, leaves the reader thinking',
        'sharp and witty — dry humor, slightly ironic, intelligent edge',
        'nostalgic and reflective — looking back to move forward, emotionally textured',
        'commanding and motivational — second person imperative, push them off the ledge',
    ]

    FORMATS = [
        'start with a specific scene or situation, then zoom out to the lesson',
        'start with the obstacle, then reveal the hidden advantage inside it',
        'start with what NOT to do today, then pivot to what will actually work',
        'start mid-thought as if continuing a conversation already in progress',
        'open with a single sharp question, then answer it across the remaining sentences',
        'lead with the outcome first, then explain what needs to happen to reach it',
        'start with something the person has been feeling but hasn\'t said out loud',
        'describe a choice between two paths — make one clearly right without stating it',
        'begin with a physical sensation or image that becomes a metaphor',
        'open with a short blunt statement of fact, then unpack why it matters today',
        'start with what someone else needs from them, then flip to what they need for themselves',
        'begin with the worst case fear, then immediately and specifically dismantle it',
    ]

    MOODS = [
        'cautious and introspective', 'bold and decisive', 'warm and romantic',
        'grounded and practical', 'restless and curious', 'hopeful and optimistic',
        'reflective and healing', 'sharp and ambitious', 'playful and light',
        'serious and determined', 'tender and vulnerable', 'energized and confident'
    ]

    OPENERS = [
        "A decision you've been avoiding demands an answer",
        "Something small has been quietly draining you",
        "Your instincts are sharper than usual right now",
        "There's an opportunity hiding in plain sight",
        "The tension you've been carrying has a source",
        "A pattern is becoming impossible to ignore",
        "You're closer to a breakthrough than you realize",
        "Someone in your life needs a boundary, not a conversation",
        "The timing on something is finally working in your favor",
        "Rest isn't laziness right now — it's strategy",
        "An old habit is costing you more than it's worth",
        "You've outgrown something and you already know it",
    ]

    def __init__(self):
        self.token = os.environ.get('GROQ_API_KEY', '')
        self.headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }

    def _pick(self, pool, seed):
        index = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(pool)
        return pool[index]

    def _daily_assignments(self, date_str):
        rng = random.Random(date_str)
        pools = [
            self.FOCUS_AREAS[:],
            self.STYLES[:],
            self.FORMATS[:],
            self.MOODS[:],
            self.OPENERS[:],
        ]
        shuffled = []
        for pool in pools:
            rng.shuffle(pool)
            shuffled.append({sign: pool[i] for i, sign in enumerate(self.SIGNS)})
        return shuffled

    def _call_api(self, system_prompt, user_prompt, max_tokens=300):
        payload = {
            'model': self.MODEL,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': 0.95
        }
        try:
            response = requests.post(self.API_URL, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            text = response.json()['choices'][0]['message']['content'].strip()
            time.sleep(1)
            return text
        except requests.RequestException as e:
            print("API error: " + str(e))
            return None

    def generate_daily(self, sign):
        if sign not in self.SIGNS:
            return None

        today = datetime.now().strftime('%B %d, %Y')
        traits = self.SIGN_TRAITS.get(sign, '')
        theme = self._pick(self.THEMES, today + sign)

        focuses, styles, formats, moods, openers = self._daily_assignments(today)

        system = (
            'You are a master astrologer who writes horoscopes with radical variety. '
            'Each horoscope must feel like it was written by a completely different person '
            'in a completely different mood. You never default to a template. '
            'Absolutely forbidden: "inner wisdom", "inner voice", "the universe", '
            '"tap into", "cosmic", "journey", "manifest", "energy", "as you", "today is a", "as a [sign]".'
        )

        user = (
            f'Write a horoscope for {sign.capitalize()} — {today}.\n\n'
            f'SIGN: {traits}\n'
            f'THEME: {theme}\n'
            f'FOCUS: {focuses[sign]} only\n'
            f'MOOD: {moods[sign]}\n'
            f'WRITING STYLE: {styles[sign]}\n'
            f'STRUCTURE: {formats[sign]}\n'
            f'OPENING IDEA (rewrite in your own words): "{openers[sign]}"\n\n'
            f'OUTPUT RULES:\n'
            f'- 3 to 4 sentences only\n'
            f'- Name one specific, concrete action or decision\n'
            f'- Return only the horoscope paragraph, nothing else'
        )

        text = self._call_api(system, user, max_tokens=250)
        if not text:
            return None

        return {
            'summary': text,
            'date': today,
            'generated_at': datetime.now().isoformat()
        }
    def generate_monthly(self, sign):
        if sign not in self.SIGNS:
            return None
    
        now = datetime.now()
        month_year = now.strftime('%B %Y')
        traits = self.SIGN_TRAITS.get(sign, '')
    
        system = (
            'You are an astrologer writing monthly forecasts, and your tone should vary widely. '
            'Depending on what feels most fitting, you may write in a poetic, blunt, cinematic, analytical, '
            'warm, symbolic, conversational, or sharply direct voice. '
            'Focus on short-term (30-day) developments with concrete themes in love, career, finances, health, '
            'or personal growth. '
            'Avoid vague spiritual language. Forbidden words: "universe", "manifest", "energy", "journey", "tap into".'
        )
    
        user = (
            f'Write a monthly horoscope for {sign.capitalize()} for {month_year}.\n\n'
            f'SIGN TRAITS: {traits}\n\n'
            f'STYLE GUIDANCE:\n'
            f'- Choose a distinct tone (e.g., warm, sharp, poetic, clinical, dramatic, reflective, symbolic, or witty)\n'
            f'- Choose a structure that fits the tone (e.g., open with a tension, start with a question, begin with an early-month shift, or lead with the month\'s biggest opportunity)\n\n'
            f'OUTPUT RULES:\n'
            f'- 6 to 8 sentences\n'
            f'- Cover at least two life areas (love, career, finances, health, or personal growth)\n'
            f'- Name one key opportunity and one challenge for the month\n'
            f'- Return only the forecast paragraph, nothing else'
        )
    
        text = self._call_api(system, user, max_tokens=400)
        if not text:
            return None
    
        return {
            'summary': text,
            'period': month_year,
            'generated_at': datetime.now().isoformat()
        }

    def generate_yearly(self, sign):
        if sign not in self.SIGNS:
            return None
    
        year = datetime.now().strftime('%Y')
        traits = self.SIGN_TRAITS.get(sign, '')
    
        system = (
            'You are a senior astrologer writing annual forecasts, and your tone should vary widely. '
            'Depending on what feels most fitting, you may write in a mythic, cinematic, analytical, reflective, '
            'symbolic, commanding, warm, or sharply direct voice. '
            'Break the year into four seasonal phases — Winter, Spring, Summer, and Fall — and describe how each season '
            'shifts the emotional, relational, and practical themes for the sign. '
            'For this forecast, randomly select 3–4 themes from the following list and weave them naturally across the seasons: '
            'communication and clarity; rest and reflection; bold action and risk-taking; finances and practical decisions; '
            'relationships and emotional depth; creativity and self-expression; ambition and career focus; healing and letting go; '
            'new beginnings and fresh starts; patience and steady progress; intuition and inner wisdom; social connections and community. '
            'Also randomly select 3–4 focus areas from the following list and incorporate them meaningfully: '
            'romantic love; career advancement; personal finances; physical health; personal growth; friendship and social life; '
            'family dynamics; creative pursuits; mental health and stress; long-term goals; daily habits and routines; self-confidence. '
            'Avoid vague spiritual language. Forbidden words: "universe", "manifest", "energy", "journey", "tap into".'
        )
    
        user = (
            f'Write a yearly horoscope overview for {sign.capitalize()} for {year}.\n\n'
            f'SIGN TRAITS: {traits}\n\n'
            f'STYLE GUIDANCE:\n'
            f'- Choose a tone that feels expansive and long-range (e.g., mythic, cinematic, analytical, reflective, symbolic, or motivational)\n'
            f'- Use a structure based on the four seasons: Winter (early year), Spring (rising momentum), Summer (peak themes), Fall (integration and resolution)\n'
            f'- Use only 3–4 randomly selected THEMES and 3–4 randomly selected FOCUS AREAS from the lists provided\n\n'
            f'OUTPUT RULES:\n'
            f'- 8 to 12 sentences\n'
            f'- Clearly reference seasonal phases (Winter, Spring, Summer, Fall)\n'
            f'- Address love, career, and personal evolution using the selected themes and focus areas\n'
            f'- End with an empowering statement about what this year means for the sign\n'
            f'- Return only the overview paragraph, nothing else'
        )
    
        text = self._call_api(system, user, max_tokens=500)
        if not text:
            return None
    
        return {
            'overview': text,
            'year': year,
            'generated_at': datetime.now().isoformat()
        }

