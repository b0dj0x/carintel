![CarIntel](https://img.shields.io/badge/CarIntel-v1.0-red?style=for-the-badge&logo=python&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![OSINT](https://img.shields.io/badge/OSINT-Tool-orange?style=for-the-badge)
![Made By](https://img.shields.io/badge/Made%20By-b0dj0x-purple?style=for-the-badge&logo=github&logoColor=white)

<div align="center">

```
ASCII = [
    " ██████╗██████╗  █████╗ ██╗███╗   ██╗███████╗██╗      ██████╗██╗  ██╗",
    "██╔════╝██╔══██╗██╔══██╗██║████╗  ██║██╔════╝██║     ██╔════╝██║  ██║",
    "██║     ██████╔╝███████║██║██╔██╗ ██║█████╗  ██║     ██║     ███████║",
    "██║     ██╔══██╗██╔══██║██║██║╚██╗██║██╔══╝  ██║     ██║     ██╔══██║",
    "╚██████╗██║  ██║██║  ██║██║██║ ╚████║██║     ███████╗╚██████╗██║  ██║",
    " ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝",
]
```

**Vehicle OSINT tool with VIN decoder, license plate lookup, recall check, and stolen vehicle check**

*Free APIs · No API Keys Required · Zero Config*

[![Twitter](https://img.shields.io/badge/Twitter-b0dj0x-1DA1F2?style=flat-square&logo=twitter&logoColor=white)](https://x.com/b0dj0x)
[![GitHub](https://img.shields.io/badge/GitHub-b0dj0x-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/b0dj0x)
[![Website](https://img.shields.io/badge/Website-b0dj0x.cc-00ff88?style=flat-square)](https://b0dj0x.cc)
[![Telegram](https://img.shields.io/badge/Telegram-b0dj0x-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/b0dj0x)
[![TryHackMe](https://img.shields.io/badge/TryHackMe-b0dj0x-88cc14?style=flat-square&logo=tryhackme&logoColor=white)](https://tryhackme.com/p/b0dj0x)
[![HackTheBox](https://img.shields.io/badge/HackTheBox-b0dj0x-9FEF00?style=flat-square&logo=hackthebox&logoColor=white)](https://app.hackthebox.com/profile/b0dj0x)

</div>

---

## What is CarIntel?

Vehicle OSINT tool with VIN decoder, license plate lookup, recall check, and stolen vehicle check

## Features

- VIN decode (150+ WMI codes, local decode + NHTSA API)
- License plate lookup (auto-detect state/region from 50 US states + Canadian provinces + Australian states)
- Recall check (NHTSA API)
- Stolen vehicle check (NICB)
- Vehicle history (30+ sources)
- Zero config, no API keys needed

## Installation

```bash
git clone https://github.com/b0dj0x/CarIntel.git
cd CarIntel
pip install -r requirements.txt
```

## Usage

```bash
python3 carintel.py vin 1HGBH41JXMN109186
python3 carintel.py plate ABC1234
python3 carintel.py recall 1HGBH41JXMN109186
python3 carintel.py stolen 1HGBH41JXMN109186
```

## Disclaimer

**For authorized security testing and educational purposes only.** The developer assumes no liability for misuse of this tool. Only use against targets you own or have written authorization to test.

---

## Author

**b0dj0x** - [https://b0dj0x.cc](https://b0dj0x.cc)

[![Twitter](https://img.shields.io/badge/Twitter-b0dj0x-1DA1F2?style=flat-square&logo=twitter&logoColor=white)](https://x.com/b0dj0x)
[![GitHub](https://img.shields.io/badge/GitHub-b0dj0x-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/b0dj0x)
[![Website](https://img.shields.io/badge/Website-b0dj0x.cc-00ff88?style=flat-square)](https://b0dj0x.cc)
[![Telegram](https://img.shields.io/badge/Telegram-b0dj0x-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/b0dj0x)
[![TryHackMe](https://img.shields.io/badge/TryHackMe-b0dj0x-88cc14?style=flat-square&logo=tryhackme&logoColor=white)](https://tryhackme.com/p/b0dj0x)
[![HackTheBox](https://img.shields.io/badge/HackTheBox-b0dj0x-9FEF00?style=flat-square&logo=hackthebox&logoColor=white)](https://app.hackthebox.com/profile/b0dj0x)
[![HackerOne](https://img.shields.io/badge/HackerOne-b0dj0x-50413C?style=flat-square&logo=hackerone&logoColor=white)](https://hackerone.com/b0dj0x)
[![Medium](https://img.shields.io/badge/Medium-b0dj0x-000000?style=flat-square&logo=medium&logoColor=white)](https://medium.com/@b0dj0x)

---

*Made with ❤ by b0dj0x*
