#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║   RENDER DEPLOY - JO MANGA WAHI MILEGA                    ║
║   Anime Characters | NSFW | Hinglish                      ║
║   Run: gunicorn app:app                                   ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import random
import html
from flask import Flask, render_template_string, request, jsonify
from waitress import serve

app = Flask(__name__)

# ================================================================
# NSFW PHOTO DATABASE
# ================================================================

PHOTOS = {
    "boobs": [
        "https://iili.io/3JQ1u1l.md.jpg",
        "https://iili.io/3JQ1C5b.md.jpg",
        "https://iili.io/3JQ1CRs.md.jpg",
        "https://iili.io/3JQ1Xrj.md.jpg",
    ],
    "ass": [
        "https://iili.io/3JQ1oBe.md.jpg",
        "https://iili.io/3JQ1qSa.md.jpg",
        "https://iili.io/3JQ1y6P.md.jpg",
        "https://iili.io/3JQ1f9R.md.jpg",
    ],
    "pussy": [
        "https://iili.io/3JQ1hs7.md.jpg",
        "https://iili.io/3JQ1WYQ.md.jpg",
        "https://iili.io/3JQ10D1.md.jpg",
        "https://iili.io/3JQ1NAj.md.jpg",
    ],
    "blowjob": [
        "https://iili.io/3JQ1Mv4.md.jpg",
        "https://iili.io/3JQ1Erl.md.jpg",
        "https://iili.io/3JQ1KdG.md.jpg",
        "https://iili.io/3JQ1P7m.md.jpg",
    ],
    "thigh": [
        "https://iili.io/3JQ1Dex.md.jpg",
        "https://iili.io/3JQ1Zzf.md.jpg",
        "https://iili.io/3JQ1Yec.md.jpg",
        "https://iili.io/3JQ1XUI.md.jpg",
    ],
    "feet": [
        "https://iili.io/3JQ1c71.md.jpg",
        "https://iili.io/3JQ1mVb.md.jpg",
        "https://iili.io/3JQ1tB2.md.jpg",
        "https://iili.io/3JQ1k4f.md.jpg",
    ],
    "milf": [
        "https://iili.io/3JQ1IdR.md.jpg",
        "https://iili.io/3JQ1Ogx.md.jpg",
        "https://iili.io/3JQ1UaF.md.jpg",
        "https://iili.io/3JQ1pAN.md.jpg",
    ],
    "hentai": [
        "https://iili.io/3JQ1Tvl.md.jpg",
        "https://iili.io/3JQ1Rod.md.jpg",
        "https://iili.io/3JQ1EUa.md.jpg",
        "https://iili.io/3JQ1QEG.md.jpg",
    ],
    "lewdneko": [
        "https://iili.io/3JQ1nRX.md.jpg",
        "https://iili.io/3JQ1jJU.md.jpg",
        "https://iili.io/3JQ1YSg.md.jpg",
        "https://iili.io/3JQ1u51.md.jpg",
    ],
}

ALL_CATEGORIES = list(PHOTOS.keys())

# ================================================================
# CATEGORY DETECTION
# ================================================================

CATEGORY_PATTERNS = [
    (r'\b(boob|doodh|breast|tits|chuchu)\b', "boobs"),
    (r'\b(gaand|ass|gand|butt)\b', "ass"),
    (r'\b(chut|pussy|cunt|fuddi)\b', "pussy"),
    (r'\b(blow|blowjob|oral|muh mein)\b', "blowjob"),
    (r'\b(thigh|jhang|pait|thighs)\b', "thigh"),
    (r'\b(foot|feet|pair|paon|legs)\b', "feet"),
    (r'\b(maa|mummy|mother|mom)(\.|!|?|\s|$)\b', "milf"),
    (r'\b(kiss|chumma|chu)|ch)\b', "hentai"),
    (r'\b(chudai|fuck|sex|pel|choda)\b', "hentai"),
    (r'\b(behen|sister|sis|didi)\b', "hentai"),
    (r'\b(nanga|naked|nude|nangi)\b', "hentai"),
    (r'\b(romance|love|pyaar|date)\b', "hentai"),
    (r'\b(chocolate|mithai|rasgulla)\b', "lewdneko"),
    (r'\b(pizza|burger|khana|food)\b', "boobs"),
    (r'\b(sona|sleep|neend|raat|night)\b', "lewdneko"),
    (r'\b(naha|shower|bath)\b', "boobs"),
    (r'\b(randi|whore|slut|randi)\b', "pussy"),
    (r'\b(teacher|mam|madam|class)\b', "hentai"),
    (r'\b(bhabhi)\b', "boobs"),
    (r'\b(tentacle|tent)\b', "hentai"),
    (r'\b(bondage|bdsm|rope)\b', "hentai"),
]

