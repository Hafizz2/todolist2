"""Day-by-day breakdown of the OWASP PCCOE cybersecurity roadmap.

Source: https://github.com/owasppccoe/cybersecurity-roadmap/blob/main/ROADMAP.md

This file is the editable source of the plan. Run it to regenerate
curriculum.json, which both the Telegram bot and the web dashboard read:

    python3 cyberbot/build_curriculum.py

Pace: ~1.5-2 hours a day. Every 7th day is a review / write-up day that is
inserted automatically, so you never add those by hand.
"""

import json
from pathlib import Path

ROADMAP = "https://github.com/owasppccoe/cybersecurity-roadmap/blob/main/ROADMAP.md"

PHASES = {
    "p0": "Phase 0 - Introduction & Exploration",
    "p1": "Phase 1 - Computer & Networking Foundations",
    "p2": "Phase 2 - Operating System Fundamentals",
    "p3": "Phase 3 - Web & Programming Fundamentals",
    "p4": "Phase 4 - Cybersecurity Fundamentals",
    "p5": "Phase 5 - Hands-On Learning",
    "p6": "Phase 6/7 - CTFs & CTF Progression",
    "p8": "Phase 8/9 - Write-ups, Community & Competitions",
    "p10": "Phase 10 - Projects & Portfolio",
    "p11": "Phase 11 - Certifications",
    "p12": "Phase 12 - Specialization Sampler",
    "p13": "Phase 13 - Career Development",
}


def thm(room, name=None):
    return (f"TryHackMe: {name or room}", f"https://tryhackme.com/room/{room}")


def bandit(a, b):
    return [(f"OverTheWire Bandit {n} -> {n + 1}", f"https://overthewire.org/wargames/bandit/bandit{n + 1}.html")
            for n in range(a, b + 1)]


def ps(path, name):
    return (f"PortSwigger Academy: {name}", f"https://portswigger.net/web-security/{path}")


# Frequently used links
THM = ("TryHackMe", "https://tryhackme.com")
PICO = ("picoGym practice", "https://play.picoctf.org/practice")
CYBERCHEF = ("CyberChef", "https://gchq.github.io/CyberChef/")
MESSER_NET = ("Professor Messer Network+ (N10-009)",
              "https://www.professormesser.com/network-plus/n10-009/n10-009-training-course/")
MESSER_SEC = ("Professor Messer Security+ (SY0-701)",
              "https://www.professormesser.com/security-plus/sy0-701/sy0-701-training-course/")
LINUX_JOURNEY = ("Linux Journey", "https://linuxjourney.com")
CS50 = ("CS50x (Harvard)", "https://cs50.harvard.edu/x/")
CS50P = ("CS50P - Python (Harvard)", "https://cs50.harvard.edu/python/")
ATBS = ("Automate the Boring Stuff with Python", "https://automatetheboringstuff.com")
MDN = ("MDN Web Docs", "https://developer.mozilla.org")
SQLBOLT = ("SQLBolt", "https://sqlbolt.com")
OWASP_TOP10 = ("OWASP Top 10", "https://owasp.org/www-project-top-ten/")
CTF101 = ("CTF101.org", "https://ctf101.org")
CRYPTOHACK = ("CryptoHack", "https://cryptohack.org")
CTFTIME = ("CTFtime", "https://ctftime.org")
MS_PS101 = ("Microsoft Learn: PowerShell 101",
            "https://learn.microsoft.com/en-us/powershell/scripting/learn/ps101/00-introduction")
WIRESHARK = ("Wireshark download", "https://www.wireshark.org/download.html")
BURP = ("Burp Suite Community", "https://portswigger.net/burp/communitydownload")
GHIDRA = ("Ghidra", "https://ghidra-sre.org")
GTFOBINS = ("GTFOBins", "https://gtfobins.github.io")
ROADMAP_LINK = ("The roadmap (ROADMAP.md)", ROADMAP)

LESSONS = []


def L(phase, title, tasks, links=(), tools=(), challenge=""):
    LESSONS.append({
        "phase": phase,
        "title": title,
        "tasks": list(tasks),
        "links": [{"name": n, "url": u} for n, u in links],
        "tools": list(tools),
        "challenge": challenge,
    })


# ---------------------------------------------------------------- Phase 0
L("p0", "What is cybersecurity? + set up your learning system",
  ["Read 'Phase 0 - What is Cybersecurity?' in the roadmap",
   "Create free accounts: TryHackMe, picoCTF, PortSwigger Academy",
   "Create a GitHub repo called `cybersec-notes` - every day's notes go here",
   "Pick a notes app (Obsidian or plain Markdown in that repo)"],
  [ROADMAP_LINK, THM, ("picoCTF", "https://picoctf.org"), ("PortSwigger Academy", "https://portswigger.net/web-security"),
   ("Krebs on Security", "https://krebsonsecurity.com")],
  ["GitHub", "Obsidian / Markdown"],
  "In 5 lines, write what cybersecurity protects and why. Include one real breach you read about on Krebs on Security.")

L("p0", "Ethics, law & responsible disclosure",
  ["Read 'Ethical & Legal Boundaries' in the roadmap - twice",
   "Read the OWASP Vulnerability Disclosure cheat sheet",
   "Look up your country's computer-misuse law (e.g. IT Act 2000 s.43/66 in India, CFAA in the US)"],
  [ROADMAP_LINK,
   ("OWASP Vulnerability Disclosure Cheat Sheet",
    "https://cheatsheetseries.owasp.org/cheatsheets/Vulnerability_Disclosure_Cheat_Sheet.html")],
  [],
  "Write your personal 'rules of engagement' (3 rules) and commit them as the first file in cybersec-notes.")

L("p0", "Explore the domains (don't choose yet!)",
  ["Study the domain mindmap in the roadmap (Offensive, AppSec, Defensive, Investigative, ...)",
   "Watch one NetworkChuck video about cybersecurity careers",
   "Search LinkedIn for one job post each in 3 domains that sound interesting"],
  [ROADMAP_LINK, ("NetworkChuck (YouTube)", "https://www.youtube.com/@NetworkChuck"),
   ("Google Cybersecurity Certificate (audit free)",
    "https://www.coursera.org/professional-certificates/google-cybersecurity")],
  [],
  "For 3 domains, write one line each: 'A normal day in this job looks like ...'")

L("p0", "Build a news habit + NIST Cybersecurity Framework",
  ["Read 3 articles on The Hacker News",
   "Skim the NIST CSF 2.0 functions: Govern, Identify, Protect, Detect, Respond, Recover",
   "Subscribe/bookmark: The Hacker News, Krebs on Security"],
  [("The Hacker News", "https://thehackernews.com"), ("NIST CSF", "https://www.nist.gov/cyberframework"),
   ("Krebs on Security", "https://krebsonsecurity.com")],
  [],
  "Pick one incident from today's news and map what went wrong to the CSF functions.")

L("p0", "Build your home lab: VirtualBox + Ubuntu VM",
  ["Install VirtualBox (or VMware Workstation Player)",
   "Download Ubuntu Desktop LTS and install it as a VM (2 CPU, 4 GB RAM, 30 GB disk)",
   "Install guest additions, update with `sudo apt update && sudo apt upgrade`",
   "Do NOT install Kali yet - the roadmap explains why"],
  [("VirtualBox", "https://www.virtualbox.org"), ("Ubuntu Desktop", "https://ubuntu.com/download/desktop")],
  ["VirtualBox", "Ubuntu"],
  "Take a VM snapshot named `clean-install`. Screenshot it into your notes.")

# ---------------------------------------------------------------- Phase 1
L("p1", "How a computer runs a program (CPU, RAM, storage)",
  ["Watch CS50x Lecture 0 (first hour is enough)",
   "Learn: CPU, RAM vs storage, fetch-decode-execute cycle"],
  [CS50, ("Nand2Tetris (optional deep dive)", "https://www.nand2tetris.org")],
  ["Ubuntu VM: `lscpu`, `free -h`, `lsblk`"],
  "In your VM, find: number of CPU cores, total RAM and disk size. Explain fetch-decode-execute in 3 sentences.")

