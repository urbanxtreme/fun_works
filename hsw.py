from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import socket
import os
import pyperclip
import subprocess
import sys
import time
import signal

# --------------------------- USER CONFIG ---------------------------
EMAIL = "skrhari2020@gmail.com"
PASSWORD = "Technology*19112005"
LOGIN_URL = "https://tracking.hard-softwerk.com"
INTERACTIVE_MODE = False
IMAGE_TO_UPLOAD = "latex.jpg"
# --------------------------- SELECTORS ---------------------------
EMAIL_SELECTOR = 'input[placeholder="Username/Email"]'
PASSWORD_SELECTOR = 'input[type="password"]'
LOGIN_BUTTON_SELECTOR = 'button:has-text("Login")'

ADD_ORG_BUTTON = '.ls-add-org-btn'
ORG_INPUT_SELECTOR = 'input.ls-dark-input[placeholder="Enter organization name"]'
TICK_BUTTON_SELECTOR = 'button.ls-save-btn[title="Save"]'

ADD_LOCALE_BUTTON_SELECTOR = '.ls-add-locale-btn'
LOCALE_NAME_INPUT_SELECTOR = 'input.ls-dark-input[placeholder="Enter locale name"]'
LOCALE_SAVE_BUTTON_SELECTOR = 'button.ls-save-btn[title="Save"]'

ADD_FLOOR_BUTTON_SELECTOR = '.ls-add-floor-btn'
FLOOR_BUTTON_ONE_MORE_SELECTOR = '.ls-floor-btn'
FLOOR_NAME_INPUT_SELECTOR = 'input.ls-dark-input[placeholder="Enter floor number"]'
FLOOR_SAVE_BUTTON_SELECTOR = 'button.ls-save-btn[title="Save"]'
FLOOR_SELECTED = 'div.ls-floor-item'

SEARCH_INPUT_FILL = 'input[placeholder*="Search for locations"]'
DROPDOWN_SELECTOR = 'div[style*="position: absolute"][style*="z-index: 1000"]'

MAP_UI_BUTTON_SELECTOR = 'div.twa-sidebar-item[title="Map UI"]'
DROPDOWN_TOGGLE_SELECTOR = 'ion-item:has-text("Image Options")'
BUTTON_LIST_SELECTOR = 'button.full-width-button'

SCALE_PLUS_BUTTON_SELECTOR = 'button.fancyBtn.IncreaseButton'

IMAGE_SAVER = 'button.full-width-button'

NEW_DROPDOWN_SELECTOR = 'ion-item:has-text("Zone Options")'
CREATE_ZONE_BUTTON_SELECTOR = 'button.MarkerButton:has-text("Create Zone")'

ANCHOR_DROPDOWN_SELECTOR = 'ion-item:has-text("Anchor Options")'
RSSI_ANCHOR_SELECTOR = 'button#RSSIhub'

ASSET_TRACKING_UI='div.twa-sidebar-item[title="Asset Tracking UI"]'
# ASSET_ZONE_SELECTOR = 'accessory-item:has-text("automated_zone")'
CREATE_ASSET_BUTTON = 'div.accessory-button:has-text("Create Asset +")'
MAC_SELECTOR = 'ion-input[placeholder="Beacon Mac"] >> input'
ASSET_NAME_SELECTOR = 'ion-input[placeholder="Asset Name"] >> input'
SAVE_ASSET_BUTTON = 'div.AssetSaveBt:has-text("Save Asset")'

USER_DROPDOWN_SELECTOR = 'button.user-dropdown-button'
ORG_SETTINGS_BUTTON='button.dropdown-item:has-text("ORG Settings")'
SEARCH_BAR_CLICK='input.form-control[placeholder="Search by name"]'
ORG_SELECTOR='div.org-item:has-text("Automation Org")'

GENERATE_BUTTON_SELECTOR = 'button.btn.btn-sm.org-settings-btn:has-text("Generate")';
CLOSE_BUTTON='button.modal-close-btn'