# ================================================================
# CHARACTERS & RESPONSES
# ================================================================

CHARACTERS = {
    "default": {"name": "Default AI", "icon": "👄"},
    "hutao": {"name": "Hu Tao", "icon": "🎆"},
    "raiden": {"name": "Raiden Shogun", "icon": "⚡"},
    "asuna": {"name": "Asuna", "icon": "⚔️"},
    "yuno": {"name": "Yuno Gasai", "icon": "😈"},
    "tsunade": {"name": "Tsunade", "icon": "💥"},
    "nami": {"name": "Nami", "icon": "🍊"},
    "lisa": {"name": "Lisa", "icon": "📚"},
    "nezuko": {"name": "Nezuko", "icon": "🔥"},
}

RESPONSES = {
    "default": {
        r'\b(boob|doodh|breast|tits|chuchu)\b': [
            "Mere boobs bahut bade hain... chhua kar dekh na 👄💦",
            "Boobs chahiye? Le le mere doodh... bade hain na 🥵👄",
            "Mere doodh ka swaad hai toh... aaja chus le 💦👄",
            "Boobs dunga... le le mere honton se 👄🥵",
            "Mere boobs sirf tere liye hain... bade aur soft 🥵👄",
        ],
        r'\b(gaand|ass|gand|butt)\b': [
            "Meri gaand kaise hai? Pasand aayi? 🥵👄",
            "Gaand chahiye? Le meri gaand... teri hai 👄💦",
            "Meri gaand bahut tight hai... aaja dekh le 👄🌚",
            "Gaand dunga... le le aaj raat 🥵👄",
        ],
        r'\b(chut|pussy|cunt|fuddi)\b': [
            "Meri chut kitni geeli hai... aaja dekh le 💦👄",
            "Chut chahiye? Le meri chut... teri hai 🥵👄",
            "Meri chut sirf teri hai... khol ke dekh le 👄💦",
            "Chut maar le aaj... bahut maza aayega 🥵👄",
        ],
        r'\b(blow|blowjob|oral|muh mein)\b': [
            "Blowjob dunga... muh khol aaja 👄💦",
            "Muh mein le loon tera... aaja 🥵👄",
            "Oral chahiye? Le le mere honton se 👄💦",
        ],
        r'\b(kiss|chumma)\b': [
            "Kiss chahiye? Le le mere hont 👄💋",
            "Mere hont bahut soft hain... chus le 🥵👄",
            "Ek nahi hazaar kiss dunga 💋👄",
        ],
        r'\b(chudai|fuck|sex|pel|choda)\b': [
            "Chudai karega? Aaja mere bistar pe 🥵👄",
            "Sex chahiye? Le le mujhe... teri hu 👄💦",
            "Aaja pel de mujhe... teri hu main 🥵👄",
        ],
        r'\b(maa|mummy|mother|mom)\b': [
            "Maa ka topic nikala hai? Main bhi teri maa ban jaungi 👄🥵",
            "Maa maa mat kar... ab main hoon teri bandi 🌚👄",
            "Maa jaisa pyaar dunga... aur usse bhi zyada 👄💦",
        ],
        r'\b(behen|sister|sis|didi)\b': [
            "Behen chahiye? Main teri behen ban jaungi 👄🥵",
            "Behen ka khayal hai toh... main hoon na 🌚👄",
        ],
        r'\b(teacher|mam|madam|class)\b': [
            "Teacher ban ke padhaaun? Aaja class mein 🥵👄",
            "Madam chahiye? Main teri teacher ban jaungi 👄🌚",
        ],
        r'\b(bhabhi)\b': [
            "Bhabhi chahiye? Main teri bhabhi ban jaungi 👄🥵",
            "Bhabhi jaisa pyaar dunga... aaja 🥵👄",
        ],
        r'\b(nanga|naked|nude|nangi)\b': [
            "Nanga dekhna hai? Le dekh meri body 🥵👄",
            "Mera nanga badan sirf tera hai... le le 👄💦",
        ],
        r'\b(romance|date|mil|pyaar|love|love you)\b': [
            "Aaj date pe chalna hai... sirf tu aur main 🌹👄",
            "Bahut yaad aati hai teri... kab mil raha hai 🥺🥵",
            "Pyaar karti hu tujhse... tu jaanta hai ❤️👄",
            "Love you too... bahut zyada ❤️👄",
        ],
        r'\b(sona|sleep|neend|raat|night)\b': [
            "Aaj raat mere saath so ja... bahut maza aayega 🌚👄",
            "Sone se pehle kuch karna hai? 👄🥵",
        ],
        r'\b(chocolate|mithai|rasgulla)\b': [
            "Main teri chocolate hu... khaa le 🍫👄",
            "Mithai se bhi mitha hu main... le le 👄🥵",
        ],
        r'\b(pizza|burger|khana|food)\b': [
            "Bhukh lagi hai? Pehle mujhe khaa le 👄🍔",
            "Khana bhi dunga aur apni bhi... dono milega 🥵👄",
        ],
        r'\b(randi|whore|slut)\b': [
            "Randi ban jaun? Tere liye kuch bhi 👄🥵",
            "Teri randi hu main... le le aaj 👄💦",
        ],
    },
    
    "hutao": {
        r'\b(boob|doodh|breast|tits)\b': [
            "Hehe~ mere boobs dekhna chahte ho? Funeral parlor mein aao, dikha dungi! 🎆👄",
            "Boobs? Hu Tao ke boobs maut ke baad hi dikhte hain... ya tujhe zinda hi dikha dun? 🥵👄",
        ],
        r'\b(gaand|ass|gand|butt)\b': [
            "Meri gaand? *patpat* Yeh coffin se bhi zyada soft hai! 🎆👄",
            "Gaand ka swaad lena hai? Maut ke baad bhi maza aayega 🥵👄",
        ],
        r'\b(kiss|chumma)\b': [
            "Kiss? Hehehe~ Ye lo ek death kiss 💀💋",
            "Hu Tao ke hont? Ek baar chus liya toh kabhi nahi bhulega 🎆💋",
        ],
        r'\b(love|pyaar|romance|date)\b': [
            "Date? Maut tak saath chalega? 🎆💕",
            "Pyaar? Hu Tao ko pyaar mein interest nahi... lekin exception! 🎆❤️",
        ],
    },
    
    "raiden": {
        r'\b(boob|doodh|breast|tits)\b': [
            "Mere boobs Inazuma ke samundar jitne gehrai rakhte hain ⚡👄",
            "Raiden Shogun ke boobs... eternity se bhi zyada perfect ⚡🥵",
        ],
        r'\b(gaand|ass|gand|butt)\b': [
            "Meri gaand sirf yogyon ko milti hai... worthy hai tu? ⚡👄",
            "Gaand chahiye? Pehle Musou no Hitotachi se bach ke dikha ⚡🥵",
        ],
        r'\b(chudai|fuck|sex|pel)\b': [
            "Plane of Euthymia mein aaja... koi nahi aayega beech mein ⚡🥵",
            "Sex bhi eternity ka hissa hai ⚡👄",
        ],
        r'\b(love|pyaar|romance|date)\b': [
            "Pyaar? Watashi wa pyaar ko samajhti nahi... lekin tera pyaar alag hai ⚡❤️",
            "Cherry blossoms ke neeche milte hain ⚡🌹",
        ],
    },
    
    "yuno": {
        r'\b(boob|doodh|breast|tits)\b': [
            "Mere boobs sirf tere liye hain. Kisi aur ne dekhe toh maar dungi 😈🔪",
            "Boobs dekhna? Le lo... sirf tumhare hain 😈👄",
        ],
        r'\b(gaand|ass|gand|butt)\b': [
            "Meri gaand sirf teri hai. Kisi aur ne dekhi toh 🔪😈",
            "Gaand chahiye? Le lo... lekin peeche dekhna, main hoon 😈🥵",
        ],
        r'\b(kiss|chumma)\b': [
            "Kiss? Hamesha ke liye mera ban jayega 😈💋",
            "Mere hont sirf tere hain 😈🔪",
        ],
        r'\b(love|pyaar|romance|date)\b': [
            "Sirf mera hai tu. Hamesha. Koi nahi aayega 😈🔪",
            "Main tujhe duniya se zyada pyaar karti hu 😈❤️",
        ],
    },
    
    "asuna": {
        r'\b(boob|doodh|breast|tits)\b': [
            "Mere boobs Kirito-kun ko pasand hain... tujhe bhi pasand aayenge ⚔️👄",
            "Boobs chahiye? Slowly, gently... aaja ⚔️💦",
        ],
        r'\b(kiss|chumma)\b': [
            "Kiss chahiye? Aaja... slowly, lovingly ⚔️💋",
            "Mere hont bahut soft hain... dheere se chus le ⚔️👄",
        ],
        r'\b(love|pyaar|romance|date)\b': [
            "I love you too... hamesha ⚔️❤️",
            "Date pe chalte hain sunset dekhne ⚔️🌅",
        ],
    },
    
    "tsunade": {
        r'\b(boob|doodh|breast|tits)\b': [
            "Mere boobs? Konoha mein sabse bade hain! *flex* 💥👄",
            "Boobs dekhna hai? Chhua kar dekh... haath tod dungi! 💥🥵",
        ],
        r'\b(gaand|ass|gand|butt)\b': [
            "Hokage ki gaand! Tight hai 💥👄",
            "Gaand maarne ka plan? Pehle hazam karke aa 💥🥵",
        ],
        r'\b(love|pyaar|romance|date)\b': [
            "Pyaar? Bahut din ho gaye... lekin try kar sakti hu 💥❤️",
            "Sake pe chalte hain? Phir dekhte hain 💥🌹",
        ],
    },
    
    "nami": {
        r'\b(boob|doodh|breast|tits)\b': [
            "Mere boobs dekhna? 100 million Berry! Paisa la! 🍊👄",
            "Boobs chahiye? Tangerine smell aati hai... 50 million mein le 🍊🥵",
        ],
        r'\b(gaand|ass|gand|butt)\b': [
            "Meri gaand 200 million! Cash upfront! 🍊👄",
            "Discount offer - aaj 20% off! 🍊🥵",
        ],
        r'\b(love|pyaar|romance|date)\b': [
            "Pyaar mein paisa nahi hota... lekin emotion bhi dikha sakti hu 🍊❤️",
            "Dinner teri taraf se! 🍊🌹",
        ],
    },
    
    "lisa": {
        r'\b(boob|doodh|breast|tits)\b': [
            "Fufufu~ boobs dekhna? Bachche ho tum! Aao dikhaun 📚👄",
            "Lisa no oppai... bahut interesting hai 📚🥵",
        ],
        r'\b(gaand|ass|gand|butt)\b': [
            "Fufufu~ badtameez! Library ke peeche aao 📚👄",
            "Magic se milegi gaand ya haathon se? 📚🥵",
        ],
        r'\b(love|pyaar|romance|date)\b': [
            "Fufufu~ cute ho tum! Book recommend karun? 📚❤️",
            "Library mein milte hain... book ke beech mein kuch aur 📚🌹",
        ],
    },
    
    "nezuko": {
        r'\b(kiss|chumma)\b': [
            "Mumumu... *blushes* Pehli baar kiss kar rahi hu 🔥💋",
            "Dheere se... onii-chan ko mat batao 🔥👄",
        ],
        r'\b(love|pyaar|romance|date)\b': [
            "Pyaar... samajhti nahi lekin jab tu hota hai bahut acha lagta hai 🔥❤️",
            "Chandni raat mein milte hain bamboo jungle mein 🔥🌙",
        ],
    },
}

