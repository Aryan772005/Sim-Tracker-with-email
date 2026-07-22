#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PhoneXtract v5.0 — OSINT Intelligence Suite
Created by : Aryan Singh Tarinai
For Educational & OSINT Use Only

Modules  :  Phone Number Analysis  +  Email Address Analysis
"""

import os
import re
import sys
import json
import time
import socket
import hashlib
import argparse
import threading
import itertools
import requests
from datetime import datetime

import phonenumbers
from phonenumbers import (
    geocoder, carrier, number_type, timezone,
    is_valid_number, is_possible_number,
    region_code_for_number, PhoneNumberFormat, format_number,
)
from colorama import init, Fore, Back, Style

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False

init(autoreset=True, strip=False)
VERSION = "5.0"

# ═══════════════════════════════════════════════════════════════════════════════
#  UNICODE / SYMBOL CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════
try:
    "◐◓◑◒✔✗►◆●→".encode(sys.stdout.encoding or "utf-8")
    U = True
except Exception:
    U = False

SPIN_F  = ["◐","◓","◑","◒"] if U else ["|","/","-","\\"]
ICO_OK  = "✔" if U else "+"
ICO_ERR = "✗" if U else "x"
ICO_WRN = "○" if U else "?"
ARR     = "►" if U else ">"
DIA     = "◆" if U else "*"
BUL     = "●" if U else "."
ARW     = "→" if U else "->"

# ═══════════════════════════════════════════════════════════════════════════════
#  HTTP HEADERS
# ═══════════════════════════════════════════════════════════════════════════════
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Referer": "https://www.google.com/",
    "DNT": "1",
}

# ═══════════════════════════════════════════════════════════════════════════════
#  ANIMATED SPINNER
# ═══════════════════════════════════════════════════════════════════════════════
class Spinner:
    def __init__(self, label, width=24):
        self.label = label
        self.width = width
        self._stop  = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        label_fmt = self.label.ljust(self.width)
        for f in itertools.cycle(SPIN_F):
            if self._stop.is_set():
                break
            sys.stdout.write(
                f"\r  {Fore.CYAN}{f}{Style.RESET_ALL}  "
                f"{Fore.CYAN}{label_fmt}{Style.RESET_ALL}  {Fore.WHITE}scanning...{Style.RESET_ALL}"
            )
            sys.stdout.flush()
            time.sleep(0.12)

    def start(self):
        self._thread.start()

    def ok(self, result):
        self._finish(Fore.GREEN + ICO_OK, Fore.GREEN, result)

    def warn(self, result):
        self._finish(Fore.YELLOW + ICO_WRN, Fore.YELLOW, result)

    def fail(self, result="FAILED"):
        self._finish(Fore.RED + ICO_ERR, Fore.RED, result)

    def _finish(self, icon, color, result):
        self._stop.set()
        self._thread.join()
        label_fmt = self.label.ljust(self.width)
        sys.stdout.write(
            f"\r  {icon}{Style.RESET_ALL}  "
            f"{Fore.CYAN}{label_fmt}{Style.RESET_ALL}  {color}{result}{Style.RESET_ALL}\n"
        )
        sys.stdout.flush()


# ═══════════════════════════════════════════════════════════════════════════════
#  TERMINAL / UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
W = 70   # total terminal width for boxes

def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def _box_top(w=W):
    return Fore.GREEN + "╔" + "═" * (w - 2) + "╗" + Style.RESET_ALL

def _box_mid(w=W):
    return Fore.GREEN + "╠" + "═" * (w - 2) + "╣" + Style.RESET_ALL

def _box_bot(w=W):
    return Fore.GREEN + "╚" + "═" * (w - 2) + "╝" + Style.RESET_ALL

def _box_row(text, w=W, color=Fore.WHITE):
    inner = w - 4   # 2 for ║ + space each side
    line  = text[:inner].ljust(inner)
    return Fore.GREEN + "║ " + color + line + Fore.GREEN + " ║" + Style.RESET_ALL

def _box_blank(w=W):
    return _box_row("", w)


def startup_animation():
    msgs = [
        "Initializing OSINT modules",
        "Loading phone intelligence",
        "Loading email intelligence",
        "Configuring OSINT links",
        "Ready",
    ]
    print()
    for msg in msgs:
        for f in SPIN_F * 3:
            sys.stdout.write(f"\r  {Fore.CYAN}{f}  {msg}...{Style.RESET_ALL}  ")
            sys.stdout.flush()
            time.sleep(0.06)
    sys.stdout.write(f"\r  {Fore.GREEN}{ICO_OK}  All modules loaded.{Style.RESET_ALL}           \n")
    sys.stdout.flush()
    time.sleep(0.4)


def banner():
    print(_box_top())
    print(_box_blank())
    art = [
        r" |  _ \| |__   ___  _ __   ___\ \/ / | |_ _ __ __ _  ___| |_",
        r" | |_) | '_ \ / _ \| '_ \ / _ \\  /  | __| '__/ _` |/ __| __|",
        r" |  __/| | | | (_) | | | |  __//  \  | |_| | | (_| | (__| |_",
        r" |_|   |_| |_|\___/|_| |_|\___/_/\_\  \__|_|  \__,_|\___|\___|",
    ]
    colors = [Fore.CYAN, Fore.CYAN, Fore.CYAN, Fore.CYAN]
    for line, col in zip(art, colors):
        print(_box_row(line, color=col))
    print(_box_blank())
    print(_box_mid())
    print(_box_row(f"  {DIA}  OSINT Intelligence Suite  {BUL}  v{VERSION}", color=Fore.YELLOW))
    print(_box_row(f"  {DIA}  Phone Number  +  Email Address  Analysis", color=Fore.YELLOW))
    print(_box_row(f"  {ARR}  By: Aryan Singh Tarinai  {BUL}  Educational & OSINT Use Only", color=Fore.MAGENTA))
    print(_box_bot())


def main_menu_box():
    mw = 52
    print()
    print(Fore.GREEN + "  ╔" + "═" * (mw - 2) + "╗" + Style.RESET_ALL)
    def row(txt, color=Fore.WHITE):
        inner = mw - 4
        return Fore.GREEN + "  ║ " + color + txt[:inner].ljust(inner) + Fore.GREEN + " ║" + Style.RESET_ALL
    def sep():
        return Fore.GREEN + "  ╠" + "═" * (mw - 2) + "╣" + Style.RESET_ALL
    def blank():
        return row("")

    print(Fore.GREEN + "  ╠" + "═" * (mw - 2) + "╣" + Style.RESET_ALL)
    print(row(f"  {DIA}  MAIN MENU", Fore.CYAN))
    print(Fore.GREEN + "  ╠" + "═" * (mw - 2) + "╣" + Style.RESET_ALL)
    print(blank())
    print(row(f"  {ARR}  [1]  Phone Number Analysis", Fore.WHITE))
    print(row(f"       Country · Carrier · Spam · OSINT · Risk", Fore.WHITE))
    print(blank())
    print(row(f"  {ARR}  [2]  Email Address Analysis", Fore.WHITE))
    print(row(f"       Validity · Provider · Breach · Gravatar · OSINT", Fore.WHITE))
    print(blank())
    print(row(f"  {ARR}  [3]  Batch Mode  (phone or email from .txt)", Fore.WHITE))
    print(blank())
    print(row(f"  {ARR}  [4]  About / Help", Fore.WHITE))
    print(blank())
    print(row(f"  {ARR}  [0]  Exit", Fore.RED))
    print(blank())
    print(Fore.GREEN + "  ╚" + "═" * (mw - 2) + "╝" + Style.RESET_ALL)


def sec_header(title):
    """Colored section header for reports."""
    bar = "─" * (W - 4)
    print()
    print(Fore.CYAN + "  ┌" + bar + "┐" + Style.RESET_ALL)
    print(Fore.CYAN + "  │  " + Fore.YELLOW + DIA + "  " + title.upper().ljust(W - 10) + Fore.CYAN + "│" + Style.RESET_ALL)
    print(Fore.CYAN + "  └" + bar + "┘" + Style.RESET_ALL)


def kv(key, val, vcolor=Fore.WHITE):
    print(f"  {Fore.CYAN}{key.ljust(20)}{Style.RESET_ALL}  {vcolor}{val}{Style.RESET_ALL}")


def loading_bar(label="Analyzing", total=25):
    print(Fore.CYAN + "\n  " + label + "  ", end="", flush=True)
    for _ in range(total):
        time.sleep(0.03)
        print(Fore.GREEN + "█", end="", flush=True)
    print(Fore.GREEN + "  DONE\n")


# ═══════════════════════════════════════════════════════════════════════════════
#  REPORT SAVERS
# ═══════════════════════════════════════════════════════════════════════════════
def save_txt(text, tag):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fp = os.path.join(os.getcwd(), f"report_{tag}_{ts}.txt")
    with open(fp, "w", encoding="utf-8") as f:
        f.write(text)
    print(Fore.GREEN + f"\n  {ICO_OK}  TXT report  {ARW}  {fp}")
    return fp


def save_json(data, tag):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fp = os.path.join(os.getcwd(), f"report_{tag}_{ts}.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(Fore.GREEN + f"\n  {ICO_OK}  JSON report {ARW}  {fp}")
    return fp


# ═══════════════════════════════════════════════════════════════════════════════
#  ▌▌▌  PHONE MODULE  ▌▌▌
# ═══════════════════════════════════════════════════════════════════════════════

def _phone_type_str(t):
    return {0:"Fixed Line",1:"Mobile",2:"Fixed/Mobile",3:"Toll Free",
            4:"Premium Rate",5:"Shared Cost",6:"VoIP",7:"Personal",
            8:"Pager",9:"UAN",10:"Voicemail",27:"Unknown"}.get(t,"Unknown")

def _sim_type_str(t):
    m = {0:"Likely Postpaid (Fixed Line)",1:"Likely Prepaid (Mobile)",
         2:"Prepaid or Postpaid",6:"VoIP / Internet Number",
         3:"Toll-Free Service",4:"Premium Rate",9:"UAN"}
    return m.get(t,"Cannot Determine")

def _call_type(parsed):
    return "Domestic (Local/STD)" if parsed.country_code == 91 else "International (ISD)"

_EMERGENCY = {"100","101","102","103","104","108","112","911","999","000","110"}

def _is_emergency(nat):
    return nat.lstrip("0") in _EMERGENCY or nat in _EMERGENCY

def _num_patterns(nat):
    pats = []
    if len(set(nat)) == 1:
        pats.append("All identical digits")
    elif len(set(nat)) <= 2:
        pats.append("Very few unique digits (vanity?)")
    for i in range(len(nat) - 3):
        s = nat[i:i+4]
        if all(int(s[j+1]) - int(s[j]) == 1 for j in range(3)):
            pats.append(f"Ascending run ({s}...)"); break
    for i in range(len(nat) - 3):
        s = nat[i:i+4]
        if all(int(s[j]) - int(s[j+1]) == 1 for j in range(3)):
            pats.append(f"Descending run ({s}...)"); break
    return pats or ["Normal / Random"]

def _is_voip(sim_int, carrier_str):
    kw = ["google","skype","twilio","vonage","magicjack","bandwidth",
          "telnyx","voip","internet","virtual","textnow","textfree","hushed","burner"]
    if sim_int == 6: return True
    c = (carrier_str or "").lower()
    return any(k in c for k in kw)

# ── India carrier map ────────────────────────────────────────────────────────
_IND_CARRIER = {
    "Airtel": ["9810","9811","9871","9870","9312","9313","9716","9717","9899",
               "9415","9820","9821","9867","9833","9845","9886","9342","9840",
               "9940","9400","9446","9447","9895","9876","9814","9815","9417",
               "9803","9501","9812","9896","9416","9830","9831","9848","9503",
               "9527","9448","9449","9480","9481","9482","9513","9535","9880",
               "9900","9980","9443","9500","9444","9952","9361","9894","8050",
               "8146","9779","9878","9472","9473","9862","9856"],
    "Jio (Reliance)": ["7011","7042","7043","7044","7045","8800","8801","7020",
                       "7021","7022","7010","7400","7450","7700","7600","7000",
                       "7087","7015","7001","7002","6200","6300","6000","6370",
                       "6360","6380","9000","9010","9100","8100","7307","7086",
                       "7770","7771","7772","7773","7904","9063"],
    "Vi (Vodafone Idea)": ["9999","9910","9990","9920","9960","9970","9449","9900",
                           "9980","9444","9496","9816","9817","9418","9779","9878",
                           "9525","9526","9474","9475","9491","9505","9937","9954",
                           "9435","9926","9425","9419","9469","9660","9694","9504",
                           "9509","9524","9529","9530","9531","9549","9550","9823",
                           "9890","9860","9167"],
    "BSNL": ["9868","9869","9436","9402","9403","9612","9615","8188","9774",
             "8414","9863","9854","9432","9434"],
    "MTNL": ["9869","9868","8826","9210"],
}

def _india_carrier(prefix4):
    for n, lst in _IND_CARRIER.items():
        if prefix4 in lst: return n
    return None


# ── India state map (300+ prefixes) ─────────────────────────────────────────
def _india_state(n):
    p = n[:4]
    m = {
        "9810":"Delhi","9811":"Delhi","9871":"Delhi","9870":"Delhi","9910":"Delhi",
        "9990":"Delhi","9999":"Delhi","9540":"Delhi","8800":"Delhi","7011":"Delhi",
        "7042":"Delhi","7043":"Delhi","7044":"Delhi","7045":"Delhi","9312":"Delhi",
        "9717":"Delhi","9716":"Delhi","9313":"Delhi","9899":"Delhi","9868":"Delhi",
        "9891":"Delhi","9873":"Delhi","8010":"Delhi","8287":"Delhi","8448":"Delhi",
        "8750":"Delhi","9667":"Delhi","9560":"Delhi","9650":"Delhi","9205":"Delhi",
        "9958":"Delhi","9953":"Delhi","9911":"Delhi","9599":"Delhi","8076":"Delhi",
        "9718":"Delhi","9212":"Delhi","9315":"Delhi",
        "9820":"Maharashtra","9821":"Maharashtra","9822":"Maharashtra","9823":"Maharashtra",
        "9850":"Maharashtra","9860":"Maharashtra","9890":"Maharashtra","9920":"Maharashtra",
        "9930":"Maharashtra","9960":"Maharashtra","9970":"Maharashtra","9503":"Maharashtra",
        "9527":"Maharashtra","9545":"Maharashtra","7020":"Maharashtra","7021":"Maharashtra",
        "8390":"Maharashtra","9167":"Maharashtra","9004":"Maharashtra","9326":"Maharashtra",
        "9373":"Maharashtra","9867":"Maharashtra","9833":"Maharashtra","9987":"Maharashtra",
        "8600":"Maharashtra","9765":"Maharashtra","8422":"Maharashtra","9819":"Maharashtra",
        "9321":"Maharashtra",
        "9881":"Goa","7798":"Goa","8322":"Goa",
        "9845":"Karnataka","9880":"Karnataka","9900":"Karnataka","9980":"Karnataka",
        "9448":"Karnataka","9449":"Karnataka","9480":"Karnataka","9481":"Karnataka",
        "9482":"Karnataka","9513":"Karnataka","9535":"Karnataka","6360":"Karnataka",
        "7022":"Karnataka","8050":"Karnataka","9972":"Karnataka","9886":"Karnataka",
        "9342":"Karnataka","7019":"Karnataka","9663":"Karnataka","9964":"Karnataka",
        "9620":"Karnataka","8277":"Karnataka","8722":"Karnataka","9611":"Karnataka",
        "9840":"Tamil Nadu","9940":"Tamil Nadu","9443":"Tamil Nadu","9500":"Tamil Nadu",
        "9514":"Tamil Nadu","9515":"Tamil Nadu","9543":"Tamil Nadu","6380":"Tamil Nadu",
        "7010":"Tamil Nadu","8300":"Tamil Nadu","9444":"Tamil Nadu","9952":"Tamil Nadu",
        "9361":"Tamil Nadu","9894":"Tamil Nadu","8124":"Tamil Nadu","9566":"Tamil Nadu",
        "7904":"Tamil Nadu","9080":"Tamil Nadu","9786":"Tamil Nadu","9942":"Tamil Nadu",
        "9385":"Tamil Nadu","9994":"Tamil Nadu",
        "9400":"Kerala","9446":"Kerala","9447":"Kerala","9495":"Kerala","9496":"Kerala",
        "9539":"Kerala","9544":"Kerala","9895":"Kerala","8281":"Kerala","9387":"Kerala",
        "7994":"Kerala","8086":"Kerala","9048":"Kerala","8547":"Kerala","9745":"Kerala",
        "9846":"Kerala","9961":"Kerala","9744":"Kerala","8606":"Kerala","9656":"Kerala",
        "9801":"Uttar Pradesh","9450":"Uttar Pradesh","9451":"Uttar Pradesh",
        "9452":"Uttar Pradesh","9506":"Uttar Pradesh","9511":"Uttar Pradesh",
        "9516":"Uttar Pradesh","9517":"Uttar Pradesh","9518":"Uttar Pradesh",
        "9519":"Uttar Pradesh","9520":"Uttar Pradesh","9521":"Uttar Pradesh",
        "9522":"Uttar Pradesh","9523":"Uttar Pradesh","9528":"Uttar Pradesh",
        "9532":"Uttar Pradesh","9536":"Uttar Pradesh","9538":"Uttar Pradesh",
        "9548":"Uttar Pradesh","9455":"Uttar Pradesh","9415":"Uttar Pradesh",
        "9616":"Uttar Pradesh","9617":"Uttar Pradesh","9618":"Uttar Pradesh",
        "9619":"Uttar Pradesh","9554":"Uttar Pradesh","9555":"Uttar Pradesh",
        "9557":"Uttar Pradesh","9670":"Uttar Pradesh","9671":"Uttar Pradesh",
        "9336":"Uttar Pradesh","9335":"Uttar Pradesh","9305":"Uttar Pradesh",
        "9307":"Uttar Pradesh","9198":"Uttar Pradesh","9369":"Uttar Pradesh",
        "8887":"Uttar Pradesh","8858":"Uttar Pradesh","8601":"Uttar Pradesh",
        "8756":"Uttar Pradesh","7500":"Uttar Pradesh","7800":"Uttar Pradesh",
        "8400":"Uttar Pradesh","9792":"Uttar Pradesh","9793":"Uttar Pradesh",
        "9795":"Uttar Pradesh","9026":"Uttar Pradesh","9453":"Uttar Pradesh",
        "9454":"Uttar Pradesh","9456":"Uttar Pradesh","9559":"Uttar Pradesh",
        "9950":"Rajasthan","9460":"Rajasthan","9461":"Rajasthan","9462":"Rajasthan",
        "9504":"Rajasthan","9509":"Rajasthan","9524":"Rajasthan","9529":"Rajasthan",
        "9530":"Rajasthan","9531":"Rajasthan","9549":"Rajasthan","7400":"Rajasthan",
        "7450":"Rajasthan","7451":"Rajasthan","7452":"Rajasthan","7453":"Rajasthan",
        "7454":"Rajasthan","7455":"Rajasthan","7456":"Rajasthan","7457":"Rajasthan",
        "7458":"Rajasthan","7459":"Rajasthan","7460":"Rajasthan","7900":"Rajasthan",
        "9414":"Rajasthan","9413":"Rajasthan","9928":"Rajasthan","9929":"Rajasthan",
        "8058":"Rajasthan","7737":"Rajasthan","9660":"Rajasthan","9694":"Rajasthan",
        "9166":"Rajasthan","8955":"Rajasthan","9784":"Rajasthan",
        "9510":"Gujarat","9512":"Gujarat","9537":"Gujarat","7600":"Gujarat",
        "8000":"Gujarat","8200":"Gujarat","9099":"Gujarat","9898":"Gujarat",
        "9427":"Gujarat","9909":"Gujarat","9824":"Gujarat","9825":"Gujarat",
        "9979":"Gujarat","8140":"Gujarat","9998":"Gujarat","8866":"Gujarat",
        "9726":"Gujarat","9712":"Gujarat","9687":"Gujarat","9429":"Gujarat",
        "9803":"Punjab","9876":"Punjab","9501":"Punjab","7700":"Punjab",
        "9779":"Punjab","9814":"Punjab","9815":"Punjab","9417":"Punjab",
        "8146":"Punjab","9878":"Punjab","7087":"Punjab","9988":"Punjab",
        "7307":"Punjab","9872":"Punjab",
        "9502":"Haryana","9525":"Haryana","9526":"Haryana","9812":"Haryana",
        "9813":"Haryana","9896":"Haryana","8901":"Haryana","7015":"Haryana",
        "9416":"Haryana","9466":"Haryana",
        "9800":"West Bengal","9830":"West Bengal","9474":"West Bengal",
        "9475":"West Bengal","9547":"West Bengal","7001":"West Bengal",
        "8100":"West Bengal","9433":"West Bengal","9831":"West Bengal",
        "8697":"West Bengal","9123":"West Bengal",
        "9490":"Andhra Pradesh","9491":"Andhra Pradesh","9505":"Andhra Pradesh",
        "9533":"Andhra Pradesh","9542":"Andhra Pradesh","9550":"Andhra Pradesh",
        "8500":"Andhra Pradesh","9848":"Andhra Pradesh","8179":"Andhra Pradesh",
        "7093":"Andhra Pradesh",
        "9492":"Telangana","9494":"Telangana","9000":"Telangana","9849":"Telangana",
        "7386":"Telangana","8801":"Telangana","9010":"Telangana","9100":"Telangana",
        "8978":"Telangana","7330":"Telangana",
        "9472":"Bihar","9473":"Bihar","9507":"Bihar","9534":"Bihar","6200":"Bihar",
        "6300":"Bihar","9006":"Bihar","7546":"Bihar","8544":"Bihar","9304":"Bihar",
        "9199":"Bihar",
        "9470":"Jharkhand","9471":"Jharkhand","9508":"Jharkhand","9546":"Jharkhand",
        "8986":"Jharkhand","7488":"Jharkhand",
        "8700":"Odisha","6370":"Odisha","9937":"Odisha","7894":"Odisha",
        "9438":"Odisha","8895":"Odisha","9777":"Odisha",
        "8900":"Assam","6000":"Assam","9954":"Assam","9435":"Assam",
        "8638":"Assam","7002":"Assam","7085":"Assam","9864":"Assam",
        "7000":"Madhya Pradesh","9926":"Madhya Pradesh","9425":"Madhya Pradesh",
        "8109":"Madhya Pradesh","7693":"Madhya Pradesh","9981":"Madhya Pradesh",
        "8878":"Madhya Pradesh","7697":"Madhya Pradesh","9977":"Madhya Pradesh",
        "9802":"Himachal Pradesh","9816":"Himachal Pradesh","9817":"Himachal Pradesh",
        "9418":"Himachal Pradesh","8894":"Himachal Pradesh",
        "9541":"Uttarakhand","9410":"Uttarakhand","7060":"Uttarakhand","8979":"Uttarakhand",
        "9770":"Chhattisgarh","7415":"Chhattisgarh","9752":"Chhattisgarh","8889":"Chhattisgarh",
        "9419":"Jammu & Kashmir","9469":"Jammu & Kashmir","7006":"Jammu & Kashmir",
        "9596":"Jammu & Kashmir","8491":"Jammu & Kashmir","9906":"Jammu & Kashmir",
        "7798":"Goa",
        "9862":"Nagaland","9402":"Nagaland","9856":"Manipur","9436":"Manipur",
        "9612":"Mizoram","9863":"Meghalaya","8414":"Tripura","9774":"Tripura",
        "9403":"Arunachal Pradesh","8974":"Arunachal Pradesh","9615":"Sikkim",
    }
    return m.get(p, "Not Available")


def _get_region(parsed, nat):
    if parsed.country_code == 91:
        return _india_state(nat)
    geo = geocoder.description_for_number(parsed, "en")
    return geo.strip() if geo and geo.strip() else "Not Available"


# ── Phone checks ─────────────────────────────────────────────────────────────
def check_whatsapp(e164):
    sp = Spinner("WhatsApp")
    sp.start()
    clean = e164.replace("+", "")
    try:
        r = requests.get("https://wa.me/" + clean, headers=HEADERS, timeout=12, allow_redirects=True)
        c = r.text.lower()
        if any(s in c for s in ["not registered","not on whatsapp","invalid phone","link is not"]):
            sp.fail("NOT REGISTERED"); return "Not Registered [-]"
        if any(s in c for s in ["send message","open whatsapp","continue to chat","chat with"]):
            sp.ok("REGISTERED"); return "Registered [+]"
        if r.status_code == 200:
            sp.ok("LIKELY REGISTERED"); return "Likely Registered [+]"
        sp.warn("INCONCLUSIVE"); return "Inconclusive"
    except requests.exceptions.Timeout:
        sp.warn("TIMEOUT"); return "Timed Out"
    except Exception:
        sp.fail(); return "Check Failed"


def check_telegram(e164):
    sp = Spinner("Telegram")
    sp.start()
    clean = e164.replace("+", "")
    try:
        r = requests.get("https://t.me/+" + clean, headers=HEADERS, timeout=10, allow_redirects=True)
        c = r.text.lower()
        if "join group" in c or "join channel" in c:
            sp.warn("INVITE LINK (inconclusive)"); return "Invite Link (inconclusive)"
        if r.status_code == 200 and "telegram" in c:
            sp.warn("CANNOT VERIFY (auth required)"); return "Cannot verify — auth required"
        sp.warn("INCONCLUSIVE"); return "Inconclusive"
    except Exception:
        sp.fail(); return "Check Failed"


def _spam_parse(text, url):
    t = text.lower()
    if any(k in t for k in ["dangerous","scam","fraud","harassing","illegal"]):
        return {"rating":"DANGEROUS / SCAM REPORTED [!!]","url":url}
    if any(k in t for k in ["spam","unwanted","telemarketing","robocall"]):
        return {"rating":"Spam Reported [!]","url":url}
    if any(k in t for k in ["safe","positive","no complaints","no reports"]):
        return {"rating":"Safe [OK]","url":url}
    if "neutral" in t:
        return {"rating":"Neutral (no strong reports)","url":url}
    return {"rating":"No Reports Found","url":url}


def _run_spam_check(label, url, key, e164=None):
    sp = Spinner(label)
    sp.start()
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200 and len(r.text) > 300:
            res = _spam_parse(r.text, url)
            res["source"] = key
            rating = res["rating"]
            if "[!!]" in rating: sp.fail(rating.split("[")[0].strip())
            elif "[!]" in rating: sp.warn(rating.split("[")[0].strip())
            elif "[OK]" in rating or "Safe" in rating: sp.ok(rating.split("[")[0].strip())
            else: sp.warn(rating.split("[")[0].strip())
            return res
        sp.warn("NO DATA")
    except Exception:
        sp.fail()
    return None


def run_spam_checks(e164):
    clean = e164.replace("+","")
    results = [
        _run_spam_check("NumLookup",     f"https://www.numlookup.com/results?phone={e164}",         "NumLookup"),
        _run_spam_check("ShouldIAnswer", f"https://www.shouldianswer.com/phone-number/{clean}",    "ShouldIAnswer"),
        _run_spam_check("WhoCalledMe",   f"https://www.whocalledme.com/PhoneNumber/{clean}",       "WhoCalledMe"),
        _run_spam_check("Tellows",       f"https://www.tellows.com/num/{clean}",                   "Tellows"),
        _run_spam_check("800notes",      f"https://800notes.com/Phone.aspx/{e164}",                "800notes"),
        _run_spam_check("SpamCalls",     f"https://spamcalls.net/en/number/{clean}",               "SpamCalls.net"),
    ]
    return results


def phone_osint_links(e164, nat, cc):
    clean   = e164.replace("+","")
    encoded = requests.utils.quote(e164)
    links = {
        "Google Search"      : f"https://www.google.com/search?q={encoded}",
        "Google (+quotes)"   : f"https://www.google.com/search?q=%22{clean}%22",
        "Bing"               : f"https://www.bing.com/search?q={encoded}",
        "DuckDuckGo"         : f"https://duckduckgo.com/?q={encoded}",
        "Truecaller"         : f"https://www.truecaller.com/search/in/{nat}",
        "GetContact"         : f"https://www.getcontact.com/en/search?phone={clean}",
        "Sync.me"            : f"https://sync.me/search/?number={clean}",
        "Facebook"           : f"https://www.facebook.com/search/top/?q={encoded}",
        "Twitter / X"        : f"https://twitter.com/search?q={encoded}",
        "WhatsApp Chat"      : f"https://wa.me/{clean}",
        "Telegram"           : f"https://t.me/+{clean}",
        "Signal"             : f"https://signal.me/#p/{e164}",
        "Viber"              : f"viber://chat?number={e164}",
        "NumLookup"          : f"https://www.numlookup.com/results?phone={e164}",
        "Tellows"            : f"https://www.tellows.com/num/{clean}",
        "800notes"           : f"https://800notes.com/Phone.aspx/{e164}",
        "SpamCalls.net"      : f"https://spamcalls.net/en/number/{clean}",
        "WhoCalledMe"        : f"https://www.whocalledme.com/PhoneNumber/{clean}",
        "ShouldIAnswer"      : f"https://www.shouldianswer.com/phone-number/{clean}",
        "WhitePages"         : f"https://www.whitepages.com/phone/{clean}",
        "PhoneBook"          : f"https://www.phonebook.com/phone/{clean}/",
    }
    return links


def phone_risk(spam_results, wa, is_voip, sim_int, patterns):
    score, factors = 0, []
    dangerous = sum(1 for r in spam_results if r and "[!!]" in r.get("rating",""))
    spammed   = sum(1 for r in spam_results if r and "[!]"  in r.get("rating",""))
    if dangerous: score += 50; factors.append(f"Flagged DANGEROUS by {dangerous} source(s)")
    if spammed:   score += min(30, spammed*10); factors.append(f"Flagged as SPAM by {spammed} source(s)")
    if is_voip:   score += 15; factors.append("VoIP / virtual number detected")
    if sim_int==4:score += 20; factors.append("Premium rate number")
    if "Not Registered" in wa: score += 5; factors.append("Not on WhatsApp")
    if any("identical" in p.lower() or "vanity" in p.lower() for p in patterns):
        score += 5; factors.append("Unusual digit pattern")
    score = min(score, 100)
    if score >= 70: lvl,col = "CRITICAL [!!!]", Fore.RED
    elif score >= 40: lvl,col = "HIGH [!!]",  Fore.RED
    elif score >= 20: lvl,col = "MEDIUM [!]", Fore.YELLOW
    else:             lvl,col = "LOW [OK]",   Fore.GREEN
    return {"score":score,"level":lvl,"color":col,"factors":factors or ["No major risk indicators"]}


def check_numverify(clean_number):
    api_key = os.getenv("NUMVERIFY_API_KEY")
    if not api_key:
        return None
    
    # Check limit
    usage_file = os.path.join(os.path.expanduser("~"), ".numverify_usage.json")
    month_key = datetime.now().strftime("%Y-%m")
    
    usage_data = {}
    if os.path.exists(usage_file):
        try:
            with open(usage_file, "r") as f:
                usage_data = json.load(f)
        except Exception:
            pass
            
    current_count = usage_data.get(month_key, 0)
    if current_count >= 1000:
        sp = Spinner("Numverify API")
        sp.start()
        sp.warn("MONTHLY LIMIT REACHED (1000/1000)")
        return {"error": "Limit Reached"}
        
    sp = Spinner("Numverify API")
    sp.start()
    try:
        # Free tier requires HTTP
        r = requests.get(f"http://apilayer.net/api/validate?access_key={api_key}&number={clean_number}", timeout=10)
        if r.status_code == 200:
            d = r.json()
            if "error" in d:
                sp.fail(d["error"].get("info", "API Error"))
                return None
            
            # Update usage since successful request was made
            usage_data[month_key] = current_count + 1
            with open(usage_file, "w") as f:
                json.dump(usage_data, f)
                
            loc = d.get("location") or "Unknown"
            car = d.get("carrier") or "Unknown"
            valid = d.get("valid", False)
            ltype = d.get("line_type") or "Unknown"
            
            summary = f"Valid:{valid} | Loc:{loc} | Carrier:{car}"
            sp.ok(summary)
            
            return {
                "valid": valid,
                "location": loc,
                "carrier": car,
                "line_type": ltype,
                "usage": usage_data[month_key]
            }
        sp.warn("HTTP Error")
    except Exception:
        sp.fail("Connection Failed")
    return None


def check_truecaller(e164, country_code):
    import base64
    from urllib.parse import unquote
    
    token = os.getenv("TRUECALLER_TOKEN")
    cookie = os.getenv("TRUECALLER_COOKIE")
    
    if not token and cookie:
        # Parse tc_user from cookie string
        tc_user_raw = None
        for part in cookie.split("; "):
            if part.startswith("tc_user="):
                tc_user_raw = part[len("tc_user="):]
                break
        
        if tc_user_raw:
            try:
                decoded = unquote(tc_user_raw)
                tc_data = json.loads(decoded)
                inner_jwt = tc_data.get("token", "")
                
                parts = inner_jwt.split(".")
                if len(parts) >= 2:
                    payload_b64 = parts[1] + "=" * (4 - len(parts[1]) % 4)
                    payload = json.loads(base64.urlsafe_b64decode(payload_b64))
                    token = payload.get("token")
            except Exception:
                pass

    if not token:
        return {"error": "Missing Token"}
        
    sp = Spinner("Truecaller API")
    sp.start()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Truecaller/11.75.5 (Android;10)",
        "Accept-Encoding": "gzip"
    }
    
    clean = e164.replace("+", "")
    cc = country_code.upper() if country_code else "IN"
    url = f"https://search5-noneu.truecaller.com/v2/search?q={clean}&countryCode={cc}&type=4&placement=SEARCHRESULTS,HISTORY,DETAILS&encoding=json"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            d = r.json()
            data_list = d.get("data", [])
            if data_list:
                name = data_list[0].get("name", "Unknown Name")
                emails = data_list[0].get("internetAddresses", [])
                email = emails[0].get("id", "No Email") if emails else "No Email"
                sp.ok(name)
                return {"name": name, "email": email}
            else:
                sp.warn("No Name Found")
                return {"error": "No Name Found"}
        elif r.status_code == 401:
            sp.fail("Token Expired — re-grab cookie from browser")
            return {"error": "Token Expired"}
        elif r.status_code == 429:
            sp.warn("Rate Limited — wait a minute and retry")
            return {"error": "Rate Limited"}
        else:
            sp.warn(f"HTTP {r.status_code}")
            return {"error": "API Error"}
    except Exception:
        sp.fail("Connection Failed")
        return {"error": "Connection Failed"}


def analyze_number(number, do_txt=False, do_json=False):
    try:
        parsed = phonenumbers.parse(number, None)
    except phonenumbers.phonenumberutil.NumberParseException as e:
        print(Fore.RED + f"\n  {ICO_ERR}  Cannot parse: {e}")
        print(Fore.YELLOW + "      Include country code  e.g. +919876543210"); return None
    if not is_valid_number(parsed):
        print(Fore.RED + f"\n  {ICO_ERR}  Invalid number. Check country code."); return None

    loading_bar("Analyzing number")

    sim_carrier  = carrier.name_for_number(parsed, "en") or "Not Available"
    sim_type_int = number_type(parsed)
    time_zones   = timezone.time_zones_for_number(parsed)
    cc           = parsed.country_code
    nat          = str(parsed.national_number)
    region_code  = region_code_for_number(parsed)
    possible     = is_possible_number(parsed)
    country      = geocoder.description_for_number(parsed, "en") or "Not Available"

    intl = format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
    natl = format_number(parsed, PhoneNumberFormat.NATIONAL)
    e164 = format_number(parsed, PhoneNumberFormat.E164)
    rfc  = format_number(parsed, PhoneNumberFormat.RFC3966)
    clean = e164.replace("+","")

    region   = _get_region(parsed, nat)
    ptype    = _phone_type_str(sim_type_int)
    simtype  = _sim_type_str(sim_type_int)
    calltype = _call_type(parsed)
    is_mob   = sim_type_int == 1
    is_toll  = sim_type_int == 3
    is_voip  = _is_voip(sim_type_int, sim_carrier)
    is_prem  = sim_type_int == 4
    is_emerg = _is_emergency(nat)
    patterns = _num_patterns(nat)
    ind_car  = _india_carrier(nat[:4]) if cc == 91 and len(nat) >= 4 else None
    wa_link  = f"https://wa.me/{clean}"

    print(Fore.CYAN + f"\n  {DIA}  Running checks...\n")

    wa  = check_whatsapp(e164)
    tg  = check_telegram(e164)
    spam_results = run_spam_checks(e164)
    valid_spam   = [r for r in spam_results if r]
    risk         = phone_risk(spam_results, wa, is_voip, sim_type_int, patterns)
    links        = phone_osint_links(e164, nat, cc)
    numverify    = check_numverify(clean)
    tc_data      = check_truecaller(e164, region_code)

    ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    SEP = "═" * W

    # ── Print report ──────────────────────────────────────────────────
    print()
    print(Fore.GREEN + "  " + SEP)
    print(Fore.YELLOW + f"  PhoneXtract v{VERSION}  {BUL}  Phone Intelligence Report")
    print(Fore.WHITE  + f"  Generated  : {ts}")
    print(Fore.WHITE  + f"  Target     : {number}")
    print(Fore.GREEN  + "  " + SEP)

    sec_header("Identification")
    kv("International",  intl)
    kv("National Format",natl)
    kv("E164 Format",    e164)
    kv("RFC3966 Format", rfc)
    kv("WhatsApp Link",  wa_link, Fore.CYAN)
    kv("Valid",          "Yes",   Fore.GREEN)
    kv("Possible",       "Yes" if possible else "No")
    kv("Emergency",      f"YES {ICO_ERR}" if is_emerg else "No",
       Fore.RED if is_emerg else Fore.WHITE)
       
    sec_header("Caller Identity")
    if tc_data:
        if "error" in tc_data:
            if tc_data["error"] == "Missing Token":
                kv("Registered Name", "Truecaller Token/Cookie not set in .env", Fore.YELLOW)
            else:
                kv("Registered Name", f"Not Found ({tc_data['error']})", Fore.YELLOW)
        else:
            kv("Registered Name", f"{tc_data.get('name')}  {ICO_OK}", Fore.GREEN)
            if tc_data.get("email") and tc_data.get("email") != "No Email":
                kv("Linked Email", tc_data.get("email"), Fore.CYAN)
    else:
        kv("Registered Name", "Unknown", Fore.YELLOW)

    sec_header("Location")
    kv("Country",        country)
    kv("Region / State", region)
    kv("Dial Code",      f"+{cc}")
    kv("ISO Code",       region_code)
    kv("Time Zone(s)",   ", ".join(time_zones) if time_zones else "Not Available")

    sec_header("Carrier & Line")
    kv("Carrier (lib)",  sim_carrier)
    if ind_car:
        kv("Carrier (prefix)", ind_car + "  (prefix estimate)", Fore.CYAN)
    kv("Phone Type",     ptype)
    kv("SIM Category",   simtype)
    kv("Call Type",      calltype)
    kv("Mobile",         "Yes" if is_mob else "No")
    kv("Toll Free",      "Yes" if is_toll else "No")
    kv("VoIP/Virtual",   f"Yes {ICO_WRN}" if is_voip else "No",
       Fore.YELLOW if is_voip else Fore.WHITE)
    kv("Premium Rate",   f"Yes {ICO_WRN}" if is_prem else "No",
       Fore.YELLOW if is_prem else Fore.WHITE)

    if numverify:
        sec_header("Numverify API (Premium)")
        if "error" in numverify:
            kv("Status", "Monthly Limit Reached (1000/1000)", Fore.RED)
        else:
            kv("API Valid",     str(numverify["valid"]), Fore.GREEN if numverify["valid"] else Fore.RED)
            kv("API Location",  numverify["location"])
            kv("API Carrier",   numverify["carrier"])
            kv("API Line Type", numverify["line_type"])
            kv("Credits Used",  f"{numverify['usage']} / 1000  (Resets next month)", Fore.CYAN)

    sec_header("Number Details")
    kv("Length",         f"{len(nat)} digits")
    kv("Area Code",      nat[:3])
    kv("Subscriber No.", nat[3:])
    kv("4-digit Prefix", nat[:4])
    kv("Pattern",        "  |  ".join(patterns))

    sec_header("Social Media")
    kv("WhatsApp",  wa,  Fore.GREEN if "[+]" in wa else Fore.RED if "[-]" in wa else Fore.YELLOW)
    kv("Telegram",  tg,  Fore.YELLOW)
    kv("Signal",    f"https://signal.me/#p/{e164}  (manual)", Fore.CYAN)
    kv("Viber",     f"viber://chat?number={e164}  (manual)",  Fore.CYAN)

    sec_header(f"Spam / Reputation  ({len(valid_spam)}/{len(spam_results)} responded)")
    if valid_spam:
        for r in valid_spam:
            rating = r["rating"]
            col = Fore.RED if "[!!]" in rating or "[!]" in rating else \
                  Fore.GREEN if "[OK]" in rating else Fore.YELLOW
            kv(r["source"], rating, col)
    else:
        kv("Status", "All sources unavailable", Fore.YELLOW)

    sec_header("Risk Assessment")
    kv("Risk Score", f"{risk['score']} / 100", risk["color"])
    kv("Risk Level", risk["level"], risk["color"])
    print(f"  {Fore.CYAN}Factors{Style.RESET_ALL}")
    for f in risk["factors"]:
        print(f"    {Fore.YELLOW}{ARW}  {f}{Style.RESET_ALL}")

    sec_header("OSINT Links  (copy & open in browser)")
    for name, url in links.items():
        print(f"  {Fore.CYAN}{name.ljust(20)}{Style.RESET_ALL}  {Fore.WHITE}{url}{Style.RESET_ALL}")

    print()
    print(Fore.GREEN + "  " + SEP)
    print(Fore.YELLOW + f"  {ICO_WRN}  Carrier/Region = prefix-based only. WhatsApp/Telegram = best-effort.")
    print(Fore.YELLOW + f"  {ICO_WRN}  All data from public sources. No API key used. Educational use only.")
    print(Fore.GREEN  + "  " + SEP)

    report_txt = f"PhoneXtract v{VERSION} | {ts} | Target: {number}\n"

    report_data = {
        "meta":{"tool":f"PhoneXtract v{VERSION}","generated":ts,"target":number},
        "identification":{"international":intl,"national":natl,"e164":e164,"rfc3966":rfc,
                          "wa_link":wa_link,"valid":True,"possible":possible,"emergency":is_emerg},
        "location":{"country":country,"region":region,"dial_code":cc,"iso":region_code,
                    "timezones":list(time_zones)},
        "carrier":{"library":sim_carrier,"prefix_india":ind_car or "N/A","type":ptype,
                   "sim":simtype,"call":calltype,"mobile":is_mob,"tollfree":is_toll,
                   "voip":is_voip,"premium":is_prem},
        "number_details":{"length":len(nat),"area":nat[:3],"subscriber":nat[3:],
                          "prefix4":nat[:4],"patterns":patterns},
        "social":{"whatsapp":wa,"telegram":tg},
        "spam":{"responded":len(valid_spam),"total":len(spam_results),"results":valid_spam},
        "risk":{"score":risk["score"],"level":risk["level"],"factors":risk["factors"]},
        "osint_links":links,
    }

    if do_txt:  save_txt(report_txt, clean)
    if do_json: save_json(report_data, clean)
    return report_data


# ═══════════════════════════════════════════════════════════════════════════════
#  ▌▌▌  EMAIL MODULE  ▌▌▌
# ═══════════════════════════════════════════════════════════════════════════════

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

# Known free/major providers
_PROVIDERS = {
    "gmail.com":        "Google (Gmail)",
    "googlemail.com":   "Google (Gmail)",
    "outlook.com":      "Microsoft (Outlook)",
    "hotmail.com":      "Microsoft (Hotmail)",
    "live.com":         "Microsoft (Live)",
    "msn.com":          "Microsoft (MSN)",
    "yahoo.com":        "Yahoo Mail",
    "yahoo.co.in":      "Yahoo Mail (India)",
    "yahoo.co.uk":      "Yahoo Mail (UK)",
    "ymail.com":        "Yahoo (ymail)",
    "protonmail.com":   "ProtonMail (Encrypted)",
    "proton.me":        "ProtonMail (Encrypted)",
    "icloud.com":       "Apple iCloud",
    "me.com":           "Apple (me.com)",
    "mac.com":          "Apple (mac.com)",
    "tutanota.com":     "Tutanota (Encrypted)",
    "tutamail.com":     "Tutanota (Encrypted)",
    "zoho.com":         "Zoho Mail",
    "rediffmail.com":   "Rediff Mail (India)",
    "rediff.com":       "Rediff Mail (India)",
    "aol.com":          "AOL Mail",
    "mail.com":         "Mail.com",
    "gmx.com":          "GMX Mail",
    "gmx.net":          "GMX Mail",
    "fastmail.com":     "Fastmail",
    "hey.com":          "HEY (Basecamp)",
    "pm.me":            "ProtonMail (pm.me)",
}

# Disposable / temporary email domains
_DISPOSABLE = {
    "mailinator.com","guerrillamail.com","guerrillamail.net","guerrillamail.org",
    "guerrillamail.biz","guerrillamail.de","guerrillamail.info","sharklasers.com",
    "grr.la","guerrillamailblock.com","spam4.me","trashmail.com","trashmail.at",
    "trashmail.io","trashmail.me","trashmail.net","trashmail.org","trashmail.xyz",
    "trashcanmail.com","trashdevil.com","trashdevil.net","trashmailer.com",
    "trashymail.com","temp-mail.org","tempmail.de","tempmail.eu","tempmail.it",
    "tempr.email","tmpmail.net","tmpmail.org","throwaway.email","throwam.com",
    "10minutemail.com","10minutemail.net","10minutemail.org","10minutemail.de",
    "yopmail.com","yopmail.fr","cool.fr.nf","jetable.fr.nf","nospam.ze.tc",
    "nomail.xl.cx","mega.zik.dj","speed.1s.fr","courriel.fr.nf","moncourrier.fr.nf",
    "monemail.fr.nf","monmail.fr.nf","maildrop.cc","spamgourmet.com",
    "spamgourmet.net","spamgourmet.org","dispostable.com","fakeinbox.com",
    "mailnull.com","discardmail.com","discardmail.de","dodgeit.com","pookmail.com",
    "spamex.com","mailtome.de","mailismagic.com","mailme.lv","mailme24.com",
    "mailmetrash.com","mailmoat.com","mailnew.com","mailscrap.com","mailshell.com",
    "mailsiphon.com","mailslapping.com","mailtemp.info","mailtothis.com",
    "mailzilla.com","mailzilla.org","byom.de","mt2014.com","mt2015.com",
    "mytempemail.com","mytrashmail.com","netzidiot.de","notmailinator.com",
    "spambob.com","spambob.net","spambob.org","spambog.com","spambog.de",
    "spambog.ru","spambox.info","spamcero.com","spamcon.org","spaml.com",
    "spaml.de","spammotel.com","spamnotice.com","spamoff.de","spamslicer.com",
    "spamspot.com","spamtroll.net","tempalias.com","tempe-mail.com",
    "tempemail.biz","tempemail.com","tempemail.net","tempemail.us",
    "tempinbox.com","tempinbox.co.uk","temporarioemail.com.br",
    "temporaryemail.net","temporaryemail.us","temporaryforwarding.com",
    "temporaryinbox.com","temporarymailaddress.com","thanksnospam.com",
    "thisisnotmyrealemail.com","tilien.com","tmail.ws","tmailinator.com",
    "toiea.com","turual.com","tyldd.com","veryrealemail.com","viralplays.com",
    "vomoto.com","webm4il.info","weg-werf-email.de","wegwerfadresse.de",
    "wegwerfemail.com","wegwerfemail.de","wegwerfemail.net","wegwerfemail.org",
    "willselfdestruct.com","xagloo.com","xemaps.com","xents.com","xmailer.be",
    "xmaily.com","yapped.net","zippymail.info","zoemail.net","zoemail.org",
    "rcpt.at","reconmail.com","rejectmail.com","rklips.com","rmqkr.net",
    "harakirimail.com","jetable.fr.nf","kasmail.com","klassmaster.com",
    "letthemeatspam.com","lr78.com","mailblocks.com","mailcatch.com",
    "mailexpire.com","mailinater.com","mintemail.com","mt2009.com",
    "nospam.ze.tc","nospamfor.us","nospammail.net","objectmail.com",
    "odaymail.com","ownmail.net","pjjkp.com","plexolan.de","quickinbox.com",
    "selfdestructingmail.com","sendspamhere.com","skeefmail.com","slipry.net",
    "slopsbox.com","smellfear.com","snakemail.com","sneakemail.com",
    "sofort-mail.de","sogetthis.com","spamla.com","spamavert.com",
}


def _validate_email_fmt(email):
    return bool(_EMAIL_RE.match(email))


def _email_parts(email):
    parts = email.split("@", 1)
    return (parts[0], parts[1]) if len(parts) == 2 else (email, "")


def _email_provider(domain):
    d = domain.lower()
    return _PROVIDERS.get(d, f"Custom / Business Domain ({domain})")


def check_mx(domain):
    sp = Spinner("MX Records")
    sp.start()
    if HAS_DNS:
        try:
            records = dns.resolver.resolve(domain, "MX")
            mx_list = [str(r.exchange).rstrip(".") for r in records]
            sp.ok(f"FOUND  ({mx_list[0]}...)")
            return True, mx_list
        except Exception:
            sp.fail("NO MX RECORDS")
            return False, []
    else:
        # Fallback: socket-based SMTP
        try:
            socket.getaddrinfo(domain, 25)
            sp.ok("DOMAIN REACHABLE (basic)")
            return True, [f"{domain} (basic check)"]
        except Exception:
            sp.warn("DNS CHECK SKIPPED (install dnspython)")
            return None, []


def check_eva_api(email):
    sp = Spinner("EVA (pingutil)")
    sp.start()
    try:
        r = requests.get(
            f"https://eva.pingutil.com/email?email={requests.utils.quote(email)}",
            timeout=10
        )
        if r.status_code == 200:
            d = r.json().get("data", {})
            deliverable  = d.get("deliverability", "UNKNOWN")
            disposable   = d.get("disposable", None)
            spam_trap    = d.get("spam_trap_status", "unknown")
            gibberish    = d.get("gibberish_check", None)
            syntax_valid = d.get("syntax_valid", True)
            summary = f"{deliverable}"
            if disposable:  summary += " | DISPOSABLE [!]"
            if spam_trap and "spam" in spam_trap.lower(): summary += " | SPAM TRAP [!!]"
            if gibberish:   summary += " | GIBBERISH [!]"
            ok = "DELIVERABLE" in deliverable and not disposable
            sp.ok(summary) if ok else sp.warn(summary)
            return {"source":"EVA","deliverable":deliverable,"disposable":disposable,
                    "spam_trap":spam_trap,"gibberish":gibberish,"syntax_valid":syntax_valid}
        sp.warn("NO RESPONSE")
    except Exception:
        sp.fail()
    return None


def check_disify(email):
    sp = Spinner("Disify")
    sp.start()
    try:
        r = requests.get(
            f"https://www.disify.com/api/email/{requests.utils.quote(email)}",
            timeout=10
        )
        if r.status_code == 200:
            d = r.json()
            fmt   = d.get("format", None)
            dns_  = d.get("dns",  None)
            disp  = d.get("disposable", None)
            white = d.get("whitelisted", None)
            parts = []
            parts.append("Format OK" if fmt else "Format BAD [!]")
            parts.append("DNS OK" if dns_ else "DNS FAIL [!]")
            if disp:  parts.append("DISPOSABLE [!]")
            if white: parts.append("Whitelisted")
            summary = " | ".join(parts)
            ok = fmt and dns_ and not disp
            sp.ok(summary) if ok else sp.warn(summary)
            return {"source":"Disify","format":fmt,"dns":dns_,"disposable":disp,"whitelisted":white}
        sp.warn("NO RESPONSE")
    except Exception:
        sp.fail()
    return None


def check_mailcheck(email):
    sp = Spinner("MailCheck.ai")
    sp.start()
    try:
        r = requests.get(
            f"https://api.mailcheck.ai/email/{requests.utils.quote(email)}",
            headers={"Accept":"application/json"}, timeout=10
        )
        if r.status_code == 200:
            d = r.json()
            mx   = d.get("mx", None)
            disp = d.get("disposable", None)
            alias= d.get("alias", None)
            parts = []
            parts.append("MX OK" if mx else "No MX [!]")
            if disp:  parts.append("DISPOSABLE [!]")
            if alias: parts.append("ALIAS detected")
            summary = " | ".join(parts)
            ok = mx and not disp
            sp.ok(summary) if ok else sp.warn(summary)
            return {"source":"MailCheck","mx":mx,"disposable":disp,"alias":alias}
        sp.warn("NO RESPONSE")
    except Exception:
        sp.fail()
    return None


def check_gravatar(email):
    sp = Spinner("Gravatar")
    sp.start()
    email_hash = hashlib.md5(email.lower().strip().encode()).hexdigest()
    url = f"https://en.gravatar.com/{email_hash}.json"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            entry = r.json().get("entry", [{}])[0]
            name  = entry.get("displayName", entry.get("preferredUsername", ""))
            about = entry.get("aboutMe", "")[:60]
            result = f"PROFILE FOUND  —  {name}"
            if about: result += f"  |  {about}"
            sp.ok(result)
            return {"found": True, "name": name, "about": about,
                    "profile_url": f"https://www.gravatar.com/{email_hash}",
                    "avatar_url":  f"https://www.gravatar.com/avatar/{email_hash}"}
        elif r.status_code == 404:
            sp.warn("No Gravatar profile")
            return {"found": False}
        sp.warn("Inconclusive")
    except Exception:
        sp.fail()
    return {"found": False}


def email_osint_links(email, username, domain):
    enc = requests.utils.quote(email)
    links = {
        "Google Search"    : f"https://www.google.com/search?q={enc}",
        "Google (+quotes)" : f"https://www.google.com/search?q=%22{enc}%22",
        "Bing"             : f"https://www.bing.com/search?q={enc}",
        "DuckDuckGo"       : f"https://duckduckgo.com/?q={enc}",
        "LinkedIn"         : f"https://www.linkedin.com/search/results/all/?keywords={enc}",
        "GitHub"           : f"https://github.com/search?q={enc}&type=users",
        "Twitter / X"      : f"https://twitter.com/search?q={enc}",
        "Facebook"         : f"https://www.facebook.com/search/top/?q={enc}",
        "Instagram (user)" : f"https://www.instagram.com/{username}/",
        "HaveIBeenPwned"   : f"https://haveibeenpwned.com/account/{enc}",
        "Intelligence X"   : f"https://intelx.io/?s={enc}",
        "Dehashed"         : f"https://www.dehashed.com/search?query={enc}",
        "Hunter.io"        : f"https://hunter.io/email-verifier/{enc}",
        "EmailRep.io"      : f"https://emailrep.io/{enc}",
        "Pipl"             : f"https://pipl.com/search/?q={enc}",
        "Spokeo"           : f"https://www.spokeo.com/email-search/{enc}",
        "Gravatar"         : f"https://en.gravatar.com/{hashlib.md5(email.lower().encode()).hexdigest()}.json",
        "Skype Search"     : f"https://web.skype.com/search?searchQuery={enc}",
        "Reddit"           : f"https://www.reddit.com/search/?q={enc}",
        "Domain Info"      : f"https://who.is/whois-email/{enc}",
        "MXToolBox"        : f"https://mxtoolbox.com/SuperTool.aspx?action=mx:{domain}",
    }
    return links


def email_risk(fmt_valid, is_disp, eva, disify, mailcheck, gravatar, domain):
    score, factors = 0, []
    if not fmt_valid: score += 40; factors.append("Invalid email format")
    if is_disp:       score += 50; factors.append("Known DISPOSABLE email domain")
    if eva:
        if eva.get("disposable"):    score += 30; factors.append("EVA flagged as disposable")
        if eva.get("gibberish"):     score += 20; factors.append("EVA flagged as gibberish")
        if eva.get("spam_trap") and "spam" in str(eva.get("spam_trap","")).lower():
            score += 30; factors.append("EVA detected spam trap")
        if "UNDELIVERABLE" in str(eva.get("deliverable","")).upper():
            score += 25; factors.append("EVA: UNDELIVERABLE")
    if disify:
        if disify.get("disposable"): score += 30; factors.append("Disify flagged as disposable")
        if not disify.get("dns"):    score += 20; factors.append("Disify: domain DNS failure")
    if mailcheck:
        if mailcheck.get("disposable"): score += 30; factors.append("MailCheck flagged as disposable")
        if not mailcheck.get("mx"):     score += 15; factors.append("MailCheck: no MX record")
    score = min(score, 100)
    if score >= 70: lvl,col = "CRITICAL [!!!]", Fore.RED
    elif score >= 40: lvl,col = "HIGH [!!]",    Fore.RED
    elif score >= 20: lvl,col = "MEDIUM [!]",   Fore.YELLOW
    else:             lvl,col = "LOW [OK]",      Fore.GREEN
    return {"score":score,"level":lvl,"color":col,
            "factors":factors or ["No major risk indicators"]}


def analyze_email(email, do_txt=False, do_json=False):
    email = email.strip()

    # format check
    if not _validate_email_fmt(email):
        print(Fore.RED + f"\n  {ICO_ERR}  Invalid email format: {email}")
        print(Fore.YELLOW + "      Example: user@gmail.com"); return None

    username, domain = _email_parts(email)
    provider = _email_provider(domain)
    is_disp  = domain.lower() in _DISPOSABLE
    is_free  = domain.lower() in _PROVIDERS

    loading_bar("Analyzing email")

    print(Fore.CYAN + f"\n  {DIA}  Running checks...\n")

    mx_ok, mx_records = check_mx(domain)
    eva      = check_eva_api(email)
    disify   = check_disify(email)
    mailchk  = check_mailcheck(email)
    gravatar = check_gravatar(email)

    risk   = email_risk(True, is_disp, eva, disify, mailchk, gravatar, domain)
    links  = email_osint_links(email, username, domain)
    ts     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    SEP    = "═" * W

    # ── Print report ──────────────────────────────────────────────────
    print()
    print(Fore.GREEN + "  " + SEP)
    print(Fore.YELLOW + f"  PhoneXtract v{VERSION}  {BUL}  Email Intelligence Report")
    print(Fore.WHITE  + f"  Generated  : {ts}")
    print(Fore.WHITE  + f"  Target     : {email}")
    print(Fore.GREEN  + "  " + SEP)

    sec_header("Email Identification")
    kv("Email Address",  email)
    kv("Username",       username)
    kv("Domain",         domain)
    kv("Format Valid",   f"Yes {ICO_OK}", Fore.GREEN)
    kv("Length",         f"{len(email)} characters")

    sec_header("Provider & Domain")
    kv("Provider",       provider)
    kv("Account Type",   "Free Personal" if is_free else "Business / Custom")
    kv("Disposable",     f"YES — HIGH RISK {ICO_ERR}" if is_disp else f"No {ICO_OK}",
       Fore.RED if is_disp else Fore.GREEN)
    if mx_ok is True:
        kv("MX Records",  f"Found {ICO_OK}  ({mx_records[0] if mx_records else 'N/A'})", Fore.GREEN)
    elif mx_ok is False:
        kv("MX Records",  f"NOT FOUND {ICO_ERR}", Fore.RED)
    else:
        kv("MX Records",  "Skipped (install dnspython)", Fore.YELLOW)

    sec_header("Verification APIs  (free, no key)")
    if eva:
        deliv = eva.get("deliverability","UNKNOWN")
        col = Fore.GREEN if "DELIVERABLE" in deliv and not eva.get("disposable") else Fore.YELLOW
        kv("EVA.pingutil",  f"{deliv}  |  Disposable:{eva.get('disposable')}  |  SpamTrap:{eva.get('spam_trap')}", col)
    else:
        kv("EVA.pingutil",  "Unavailable", Fore.YELLOW)

    if disify:
        parts = []
        parts.append(f"Format:{disify.get('format')}")
        parts.append(f"DNS:{disify.get('dns')}")
        parts.append(f"Disposable:{disify.get('disposable')}")
        parts.append(f"Whitelisted:{disify.get('whitelisted')}")
        col = Fore.GREEN if not disify.get("disposable") and disify.get("dns") else Fore.YELLOW
        kv("Disify",         "  |  ".join(parts), col)
    else:
        kv("Disify",         "Unavailable", Fore.YELLOW)

    if mailchk:
        parts = [f"MX:{mailchk.get('mx')}",
                 f"Disposable:{mailchk.get('disposable')}",
                 f"Alias:{mailchk.get('alias')}"]
        col = Fore.GREEN if mailchk.get("mx") and not mailchk.get("disposable") else Fore.YELLOW
        kv("MailCheck.ai",   "  |  ".join(parts), col)
    else:
        kv("MailCheck.ai",   "Unavailable", Fore.YELLOW)

    sec_header("Gravatar  (social profile)")
    if gravatar and gravatar.get("found"):
        kv("Profile",       f"FOUND {ICO_OK}", Fore.GREEN)
        kv("Display Name",  gravatar.get("name","N/A"), Fore.GREEN)
        kv("About",         gravatar.get("about","N/A") or "N/A")
        kv("Profile URL",   gravatar.get("profile_url",""), Fore.CYAN)
        kv("Avatar URL",    gravatar.get("avatar_url",""),  Fore.CYAN)
    else:
        kv("Profile",       f"Not found {ICO_WRN}", Fore.YELLOW)

    sec_header("Risk Assessment")
    kv("Risk Score",    f"{risk['score']} / 100", risk["color"])
    kv("Risk Level",    risk["level"], risk["color"])
    print(f"  {Fore.CYAN}Factors{Style.RESET_ALL}")
    for f in risk["factors"]:
        print(f"    {Fore.YELLOW}{ARW}  {f}{Style.RESET_ALL}")

    sec_header("OSINT Links  (copy & open in browser)")
    for name, url in links.items():
        print(f"  {Fore.CYAN}{name.ljust(20)}{Style.RESET_ALL}  {Fore.WHITE}{url}{Style.RESET_ALL}")

    print()
    print(Fore.GREEN + "  " + SEP)
    print(Fore.YELLOW + f"  {ICO_WRN}  All checks use free public APIs — no API key required.")
    print(Fore.YELLOW + f"  {ICO_WRN}  For breach checks, visit HaveIBeenPwned manually.")
    print(Fore.YELLOW + f"  {ICO_WRN}  For educational & OSINT research use only.")
    print(Fore.GREEN  + "  " + SEP)

    report_data = {
        "meta":{"tool":f"PhoneXtract v{VERSION}","module":"email","generated":ts,"target":email},
        "identification":{"email":email,"username":username,"domain":domain,"length":len(email)},
        "provider":{"name":provider,"free_account":is_free,"disposable":is_disp,
                    "mx_ok":mx_ok,"mx_records":mx_records},
        "api_checks":{"eva":eva,"disify":disify,"mailcheck":mailchk,"gravatar":gravatar},
        "risk":{"score":risk["score"],"level":risk["level"],"factors":risk["factors"]},
        "osint_links":links,
    }

    if do_txt:  save_txt(f"PhoneXtract v{VERSION} Email Report | {ts} | {email}", email.replace("@","_"))
    if do_json: save_json(report_data, email.replace("@","_"))
    return report_data


# ═══════════════════════════════════════════════════════════════════════════════
#  BATCH MODE
# ═══════════════════════════════════════════════════════════════════════════════
def batch_mode():
    print(Fore.CYAN + f"\n  {DIA}  Batch Mode")
    print(Fore.YELLOW + "  One entry per line. Lines starting with # are ignored.")
    print(Fore.YELLOW + "  Entries can be phone numbers (+country code) or emails.\n")

    filepath = input(Fore.CYAN + f"  [{ARR}] Path to .txt file: ").strip()
    filepath = os.path.expanduser(os.path.expandvars(filepath))

    if not os.path.exists(filepath):
        print(Fore.RED + f"  {ICO_ERR}  File not found."); return

    with open(filepath, "r", encoding="utf-8") as f:
        entries = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]

    if not entries:
        print(Fore.RED + f"  {ICO_ERR}  No valid entries."); return

    print(Fore.GREEN + f"\n  {ICO_OK}  {len(entries)} entries loaded.")
    try:
        do_txt  = input(Fore.CYAN + f"  [?] Save TXT reports?  (Y/N): ").strip().lower() == "y"
        do_json = input(Fore.CYAN + f"  [?] Save JSON reports? (Y/N): ").strip().lower() == "y"
    except (KeyboardInterrupt, EOFError):
        do_txt = do_json = False

    for i, entry in enumerate(entries, 1):
        print(Fore.YELLOW + f"\n  [{i}/{len(entries)}] ─── Target: {entry} ───")
        if "@" in entry:
            analyze_email(entry, do_txt, do_json)
        else:
            analyze_number(entry, do_txt, do_json)
        if i < len(entries): time.sleep(1.5)

    print(Fore.GREEN + f"\n  {ICO_OK}  Batch complete. {len(entries)} entries analyzed.")


# ═══════════════════════════════════════════════════════════════════════════════
#  ABOUT
# ═══════════════════════════════════════════════════════════════════════════════
ABOUT = f"""
  PhoneXtract v{VERSION}  ─  OSINT Intelligence Suite
  ═══════════════════════════════════════════════════════════════

  PHONE NUMBER MODULE:
  {ICO_OK}  Country, Region/State, Time Zone
  {ICO_OK}  Carrier (library + Indian prefix: Jio/Airtel/Vi/BSNL/MTNL)
  {ICO_OK}  Phone type: Mobile / Fixed / VoIP / Toll-Free / Premium Rate
  {ICO_OK}  SIM category: Prepaid / Postpaid estimate
  {ICO_OK}  All number formats: International / National / E164 / RFC3966
  {ICO_OK}  Number pattern analysis (sequential, repeated, vanity)
  {ICO_OK}  Emergency number detection
  {ICO_OK}  WhatsApp registration probe + direct chat link
  {ICO_OK}  Telegram probe (best-effort)
  {ICO_OK}  Signal / Viber manual check links
  {ICO_OK}  6 spam sources: Tellows, 800notes, SpamCalls, NumLookup, +more
  {ICO_OK}  Risk Score (0-100) with factor breakdown
  {ICO_OK}  20+ OSINT links (Truecaller, GetContact, Sync.me, ...)

  EMAIL MODULE  (NEW):
  {ICO_OK}  Email format validation
  {ICO_OK}  Provider detection (Gmail, Outlook, Yahoo, ProtonMail, ...)
  {ICO_OK}  Disposable email detection (200+ known domains)
  {ICO_OK}  MX record lookup (DNS verification)
  {ICO_OK}  3 free APIs: EVA, Disify, MailCheck.ai (no key needed)
  {ICO_OK}  Gravatar profile check (linked social identity)
  {ICO_OK}  Risk Score with factor breakdown
  {ICO_OK}  20+ OSINT links (LinkedIn, GitHub, HaveIBeenPwned, ...)

  GENERAL:
  {ICO_OK}  Batch mode: phone + email mixed files
  {ICO_OK}  Save reports as TXT and/or JSON
  {ICO_OK}  CLI mode: pass phone/email directly
  {ICO_OK}  NO API KEY REQUIRED — 100% free

  CLI USAGE:
    bash run.sh +919876543210 --save --json
    bash run.sh user@gmail.com --email --save
    bash run.sh --batch numbers.txt
