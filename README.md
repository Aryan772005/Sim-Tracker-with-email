<img width="1875" height="1067" alt="Screenshot 2026-07-23 011901" src="https://github.com/user-attachments/assets/33a3b6a9-2811-4db1-8ee6-18c51c2afdf5" />
<h1 align="center">
  <br>
  <img src="https://upload.wikimedia.org/wikipedia/commons/f/f4/Kali_Linux_2.0_wordmark.svg" alt="Kali" width="200">
  <br>
  PhoneXtract v5.0
  <br>
</h1>


<h4 align="center">Advanced OSINT & Cyber-Intelligence Framework for Phone Number Extraction.</h4>
<img width="1917" height="1041" alt="Screenshot 2026-07-23 011935" src="https://github.com/user-attachments/assets/fac117ec-f0f2-4f2d-9345-b7e73966cafe" />


<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  </a>
  <a href="https://kali.org">
    <img src="https://img.shields.io/badge/OS-Kali%20Linux%20%7C%20Ubuntu-orange.svg" alt="Kali Linux">
  </a>
  <a href="https://github.com/aryan">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  </a>
</p>
<img width="1412" height="660" alt="Screenshot 2026-07-23 011944" src="https://github.com/user-attachments/assets/9c4b4924-9bdf-464e-be89-97bfdafb81d0" />

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#configuration">Configuration (API Keys)</a> •
  <a href="#usage">Usage</a> •
  <a href="#disclaimer">Disclaimer</a>
</p>
<img width="1007" height="650" alt="Screenshot 2026-07-23 011956" src="https://github.com/user-attachments/assets/58cfcaae-cbcb-4b44-b6eb-cc5f09669051" />


---

## ⚠️ Disclaimer
**PhoneXtract is designed strictly for cybersecurity researchers, penetration testers, and OSINT analysts.**  
Do not use this tool for malicious purposes, stalking, or harassment. The author is not responsible for any misuse or damage caused by this program. **Use responsibly and ethically.**

---

## 🎯 Features

PhoneXtract leverages massive data sources and zero-day scraping techniques to extract critical intelligence on any phone number worldwide.

* **Caller Identity (Truecaller Bypass):** Extracts the registered owner's real name and linked emails by hijacking the internal Truecaller API via browser session cookies (bypassing SMS OTP blocks).
* **Premium Carrier Data (Numverify):** Identifies exact carrier, line type (Mobile/Landline), and location routing using Numverify's premium API.
* **Risk & Threat Intelligence:** Cross-references the target number against 6 major spam and scam databases (ShouldIAnswer, NumLookup, Tellows, SpamCalls, etc.) to calculate a unified risk score.
* **Virtual / VoIP Detection:** Instantly flags Burner numbers, VoIP setups, or disposable numbers favored by threat actors.
* **Social Media Recon:** Checks WhatsApp and Telegram footprints. Generates automated deep-links for instant interaction (Signal, Viber).
* **Automated OSINT Dorking:** Generates Google and DuckDuckGo dorks to find the number leaked across the surface web.
* **Forensic Reporting:** Exports clean, formatted forensic reports in both `.TXT` and `.JSON` formats for integration into larger OSINT pipelines (like Maltego or Spiderfoot).

---

## ⚙️ Installation

PhoneXtract is fully optimized for **Kali Linux**, **Parrot Security OS**, and **Ubuntu/Debian** systems. 

Open your terminal and execute the following commands:

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_GITHUB_USERNAME/phone-extractor.git

# 2. Navigate into the directory
cd phone-extractor

# 3. Give execution permissions to the setup and run scripts
chmod +x setup.sh run.sh

# 4. Run the automated installer (creates virtual environment & installs dependencies)
bash setup.sh
```

---

## 🔑 Configuration (Unlocking Maximum Power)

To get the exact Owner Name and highly accurate Carrier details, PhoneXtract needs to bypass standard rate limits using your personal API keys/cookies.

1. Create a hidden file named `.env` in the root of the `phone-extractor` directory:
```bash
nano .env
```

2. Add the following lines to your `.env` file:
```env
NUMVERIFY_API_KEY=your_numverify_api_key_here
TRUECALLER_COOKIE=your_massive_truecaller_cookie_here
```

### How to get the Truecaller Cookie (Bypass Method):
Because Truecaller blocks automated CLI logins, PhoneXtract uses a session hijacking method to read the data.
1. Go to [Truecaller Web](https://www.truecaller.com) and log in.
2. Search for any random number.
3. Open **Developer Tools** (F12) -> **Network Tab**.
4. Click on the very first file request at the top (it will be the phone number).
5. Scroll down to **Request Headers** and find the `cookie:` field.
6. Right-click and copy the massive string of text, and paste it into your `.env` file.

---

## 🚀 Usage

Once installed and configured, launch the framework using the bash script:

```bash
bash run.sh
```

1. Enter the target phone number in standard international format (e.g., `+919876543210` or `+14155552671`).
2. Select whether you want to save the forensic reports locally (TXT/JSON).
3. Let the framework run its checks.

### Example Output:
```console
┌──────────────────────────────────────────────────────────────────┐
│  ◆  CALLER IDENTITY                                              │
└──────────────────────────────────────────────────────────────────┘
Registered Name       Aryan Singh  ✔
Linked Email          aryan***@gmail.com

┌──────────────────────────────────────────────────────────────────┐
│  ◆  RISK ASSESSMENT                                              │
└──────────────────────────────────────────────────────────────────┘
Risk Score            85 / 100
Risk Level            HIGH [WARNING]
Factors               Reported as SPAM on Tellows, VoIP Detected
```

---
<p align="center">
  <i>Developed for the InfoSec Community. Happy Hunting! 🕷️</i>
</p>