HEAT_MAP_UI_BUTTON_SELECTOR = 'div.twa-sidebar-item[title="Heat Map UI"]'
HEAT_MAP_CREATOR_OPENER = 'ion-item:has-text("Heat Map Creation")'
HEAT_MAP_ASSET_SELECTOR = 'div.beacon-item:has-text("Automation Asset")'
RSSI_HEAT_ANCHOR_SELECTOR = 'div.rssi-item:has-text("Anchor ID: hub55555556")'
# --------------------------- FEATS ---------------------------
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False
def wait_if_interactive(msg=""):
    if INTERACTIVE_MODE:
        input(msg or "Press Enter to continue...")
# --------------------------- FUNCS ---------------------------
def login_to_app():
    if not check_internet():
        print("Internet connection is down. Please check and try again.")
        exit(1)
    print("Launching browser and logging in...")
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(LOGIN_URL)
        page.wait_for_selector(EMAIL_SELECTOR)
        page.fill(EMAIL_SELECTOR, EMAIL)
        page.wait_for_selector(PASSWORD_SELECTOR)
        page.fill(PASSWORD_SELECTOR, PASSWORD)
        page.wait_for_selector(LOGIN_BUTTON_SELECTOR)
        page.click(LOGIN_BUTTON_SELECTOR)
        page.wait_for_timeout(5000)
        print("Login successful!")
        return page, browser, playwright
    except PlaywrightTimeoutError as e:
        print(f"Login failed due to timeout: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error during login: {e}")
        exit(1)
def create_org(page, org_name):
    try:
        print(f"Creating organization '{org_name}'...")
        page.wait_for_selector(ADD_ORG_BUTTON)
        page.click(ADD_ORG_BUTTON)
        page.wait_for_selector(ORG_INPUT_SELECTOR)
        page.fill(ORG_INPUT_SELECTOR, org_name)
        page.wait_for_selector(TICK_BUTTON_SELECTOR)
        page.click(TICK_BUTTON_SELECTOR)
        page.wait_for_timeout(3000)
        print("Organization created.")
    except Exception as e:
        print(f"Error while creating organization: {e}")

def create_locale(page, locale_name):
    try:
        print(f"Creating locale '{locale_name}'...")
        page.wait_for_selector(ADD_LOCALE_BUTTON_SELECTOR)
        page.click(ADD_LOCALE_BUTTON_SELECTOR)
        page.wait_for_selector(LOCALE_NAME_INPUT_SELECTOR)
        page.fill(LOCALE_NAME_INPUT_SELECTOR, locale_name)
        page.wait_for_selector(LOCALE_SAVE_BUTTON_SELECTOR)
        page.click(LOCALE_SAVE_BUTTON_SELECTOR)
        page.wait_for_timeout(3000)
        print("Locale created.")
    except Exception as e:
        print(f"Error while creating locale: {e}")

def create_floor(page, floor_name):
    try:
        print(f"Creating floor '{floor_name}'...")
        page.wait_for_selector(ADD_FLOOR_BUTTON_SELECTOR)
        page.click(ADD_FLOOR_BUTTON_SELECTOR)
        page.wait_for_selector(FLOOR_BUTTON_ONE_MORE_SELECTOR)
        page.click(FLOOR_BUTTON_ONE_MORE_SELECTOR)
        page.wait_for_selector(FLOOR_NAME_INPUT_SELECTOR)
        page.fill(FLOOR_NAME_INPUT_SELECTOR, floor_name)
        page.wait_for_selector(FLOOR_SAVE_BUTTON_SELECTOR)
        page.click(FLOOR_SAVE_BUTTON_SELECTOR)
        page.wait_for_selector(FLOOR_SELECTED)
        page.click(FLOOR_SELECTED)
        print("Floor created.")
    except Exception as e:
        print(f"Error while creating floor: {e}")