L("p1", "Processes, memory & filesystems - what an OS does",
  ["Do the TryHackMe room 'Operating Systems Introduction'",
   "Learn: process vs program, PID, virtual memory, filesystem"],
  [thm("operatingsystemsintroduction", "Operating Systems Introduction")],
  ["`ps aux`, `top`, `df -h`"],
  "Using `top`, find the process using the most memory in your VM. What is its PID and owner?")

L("p1", "Binary, hex & how data is represented",
  ["Learn binary and hexadecimal counting (CS50 week 0 notes)",
   "Learn ASCII - every character is a number",
   "Play with CyberChef 'To Binary', 'To Hex', 'From Hex'"],
  [CS50, CYBERCHEF],
  ["CyberChef"],
  "By hand: convert 192 to binary and hex, and 0x41 to its ASCII letter. Verify in CyberChef.")

L("p1", "What is a network? LAN vs WAN",
  ["TryHackMe: 'What Is Networking?'",
   "Professor Messer Network+: watch the networking intro videos"],
  [thm("whatisnetworking", "What Is Networking?"), MESSER_NET],
  [],
  "Draw your home network (router, phone, laptop, ISP) and add the diagram to your notes.")

L("p1", "IP addressing - public vs private",
  ["TryHackMe: 'Intro to Networking'",
   "Learn the private ranges: 10/8, 172.16/12, 192.168/16"],
  [thm("introtonetworking", "Intro to Networking")],
  ["`ip a`", "`curl ifconfig.me`"],
  "Find your private IP and your public IP. Explain in your notes why they are different.")

L("p1", "Subnetting & CIDR",
  ["Learn CIDR notation, network/broadcast address, usable hosts",
   "Do 10 practice questions on subnettingpractice.com"],
  [MESSER_NET, ("Subnetting Practice", "https://subnettingpractice.com")],
  [],
  "For 192.168.10.0/26: network address, broadcast address, usable host count? (Check with /challenge too.)")

L("p1", "MAC addresses, Ethernet & ARP",
  ["TryHackMe: 'Layer 2'",
   "Learn how ARP maps IP -> MAC and why ARP spoofing works"],
  [thm("layer2", "Layer 2"), ("Wireshark OUI lookup", "https://www.wireshark.org/tools/oui-lookup.html")],
  ["`ip neigh`"],
  "Read your ARP table and look up the vendor of your router's MAC address.")

L("p1", "Ports, protocols, TCP vs UDP",
  ["TryHackMe: 'Networking Concepts'",
   "Learn TCP (reliable, connection) vs UDP (fast, connectionless)"],
  [thm("networkingconcepts", "Networking Concepts")],
  ["`ss -tulpn`"],
  "From memory, list 15 well-known ports and their services (21, 22, 25, 53, 80, 443, 445, 3389 ...).")

L("p1", "TCP handshake + your first Wireshark capture",
  ["Install Wireshark",
   "TryHackMe: 'Network Traffic Basics'",
   "Capture traffic while you open a website"],
  [WIRESHARK, thm("networktrafficbasics", "Network Traffic Basics")],
  ["Wireshark"],
  "In your capture, find the SYN, SYN-ACK and ACK of one TCP connection. Screenshot the 3 packets.")

L("p1", "DNS in detail",
  ["TryHackMe: 'DNS in Detail'",
   "Learn record types: A, AAAA, CNAME, MX, TXT, NS"],
  [thm("dnsindetail", "DNS in Detail")],
  ["`dig`", "`nslookup`"],
  "Use `dig` to find the MX and TXT records of owasp.org. What does the SPF TXT record tell you?")

L("p1", "DHCP, routing & NAT",
  ["Learn DHCP DORA (Discover, Offer, Request, Ack)",
   "Learn how NAT lets many private IPs share one public IP",
   "Professor Messer: routing & NAT videos"],
  [MESSER_NET],
  ["`ip route`", "`traceroute`"],
  "Run `traceroute google.com`. How many hops? Which hop is your own router?")

L("p1", "HTTP & HTTPS",
  ["TryHackMe: 'HTTP in Detail'",
   "Learn methods (GET/POST), status codes, headers"],
  [thm("httpindetail", "HTTP in Detail"), MDN],
  ["`curl -I`", "Browser DevTools"],
  "Run `curl -I https://owasp.org`. Write down the status code and 3 security-related headers you see.")

L("p1", "TLS & certificates",
  ["Learn how TLS protects HTTP: certificates, CAs, handshake (high level)",
   "Inspect a website's certificate in your browser"],
  [MDN],
  ["`openssl s_client -connect example.com:443`"],
  "For github.com find: certificate issuer, expiry date, and which TLS version was negotiated.")

L("p1", "Firewalls",
  ["Learn stateless vs stateful firewalls",
   "Configure `ufw` in your Ubuntu VM"],
  [MESSER_NET],
  ["`ufw`"],
  "Enable ufw, allow only SSH (22) inbound, then list the rules with `sudo ufw status verbose`.")

L("p1", "The OSI model",
  ["Learn the 7 layers (Please Do Not Throw Sausage Pizza Away)",
   "TryHackMe: 'Network Security Essentials'"],
  [thm("networksecurityessentials", "Network Security Essentials"), MESSER_NET],
  [],
  "Map these to an OSI layer: switch, router, HTTP, TCP, IP, Ethernet, TLS, DNS, MAC address, cable.")

L("p1", "TCP/IP model + Wireshark filters",
  ["Compare TCP/IP (4 layers) with OSI (7 layers)",
   "Practice Wireshark display filters: `ip.addr==`, `tcp.port==`, `http`, `dns`",
   "Download `http.cap` from Wireshark Sample Captures"],
  [("Wireshark Sample Captures", "https://wiki.wireshark.org/SampleCaptures"), WIRESHARK],
  ["Wireshark"],
  "Open http.cap: what URL was requested and what web server answered?")

L("p1", "Networking checkpoint: build a cheat sheet",
  ["Write a one-page networking cheat sheet (ports, OSI, subnetting, DNS records, commands)",
   "Push it to your cybersec-notes repo",
   "TryHackMe: 'Beginner Path Intro'"],
  [thm("beginnerpathintro", "Beginner Path Intro")],
  ["GitHub"],
  "Without notes, explain what happens when you type a URL in the browser and press Enter (DNS -> TCP -> TLS -> HTTP).")

# ---------------------------------------------------------------- Phase 2
L("p2", "Linux filesystem & navigation",
  ["Linux Journey: 'Command Line' section",
   "Learn the hierarchy: /etc, /home, /var, /tmp, /usr, /bin",
   "Read OverTheWire Bandit rules, then solve level 0"],
  [LINUX_JOURNEY, ("OverTheWire Bandit", "https://overthewire.org/wargames/bandit/")] + bandit(0, 0),
  ["`ls`, `cd`, `pwd`, `cat`", "`ssh`"],
  "Solve Bandit 0 -> 1. Save the password in a private notes file (not on GitHub!).")

L("p2", "Files & directories",
  ["TryHackMe: 'Linux Fundamentals Part 1'",
   "Practice cp, mv, rm, mkdir, touch, special filenames (`-`, spaces, hidden)"],
  [thm("linuxfundamentalspart1", "Linux Fundamentals Part 1")] + bandit(1, 3),
  ["`cp`, `mv`, `rm`, `mkdir`"],
  "Solve Bandit levels 1 -> 4.")

L("p2", "Finding files: find & file",
  ["Learn `find` with -name, -type, -size, -user, -group",
   "Learn `file` to detect file types"],
  bandit(4, 6),
  ["`find`", "`file`"],
  "Solve Bandit 4 -> 7.")

