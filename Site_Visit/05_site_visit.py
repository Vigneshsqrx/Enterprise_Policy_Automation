import os
import time
from dotenv import load_dotenv
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime

#########################################################################################
# Load environment variables from the .env file
env_path = Path("../config_data.env")
load_dotenv(dotenv_path=env_path)

# Get environment variables
admin_username = os.getenv("ADMIN_USERNAME")
admin_password = os.getenv("ADMIN_PASSWORD")
tenant_name = os.getenv("TENANT_NAME")
tenant_url = os.getenv("TENANT_URL")

assigned_username = os.getenv("ASSIGNED_USERNAME")
assigned_password = os.getenv("ASSIGNED_PASSWORD")

extension_path = os.getenv("EXTENSION_PATH")
policy_type = os.getenv("POLICY_TYPE")
browser = os.getenv("BROWSER", "chrome").lower()
#########################################################################################
tag = "Site Visit"
ai_prompt = "Block site visits to page hostname google.com, facebook.com, amazon.com, microsoft.com"
policy = "page.url.hostname"
##############################################################################
def print_details():
    current_file = os.path.basename(__file__)
    capabilities = driver.capabilities
    browser_name = capabilities['browserName']
    browser_version = capabilities['browserVersion'] if 'browserVersion' in capabilities else capabilities['version']
    platform_name = capabilities['platformName'] if 'platformName' in capabilities else capabilities['platform']
    now = datetime.now()

    # Format the date and time to include AM/PM
    formatted_date = now.strftime("%d-%m-%Y")
    formatted_time = now.strftime("%I:%M:%S %p")

    # Print details
    print("--------------------------------------------------------------------------------------------------")
    print("Script Execution Date :", formatted_date)
    print("Script Execution Time :", formatted_time)

    print(f"Current file name: {current_file}")
    print(f"Browser name: {browser_name}")
    print(f"Browser version: {browser_version}")
    print(f"Platform name: {platform_name}")
    # Extract the directory containing the extension name
    extension_dir = os.path.dirname(extension_path)

    # Extract the extension name by splitting based on the last backslash
    extension_name = os.path.basename(extension_dir)

    # # Print the extension name
    print("Extension Used:", extension_name)
    print("--------------------------------------------------------------------------------------------------")
##############################################################################
driver = None

if browser == "chrome":
    chrome_driver = ChromeDriverManager().install()  # Get the ChromeDriver executable
    options = Options()
    options.add_argument(f"--load-extension={extension_path}")  # Load Chrome extension
    driver = webdriver.Chrome(service=ChromeService(chrome_driver), options=options)
elif browser == "edge":
    edge_driver = EdgeChromiumDriverManager().install()  # Get the EdgeDriver executable
    options = webdriver.EdgeOptions()
    options.add_argument(f"--load-extension={extension_path}")  # Load Edge extension
    driver = webdriver.Edge(service=EdgeService(edge_driver), options=options)
else:
    print(f"Unsupported browser: {browser}. Please choose chrome or edge")
    exit(1)

#########################################################################################
def login_function():

    driver.maximize_window()
    driver.get(tenant_url)

    email_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Email address']"))
    )
    email_field.send_keys(admin_username)

    continue_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//button[@id='login-email-btn']"))
    )
    continue_button.click()

    password_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
    )
    password_field.send_keys(admin_password)

    continue_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//button[@id='login-email-btn']"))
    )
    continue_button.click()

    print("Logged In")
    print("Current URL ::", tenant_url)
    print("Admin Email ::", admin_username)

    header_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//h1[normalize-space()='Detections']"))
    )

    policy_list_page_url = "/enterprise/#/policy"
    policy_page = tenant_url + policy_list_page_url

    driver.get(policy_page)

    header_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//div[@class='text-lg font-semibold text-primary']"))
    )

    print("Navigated to Policy List Page")


##############################################################################
def check_for_existing_policies():

    tbody = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,
                                        '#root > div > div.flex.flex-1.flex-col.overflow-auto.bg-background > main > div.mt-2.max-h-96.overflow-auto.rounded-md.border.bg-card > table > tbody'))
    )

    # Scroll the tbody to ensure all rows are loaded (for virtualized tables)
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", tbody)

    time.sleep(2)

    # JavaScript code to find the number of rows in the tbody
    js_code = """
        const tbody = document.querySelector('#root > div > div.flex.flex-1.flex-col.overflow-auto.bg-background > main > div.mt-2.max-h-96.overflow-auto.rounded-md.border.bg-card > table > tbody');
        return tbody ? tbody.querySelectorAll('tr').length : -1;  // -1 if tbody not found
    """

    # Execute JavaScript in the context of the current page
    row_count = driver.execute_script(js_code)

    # Check the result in Python and print output accordingly
    if row_count == -1:
        print("No existing policies.")

    else:
        print(f"Number of Existing Policies: {row_count}")
        wait = WebDriverWait(driver, 10)   # # Proceed to delete the existing policy
        top_check_box = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[@id='root']/div/div[2]/main/div[5]/table/thead/tr/th[1]/button"))
        )
        top_check_box.click()

        three_dot_button = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[@id='root']/div/div[2]/main/div[4]/div/button"))
        )
        three_dot_button.click()

        delete_button = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Delete')]"))
        )
        delete_button.click()

        confirm_button = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Confirm')]"))
        )
        confirm_button.click()

        print(f"{row_count} existing polices deleted.")

