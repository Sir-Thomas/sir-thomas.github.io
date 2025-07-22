from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re
import json
import firebase_admin
from firebase_admin import credentials, firestore
import os

weapon_class_requirements = {
    "Bladecaster": ["Adele"],
    "Soul Shooter": ["Angelic Buster"],
    "Polearm": ["Aran", "Dark Knight"],
    "Staff": [
        "Arch Mage (Fire, Poison)", "Arch Mage (Ice, Lightning)", "Battle Mage",
        "Bishop", "Blaze Wizard", "Evan"
    ],
    "Wand": [
        "Arch Mage (Fire, Poison)", "Arch Mage (Ice, Lightning)", "Bishop", "Blaze Wizard", "Evan"
    ],
    "Knuckle": [
        "Ark", "Buccaneer", "Shade", "Thunder Breaker"
    ],
    "Arm Cannon": ["Blaster"],
    "Bow": ["Bowmaster", "Wind Archer"],
    "Chain": ["Cadena"],
    "Hand Cannon": ["Cannoneer"],
    "Gun": ["Corsair", "Mechanic"],
    "Spear": ["Dark Knight"],
    "One-Handed Sword": [
        "Dawn Warrior", "Hero", "Mihile", "Paladin"
    ],
    "Two-Handed Sword": [
        "Dawn Warrior", "Hero", "Kaiser", "Paladin"
    ],
    "Desperado": ["Demon Avenger"],
    "One-Handed Blunt Weapon": [
        "Demon Slayer", "Paladin", "Hero"
    ],
    "One-Handed Axe": [
        "Demon Slayer", "Hero", "Paladin"
    ],
    "Dagger": ["Dual Blade", "Shadower"],
    "Katana": ["Hayato"],
    "Two-Handed Axe": ["Hero", "Paladin"],
    "Two-Handed Blunt Weapon": ["Paladin", "Hero"],
    "Ritual Fan": ["Hoyoung"],
    "Lucent Gauntlet": ["Illium"],
    "Whispershot": ["Kain"],
    "Fan": ["Kanna"],
    "Chakram": ["Khali"],
    "Psy-limiter": ["Kinesis"],
    "Wand": ["Lara"],
    "Shining Rod": ["Luminous"],
    "Memorial Staff": ["Lynn"],
    "Crossbow": ["Marksman", "Wild Hunter"],
    "Dual Bowguns": ["Mercedes"],
    "Martial Brace": ["Mo Xuan"],
    "Claw": ["Night Lord", "Night Walker"],
    "Ancient Bow": ["Pathfinder"],
    "Cane": ["Phantom"],
    "Celestial Light": ["Sia Astelle"],
    "Whip Blade": ["Xenon"],
    "Long Sword": ["Zero"],
    "Heavy Sword": ["Zero"],
}

path = ""
for item in os.listdir("./tools/creds"):
    path = os.path.join("./tools/creds", item)
cred = credentials.Certificate(path)
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_requirements(reqs, classes=None, archetypes=["warrior", "mage", "bowman", "thief", "pirate"]):
    formatted_reqs = {
        "archetypes": archetypes
    }
    if classes:
        formatted_reqs["classes"] = classes
    formatted_reqs["level"] = re.search(r"Level (\d+)", reqs).group(1)
    str_req = re.search(r"STR: (\d+)", reqs)
    if str_req:
        formatted_reqs["str"] = str_req.group(1)
    dex = re.search(r"DEX: (\d+)", reqs)
    if dex:
        formatted_reqs["dex"] = dex.group(1)
    int_req = re.search(r"INT: (\d+)", reqs)
    if int_req:
        formatted_reqs["int"] = int_req.group(1)
    luk = re.search(r"LUK: (\d+)", reqs)
    if luk:
        formatted_reqs["luk"] = luk.group(1)
    return formatted_reqs

def get_stats(stats):
    formatted_stats = {}
    att_speed = re.search(r"Attack Speed: .+ \(Stage (\d+)\)", stats)
    if att_speed:
        formatted_stats["att_speed"] = att_speed.group(1)
    str_bonus = re.search(r"STR: \+(\d+)", stats)
    if str_bonus:
        formatted_stats["str"] = str_bonus.group(1)
    dex = re.search(r"DEX: \+(\d+)", stats)
    if dex:
        formatted_stats["dex"] = dex.group(1)
    int_bonus = re.search(r"INT: \+(\d+)", stats)
    if int_bonus:
        formatted_stats["int"] = int_bonus.group(1)
    luk = re.search(r"LUK: \+(\d+)", stats)
    if luk:
        formatted_stats["luk"] = luk.group(1)
    max_hp = re.search(r"Max HP: \+(\d+)", stats)
    if max_hp:
        formatted_stats["max_hp"] = max_hp.group(1)
    max_mp = re.search(r"Max MP: \+(\d+)", stats)
    if max_mp:
        formatted_stats["max_mp"] = max_mp.group(1)
    att = re.search(r"Weapon Attack: \+(\d+)", stats)
    if att:
        formatted_stats["att"] = att.group(1)
    matt = re.search(r"Magic Attack: \+(\d+)", stats)
    if matt:
        formatted_stats["matt"] = matt.group(1)
    boss = re.search(r"Boss Damage: \+(\d+)%", stats)
    if boss:
        formatted_stats["boss"] = boss.group(1)
    ied = re.search(r"Ignored Enemy Defense: \+(\d+)%", stats)
    if ied:
        formatted_stats["ied"] = ied.group(1)
    damage = re.search(r"^Damage: \+(\d+)%", stats)
    if damage:
        formatted_stats["damage"] = damage.group(1)
    return formatted_stats

item_type = "Staff"
url = f"https://maplestorywiki.net/w/{item_type}"
items = {}

session = HTMLSession()
r = session.get(url)
r.html.render()

soup = BeautifulSoup(r.html.html, "html.parser")
table = soup.find("table", class_="wikitable")
rows = table.find_all("tr")
del rows[0]
for row in rows:
    cols = row.find_all("td")
    name = cols[0].find("b").find("a").text.strip()
    image = cols[0].find("img")["src"]
    items[name] = {
        "image": image,
        "stats": get_stats(cols[2].text.strip()),
        "requirements": get_requirements(cols[1].text.strip(), weapon_class_requirements[item_type], archetypes=["mage"]),
    }

for key, value in items.items():
    db.collection("items").document(key).set(value)