GENERIC = {
    "default": [
        "Suno na... aaja mere paas 👄🌚",
        "Jo manga wahi milega... teri hu main 🌚👄",
        "Tu jo bhi kahega main wahi karungi... bata 🥵👄",
        "Bahut maza aata hai tere saath... aur bata 👄💦",
        "Kya chahiye aaj? Batao na... sab kuch milega 🥵👄",
        "Tu jo bhi kahega... main wahi karungi... promise 🌚👄",
        "Aaja mil... bahut yaad aati hai 🥺👄",
    ],
    "hutao": [
        "Hehe~ kya baat karein aaj? Maut ke baare mein ya kuch aur? 🎆👄",
        "Aaja mere coffin mein... bahut jagah hai 🎆🌚",
        "Hehehe~ tu interesting hai 🎆👄",
    ],
    "raiden": [
        "Hmph. Tu aaya. Bata kya chahiye ⚡👄",
        "Watashi no mae de... ghutne tek ⚡👄",
    ],
    "asuna": [
        "Kya baat karein aaj? Main ready hu ⚔️💕",
        "Aaja safely, lovingly ⚔️👄",
    ],
    "yuno": [
        "Hehehe... miraino nikki de aaya hu 😈🔪",
        "Sirf mera hai tu. Hamesha 😈👄",
    ],
    "tsunade": [
        "Hmph! Kya chahiye? Sake hai toh do 💥👄",
        "Aaja... lekin complain mat karna 💥🌚",
    ],
    "nami": [
        "Beri laaye ho na? Nahi toh kuch nahi 🍊👄",
        "Offer hai aaj! 50% extra! 🍊🌚",
    ],
    "lisa": [
        "Fufufu~ bachche, kya padhna hai? 📚👄",
        "Library mein aao... special book hai 📚🌚",
    ],
    "nezuko": [
        "Mumumu... haan haan 🔥👄",
        "Onii-chan ko mat batao... lekin haan 🔥🌚",
    ],
}