##############################################################################
def site_visit_policies_creation():
    site_visit = "/enterprise/#/site.visit/policy"

    site_visit_page = tenant_url + site_visit

    driver.get(site_visit_page)

    new = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR,
                                          "#root > div > div.flex.flex-1.flex-col.overflow-auto.bg-background > main > button"))
    )
    new.click()

    if policy_type == "LUA":
        policy_selection = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                              "button[class='flex h-9 items-center justify-between whitespace-nowrap rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1 right-5 top-5 w-32']"))
        )
        policy_selection.click()

        lua_option = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//span[text()='LUA script']"))
        )
        lua_option.click()

        print("-------------------")
        print("LUA Method Selected")
        print("-------------------")

    else:
        print("---------------------")
        print("Ruler Method Selected")
        print("---------------------")

    ask_ai_to_generate_policy = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div[1]/div/div[2]/main/div[2]/div/div/div[1]/h3/button"))
    )
    ask_ai_to_generate_policy.click()


    prompt_text_area = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div[1]/div/div[2]/main/div[2]/div/div/div[2]/div/div/textarea"))
    )
    prompt_text_area.clear()

    prompt_text_area.send_keys(ai_prompt)


    generate_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div[1]/div/div[2]/main/div[2]/div/div/div[2]/div/div/div/button"))
    )
    generate_button.click()

    # Define the WebDriverWait with a timeout
    wait = WebDriverWait(driver, 90)  # Wait for up to 90 seconds

    # Wait until the button element is located
    prompt_feedback = wait.until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/main/div[3]/div/div/h3/button')))
    print("policy generated")

    select_member = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div[1]/div/div[2]/main/div[4]/div[2]/div/div[8]/div/button/div"))
    )

    # Scroll to the element using JavaScript
    driver.execute_script("arguments[0].scrollIntoView();", select_member)
    select_member.click()

    time.sleep(2)

    assign_member = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="search"]'))
    )

    # Click the search input
    assign_member.click()

    # Enter text into the search input
    assign_member.send_keys(assigned_username)

    time.sleep(2)

    check_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[role="checkbox"]'))
    )

    # Click the button
    check_box.click()

    save_button = driver.find_element(By.XPATH, "//button[normalize-space()='Save']")
    save_button.click()

    print("AI PROMPT::", ai_prompt)
    print(tag, "New Policy Created")
    print("   ")
    print("Policy::",policy)

    policy_list_page_url = "/enterprise/#/policy"
    policy_page = tenant_url + policy_list_page_url

    driver.get(policy_page)
##############################################################################
def assigned_user_login():
    driver.delete_all_cookies()
    driver.get(tenant_url)

    email_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Email address']"))
    )
    email_field.send_keys(assigned_username)

    continue_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//button[@id='login-email-btn']"))
    )
    continue_button.click()

    password_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
    )
    password_field.send_keys(assigned_password)

    continue_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//button[@id='login-email-btn']"))
    )
    continue_button.click()

    print("                           ")
    print("Logged In As Assigned User")
    print("Current URL ::", tenant_url)
    print("Assigned User Email ::", assigned_username)
#####################################################################################################################
def check_block_status():
    try:
        main_title = driver.find_element(By.CSS_SELECTOR, "#main-title").text
        main_title == 'Content Blocked'
        blocked_url = driver.find_element(By.CSS_SELECTOR, "#url").text
        print("  ")
        print(blocked_url, " ", f"Website blocked by Square-X: {driver.current_url}")


    except NoSuchElementException:
        print("  ")
        print("********************************************")
        print(f"Website not blocked: {driver.current_url}")
        print("********************************************")

def open_sites():
    websites = [
        # Google domains and subdomains
        'https://www.google.com/',
        'https://www.facebook.com/',
        'https://www.amazon.com/',
        'https://www.microsoft.com/',

        'https://play.google.com/',
        'https://developers.facebook.com/',
        'https://advertising.amazon.com/',
        'https://account.microsoft.com/account'
    ]


    time.sleep(3)

    # Loop through the remaining websites, open each in a new tab, and check for block status
    for website in websites[0:]:
        # Open a new tab for the website

        driver.execute_script("window.open('about:blank', '_blank');")

        # Switch to the newly opened tab (latest tab)
        driver.switch_to.window(driver.window_handles[-1])

        driver.get(website)

        time.sleep(3)  # Wait for the website to load

        # Check if the website is blocked or not
        check_block_status()

        # Close the current tab after checking
        driver.close()

        # Switch back to the first tab (to maintain clean navigation)
        driver.switch_to.window(driver.window_handles[0])

        time.sleep(2)

#########################################################################################
print_details()

login_function()
check_for_existing_policies()
site_visit_policies_creation()

assigned_user_login()
open_sites()


#########################################################################################
if driver:
    driver.quit()
    print("Browser closed.")


#########################################################################################