def search_college_of_engineering(page, college_name):
    try:
        print(f"Searching for '{college_name}'...")
        search_input = page.locator('input[placeholder="\\A0Search for locations..."]')
        search_input.click()
        search_input.fill(college_name)
        page.wait_for_selector(DROPDOWN_SELECTOR)
        dropdown_option = page.locator(f"{DROPDOWN_SELECTOR} div").first
        dropdown_option.click()
        page.wait_for_timeout(3000)
        print("College selected and zoomed.")
    except Exception as e:
        print(f"Error while searching college: {e}")

def go_to_map_ui_section(page):
    print("Navigating to 'Map UI' section...")
    try:
        page.wait_for_selector(MAP_UI_BUTTON_SELECTOR, timeout=5000)
        page.click(MAP_UI_BUTTON_SELECTOR)
        page.wait_for_timeout(2000)
        print("Clicked 'Map UI' section.")
    except Exception as e:
        print(f"Failed to click 'Map UI' section: {e}")

def upload_image_and_edit(page):
    print("Uploading image and clicking edit...")
    try:
        page.wait_for_selector(DROPDOWN_TOGGLE_SELECTOR, timeout=8000)
        page.click(DROPDOWN_TOGGLE_SELECTOR)
        print("Dropdown opened.")
        page.wait_for_timeout(1500)
        file_path = os.path.abspath(IMAGE_TO_UPLOAD)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found at: {file_path}")
        buttons = page.locator(BUTTON_LIST_SELECTOR)
        with page.expect_file_chooser() as fc_info:
            buttons.nth(0).click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        print(f"Image uploaded: {file_path}")
        page.wait_for_timeout(5000)
        buttons.nth(1).click()
        print("Edit button clicked.")
    except Exception as e:
        print(f"Error during image upload/edit: {e}")

def increase_scale(page, times=20):
    print(f"Increasing scale by clicking '+' {times} times...")
    try:
        scale_section = page.locator("text=Scale").locator("..").locator("..")
        increase_button = scale_section.locator("button.fancyBtn.IncreaseButton")
        for _ in range(times):
            increase_button.first.click()
            page.wait_for_timeout(300)
        print("Scale increased successfully.")
    except Exception as e:
        print(f"Error while increasing scale: {e}")

def increase_rotation(page, times=20):
    try:
        print(f"Increasing rotation by clicking '+' {times} times...")
        increase_buttons = page.locator("button.fancyBtn.IncreaseButton")
        for _ in range(times):
            increase_buttons.nth(2).click()
            page.wait_for_timeout(300)
        print("Rotation increased successfully.")
    except Exception as e:
        print(f"Error while increasing rotation: {e}")

def increase_opacity(page, times=20):
    try:
        print(f"Increasing opacity by clicking '+' {times} times...")
        increase_buttons = page.locator("button.fancyBtn.IncreaseButton")
        for _ in range(times):
            increase_buttons.nth(3).click()
            page.wait_for_timeout(300)
        print("Opacity increased successfully.")
    except Exception as e:
        print(f"Error while increasing opacity: {e}")

def image_saver(page):
    try:
        print("Saving image...")
        buttons = page.locator('button.full-width-button')
        save_button = buttons.last
        save_button.click()
        page.wait_for_timeout(3000)
        print("Image saved successfully.")
    except Exception as e:
        print(f"Error while saving image: {e}")

def zoning_in(page, zone_type="Polygon Zone"):
    try:
        print(f"Creating {zone_type}")
        page.wait_for_selector(DROPDOWN_TOGGLE_SELECTOR, timeout=8000)
        page.click(DROPDOWN_TOGGLE_SELECTOR)
        page.wait_for_selector(NEW_DROPDOWN_SELECTOR, timeout=5000)
        page.click(NEW_DROPDOWN_SELECTOR)
        page.wait_for_selector(CREATE_ZONE_BUTTON_SELECTOR, timeout=5000)
        page.click(CREATE_ZONE_BUTTON_SELECTOR)
        target_button = page.locator(f'button.MarkerButton:has-text("{zone_type}")')
        target_button.wait_for(timeout=5000)
        target_button.click()
        print(f"{zone_type} clicked.")
    except Exception as e:
        print(f"Failed to create zone: {e}")