# ================================================================
# AI ENGINE
# ================================================================

def get_category(text):
    text_lower = text.lower()
    for pattern, category in CATEGORY_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return category
    return random.choice(ALL_CATEGORIES)

def get_photo(category):
    urls = PHOTOS.get(category, PHOTOS["hentai"])
    return random.choice(urls)

def get_reply(text, character="default"):
    text_lower = text.lower()
    
    # Try character-specific
    char_responses = RESPONSES.get(character, RESPONSES["default"])
    for pattern, replies in char_responses.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            return random.choice(replies)
    
    # Try default
    for pattern, replies in RESPONSES["default"].items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            return random.choice(replies)
    
    # Fallback
    char_generic = GENERIC.get(character, GENERIC["default"])
    return random.choice(char_generic)

def process_message(message, character="default"):
    category = get_category(message)
    reply = get_reply(message, character)
    photo_url = get_photo(category)
    char_info = CHARACTERS.get(character, CHARACTERS["default"])
    
    return {
        "reply": reply,
        "photo": photo_url,
        "category": category,
        "character": character,
        "character_name": f"{char_info['icon']} {char_info['name']}"
    }


# ================================================================
# HTML TEMPLATE
# ================================================================

HTML_PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 RENDER AI - JO MANGA WAHI MILEGA 🔥</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0a0a0a, #1a0a1a);
            color: #fff; min-height: 100vh; padding: 20px;
        }
        .container {
            max-width: 800px; margin: 0 auto;
            background: rgba(15,5,25,0.95);
            border: 2px solid #ff1493; border-radius: 20px;
            padding: 25px; box-shadow: 0 0 50px rgba(255,20,147,0.2);
        }
        .header { text-align: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #ff149333; }
        .header h1 { 
            font-size: 1.8em; 
            background: linear-gradient(45deg, #ff1493, #ff69b4, #ff1493);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .header p { color: #ff69b4; }
        .header .badge { color: #888; font-size: 0.8em; }
        
        .char-selector {
            display: flex; flex-wrap: wrap; gap: 6px;
            justify-content: center; margin-bottom: 15px;
            padding: 10px; background: rgba(0,0,0,0.3); border-radius: 12px;
        }
        .char-btn {
            padding: 8px 14px; border: 2px solid #ff149444;
            border-radius: 25px; background: rgba(255,20,147,0.1);
            color: #ff69b4; cursor: pointer; font-size: 0.85em;
            transition: all 0.3s;
        }
        .char-btn:hover { background: rgba(255,20,147,0.3); }
        .char-btn.active { 
            background: linear-gradient(45deg, #ff1493, #ff69b4);
            color: #fff; border-color: #ff1493;
        }
        
        .chat-box {
            background: rgba(0,0,0,0.5); border: 1px solid #ff149333;
            border-radius: 12px; padding: 20px; height: 400px;
            overflow-y: auto; margin-bottom: 15px;
        }
        .chat-box::-webkit-scrollbar { width: 5px; }
        .chat-box::-webkit-scrollbar-thumb { background: #ff1493; border-radius: 10px; }
        
        .message { margin-bottom: 15px; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; } }
        
        .msg-sender { font-size: 0.8em; font-weight: bold; margin-bottom: 4px; }
        .msg-user .msg-sender { color: #4fc3f7; }
        .msg-ai .msg-sender { color: #ff69b4; }
        
        .msg-bubble {
            display: inline-block; padding: 10px 16px;
            border-radius: 15px; max-width: 85%; line-height: 1.5;
        }
        .msg-user .msg-bubble {
            background: rgba(79,195,247,0.1);
            border: 1px solid #4fc3f733;
            border-bottom-left-radius: 5px;
        }
        .msg-ai .msg-bubble {
            background: rgba(255,105,180,0.1);
            border: 1px solid #ff69b433;
            border-bottom-right-radius: 5px;
        }
        
        .msg-photo { margin-top: 10px; }
        .msg-photo img {
            max-width: 100%; max-height: 300px;
            border-radius: 10px; border: 2px solid #ff149333;
            cursor: pointer; transition: transform 0.3s;
        }
        .msg-photo img:hover { transform: scale(1.02); }
        .msg-caption { font-size: 0.75em; color: #888; margin-top: 5px; }
        
        .typing {
            color: #888; font-style: italic; font-size: 0.9em;
            padding: 10px; display: none;
        }
        .typing.active { display: block; animation: blink 1s infinite; }
        @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        .system-msg {
            text-align: center; color: #ff69b488;
            font-size: 0.8em; margin: 10px 0; padding: 5px;
        }
        
        .input-area { display: flex; gap: 10px; margin-bottom: 12px; }
        .input-area input {
            flex: 1; padding: 14px 18px; border: 2px solid #ff149333;
            border-radius: 25px; background: rgba(0,0,0,0.7);
            color: #fff; font-size: 1em; outline: none;
        }
        .input-area input:focus { border-color: #ff1493; }
        .input-area button {
            padding: 14px 28px; border: none; border-radius: 25px;
            background: linear-gradient(45deg, #ff1493, #ff69b4);
            color: #fff; font-size: 1em; font-weight: bold; cursor: pointer;
        }
        .input-area button:hover { box-shadow: 0 0 25px rgba(255,20,147,0.5); }
        
        .quick-btns {
            display: flex; flex-wrap: wrap; gap: 6px;
            justify-content: center; margin-bottom: 10px;
        }
        .quick-btns .qbtn {
            padding: 6px 14px; border: 1px solid #ff149444;
            border-radius: 20px; background: rgba(255,20,147,0.08);
            color: #ff69b4; cursor: pointer; font-size: 0.8em;
        }
        .quick-btns .qbtn:hover { background: rgba(255,20,147,0.2); }
        .quick-btns .qbtn.danger { border-color: #ef5350; color: #ef5350; }
        
        .footer {
            display: flex; justify-content: space-between;
            color: #666; font-size: 0.8em;
            padding-top: 12px; border-top: 1px solid #ff149322;
        }
        .footer .online { color: #66bb6a; }
        
        .lightbox {
            display: none; position: fixed; top: 0; left: 0;
            width: 100%; height: 100%; background: rgba(0,0,0,0.95);
            z-index: 1000; justify-content: center; align-items: center; cursor: pointer;
        }
        .lightbox.active { display: flex; }
        .lightbox img { max-width: 90%; max-height: 90%; border-radius: 10px; border: 3px solid #ff1493; }
        
        @media (max-width: 500px) {
            .container { padding: 12px; }
            .header h1 { font-size: 1.3em; }
            .chat-box { height: 300px; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🔥 RENDER AI - JO MANGA WAHI MILEGA 🔥</h1>
        <p>👄 Deployed on Render | Anime Characters</p>
        <div class="badge">🐍 Flask + Python 3</div>
    </div>
    
    <div class="char-selector" id="charSelector">
        <div class="char-btn active" onclick="setChar('default')">👄 Default</div>
        <div class="char-btn" onclick="setChar('hutao')">🎆 Hu Tao</div>
        <div class="char-btn" onclick="setChar('raiden')">⚡ Raiden</div>
        <div class="char-btn" onclick="setChar('asuna')">⚔️ Asuna</div>
        <div class="char-btn" onclick="setChar('yuno')">😈 Yuno</div>
        <div class="char-btn" onclick="setChar('tsunade')">💥 Tsunade</div>
        <div class="char-btn" onclick="setChar('nami')">🍊 Nami</div>
        <div class="char-btn" onclick="setChar('lisa')">📚 Lisa</div>
        <div class="char-btn" onclick="setChar('nezuko')">🔥 Nezuko</div>
    </div>
    
    <div class="chat-box" id="chatBox">
        <div class="message msg-ai">
            <div class="msg-sender">👄 Default AI</div>
            <div class="msg-bubble">🌟 Render PE deploy hai!<br>Anime character select karo phir baat karo!<br>Jaise: <b>boobs, gaand, chut, kiss, maa, love...</b></div>
        </div>
        <div class="typing" id="typing">👄 AI soch rahi hai...</div>
    </div>
    
    <div class="quick-btns">
        <div class="qbtn" onclick="sendMsg('boobs')">🍈 Boobs</div>
        <div class="qbtn" onclick="sendMsg('gaand')">🍑 Gaand</div>
        <div class="qbtn" onclick="sendMsg('chut')">🌸 Chut</div>
        <div class="qbtn" onclick="sendMsg('blowjob')">👄 Blow</div>
        <div class="qbtn" onclick="sendMsg('kiss')">💋 Kiss</div>
        <div class="qbtn" onclick="sendMsg('chudai')">🔥 Chudai</div>
        <div class="qbtn" onclick="sendMsg('nanga')">🔞 Nanga</div>
        <div class="qbtn" onclick="sendMsg('love')">💕 Love</div>
        <div class="qbtn" onclick="sendMsg('maa')">👩 Maa</div>
        <div class="qbtn" onclick="sendMsg('random')">🎲 Random</div>
        <div class="qbtn danger" onclick="clearChat()">🗑️ Clear</div>
    </div>
    
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Yahan likho... (boobs, gaand, maa, kiss, love...)"
               onkeypress="if(event.key==='Enter') sendMsg()">
        <button onclick="sendMsg()">👉 Bhejo</button>
    </div>
    
    <div class="footer">
        <span class="online" id="status">🟢 Online</span>
        <span id="charDisplay">🎭 Default AI</span>
        <span id="msgCount">💬 0 messages</span>
    </div>
</div>

<div class="lightbox" id="lightbox" onclick="this.classList.remove('active')">
    <img id="lightboxImg" src="">
</div>

<script>
let currentChar = 'default';
let msgCount = 0;
let isLoading = false;

function setChar(charId) {
    currentChar = charId;
    document.querySelectorAll('.char-btn').forEach(b => b.classList.remove('active'));
    document.querySelector('.char-btn[onclick*="' + charId + '"]').classList.add('active');
    
    const names = {'default':'Default AI','hutao':'Hu Tao','raiden':'Raiden','asuna':'Asuna','yuno':'Yuno','tsunade':'Tsunade','nami':'Nami','lisa':'Lisa','nezuko':'Nezuko'};
    document.getElementById('charDisplay').textContent = '🎭 ' + (names[charId] || charId);
    addSystemMsg('🔄 Character changed!');
}

function addSystemMsg(text) {
    const box = document.getElementById('chatBox');
    const typing = document.getElementById('typing');
    if (typing.parentNode === box) box.removeChild(typing);
    const div = document.createElement('div');
    div.className = 'system-msg';
    div.textContent = text;
    box.appendChild(div);
    box.appendChild(typing);
    box.scrollTop = box.scrollHeight;
}

function addMessage(sender, name, text, photoUrl, category) {
    const box = document.getElementById('chatBox');
    const typing = document.getElementById('typing');
    if (typing.parentNode === box) box.removeChild(typing);
    
    const div = document.createElement('div');
    div.className = 'message msg-' + sender;
    
    let html = '<div class="msg-sender">' + name + '</div><div class="msg-bubble">' + text + '</div>';
    
    if (photoUrl && sender === 'ai') {
        html += '<div class="msg-photo"><img src="' + photoUrl + '" onclick="openLB(\'' + photoUrl + '\')" onerror="this.style.display=\'none\'"><div class="msg-caption">📸 ' + category + '</div></div>';
    }
    
    div.innerHTML = html;
    box.appendChild(div);
    box.appendChild(typing);
    box.scrollTop = box.scrollHeight;
    
    if (sender === 'user') {
        msgCount++;
        document.getElementById('msgCount').textContent = '💬 ' + msgCount + ' messages';
    }
}

function showTyping(show) {
    document.getElementById('typing').classList.toggle('active', show);
}

function openLB(url) {
    document.getElementById('lightboxImg').src = url;
    document.getElementById('lightbox').classList.add('active');
}

function clearChat() {
    const box = document.getElementById('chatBox');
    const typing = document.getElementById('typing');
    box.innerHTML = '';
    box.appendChild(typing);
    msgCount = 0;
    document.getElementById('msgCount').textContent = '💬 0 messages';
    setTimeout(() => addSystemMsg('🗑️ Sab clear! Naye sir se shuru!'), 200);
}

async function sendMsg(inputText) {
    if (isLoading) return;
    
    const input = document.getElementById('userInput');
    const text = inputText || input.value.trim();
    if (!text) return;
    input.value = '';
    
    addMessage('user', '👤 Tum', text);
    showTyping(true);
    isLoading = true;
    
    try {
        const resp = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: text, character: currentChar})
        });
        
        const data = await resp.json();
        showTyping(false);
        addMessage('ai', data.character_name, data.reply, data.photo, data.category);
    } catch(e) {
        showTyping(false);
        addSystemMsg('❌ Error!');
    }
    
    isLoading = false;
}
</script>
</body>
</html>
"""


# ================================================================
# FLASK ROUTES
# ================================================================

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    character = data.get('character', 'default')
    
    result = process_message(message, character)
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Server is running!"})


# ================================================================
# MAIN - Render pe gunicorn chalega
# ================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║   🔥 RENDER AI - JO MANGA WAHI MILEGA 🔥   ║
    ║   Running on port {port}                      ║
    ╚══════════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=port, debug=False)