L("p2", "grep, sort, uniq & pipes",
  ["TryHackMe: 'Linux Fundamentals Part 2'",
   "Learn pipes `|` and redirection `>`, `>>`, `2>/dev/null`"],
  [thm("linuxfundamentalspart2", "Linux Fundamentals Part 2")] + bandit(7, 9),
  ["`grep`", "`sort | uniq -c`", "`strings`"],
  "Solve Bandit 7 -> 10.")

L("p2", "Encoding tricks on the command line",
  ["Learn `base64 -d`, `tr` (ROT13), `xxd`, gzip/bzip2/tar",
   "Bandit 12 is long - be patient and use a /tmp working dir"],
  bandit(10, 12) + [CYBERCHEF],
  ["`base64`", "`tr`", "`xxd`", "`tar`"],
  "Solve Bandit 10 -> 13.")

L("p2", "Permissions, users & groups",
  ["TryHackMe: 'Linux Fundamentals Part 3'",
   "Learn rwx, octal (755, 640), chown, sudo, /etc/passwd vs /etc/shadow"],
  [thm("linuxfundamentalspart3", "Linux Fundamentals Part 3"), LINUX_JOURNEY],
  ["`chmod`", "`chown`", "`useradd`", "`id`"],
  "In your VM create user `analyst`, group `soc`, and a folder only the soc group can read (mode 750).")

L("p2", "SSH & keys",
  ["Learn SSH key auth (private vs public key)",
   "Generate an ed25519 key and SSH from your host into your VM"],
  bandit(13, 14),
  ["`ssh-keygen`", "`ssh -i`", "`scp`"],
  "Solve Bandit 13 -> 15 and log into your own VM with a key instead of a password.")

L("p2", "Networking from the terminal: nc & openssl",
  ["Learn `nc` (netcat) to talk to ports",
   "Learn `openssl s_client` for TLS ports",
   "Learn basic `nmap` on localhost only"],
  bandit(15, 17),
  ["`nc`", "`openssl`", "`nmap localhost`"],
  "Solve Bandit 15 -> 18.")

L("p2", "Processes & services",
  ["Learn ps, top, kill, jobs, systemctl, journalctl",
   "Install nginx in your VM and manage it as a service"],
  [LINUX_JOURNEY],
  ["`systemctl`", "`journalctl`", "`kill`"],
  "Install nginx, stop/start it, and find its log lines with `journalctl -u nginx`.")

L("p2", "Package management, PATH & environment variables",
  ["Learn apt (install, remove, search), dpkg",
   "Learn env vars: `$PATH`, `$HOME`, `export`, `.bashrc`"],
  bandit(18, 20),
  ["`apt`", "`env`", "`export`"],
  "Solve Bandit 18 -> 21. Then add `~/bin` to your PATH permanently.")

L("p2", "Cron & scheduled jobs",
  ["Learn crontab syntax (`m h dom mon dow`)",
   "Understand why writable cron scripts are a privilege-escalation risk"],
  bandit(21, 23) + [("crontab.guru", "https://crontab.guru")],
  ["`crontab -e`", "crontab.guru"],
  "Solve Bandit 21 -> 24.")

L("p2", "Linux logs",
  ["Explore /var/log (auth.log, syslog)",
   "TryHackMe: 'Intro to Logs'"],
  [thm("introtologs", "Intro to Logs")],
  ["`grep`", "`tail -f`", "`journalctl`"],
  "Make 3 failed SSH logins to your VM, then find them in /var/log/auth.log with one grep command.")

L("p2", "Bandit: scripting & git",
  ["Bandit 24 needs a small brute-force loop (bash)",
   "Bandit 27-31 teach git - use `git log`, branches and tags"],
  bandit(24, 24) + bandit(27, 31),
  ["bash loops", "`git`"],
  "Solve Bandit 24 -> 25 and 27 -> 32. (25-26 are optional tricky ones.)")

L("p2", "Windows fundamentals 1",
  ["TryHackMe: 'Windows Fundamentals 1'",
   "Explore: file system (NTFS), Task Manager, services.msc"],
  [thm("windowsfundamentals1xbx", "Windows Fundamentals 1"),
   ("Microsoft Learn", "https://learn.microsoft.com/en-us/training/")],
  ["Task Manager", "services.msc"],
  "List 3 Windows services, their startup type and the account they run as.")

L("p2", "Windows users, permissions & UAC",
  ["TryHackMe: 'Windows Fundamentals 2'",
   "Learn local users/groups, UAC, NTFS permissions"],
  [thm("windowsfundamentals2x0x", "Windows Fundamentals 2")],
  ["lusrmgr.msc", "`whoami /priv`"],
  "Run `whoami /all` and explain 3 privileges listed.")

L("p2", "Windows command line",
  ["TryHackMe: 'Windows Command Line'"],
  [thm("windowscommandline", "Windows Command Line")],
  ["`ipconfig /all`", "`netstat -ano`", "`tasklist`"],
  "Use `netstat -ano` + `tasklist` to find which program owns one listening port.")

L("p2", "Windows Event Logs",
  ["TryHackMe: 'Windows Fundamentals 3'",
   "Open Event Viewer -> Windows Logs -> Security"],
  [thm("windowsfundamentals3xzx", "Windows Fundamentals 3")],
  ["Event Viewer"],
  "Find a 4624 (successful logon) and 4625 (failed logon) event. What logon type did each have?")

L("p2", "PowerShell basics",
  ["Microsoft Learn: PowerShell 101 (chapters 1-3)",
   "Learn Get-Help, Get-Command, Get-Member, the pipeline"],
  [MS_PS101],
  ["PowerShell"],
  "One-liner: show the 5 processes using the most CPU (`Get-Process | Sort-Object CPU -Descending | Select-Object -First 5`).")