def draw_polygon_zone(page):
    try:
        coordinates = [
            (730, 600),  
            (800, 600),  
            (800, 660),  
            (730, 660),  
            (730, 600)
        ]
        for x, y in coordinates:
            page.mouse.click(x, y)
            page.wait_for_timeout(300)
        print("Polygon drawn at target location.")
    except Exception as e:
        print(f"Error while drawing polygon: {e}")

def name_and_save_zone(page, zone_name="automated_zone"):
    try:
        print("Naming and saving the created zone...")
        zone_paths = page.locator("path.leaflet-interactive")
        count = zone_paths.count()
        if count == 0:
            print("No zone found.")
            return
        zone_paths.nth(count - 1).click()
        page.wait_for_timeout(1000)
        page.wait_for_selector('#zoneName\\$Add', timeout=5000)
        page.fill('#zoneName\\$Add', zone_name)
        print(f"Zone name entered: {zone_name}")
        page.click('#SaveZoneButton\\$Add')
        page.wait_for_timeout(2000)
        print("Zone saved successfully.")
    except Exception as e:
        print(f"Failed to name and save zone: {e}")

def create_circular_zone(page, start_x=750, start_y=450, end_x=800, end_y=450, zone_name="auto_circle_zone"):
    try:
        print("Creating circular zone...")
        circular_button = page.locator('button.MarkerButton:has-text("Circular Zone")')
        circular_button.wait_for(timeout=5000)
        circular_button.click()
        print("Circular Zone button clicked.")
        page.wait_for_timeout(1000)
        print(f"Clicking center at ({start_x}, {start_y})")
        page.mouse.click(start_x, start_y)
        page.wait_for_timeout(500)
        print(f"Dragging to radius point at ({end_x}, {end_y}) and finalizing")
        page.mouse.move(end_x, end_y)
        page.mouse.click(end_x, end_y)
        page.wait_for_timeout(1000)
        print("Clicking on the newly created circular zone...")
        zone_paths = page.locator("path.leaflet-interactive")
        count = zone_paths.count()
        if count == 0:
            print("No zone paths found.")
            return
        zone_paths.nth(count - 1).click()
        page.wait_for_timeout(1000)
        print("Waiting for zone name input field...")
        page.wait_for_selector('#zoneName\\$Add', timeout=5000)
        page.fill('#zoneName\\$Add', zone_name)
        page.click('#SaveZoneButton\\$Add')
        page.wait_for_timeout(2000)
        print(f"Circular zone '{zone_name}' created and saved.")

    except Exception as e:
        print(f"Failed to create circular zone: {e}")


def anchor_making(page): 
    try:
        print("Creating RSSI Anchor...")
        page.wait_for_selector(DROPDOWN_TOGGLE_SELECTOR, timeout=5000)
        page.click(DROPDOWN_TOGGLE_SELECTOR)
        print("Dropdown toggled")
        page.wait_for_selector(ANCHOR_DROPDOWN_SELECTOR, timeout=5000)
        page.click(ANCHOR_DROPDOWN_SELECTOR)
        print("Anchor Options clicked")
        page.wait_for_selector(RSSI_ANCHOR_SELECTOR, timeout=5000)
        page.click(RSSI_ANCHOR_SELECTOR)
        print("RSSI Anchor selected")
        page.mouse.click(700, 500)
        page.wait_for_timeout(1000)
        print("Anchor placed on map.")
    except Exception as e:
        print(f"Error while creating anchor: {e}")