"""


# ═══════════════════════════════════════════════════════════════════════════════
#  INTERACTIVE MENU
# ═══════════════════════════════════════════════════════════════════════════════
def menu_prompt():
    try:
        return input(
            Fore.CYAN + f"\n  [{ARR}] Enter choice: " + Style.RESET_ALL
        ).strip()
    except (KeyboardInterrupt, EOFError):
        return "0"


def ask_saves():
    try:
        do_txt  = input(Fore.CYAN + f"  [?] Save TXT report?  (Y/N): ").strip().lower() == "y"
        do_json = input(Fore.CYAN + f"  [?] Save JSON report? (Y/N): ").strip().lower() == "y"
    except (KeyboardInterrupt, EOFError):
        do_txt = do_json = False
    return do_txt, do_json


def main_menu():
    startup_animation()
    while True:
        clear_screen()
        banner()
        main_menu_box()

        choice = menu_prompt()

        if choice == "1":
            clear_screen(); banner()
            print(Fore.CYAN + f"\n  {DIA}  Phone Number Analysis\n")
            print(Fore.WHITE + "  Include country code:  +919876543210  |  +14155552671\n")
            try:
                num = input(Fore.CYAN + f"  [{ARR}] Phone number: " + Style.RESET_ALL).strip()
            except (KeyboardInterrupt, EOFError): continue
            if not num:
                print(Fore.RED + f"\n  {ICO_ERR}  No input."); time.sleep(1); continue
            do_txt, do_json = ask_saves()
            analyze_number(num, do_txt, do_json)
            try: input(Fore.CYAN + f"\n  [{ARR}] Press Enter to return...")
            except: pass

        elif choice == "2":
            clear_screen(); banner()
            print(Fore.CYAN + f"\n  {DIA}  Email Address Analysis\n")
            print(Fore.WHITE + "  Example:  user@gmail.com  |  name@company.com\n")
            try:
                email = input(Fore.CYAN + f"  [{ARR}] Email address: " + Style.RESET_ALL).strip()
            except (KeyboardInterrupt, EOFError): continue
            if not email:
                print(Fore.RED + f"\n  {ICO_ERR}  No input."); time.sleep(1); continue
            do_txt, do_json = ask_saves()
            analyze_email(email, do_txt, do_json)
            try: input(Fore.CYAN + f"\n  [{ARR}] Press Enter to return...")
            except: pass

        elif choice == "3":
            clear_screen(); banner()
            batch_mode()
            try: input(Fore.CYAN + f"\n  [{ARR}] Press Enter to return...")
            except: pass

        elif choice == "4":
            clear_screen(); banner()
            print(Fore.CYAN + ABOUT)
            try: input(Fore.CYAN + f"\n  [{ARR}] Press Enter to go back...")
            except: pass

        elif choice == "0":
            print(Fore.GREEN + f"\n  {ICO_OK}  Exiting. Stay ethical.\n")
            print(Fore.MAGENTA + f"      Created by Aryan Singh Tarinai\n")
            break
        else:
            print(Fore.RED + f"\n  {ICO_ERR}  Invalid choice. Enter 0–4.")
            time.sleep(1)


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI ENTRYPOINT
# ═══════════════════════════════════════════════════════════════════════════════
def build_cli():
    p = argparse.ArgumentParser(
        prog="phonextract",
        description=f"PhoneXtract v{VERSION} — OSINT Intelligence Suite",
        epilog="Examples:\n"
               "  python3 phonextract.py +919876543210 --save --json\n"
               "  python3 phonextract.py user@gmail.com --email --save\n"
               "  python3 phonextract.py --batch targets.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("target",  nargs="?", help="Phone number or email address")
    p.add_argument("--email", "-e", action="store_true", help="Force email mode")
    p.add_argument("--save",  "-s", action="store_true", help="Save TXT report")
    p.add_argument("--json",  "-j", action="store_true", dest="do_json", help="Save JSON report")
    p.add_argument("--batch", "-b", metavar="FILE",      help="Analyze entries from a .txt file")
    p.add_argument("--version",     action="version",    version=f"PhoneXtract v{VERSION}")
    return p


def main():
    parser = build_cli()
    args   = parser.parse_args()

    if args.batch:
        banner()
        fp = os.path.expanduser(os.path.expandvars(args.batch))
        if not os.path.exists(fp):
            print(Fore.RED + f"  {ICO_ERR}  File not found: {fp}"); sys.exit(1)
        with open(fp, encoding="utf-8") as f:
            entries = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
        if not entries:
            print(Fore.RED + f"  {ICO_ERR}  No entries found."); sys.exit(1)
        for i, entry in enumerate(entries, 1):
            print(Fore.YELLOW + f"\n  [{i}/{len(entries)}] ─── {entry} ───")
            if "@" in entry or args.email:
                analyze_email(entry, args.save, args.do_json)
            else:
                analyze_number(entry, args.save, args.do_json)
            if i < len(entries): time.sleep(1.5)
        return

    if args.target:
        banner()
        if "@" in args.target or args.email:
            analyze_email(args.target, args.save, args.do_json)
        else:
            analyze_number(args.target, args.save, args.do_json)
        return

    main_menu()


if __name__ == "__main__":
    main()
