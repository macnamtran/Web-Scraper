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
import schedule

def linkedinTest():
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)  # Keep the browser open
        chrome_options.add_argument("--start-maximized")  # Start browser maximized
        chrome_options.add_argument("--disable-extensions")  # Disable extensions for cleaner testing environment
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU usage
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
        user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0']

        # Randomly select a user agent
        user_agent = random.choice(user_agents)

        # Set the user agent
        chrome_options.add_argument(f"user-agent={user_agent}")

        # Open the website
        url = 'https://www.linkedin.com/jobs/search/?currentJobId=3852362311&keywords=eng&origin=JOBS_HOME_SEARCH_BUTTON&refresh=true'
        driver.get(url)

        #random wait time
        time.sleep(random.randint(1, 3))

        searchBar = driver.find_element(By.XPATH, '//*[@id="job-search-bar-keywords"]')
        searchBar.click()
        searchBar.clear()
        time.sleep(random.randint(1, 3))
        searchBar.send_keys('Software Engineer')
        searchBar.send_keys(Keys.ENTER)


        #wait for the page to load
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/section[2]/ul/li')))

        #initialize the list of data
        titles = []
        companies = []
        locations = []
        links = []

        job_num = 100 # Number of jobs to scrape
        while len(titles) < job_num:
                job_listings = driver.find_elements(By.XPATH, '//*[@id="main-content"]/section[2]/ul/li')

                if not job_listings:
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        continue

                #Extract and store the data
                for job in job_listings:
                        if len(titles) >= job_num:
                                break
                        try:
                                job_title_element = job.find_element(By.CLASS_NAME, 'sr-only')
                                job_title = job_title_element.text
                                titles.append(job_title)

                                company_element = job.find_element(By.CLASS_NAME, 'hidden-nested-link')
                                company = company_element.text
                                companies.append(company)

                                location_element = job.find_element(By.CLASS_NAME, 'job-search-card__location')
                                location = location_element.text
                                locations.append(location)

                                link_element = job.find_element(By.CLASS_NAME, 'base-card__full-link')
                                link = link_element.get_attribute('href')
                                links.append(link)

                                time.sleep(random.randint(20, 40)) # Sleep for a random amount of wait time
                        except Exception as e:
                                print("Error: ", e)
                                continue

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Save the data to a CSV file
        pd.DataFrame({'Title': titles,
                      'Company': companies,
                      'Location': locations,
                      'Link': links}).to_csv('linkedin_jobs.csv', index=False)

        driver.quit()

# Schedule the function to run every day at 7AM
schedule.every().day.at("07:00").do(linkedinTest)

# Run the scheduler
while True:
        schedule.run_pending()
        time.sleep(1)