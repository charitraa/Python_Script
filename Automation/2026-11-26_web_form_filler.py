"""
This script demonstrates how to automate filling out a web form using Selenium WebDriver.

It navigates to a specified URL, locates form fields by their IDs (or other selectors),
fills them with provided data, and then submits the form.
This is useful for repetitive tasks like testing forms, automating data entry,
or performing simple automated submissions on web pages.

Requires the 'selenium' and 'webdriver-manager' packages:
pip install selenium webdriver-manager

Also requires a web browser (e.g., Google Chrome) to be installed on your system.
The 'webdriver-manager' package will automatically download the correct browser driver
(e.g., ChromeDriver for Chrome) for you, making setup easier.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

def fill_web_form(url, form_data, submit_button_selector, driver_path=None):
    """
    Automates the process of filling and submitting a web form.

    Args:
        url (str): The URL of the web page containing the form.
        form_data (dict): A dictionary where keys are field identifiers (e.g., 'id' or 'name' attributes)
                          and values are the data to input into those fields.
                          For 'select' elements (dropdowns), the value should be the exact visible text
                          of the option to select.
        submit_button_selector (tuple): A tuple (By strategy, selector string) to locate the submit button.
                                        Example: (By.CSS_SELECTOR, "button[type='submit']")
                                        or (By.ID, "submit-btn")
        driver_path (str, optional): Path to the WebDriver executable (e.g., path to chromedriver.exe).
                                     If None, `webdriver_manager` will attempt to automatically download
                                     and manage the driver (recommended for simplicity).
    """
    driver = None
    try:
        # Initialize WebDriver
        # If a specific driver_path is provided, use it.
        # Otherwise, use webdriver_manager to automatically handle the driver.
        if driver_path:
            service = ChromeService(executable_path=driver_path)
            driver = webdriver.Chrome(service=service)
            print(f"WebDriver initialized using custom path: {driver_path}")
        else:
            # This line automatically downloads and manages ChromeDriver.
            # It requires the 'webdriver-manager' package.
            print("Attempting to auto-manage ChromeDriver with webdriver_manager...")
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            print("ChromeDriver successfully initialized.")

        print(f"Navigating to {url}")
        driver.get(url)

        # Give the page some time to load completely
        time.sleep(2)

        print("Filling form fields...")
        for field_id, value in form_data.items():
            try:
                # Find the element primarily by ID. You can extend this to By.NAME, By.CLASS_NAME, etc.
                element = driver.find_element(By.ID, field_id)
                
                # Special handling for 'select' dropdown elements
                if element.tag_name == 'select':
                    select_element = Select(element)
                    select_element.select_by_visible_text(str(value))
                    print(f"  Selected '{value}' in dropdown '{field_id}'")
                else:
                    # For input fields, clear existing text and send new keys
                    element.clear() 
                    element.send_keys(str(value))
                    print(f"  Entered '{value}' into field '{field_id}'")
            except Exception as e:
                print(f"  Warning: Could not find or interact with field '{field_id}'. Error: {e}")
                # You might want to log this or stop the script if a field is critical.

        # Give a brief moment to observe the filled fields before submitting
        time.sleep(1)

        # Locate and click the submit button
        print(f"Locating submit button using strategy '{submit_button_selector[0].name}' with selector '{submit_button_selector[1]}'")
        submit_button = driver.find_element(submit_button_selector[0], submit_button_selector[1])
        submit_button.click()
        print("Submit button clicked.")

        # Wait for the page to process the submission or navigate to a new page
        time.sleep(3) # Adjust this duration based on the form's response time

        print("Form submission process completed.")
        print(f"Current page title after submission: {driver.title}")
        print(f"Current URL after submission: {driver.current_url}")

    except Exception as e:
        print(f"\nAn error occurred during form filling: {e}")
        # Provide user-friendly instructions if WebDriver executable is not found
        if "Message: 'chromedriver' executable needs to be in PATH" in str(e) or \
           "WebDriverException: Message: 'geckodriver' executable needs to be in PATH" in str(e) or \
           "executable_path' must be a string" in str(e):
            print("\n------------------------------------------------------------")
            print("ERROR: WebDriver executable not found or not correctly configured.")
            print("Please ensure you have a browser driver (e.g., ChromeDriver) installed.")
            print("  - If using 'webdriver-manager' (default), ensure 'webdriver-manager' is installed (`pip install webdriver-manager`).")
            print("    It should automatically download the driver.")
            print("  - If managing manually, download the correct WebDriver for your browser version")
            print("    (e.g., ChromeDriver from https://chromedriver.chromium.org/downloads)")
            print("    and either place it in your system's PATH, or provide its full path")
            print("    via the `driver_path` argument when calling `fill_web_form`.")
            print("------------------------------------------------------------")
    finally:
        if driver:
            print("Closing browser.")
            driver.quit() # Always ensure the browser is closed when done.

if __name__ == "__main__":
    print("--- Web Form Filler Example ---")

    # This example uses a publicly available test form from Formy Project.
    # It's a stable resource designed for practicing Selenium automation.
    test_form_url = "https://formy-project.herokuapp.com/form"

    # Define the data to fill into the form fields.
    # Keys are the 'id' attributes of the input fields on the target page.
    # For 'select' dropdowns, the value must be the exact visible text of the option.
    form_data_to_fill = {
        "first-name": "Alice",
        "last-name": "Smith",
        "job-title": "Data Scientist",
        "select-menu": "2-4",  # Example: Selecting "2-4" years of experience from the dropdown
        "datepicker": "05/15/2025" # Example date
    }

    # Define how to locate the submit button.
    # On the Formy test page, the "Submit" element is an <a> tag styled as a button
    # with specific classes. By.CSS_SELECTOR is a robust way to find it.
    submit_button_selector_tuple = (By.CSS_SELECTOR, "a.btn.btn-lg.btn-primary")

    # --- How to run this example ---
    # The script is configured to use 'webdriver_manager' by default, which simplifies setup.
    # 1. Ensure you have Python installed.
    # 2. Install the necessary packages:
    #    pip install selenium webdriver-manager
    # 3. Run this Python script.
    #    A Chrome browser window should open, navigate to the form, fill it, and submit.
    # -----------------------------------

    # To use automatic driver management (recommended for simplicity, `driver_path` is None):
    fill_web_form(test_form_url, form_data_to_fill, submit_button_selector_tuple)

    # --- Advanced (Manual WebDriver Path) ---
    # If you prefer to manually specify the path to your ChromeDriver executable:
    # 1. Download ChromeDriver (or equivalent for your browser) matching your browser's version
    #    from its official site (e.g., https://chromedriver.chromium.org/downloads).
    # 2. Replace the placeholder path below with the actual path to your downloaded driver.
    #    Example: my_driver_path = "C:/Users/YourUser/Downloads/chromedriver.exe" # Windows
    #    Example: my_driver_path = "/usr/local/bin/chromedriver" # macOS/Linux (if in PATH)
    #    Example: my_driver_path = "/Users/YourUser/Documents/chromedriver" # macOS/Linux (custom location)
    #
    # Uncomment the following lines and modify `my_driver_path` if you want to use a manual path:
    # my_driver_path = "/path/to/your/chromedriver" # <--- REPLACE THIS WITH YOUR ACTUAL DRIVER PATH!
    # # fill_web_form(test_form_url, form_data_to_fill, submit_button_selector_tuple, driver_path=my_driver_path)

    print("\n--- Example Finished ---")
