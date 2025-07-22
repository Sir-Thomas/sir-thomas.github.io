from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re
import json

def get_requirements(reqs):
    level = re.search(r"Level (\d+)", reqs).group(1)
    str_req = re.search(r"STR: (\d+)", reqs)
    if str_req:
        str_req = str_req.group(1)
    else:
        str_req = 0
    dex = re.search(r"DEX: (\d+)", reqs)
    if dex:
        dex = dex.group(1)
    else:
        dex = 0
    int_req = re.search(r"INT: (\d+)", reqs)
    if int_req:
        int_req = int_req.group(1)
    else:
        int_req = 0
    luk = re.search(r"LUK: (\d+)", reqs)
    if luk:
        luk = luk.group(1)
    else:
        luk = 0
    return {
        "level": level,
        "str": str_req,
        "dex": dex,
        "int": int_req,
        "luk": luk
    }

def get_stats(stats):
    att_speed = re.search(r"Attack Speed: .+ \(Stage (\d+)\)", stats).group(1)
    str_bonus = re.search(r"STR: \+(\d+)", stats)
    if str_bonus:
        str_bonus = str_bonus.group(1)
    else:
        str_bonus = 0
    dex = re.search(r"DEX: \+(\d+)", stats)
    if dex:
        dex = dex.group(1)
    else:
        dex = 0
    int_bonus = re.search(r"INT: \+(\d+)", stats)
    if int_bonus:
        int_bonus = int_bonus.group(1)
    else:
        int_bonus = 0
    luk = re.search(r"LUK: \+(\d+)", stats)
    if luk:
        luk = luk.group(1)
    else:
        luk = 0
    max_hp = re.search(r"Max HP: \+(\d+)", stats)
    if max_hp:
        max_hp = max_hp.group(1)
    else:
        max_hp = 0
    max_mp = re.search(r"Max MP: \+(\d+)", stats)
    if max_mp:
        max_mp = max_mp.group(1)
    else:
        max_mp = 0
    att = re.search(r"Weapon Attack: \+(\d+)", stats).group(1)
    matt = re.search(r"Magic Attack: \+(\d+)", stats)
    if matt:
        matt = matt.group(1)
    else:
        matt = 0
    boss = re.search(r"Boss Damage: \+(\d+)%", stats)
    if boss:
        boss = boss.group(1)
    else:
        boss = 0
    ied = re.search(r"Ignored Enemy Defense: \+(\d+)%", stats)
    if ied:
        ied = ied.group(1)
    else:
        ied = 0
    damage = re.search(r"^Damage: \+(\d+)%", stats)
    if damage:
        damage = damage.group(1)
    else:
        damage = 0
    return {
        "attack_speed": att_speed,
        "str": str_bonus,
        "dex": dex,
        "int": int_bonus,
        "luk": luk,
        "max_hp": max_hp,
        "max_mp": max_mp,
        "attack": att,
        "magic_attack": matt,
        "boss_damage": boss,
        "ignore_enemy_defense": ied,
        "damage": damage
    }

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
        "requirements": get_requirements(cols[1].text.strip()),
    }

json_dump = json.dumps(items, indent=4)
with open(f"../data/{item_type.lower()}.json", "w") as outfile:
    outfile.write(json_dump)