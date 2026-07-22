<img width="1875" height="1067" alt="Screenshot 2026-07-23 011901" src="https://github.com/user-attachments/assets/33a3b6a9-2811-4db1-8ee6-18c51c2afdf5" />
<h1 align="center">
  <br>
  <img src="https://upload.wikimedia.org/wikipedia/commons/f/f4/Kali_Linux_2.0_wordmark.svg" alt="Kali" width="200">
  <br>
  PhoneXtract v5.0
  <br>
</h1>
<p><h6>#1st one</h6></p>

<h4 align="center">Advanced OSINT & Cyber-Intelligence Framework for Phone Number Extraction.</h4>
<img width="1917" height="1041" alt="Screenshot 2026-07-23 011935" src="https://github.com/user-attachments/assets/fac117ec-f0f2-4f2d-9345-b7e73966cafe" />



  <a href="https://github.com/aryan">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  </a>
</p>
<img width="1412" height="660" alt="Screenshot 2026-07-23 011944" src="https://github.com/user-attachments/assets/9c4b4924-9bdf-464e-be89-97bfdafb81d0" />


<img width="1007" height="650" alt="Screenshot 2026-07-23 011956" src="https://github.com/user-attachments/assets/58cfcaae-cbcb-4b44-b6eb-cc5f09669051" />


---

## Installation

PhoneXtract is fully optimized for **Kali Linux**, **Parrot Security OS**, and **Ubuntu/Debian** systems. 

Open your terminal and execute the following commands:

```bash
# 1. Clone the repository
git clone https://github.com/Aryan772005/phone-extractor.git

# 2. Navigate into the directory
cd phone-extractor

# 3. Give execution permissions to the setup and run scripts
chmod +x setup.sh run.sh

# 4. Run the automated installer (creates virtual environment & installs dependencies)
bash setup.sh
```

---


---




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
  <i>Developed By Aryan With Ubuntu And kali linux (it will work in kali and ubuntu only)🕷️</i>
</p>