# ---------------------------------------------------------------- Phase 3
L("p3", "How web applications work",
  ["TryHackMe: 'Web Application Basics'",
   "MDN: An overview of HTTP",
   "Remember: no SQL injection before you understand SQL and web apps"],
  [thm("webapplicationbasics", "Web Application Basics"),
   ("MDN: HTTP overview", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview")],
  ["Browser DevTools (Network tab)"],
  "Open DevTools on any site and list every request header your browser sent for the main page.")

L("p3", "HTML & JavaScript basics",
  ["MDN: Getting started with the web (HTML + JS)",
   "Re-read your own todolist2 `script.js` - you already wrote JS!"],
  [("MDN: Getting started", "https://developer.mozilla.org/en-US/docs/Learn"),
   ("freeCodeCamp", "https://www.freecodecamp.org")],
  ["VS Code", "DevTools Console"],
  "Your todo app uses `textContent`. Write in notes why `innerHTML` with user input would be dangerous (hint: XSS).")

L("p3", "Cookies, sessions, authentication vs authorization",
  ["MDN: HTTP cookies",
   "Learn session IDs, cookie flags: HttpOnly, Secure, SameSite",
   "Authentication = who you are, Authorization = what you may do"],
  [("MDN: Cookies", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies")],
  ["DevTools -> Application -> Cookies"],
  "Log into a site you use. Which cookie is the session cookie, and which flags does it have?")

L("p3", "REST APIs & JSON",
  ["Learn REST verbs (GET, POST, PUT, DELETE), JSON, status codes",
   "Call the public GitHub API"],
  [("GitHub REST API docs", "https://docs.github.com/en/rest")],
  ["`curl`", "`jq`"],
  "`curl https://api.github.com/users/<your-username>` and use jq to print only your public repo count.")

L("p3", "SQL basics 1",
  ["SQLBolt lessons 1-6 (SELECT, WHERE, ORDER BY, LIMIT)"],
  [SQLBOLT],
  [],
  "Finish SQLBolt lessons 1-6.")

L("p3", "SQL basics 2",
  ["SQLBolt lessons 7-12 (JOINs, NULL, expressions, aggregates)"],
  [SQLBOLT],
  [],
  "Finish SQLBolt lessons 7-12.")

L("p3", "SQL basics 3",
  ["SQLBolt lessons 13-18 (INSERT, UPDATE, DELETE, CREATE)",
   "Think: how is a login query built? `SELECT * FROM users WHERE name='?' AND pass='?'`"],
  [SQLBOLT],
  [],
  "Finish SQLBolt. Then write in notes what happens to that login query if the name is `admin'--`.")

L("p3", "Python 1: variables, types, conditionals",
  ["Install Python 3 + VS Code",
   "CS50P Lecture 0 (Functions, Variables) and Lecture 1 (Conditionals)"],
  [CS50P, ("Python downloads", "https://www.python.org/downloads/")],
  ["Python 3", "VS Code"],
  "Write `grade.py`: read a score 0-100 and print A/B/C/D/F. Handle invalid input.")

L("p3", "Python 2: loops & functions",
  ["CS50P Lecture 2 (Loops)",
   "TryHackMe: 'Python Basics'"],
  [CS50P, thm("pythonbasics", "Python Basics")],
  ["Python 3"],
  "Write `is_prime(n)` and print all primes below 100.")

L("p3", "Python 3: lists & dictionaries",
  ["Practice list/dict operations, comprehensions",
   "Automate the Boring Stuff: chapters 4-5"],
  [ATBS],
  ["Python 3"],
  "Count word frequency in any .txt file and print the top 10 words.")

L("p3", "Python 4: files & exceptions",
  ["CS50P Lecture 3 (Exceptions) and Lecture 6 (File I/O)"],
  [CS50P],
  ["Python 3"],
  "Parse your VM's /var/log/auth.log and count failed SSH logins per IP address.")

L("p3", "Python 5: modules & command-line arguments",
  ["Learn `import`, `argparse`, `sys.argv`, virtual environments (`python -m venv`)"],
  [("Python argparse tutorial", "https://docs.python.org/3/howto/argparse.html")],
  ["argparse", "venv"],
  "Turn yesterday's log parser into `logparse.py --file auth.log --top 5`.")

L("p3", "Python 6: HTTP requests",
  ["Automate the Boring Stuff: Web Scraping chapter",
   "Install `requests` in a venv"],
  [ATBS, ("requests docs", "https://requests.readthedocs.io")],
  ["requests"],
  "Script: given a URL, print status code and whether HSTS, CSP and X-Frame-Options headers are present.")

L("p3", "Python 7: sockets & a banner grabber",
  ["Learn the `socket` module: connect, send, recv",
   "TryHackMe: 'Custom Tooling with Python'"],
  [thm("customtoolingpython", "Custom Tooling with Python"),
   ("Python socket docs", "https://docs.python.org/3/library/socket.html")],
  ["socket"],
  "Grab the SSH banner of YOUR VM with a 10-line Python script.")

L("p3", "Python 8: build a port scanner (your own VM only)",
  ["Combine sockets + threads (`concurrent.futures`)",
   "Only scan machines you own - roadmap rule #1"],
  [("concurrent.futures docs", "https://docs.python.org/3/library/concurrent.futures.html")],
  ["Python 3"],
  "Scan ports 1-1024 on your VM in under 10 seconds. Compare with `nmap` output.")

L("p3", "Python 9: hashing & a password strength checker",
  ["Learn `hashlib` (md5, sha256) and why fast hashes are bad for passwords (use bcrypt/argon2)"],
  [("hashlib docs", "https://docs.python.org/3/library/hashlib.html")],
  ["hashlib"],
  "Build `pwcheck.py`: score length, character classes, and reject passwords from a small common-password list.")

L("p3", "Bash scripting 1",
  ["learnshell.org: basics, variables, arrays, loops, conditions"],
  [("learnshell.org", "https://www.learnshell.org")],
  ["bash"],
  "Write `sweep.sh` that pings 192.168.x.1-254 on YOUR home network and prints live hosts.")

L("p3", "Bash scripting 2: functions & automation",
  ["Learn functions, `$1 $2 $@`, exit codes, `set -euo pipefail`"],
  [("learnshell.org", "https://www.learnshell.org")],
  ["bash", "cron"],
  "Write `backup.sh` that tars your notes folder with a date in the filename; schedule it with cron.")

L("p3", "PowerShell scripting",
  ["Microsoft Learn: PowerShell 101 chapters 4-6 (functions, scripts)"],
  [MS_PS101],
  ["PowerShell"],
  "Script that lists local users, whether they are enabled, and their last logon (`Get-LocalUser`).")

L("p3", "(Optional) C basics: memory, pointers, stack",
  ["CS50x Week 4: Memory - pointers, malloc, stack vs heap",
   "Optional for web/SOC paths, important for RE & pwn later"],
  [CS50],
  ["gcc"],
  "Write a C program that prints the address of a local variable and a malloc'd buffer. Which is stack, which is heap?")

L("p3", "Git & GitHub portfolio day",
  ["Create a `security-scripts` repo with your port scanner, log parser and pwcheck",
   "Write a README for each: problem, usage, what you learned"],
  [("GitHub Docs: About READMEs",
    "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes")],
  ["git", "GitHub"],
  "Push the repo and pin it on your GitHub profile.")

# ---------------------------------------------------------------- Phase 4
L("p4", "CIA triad & AAA",
  ["Professor Messer Security+: security concepts videos",
   "Learn Confidentiality, Integrity, Availability + Authentication, Authorization, Accounting"],
  [MESSER_SEC, ("NIST Glossary", "https://csrc.nist.gov/glossary")],
  [],
  "For each: ransomware, a leaked database, a tampered bank transaction - which CIA pillar is hit?")

L("p4", "Authentication, MFA & password storage",
  ["Learn factors: know / have / are",
   "Learn salting + slow hashing (bcrypt, argon2)",
   "Enable MFA on your email and GitHub today"],
  [MESSER_SEC, ("OWASP Password Storage Cheat Sheet",
                "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html")],
  ["Authenticator app"],
  "Explain in notes why SMS is the weakest second factor and why salts stop rainbow tables.")

L("p4", "Encoding vs hashing vs encryption",
  ["TryHackMe: 'CyberChef: The Basics'",
   "Encoding = reversible, no key. Hashing = one-way. Encryption = reversible with key"],
  [thm("cyberchefbasics", "CyberChef: The Basics"), CYBERCHEF],
  ["CyberChef"],
  "In CyberChef: Base64 'hello', MD5 'hello', AES-encrypt 'hello'. Explain which one is NOT security.")

L("p4", "Symmetric vs asymmetric cryptography",
  ["Learn AES (shared key) vs RSA/ECC (key pairs), key exchange",
   "Use openssl on the command line"],
  [MESSER_SEC],
  ["`openssl enc -aes-256-cbc -pbkdf2`", "`openssl genpkey`"],
  "AES-encrypt a file with a password, then generate an RSA key pair and encrypt a short message with the public key.")

L("p4", "Hashes & password cracking concepts",
  ["TryHackMe: 'Crack the Hash'",
   "Learn hash identification and wordlists (rockyou)"],
  [thm("crackthehash", "Crack the Hash"), ("hashcat example hashes", "https://hashcat.net/wiki/doku.php?id=example_hashes")],
  ["hashcat", "John the Ripper", "CrackStation"],
  "Finish Level 1 of Crack the Hash.")

L("p4", "Digital signatures & PKI",
  ["Learn: sign with private key, verify with public key; certificate chains"],
  [MESSER_SEC, ("GitHub: signing commits",
                "https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits")],
  ["gpg", "ssh-keygen -Y sign"],
  "Sign a git commit and get the 'Verified' badge on GitHub.")

L("p4", "Vulnerabilities, threats, exploits, risk + CVE/CVSS",
  ["TryHackMe: 'Vulnerabilities 101'",
   "Learn how CVE IDs and CVSS scores work"],
  [thm("vulnerabilities101", "Vulnerabilities 101"), ("NVD", "https://nvd.nist.gov")],
  [],
  "Look up CVE-2021-44228 (Log4Shell): CVSS score, affected product, and why it was so severe.")

L("p4", "Attack surface & common attacks",
  ["TryHackMe: 'Common Attacks'",
   "Learn: phishing, malware, MITM, password attacks, DoS"],
  [thm("commonattacks", "Common Attacks")],
  [],
  "List the full attack surface of your todolist2 web app (inputs, hosting, dependencies, users).")

L("p4", "Phishing analysis",
  ["TryHackMe: 'Phishing Emails 1'",
   "Learn email headers: From vs Return-Path, SPF, DKIM, DMARC"],
  [thm("phishingemails1tryoe", "Phishing Emails 1")],
  ["Gmail 'Show original'"],
  "Open 'Show original' on a spam mail in your inbox. Did SPF/DKIM pass? What gave it away?")

L("p4", "Defense in depth & security controls",
  ["TryHackMe: 'Defensive Security Intro'",
   "Learn control types: preventive, detective, corrective; technical vs administrative"],
  [thm("defensivesecurityintroQR", "Defensive Security Intro")],
  [],
  "Design 5 layers of defense for a college computer lab. Name the control type of each.")

L("p4", "OWASP Top 10 - part 1 (A01-A05)",
  ["Read A01 Broken Access Control to A05 Security Misconfiguration",
   "TryHackMe: 'Intro to Web Application Security'"],
  [OWASP_TOP10, thm("introwebapplicationsecurity", "Intro to Web Application Security")],
  [],
  "For each of A01-A05 write one real-world example in one line.")

L("p4", "OWASP Top 10 - part 2 (A06-A10)",
  ["Read A06 Vulnerable Components to A10 SSRF",
   "TryHackMe: 'Web Security Essentials'"],
  [OWASP_TOP10, thm("websecurityessentials", "Web Security Essentials")],
  [],
  "For each of A06-A10 write how a developer would prevent it.")

L("p4", "Threat modeling with STRIDE",
  ["Read the OWASP Threat Modeling cheat sheet",
   "STRIDE: Spoofing, Tampering, Repudiation, Info disclosure, DoS, Elevation of privilege"],
  [("OWASP Threat Modeling Cheat Sheet",
    "https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html")],
  ["draw.io"],
  "Draw a data-flow diagram of a login page and list one STRIDE threat per category.")

L("p4", "Milestone: ISC2 Certified in Cybersecurity (free)",
  ["Read about ISC2 CC - free training + exam voucher (when available)",
   "Register and start the free official training (1 module/week alongside this plan)"],
  [("ISC2 CC", "https://www.isc2.org/certifications/cc"), MESSER_SEC],
  [],
  "Register for ISC2 CC training and write down your target exam month.")

# ---------------------------------------------------------------- Phase 5
L("p5", "Burp Suite setup & Repeater",
  ["Install Burp Suite Community and use its built-in browser",
   "TryHackMe: 'Burp Suite: Repeater'"],
  [BURP, thm("burpsuiterepeater", "Burp Suite: Repeater"),
   ("Burp getting started", "https://portswigger.net/burp/documentation/desktop/getting-started")],
  ["Burp Suite"],
  "Intercept a request in a lab, change a parameter in Repeater and observe the different response.")

L("p5", "SQL injection 1 (PortSwigger)",
  ["Read the PortSwigger SQL injection topic",
   "Solve the first 2 Apprentice labs (WHERE clause, login bypass)"],
  [ps("sql-injection", "SQL injection")],
  ["Burp Suite"],
  "Solve both labs and explain the payload in your notes.")

L("p5", "SQL injection 2: UNION attacks",
  ["PortSwigger: SQL injection UNION attacks",
   "Learn to find column count and which columns show text"],
  [ps("sql-injection/union-attacks", "SQLi UNION attacks")],
  ["Burp Suite"],
  "Solve the 'retrieving data from other tables' lab.")

L("p5", "Cross-site scripting (XSS)",
  ["PortSwigger: Cross-site scripting",
   "Solve reflected XSS and stored XSS apprentice labs"],
  [ps("cross-site-scripting", "Cross-site scripting")],
  ["Burp Suite", "DevTools"],
  "Solve 2 XSS labs. Then explain why your todo app using `textContent` is safe.")

L("p5", "Path traversal",
  ["PortSwigger: Path traversal"],
  [ps("file-path-traversal", "Path traversal")],
  ["Burp Suite"],
  "Solve the simple-case lab and 1 more (absolute path or nested sequences).")

L("p5", "Access control & IDOR",
  ["PortSwigger: Access control vulnerabilities (OWASP A01)"],
  [ps("access-control", "Access control")],
  ["Burp Suite"],
  "Solve 3 apprentice access-control labs, including one IDOR.")

L("p5", "Authentication vulnerabilities",
  ["PortSwigger: Authentication vulnerabilities"],
  [ps("authentication", "Authentication")],
  ["Burp Suite Intruder"],
  "Solve 'username enumeration via different responses' and '2FA simple bypass'.")

L("p5", "OS command injection",
  ["PortSwigger: OS command injection"],
  [ps("os-command-injection", "OS command injection")],
  ["Burp Suite"],
  "Solve the simple-case lab and explain how input validation would have prevented it.")

L("p5", "Server-side request forgery (SSRF)",
  ["PortSwigger: SSRF (OWASP A10)"],
  [ps("ssrf", "SSRF")],
  ["Burp Suite"],
  "Solve the 'basic SSRF against the local server' lab.")

L("p5", "OWASP Juice Shop setup",
  ["Install Docker in your VM",
   "Run Juice Shop: `docker run -d -p 3000:3000 bkimminich/juice-shop`"],
  [("OWASP Juice Shop", "https://owasp.org/www-project-juice-shop/"),
   ("Pwning OWASP Juice Shop (free book)", "https://pwning.owasp-juice.shop")],
  ["Docker", "Burp Suite"],
  "Find the hidden Score Board page.")

L("p5", "Juice Shop: 1-star challenges",
  ["Solve 1-star challenges only; use hints from the free book if stuck"],
  [("Pwning OWASP Juice Shop (free book)", "https://pwning.owasp-juice.shop")],
  ["Burp Suite", "DevTools"],
  "Solve 5 one-star Juice Shop challenges.")

L("p5", "DVWA: SQLi & XSS on low security",
  ["Run DVWA in Docker or follow its README",
   "Set security to 'low', then try 'medium' and read the source code difference"],
  [("DVWA", "https://github.com/digininja/DVWA")],
  ["Docker", "Burp Suite"],
  "Exploit SQL Injection on low AND medium. What changed in the code?")

L("p5", "Passive reconnaissance",
  ["TryHackMe: 'Passive Recon'",
   "Learn whois, DNS, certificate transparency (crt.sh)"],
  [thm("passiverecon", "Passive Recon"), ("crt.sh", "https://crt.sh")],
  ["whois", "dig", "crt.sh"],
  "Use crt.sh to list subdomains of owasp.org (public data only - no scanning).")

L("p5", "Active reconnaissance",
  ["TryHackMe: 'Active Recon'"],
  [thm("activerecon", "Active Recon")],
  ["ping", "traceroute", "telnet", "nc"],
  "Finish the room. Write the difference between passive and active recon - and why active needs permission.")

L("p5", "Nmap",
  ["TryHackMe: 'Nmap' and 'Further Nmap'"],
  [thm("nmap02", "Nmap"), thm("furthernmap", "Further Nmap"), ("Nmap book (free)", "https://nmap.org/book/")],
  ["nmap"],
  "Scan your own VM with `nmap -sV -sC` and explain every open port.")

L("p5", "Network services 1 (SMB, Telnet, FTP)",
  ["TryHackMe: 'Network Services'"],
  [thm("networkservices", "Network Services")],
  ["smbclient", "enum4linux", "ftp"],
  "Finish the room.")

L("p5", "Network services 2 (NFS, SMTP, MySQL)",
  ["TryHackMe: 'Network Services 2'"],
  [thm("networkservices2", "Network Services 2")],
  ["showmount", "mysql client"],
  "Finish the room.")

L("p5", "Brute force with Hydra",
  ["TryHackMe: 'Hydra'",
   "Then do 'Brute It'"],
  [thm("hydra", "Hydra"), thm("bruteit", "Brute It")],
  ["hydra", "john"],
  "Finish both rooms. Note how a lockout policy would have stopped you.")

L("p5", "Metasploit introduction",
  ["TryHackMe: 'Metasploit: Introduction'"],
  [thm("metasploitintro", "Metasploit: Introduction")],
  ["msfconsole"],
  "Finish the room. Explain exploit vs payload vs module in your notes.")

L("p5", "First box: Pickle Rick",
  ["TryHackMe: 'Pickle Rick' - recon -> web -> command injection",
   "Write notes as you go: what you tried, what failed"],
  [thm("picklerick", "Pickle Rick")],
  ["nmap", "gobuster/ffuf", "Burp Suite"],
  "Find all 3 ingredients.")

L("p5", "Box: Basic Pentesting",
  ["TryHackMe: 'Basic Pentesting'"],
  [thm("basicpentestingjt", "Basic Pentesting")],
  ["nmap", "enum4linux", "hydra"],
  "Root the box.")

L("p5", "Box: Agent Sudo",
  ["TryHackMe: 'Agent Sudo'"],
  [thm("agentsudoctf", "Agent Sudo")],
  ["hydra", "steghide", "binwalk"],
  "Root the box.")

L("p5", "Box: Blue (Windows)",
  ["TryHackMe: 'Blue' (EternalBlue / MS17-010)"],
  [thm("blue", "Blue")],
  ["nmap", "Metasploit"],
  "Root the box and read about the WannaCry outbreak that used the same bug.")

L("p5", "Linux privilege escalation basics",
  ["TryHackMe: 'Linux PrivEsc'",
   "Learn sudo -l, SUID binaries, cron, writable files"],
  [thm("linprivesc", "Linux PrivEsc"), GTFOBINS],
  ["`find / -perm -4000 2>/dev/null`", "GTFOBins"],
  "Complete the first 5 tasks and explain SUID abuse in your own words.")

L("p5", "Boxes: Bounty Hacker + Brooklyn Nine Nine",
  ["TryHackMe: 'Bounty Hacker' (cowboyhacker) and 'Brooklyn Nine Nine'"],
  [thm("cowboyhacker", "Bounty Hacker"), thm("brooklynninenine", "Brooklyn Nine Nine")],
  ["nmap", "hydra", "GTFOBins"],
  "Root both boxes.")

L("p5", "Hacker101 CTF",
  ["Watch the first Hacker101 video lesson",
   "Start the Hacker101 CTF"],
  [("Hacker101", "https://www.hacker101.com"), ("Hacker101 CTF", "https://ctf.hacker101.com")],
  ["Burp Suite"],
  "Capture 2 flags in Hacker101 CTF.")

# ---------------------------------------------------------------- Phase 6/7
L("p6", "What is a CTF? Categories tour",
  ["Read the Phase 6 section of the roadmap",
   "Skim CTF101.org categories"],
  [ROADMAP_LINK, CTF101, PICO],
  [],
  "Solve 3 picoGym 'General Skills' challenges.")

L("p6", "picoGym General Skills",
  ["Filter picoGym by General Skills, easiest first"],
  [PICO],
  ["Linux terminal", "Python"],
  "Solve 5 General Skills challenges.")

L("p6", "Crypto 1: classical ciphers",
  ["CTF101: Classic ciphers (Caesar, Vigenere, substitution)",
   "Try dcode.fr for cipher identification"],
  [CTF101, PICO, ("dCode", "https://www.dcode.fr/en")],
  ["CyberChef", "dCode"],
  "Solve 3 easy picoGym Cryptography challenges.")

L("p6", "Crypto 2: encoding & XOR",
  ["CryptoHack: 'Introduction' + 'General' (Encoding, XOR)"],
  [CRYPTOHACK],
  ["Python", "pwntools (`pip install pwntools`)"],
  "Finish CryptoHack General -> Encoding and XOR sections.")

L("p6", "Crypto 3: RSA concepts",
  ["CryptoHack: RSA Starter 1-6",
   "Learn n, e, d, phi - and why small e / shared primes break RSA"],
  [CRYPTOHACK],
  ["Python"],
  "Finish RSA Starter 1-6.")

L("p6", "Web exploitation CTFs 1",
  ["picoGym: Web Exploitation, easiest first",
   "Always check: page source, cookies, robots.txt, headers"],
  [PICO],
  ["DevTools", "Burp Suite", "curl"],
  "Solve 4 Web Exploitation challenges.")

L("p6", "Web exploitation CTFs 2",
  ["Continue picoGym Web; try TryHackMe 'Juicy Details' for log analysis of a web attack"],
  [PICO, thm("juicydetails", "Juicy Details")],
  ["Burp Suite"],
  "Solve 3 more Web challenges.")

L("p6", "Forensics 1: files & metadata",
  ["Learn file signatures (magic bytes), metadata, carving",
   "picoGym: Forensics easy"],
  [PICO, ("File signatures list", "https://en.wikipedia.org/wiki/List_of_file_signatures")],
  ["file", "exiftool", "binwalk", "xxd"],
  "Solve 3 Forensics challenges.")

L("p6", "Forensics 2: PCAP analysis",
  ["Wireshark: Follow TCP stream, Export Objects, Statistics -> Conversations"],
  [PICO, WIRESHARK],
  ["Wireshark", "tshark"],
  "Solve 2 PCAP-based challenges on picoGym.")

L("p6", "Steganography & encodings",
  ["TryHackMe: 'c4ptur3-th3-fl4g'"],
  [thm("c4ptur3th3fl4g", "c4ptur3-th3-fl4g")],
  ["steghide", "zsteg", "exiftool", "Audacity/Sonic Visualiser"],
  "Finish the room.")

L("p6", "OSINT 1",
  ["TryHackMe: 'OhSINT'",
   "Learn Google dorking operators: site:, filetype:, inurl:"],
  [thm("ohsint", "OhSINT"), ("Google Hacking Database", "https://www.exploit-db.com/google-hacking-database")],
  ["exiftool", "Reverse image search"],
  "Finish OhSINT.")

L("p6", "OSINT 2: search skills",
  ["TryHackMe: 'Search Skills'"],
  [thm("searchskills", "Search Skills"), ("Shodan", "https://www.shodan.io")],
  ["Shodan", "Google dorks"],
  "Finish the room. Write your 5 favourite dorks in your notes.")

L("p6", "Reverse engineering 1",
  ["Learn static analysis basics: strings, file, ltrace/strace",
   "picoGym: Reverse Engineering easy"],
  [PICO, GHIDRA],
  ["strings", "ltrace", "Ghidra"],
  "Solve 3 Reverse Engineering challenges.")

L("p6", "Reverse engineering 2: Ghidra",
  ["Install Ghidra; learn the decompiler view",
   "Try a level-1 crackme from crackmes.one"],
  [GHIDRA, ("crackmes.one", "https://crackmes.one")],
  ["Ghidra"],
  "Solve one difficulty-1 crackme and document it.")

L("p6", "Binary exploitation 1: buffer overflows",
  ["Watch LiveOverflow's binary exploitation intro videos",
   "Start pwn.college 'Getting Started'"],
  [("LiveOverflow", "https://www.youtube.com/@LiveOverflow"), ("pwn.college", "https://pwn.college")],
  ["gdb", "pwntools"],
  "Explain the stack, return address and why overflowing a buffer can change control flow.")

L("p6", "Binary exploitation 2",
  ["picoGym: 'buffer overflow 0' and 'buffer overflow 1'"],
  [PICO],
  ["gdb", "pwntools", "checksec"],
  "Solve buffer overflow 0 (and 1 if you can).")

L("p6", "CTF Collection Vol. 1",
  ["TryHackMe: 'CTF Collection Vol. 1' - mixed categories"],
  [thm("ctfcollectionvol1", "CTF Collection Vol. 1")],
  ["CyberChef", "exiftool", "steghide"],
  "Solve at least 10 tasks.")

# ---------------------------------------------------------------- Phase 8/9
L("p8", "Reading write-ups the right way",
  ["Read Phase 8 of the roadmap - the 7-step method",
   "Pick a challenge you failed; read only enough of a write-up to get unstuck"],
  [ROADMAP_LINK, ("CTFtime write-ups", "https://ctftime.org/writeups"), ("0xdf's blog", "https://0xdf.gitlab.io")],
  [],
  "Finish that failed challenge, then reproduce the full solution from scratch without the write-up.")

L("p8", "Write your first write-up",
  ["Use the roadmap template: description, analysis, approach, tools, steps, what failed, key learning",
   "Never publish write-ups for a live competition"],
  [ROADMAP_LINK, ("awesome-ctf", "https://github.com/apsdehal/awesome-ctf")],
  ["Markdown", "GitHub"],
  "Publish a write-up of your favourite solved challenge to GitHub.")

L("p8", "Find a competition on CTFtime",
  ["Browse upcoming events on CTFtime, prefer beginner/low-weight ones",
   "Check for college CTFs and picoCTF dates"],
  [("CTFtime upcoming", "https://ctftime.org/event/list/upcoming"), CTFTIME],
  [],
  "Register for one upcoming beginner CTF and put it in your calendar.")

L("p8", "Mock CTF: 3-hour timed session",
  ["Set a 3-hour timer, pick 6 unsolved picoGym challenges across categories",
   "Work like a real CTF: notes, time-box 30 min per challenge"],
  [PICO],
  ["Everything so far"],
  "Solve as many as you can; log time spent and where you got stuck.")

L("p8", "Join the community",
  ["Find your local OWASP chapter",
   "Join r/netsec, r/cybersecurity and one Discord (The Many Hats Club / InfoSec Prep)",
   "Join or form a CTF team"],
  [("OWASP Chapters", "https://owasp.org/chapters/"), ("r/netsec", "https://www.reddit.com/r/netsec/"),
   ("The Many Hats Club", "https://discord.com/invite/tmhc")],
  ["Discord"],
  "Introduce yourself in one community and ask one good question about something you're stuck on.")

L("p8", "Learn from real bug reports",
  ["Read 3 disclosed reports on HackerOne Hacktivity"],
  [("HackerOne Hacktivity", "https://hackerone.com/hacktivity")],
  [],
  "Summarize one report: bug class, impact, how it was found, how it was fixed.")

# ---------------------------------------------------------------- Phase 10
L("p10", "Project: password strength checker v2",
  ["Upgrade pwcheck.py: entropy estimate, HaveIBeenPwned k-anonymity check, unit tests",
   "README: problem, approach, what you learned"],
  [("HIBP Pwned Passwords API", "https://haveibeenpwned.com/API/v3#PwnedPasswords"),
   ("Awesome README", "https://github.com/matiassingers/awesome-readme")],
  ["Python", "pytest"],
  "Ship it on GitHub with tests and a screenshot in the README.")

L("p10", "Project: file integrity monitor (part 1)",
  ["Hash every file in a folder (sha256) and store a baseline JSON",
   "Re-scan and report added / removed / modified files"],
  [("hashlib docs", "https://docs.python.org/3/library/hashlib.html")],
  ["Python"],
  "Modify a file and show your FIM detects it.")

L("p10", "Project: file integrity monitor (part 2)",
  ["Schedule the FIM with cron",
   "Send alerts to Telegram - reuse code from this very bot!"],
  [("Telegram Bot API", "https://core.telegram.org/bots/api")],
  ["cron", "Telegram"],
  "Get a Telegram alert on your phone when a watched file changes.")

L("p10", "Project: log analyzer",
  ["Detect SSH brute force in auth.log: N failures from one IP within M minutes",
   "Output a Markdown report"],
  [],
  ["Python", "regex"],
  "Run it on your VM's logs after simulating a brute force with hydra against yourself.")

L("p10", "Project: packet analyzer with Scapy",
  ["Learn Scapy basics: sniff, layers, summary",
   "Count packets per protocol and top talkers - only on your own network"],
  [("Scapy docs", "https://scapy.readthedocs.io")],
  ["Scapy", "Wireshark"],
  "Print the top 5 destination IPs from 1 minute of your own traffic.")

L("p10", "Project: encryption tool",
  ["Use the `cryptography` library: Fernet / AES-GCM with a password-derived key (scrypt)"],
  [("cryptography docs", "https://cryptography.io")],
  ["Python"],
  "Encrypt and decrypt a file; explain in README why you used a KDF and a nonce.")

L("p10", "SOC home lab: plan & SIEM intro",
  ["TryHackMe: 'Intro to SIEM'",
   "Choose a free SIEM: Wazuh or Splunk Free",
   "Plan: 1 SIEM VM + 1 Ubuntu victim + 1 attacker VM"],
  [thm("introtosiem", "Intro to SIEM"), ("Wazuh", "https://wazuh.com")],
  ["Wazuh / Splunk"],
  "Draw your lab diagram with IPs and what each VM does.")

L("p10", "SOC home lab: build",
  ["Install the SIEM and an agent on your Ubuntu VM"],
  [("Wazuh docs", "https://documentation.wazuh.com")],
  ["Wazuh / Splunk"],
  "See your Ubuntu VM's logs arriving in the SIEM dashboard.")

L("p10", "SOC home lab: detect an attack",
  ["From the attacker VM, brute-force SSH on the victim (your own lab)",
   "Find the alert in the SIEM and write a mini incident report"],
  [],
  ["hydra", "Wazuh / Splunk"],
  "Write a 1-page incident report: timeline, indicators, response.")

L("p10", "Project: honeypot",
  ["Deploy Cowrie SSH honeypot in an isolated VM"],
  [("Cowrie", "https://github.com/cowrie/cowrie")],
  ["Cowrie", "Docker"],
  "Log in to your honeypot yourself and find your commands in its logs.")

L("p10", "Portfolio polish",
  ["Create a GitHub profile README",
   "Pin your best 6 repos; make sure each has a clear README"],
  [("Awesome README", "https://github.com/matiassingers/awesome-readme")],
  ["GitHub"],
  "Ask a friend to read your profile for 2 minutes - can they tell what you can do?")

# ---------------------------------------------------------------- Phase 11
L("p11", "Certification landscape",
  ["Read Phase 11 of the roadmap: learn -> practice -> validate",
   "Explore Paul Jerimy's certification roadmap"],
  [ROADMAP_LINK, ("Paul Jerimy's Certification Roadmap", "https://pauljerimy.com/security-certification-roadmap/")],
  [],
  "Pick the ONE cert that fits your goals best (ISC2 CC, Security+, eJPT, BTL1...) and write why.")

L("p11", "Cert study plan",
  ["Break your chosen cert's exam objectives into weekly blocks",
   "Book a realistic exam date"],
  [("ISC2 CC", "https://www.isc2.org/certifications/cc"), ("CompTIA Security+", "https://www.comptia.org/certifications/security"),
   ("eJPT", "https://ine.com/learning/certifications/junior-penetration-tester")],
  [],
  "Commit your study plan to cybersec-notes.")

# ---------------------------------------------------------------- Phase 12
L("p12", "Blue team 1: SOC analyst taste",
  ["Create a LetsDefend free account and do an intro alert",
   "TryHackMe: 'Pyramid of Pain'"],
  [("LetsDefend", "https://letsdefend.io"), thm("pyramidofpainax", "Pyramid of Pain")],
  ["SIEM"],
  "Triage one alert end to end: true or false positive? Why?")

L("p12", "Blue team 2: Windows logging",
  ["TryHackMe: 'Windows Logging for SOC'",
   "Learn Sysmon basics"],
  [thm("windowsloggingforsoc", "Windows Logging for SOC")],
  ["Event Viewer", "Sysmon"],
  "List 5 Windows Event IDs every SOC analyst should know and what they mean.")

L("p12", "DFIR 1: intro",
  ["TryHackMe: 'Intro to Digital Forensics' and 'Intro to DFIR'"],
  [thm("introdigitalforensics", "Intro to Digital Forensics"),
   thm("introductoryroomdfirmodule", "Intro to DFIR")],
  [],
  "Explain chain of custody and order of volatility.")

L("p12", "DFIR 2: Autopsy",
  ["TryHackMe: 'Autopsy'"],
  [thm("autopsy2ze0", "Autopsy")],
  ["Autopsy"],
  "Finish the room.")

L("p12", "DFIR 3: memory forensics",
  ["TryHackMe: 'Memory Forensics'"],
  [thm("memoryforensics", "Memory Forensics"), ("Volatility 3", "https://github.com/volatilityfoundation/volatility3")],
  ["Volatility"],
  "Finish the room and list the Volatility plugins you used.")

L("p12", "Malware analysis 1",
  ["TryHackMe: 'History of Malware' and 'Malware Classification'",
   "Look at a public Any.Run report (do NOT download samples on your host)"],
  [thm("historyofmalware", "History of Malware"), thm("malwareclassification", "Malware Classification"),
   ("Any.Run", "https://any.run")],
  ["Any.Run"],
  "From one public Any.Run report, list 3 IOCs (hash, domain, IP).")

L("p12", "Malware analysis 2",
  ["TryHackMe: 'MalMal: Introductory'"],
  [thm("malmalintroductory", "MalMal: Introductory")],
  ["PEStudio", "strings"],
  "Finish the room.")

L("p12", "Reverse engineering track",
  ["TryHackMe: 'x86-64 Architecture'",
   "Start Malware Unicorn RE101"],
  [thm("x8664arch", "x86-64 Architecture"), ("Malware Unicorn workshops", "https://malwareunicorn.org/#/workshops")],
  ["Ghidra", "x64dbg"],
  "Explain registers RIP, RSP, RBP and what `call` / `ret` do.")

L("p12", "Active Directory 1",
  ["TryHackMe: 'Introduction to Active Directory Authentication' and 'AD Basics: Enumeration'"],
  [thm("introtoactivedirectoryauthentication", "Intro to AD Authentication"),
   thm("adbasicenumeration", "AD Basics: Enumeration")],
  ["BloodHound", "PowerView"],
  "Explain Kerberos TGT vs TGS in your own words.")

L("p12", "Active Directory 2",
  ["TryHackMe: 'Attacktive Directory'"],
  [thm("attacktivedirectory", "Attacktive Directory")],
  ["impacket", "kerbrute"],
  "Finish the room.")

L("p12", "Cloud security",
  ["AWS Skill Builder: Cloud Practitioner Essentials (start)",
   "Play flaws.cloud - a free AWS misconfiguration CTF"],
  [("AWS Skill Builder", "https://skillbuilder.aws"), ("flaws.cloud", "http://flaws.cloud")],
  ["AWS CLI"],
  "Solve flaws.cloud levels 1-3.")

L("p12", "Threat intelligence & MITRE ATT&CK",
  ["TryHackMe: 'Intro to Cyber Threat Intel'",
   "Explore MITRE ATT&CK"],
  [thm("cyberthreatintel", "Intro to Cyber Threat Intel"), ("MITRE ATT&CK", "https://attack.mitre.org")],
  ["ATT&CK Navigator"],
  "Pick one threat group on ATT&CK and list 5 of its techniques.")

L("p12", "GRC: risk assessment",
  ["Re-read NIST CSF 2.0",
   "Learn risk = likelihood x impact; risk register"],
  [("NIST CSF", "https://www.nist.gov/cyberframework")],
  ["Spreadsheet"],
  "Write a mock risk register (5 risks) for a small college club website.")

L("p12", "Choose your specialization",
  ["Re-read Phase 12 of the roadmap",
   "Score every domain you tried: enjoyment / skill / job market (1-5)"],
  [ROADMAP_LINK],
  [],
  "Pick your top specialization and write a 3-month plan for it.")

# ---------------------------------------------------------------- Phase 13
L("p13", "LinkedIn & resume",
  ["Write a security-focused resume: projects, CTFs, write-ups first",
   "Update LinkedIn headline + featured section"],
  [("LinkedIn Learning", "https://www.linkedin.com/learning/")],
  [],
  "Get feedback on your resume from one senior in your community.")

L("p13", "Write a blog post",
  ["Write about something you learned (not just a CTF write-up)",
   "Publish on GitHub Pages / Medium / Hashnode"],
  [],
  ["Markdown"],
  "Publish and share it in one community.")

L("p13", "Open-source contribution",
  ["Find a 'good first issue' in an OWASP project",
   "Even docs fixes count"],
  [("OWASP Projects", "https://owasp.org/projects/"), ("OWASP on GitHub", "https://github.com/OWASP")],
  ["git", "GitHub"],
  "Open your first pull request to a security project.")

L("p13", "Bug bounty readiness",
  ["Bugcrowd University basics",
   "Read 2 program policies: scope, out-of-scope, safe harbor",
   "Only start hunting once your AppSec basics are solid"],
  [("Bugcrowd University", "https://www.bugcrowd.com/hackers/bugcrowd-university/"),
   ("HackerOne Hacktivity", "https://hackerone.com/hacktivity")],
  ["Burp Suite"],
  "Summarize what is in and out of scope for one program.")

L("p13", "Graduation: internships & your next 90 days",
  ["List 10 internships / roles to apply to",
   "Write your 90-day plan for your chosen specialization",
   "Celebrate - you finished the roadmap!"],
  [ROADMAP_LINK, ("levels.fyi", "https://www.levels.fyi")],
  [],
  "Apply to your first 3 internships today.")


def review_day(week_lessons, week_no):
    titles = [l["title"] for l in week_lessons]
    return {
        "phase": week_lessons[-1]["phase"],
        "title": f"Week {week_no} review & write-up day",
        "review": True,
        "tasks": ["Re-read your notes for this week: " + "; ".join(titles),
                  "Redo the hardest exercise of the week without looking at your notes",
                  "Write a 'What I learned / What confused me' note and push it to cybersec-notes",
                  "Solve 2 bonus challenges (/challenge in the bot or on the dashboard)"],
        "links": [{"name": "The roadmap", "url": ROADMAP}],
        "tools": ["GitHub", "your notes"],
        "challenge": f"Teach-back: explain '{titles[0]}' out loud in 2 minutes as if to a friend.",
    }


def build():
    days, week = [], []
    for lesson in LESSONS:
        week.append(lesson)
        days.append(lesson)
        if len(week) == 6:
            days.append(review_day(week, len([d for d in days if d.get("review")]) + 1))
            week = []
    if week:
        days.append(review_day(week, len([d for d in days if d.get("review")]) + 1))
    for i, d in enumerate(days, 1):
        d["day"] = i
        d["phase_name"] = PHASES[d["phase"]]
        d.setdefault("review", False)
    return {"source": ROADMAP, "phases": PHASES, "days": days}


if __name__ == "__main__":
    data = build()
    out = Path(__file__).with_name("curriculum.json")
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(f"Wrote {len(data['days'])} days to {out}")

    md = ["# Day-by-day cybersecurity plan", "",
          f"Generated from [`build_curriculum.py`](build_curriculum.py), based on the [OWASP roadmap]({ROADMAP}).",
          f"{len(data['days'])} days at ~1.5-2 h/day. Every 7th day is a review day.", ""]
    phase = None
    for d in data["days"]:
        if d["phase"] != phase:
            phase = d["phase"]
            md += [f"## {PHASES[phase]}", ""]
        links = ", ".join(f"[{l['name']}]({l['url']})" for l in d["links"])
        md.append(f"- **Day {d['day']} - {d['title']}**" + (f"  \n  {links}" if links else ""))
    md_out = Path(__file__).with_name("PLAN.md")
    md_out.write_text("\n".join(md) + "\n")
    print(f"Wrote {md_out}")