def fill_anchor_form_with_zone(page):
    try:                                                                                            
        print("Filling updated anchor form...")
        mac_id_input = page.locator('input#ID').last
        mac_id_input.wait_for(timeout=3000)  # Wait for it to be interactable
        mac_id_input.click()
        mac_id_input.fill('hub55555556')
        print("MAC ID set to '55555556'")
        description_input = page.locator('input#description').last
        description_input.click()
        description_input.fill('TESTING AUTOMATION')
        print("Description set to 'TESTING AUTOMATION'")
        zone_dropdown = page.locator('select#zone').last
        zone_dropdown.select_option("auto_circle_zone")
        print("Zone 'automated_zone' selected")
        save_button = page.locator('button.submit-btn', has_text="Save").last
        save_button.click()
        print("Anchor form submitted!")
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Error while submitting anchor form: {e}")

def create_asset(page):
    try:
        page.wait_for_selector(ASSET_TRACKING_UI, timeout=5000)
        page.click(ASSET_TRACKING_UI)
        page.wait_for_selector(CREATE_ASSET_BUTTON, timeout=5000)
        page.click(CREATE_ASSET_BUTTON)
        page.wait_for_selector(MAC_SELECTOR, timeout=5000)
        page.fill(MAC_SELECTOR, "E4E1129BDB4D")
        page.wait_for_selector(ASSET_NAME_SELECTOR, timeout=5000)
        page.fill(ASSET_NAME_SELECTOR, "Automation Asset")
        page.wait_for_selector(SAVE_ASSET_BUTTON, timeout=5000)
        page.click(SAVE_ASSET_BUTTON)
        print("Asset created successfully.")
    except Exception as e:
        print(f"Error while navigating to Asset Tracking UI: {e}")

def take_x_api(page):
    try:
        page.wait_for_selector(USER_DROPDOWN_SELECTOR, timeout=5000)
        page.click(USER_DROPDOWN_SELECTOR)
        page.wait_for_selector(ORG_SETTINGS_BUTTON, timeout=5000)
        page.click(ORG_SETTINGS_BUTTON)
        page.wait_for_selector(SEARCH_BAR_CLICK, timeout=5000)
        page.click(SEARCH_BAR_CLICK)
        page.wait_for_selector(ORG_SELECTOR, timeout=5000)
        page.click(ORG_SELECTOR)
        copy_button = page.locator('button[title="Copy to clipboard"]:below(:text("Data API Key"))')
        generate_button = page.locator('button:has-text("Generate"):below(:text("Data API Key"))')
        if copy_button.is_visible():
            print("Copy button is already visible. Copying API key...")
            copy_button.click()
        else:
            print("Copy button not visible. Generating API key...")
            generate_button.wait_for(timeout=10000)
            generate_button.click()
            page.wait_for_timeout(2000)  # wait for key to be generated and copy button to appear
            copy_button.wait_for(timeout=5000)
            copy_button.click()
            print("API key generated and copied.")
        page.wait_for_selector(CLOSE_BUTTON, timeout=5000)
        page.click(CLOSE_BUTTON)
    except Exception as e:
        print(f"Error while handling API key: {e}")

def get_clipboard_content():
    try:
        return pyperclip.paste().strip()
    except Exception as e:
        print(f"Failed to get clipboard content: {e}")
        return None

