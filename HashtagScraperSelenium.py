from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
import random
import pandas as pd
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)  # Keep the browser open
chrome_options.add_argument("--start-maximized")  # Start browser maximized
chrome_options.add_argument("--disable-extensions")  # Disable extensions for cleaner testing environment
# chrome_options.add_argument("--headless")  # Run in headless mode
# chrome_options.add_argument("--disable-gpu")  # Disable GPU usage
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

# Initialize the webdriver and server
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Initialize the wait
wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements to be available

# Apply the stealth
stealth(driver, languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True)

# User agents
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0'
]

# Randomly select a user agent
user_agent = random.choice(user_agents)

# Set the user agent
chrome_options.add_argument(f"user-agent={user_agent}")

# Open the website
url = 'https://www.linkedin.com/feed/hashtag/?keywords=collisionconf'
driver.get(url)

# Wait for the page to load completely
wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
loginBar = driver.find_element(By.XPATH, '//*[@id="username"]')
loginBar.send_keys("//enter your username")
passwordBar = driver.find_element(By.XPATH, '//*[@id="password"]')
passwordBar.send_keys("//enter your password")
passwordBar.send_keys(Keys.ENTER)

time.sleep(random.randint(1, 3))  # Random wait time

# Initialize the array
profiles = []
urls = []

profiles_number = 10
while len(profiles) < profiles_number:
    postings = driver.find_elements(By.XPATH, "//a[@class='app-aware-link  update-components-actor__meta-link']")

    if not postings:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        continue

    for posting in postings:
        if len(profiles) >= profiles_number:
            break
        try:
            name_element = posting.find_element(By.XPATH, ".//span[@dir='ltr']//span[@aria-hidden]")
            name = name_element.text
            url = posting.get_attribute("href")
            if name not in profiles:  # Avoid duplicate profiles
                profiles.append(name)
                urls.append(url)
        except Exception as e:
            print("Error: ", e)
            continue

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(random.randint(1, 3))  # Random wait time for scrolling

# Create a dataframe
df = pd.DataFrame(list(zip(profiles, urls)), columns=['Profile', 'URL'])
df.to_csv('collisionProfiles.csv', index=False)
