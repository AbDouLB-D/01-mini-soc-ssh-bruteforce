import re
from collections import defaultdict
import subprocess

file_log = "/var/log/auth.log"

# Regex IP
ip_pattern = r"\d+\.\d+\.\d+\.\d+"

# Dictionnaire des tentatives par IP
ip_counts = defaultdict(int)

def block_ip(ip):
    subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
    print(f"[BLOCKED]: {ip}")

def parse_log(file_log):
    with open(file_log, "r") as f:
        for line in f:
            if "Failed password" in line:
                match = re.search(ip_pattern, line)
                if match:
                    ip = match.group()
                    ip_counts[ip] += 1

    print("---------------------tentative de brute force-------------------------")
    #alert 
    for ip, count in ip_counts.items():
        if count >= 5:
            print(f"[ALERT]: {ip} -> {count} tentatives")
            block_ip(ip)


parse_log(file_log)