def heatmap_creation(page):
    try:
        print("Navigating to Heat Map UI...")
        page.wait_for_selector(HEAT_MAP_UI_BUTTON_SELECTOR, timeout=5000)
        page.click(HEAT_MAP_UI_BUTTON_SELECTOR)

        print("Opening Heat Map Creation section...")
        page.wait_for_selector(HEAT_MAP_CREATOR_OPENER, timeout=5000)
        page.click(HEAT_MAP_CREATOR_OPENER)

        print("Selecting asset for heat map...")
        page.wait_for_selector(HEAT_MAP_ASSET_SELECTOR, timeout=5000)
        page.click(HEAT_MAP_ASSET_SELECTOR)

        print("Selecting the RSSI Anchor...")
        page.wait_for_selector(RSSI_HEAT_ANCHOR_SELECTOR, timeout=5000)
        page.click(RSSI_HEAT_ANCHOR_SELECTOR)
        page.wait_for_timeout(1000)

        # Optional: focus map area
        page.mouse.move(750, 600)

        print("Clicking on map to create heatmap points...")
        coordinates = [
            (740, 610), (770, 620), (800, 630), (770, 690),
            (680, 650), (790, 660), (830, 670), (845, 730),
            (820, 690), (830, 700), (840, 710), (850, 720),
        ]
        for idx, (x, y) in enumerate(coordinates):
            page.mouse.click(x, y)
            print(f"✔️ Point {idx+1} clicked at ({x}, {y})")
            page.wait_for_timeout(500)  # Increased from 300ms to 500ms

        print("✅ Heat map creation clicks completed.")
    except Exception as e:
        print(f"Error while creating heat map: {e}")




# --------------------------- MAIN STUFF ---------------------------
if __name__ == "__main__":
    page, browser, playwright = login_to_app()
    wait_if_interactive("Press Enter to create a new organization...")
    create_org(page, "Automation Org")
    wait_if_interactive("Press Enter to create a new locale...")
    create_locale(page, "Auto Locale")
    wait_if_interactive("Press Enter to create a new floor...")
    create_floor(page, "1")
    wait_if_interactive("Press Enter to search for your college...")
    search_college_of_engineering(page, "College of Engineering Attingal")
    wait_if_interactive("Press Enter to go to 'Map UI' section...")
    go_to_map_ui_section(page)
    wait_if_interactive("Press Enter to upload image and click edit...")
    upload_image_and_edit(page)
    wait_if_interactive("Press Enter to increase scale...")
    increase_scale(page,times=20)
    wait_if_interactive("Press Enter to increase rotation...")
    increase_rotation(page,times=20)
    wait_if_interactive("Press Enter to increase opacity...")
    increase_opacity(page,times=20)
    wait_if_interactive("Press Enter to save the image...")
    image_saver(page)
    wait_if_interactive("Press Enter to create a zone...")
    zoning_in(page, zone_type="Polygon Zone")
    draw_polygon_zone(page)
    name_and_save_zone(page, zone_name="automated_zone")
    wait_if_interactive("Press Enter to create circular zone...")
    create_circular_zone(page, start_x=750, start_y=450, end_x=800, end_y=450, zone_name="auto_circle_zone")
    wait_if_interactive("Press Enter to create an anchor...")
    anchor_making(page)
    page.wait_for_timeout(1000)
    fill_anchor_form_with_zone(page)
    wait_if_interactive("Press Enter to create an asset...")
    create_asset(page)
    wait_if_interactive("Press Enter to take X API...")
    take_x_api(page)
    wait_if_interactive("Press Enter to get X-API KEY and MAC ID...")
    x_api_key = get_clipboard_content()
    mac_id = "E4E1129BDB4D"
    print(f"Retrieved X-API KEY: {x_api_key}")
    print(f"Retrieved MAC ID: {mac_id}")
    print("Starting Hub Simulator with real values...")
    hubsendata_process = subprocess.Popen([sys.executable, "hubsendata.py", mac_id, x_api_key])
    print("Waiting 30 seconds before proceeding to heatmap setup...")
    time.sleep(30)
    wait_if_interactive("Press Enter to create heatmap...")
    heatmap_creation(page)
    input("Press Enter to close browser and stop simulation...")
    browser.close()
    playwright.stop()
    print("Stopping Hub Simulator...")
    try:
        hubsendata_process.send_signal(signal.SIGINT)
        hubsendata_process.wait(timeout=5)
    except Exception:
        hubsendata_process.terminate()
    print("Hub Simulator stopped.")