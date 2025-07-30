from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time

# --------------------------- USER CONFIG ---------------------------
EMAIL = "skrhari2020@gmail.com"
PASSWORD = "Technology*19112005"
LOGIN_URL = "https://tracking.hard-softwerk.com"

EMAIL_SELECTOR = 'input[placeholder="Username/Email"]'
PASSWORD_SELECTOR = 'input[type="password"]'
LOGIN_BUTTON_SELECTOR = 'button:has-text("Login")'

FLOOR_SELECTED = 'div.ls-floor-item'
HEAT_MAP_UI_BUTTON_SELECTOR = 'div.twa-sidebar-item[title="Heat Map UI"]'
MAP_UI_BUTTON_SELECTOR = 'div.twa-sidebar-item[title="Map UI"]'
DELETE_BUTTON = 'button:has-text("Delete")'

DELETE_BUTTON = 'button.delete-btn delete-zone:has-text("Delete")'
DROPDOWN_TOGGLE_SELECTOR = 'ion-item:has-text("Image Options")'
IMAGE_EDIT='button.full-width-button:has-text("Edit")'
IMAGE_DELETE='button.full-width-button:has-text("Delete")'

LOCATION_SELECTOR = 'div.twa-sidebar-item[title="Location Selector"]'
DELETE_FLOOR_BUTTON = 'buttonls-delete-btn'

USER_DROPDOWN_SELECTOR = 'button.user-dropdown-button'
ORG_SETTINGS_BUTTON='button.dropdown-item:has-text("ORG Settings")'
SEARCH_BAR_CLICK='input.form-control[placeholder="Search by name"]'
ORG_SELECTOR='div.org-item:has-text("Automation Org")'
ORG_DELETE_CONFO='button.ayyo-cancel btnX:has-text("Yes, Delete Organization")'

# --------------------------- LOGIN FUNCTION ---------------------------
def login_to_app():
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto(LOGIN_URL)
        page.fill(EMAIL_SELECTOR, EMAIL)
        page.fill(PASSWORD_SELECTOR, PASSWORD)
        page.click(LOGIN_BUTTON_SELECTOR)
        page.wait_for_timeout(5000)
        print("Login successful!")
        time.sleep(3)
        return page, browser, playwright
    except Exception as e:
        print(f"Login failed: {e}")
        exit(1)


# ------------------------ SELECT ORG FUNCTION ------------------------
def select_organization(page, org_name="Automation Org"):
    try:
        time.sleep(1)
        org_items = page.locator(".ls-org-item")
        count = org_items.count()
        for i in range(count):
            item = org_items.nth(i)
            header = item.locator(".ls-org-header")
            if org_name in header.inner_text():
                print(f"Found matching org: '{org_name}'")
                box = header.bounding_box()
                if box:
                    x = box["x"] + box["width"] / 2
                    y = box["y"] + box["height"] / 2
                    page.mouse.move(x, y)
                    page.mouse.click(x, y)
                    print("Clicked on org header.")
                    time.sleep(1)
                    content = item.locator(".ls-org-content")
                    content.wait_for(state="visible", timeout=5000)
                    print("Org dropdown visible.")
                    time.sleep(1)
                    return item
                else:
                    print("Couldn't determine bounding box for org.")
        print(f"Org '{org_name}' not found.")
    except Exception as e:
        print(f"Error selecting org: {e}")


# ------------------------ SELECT LOCALE FUNCTION ------------------------
def select_locale(org_block):
    try:
        time.sleep(1)
        locale_header = org_block.locator(".ls-locale-header").first
        locale_header.wait_for(timeout=5000)
        box = locale_header.bounding_box()
        if box:
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            org_block.page.mouse.move(x, y)
            org_block.page.mouse.click(x, y)
            print("Locale button clicked successfully!")
            time.sleep(1)
        else:
            print("Couldn't determine bounding box for locale.")
        page = org_block.page
        page.wait_for_selector(FLOOR_SELECTED, timeout=5000)
        page.click(FLOOR_SELECTED)
        print("Floor selected.")
        time.sleep(1)
        page.wait_for_selector(HEAT_MAP_UI_BUTTON_SELECTOR, timeout=5000)
        page.click(HEAT_MAP_UI_BUTTON_SELECTOR)
        print("Heat Map UI opened.")
        time.sleep(2)
    except Exception as e:
        print(f"Error clicking locale or floor: {e}")


# ------------------------ DELETE ALL HEATMAPS ------------------------
def delete_all_heatmaps(page):
    try:
        time.sleep(2)
        while True:
            markers = page.locator("div.leaflet-marker-icon.rssi-marker")
            count = markers.count()
            if count == 0:
                print("No more heatmap markers found.")
                break
            marker = markers.nth(0)
            box = marker.bounding_box()
            if not box:
                print("Skipping a marker — no bounding box.")
                continue
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            page.mouse.move(x, y)
            page.mouse.click(x, y)
            print("Clicked a heatmap marker.")
            time.sleep(1)
            delete_btn = page.locator('button[id^="delete-point-"]')
            delete_btn.wait_for(state="visible", timeout=5000)
            delete_btn.click()
            print("Heatmap marker deleted.")
            time.sleep(2)
    except Exception as e:
        print(f"Error while deleting heatmaps: {e}")

def map_Stuffs(page):
    try:
        page.wait_for_selector(MAP_UI_BUTTON_SELECTOR, timeout=5000)
        page.click(MAP_UI_BUTTON_SELECTOR)
        print("Map UI opened.")
        time.sleep(2)
    except Exception as e:
        print(f"Error opening Map UI: {e}")


def delete_polygon_zone(page):
    try:
        print("Opening 'Map UI' to edit zone...")
        page.wait_for_selector(MAP_UI_BUTTON_SELECTOR, timeout=5000)
        page.click(MAP_UI_BUTTON_SELECTOR)
        page.wait_for_timeout(3000)
        print("Scrolling map upward to expose hidden zone...")
        time.sleep(2)
        print("Clicking on the 'automated_zone' polygon...")
        zone_paths = page.locator("path.leaflet-interactive")
        count = zone_paths.count()
        if count == 0:
            print("No zones detected on map.")
            return
        target_zone = zone_paths.nth(count - 2)
        box = target_zone.bounding_box()
        if box:
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            page.mouse.click(x, y)
            print(f"Clicked zone at approx center ({x:.0f}, {y:.0f})")
        else:
            target_zone.click()
            print("Clicked zone using fallback.")
        page.wait_for_timeout(1500)
        def handle_dialog(dialog):
            print(f"Confirmation Dialog: {dialog.message}")
            dialog.accept()
            print("Dialog accepted.")
        page.once("dialog", handle_dialog)
        delete_btn = page.locator('button[id="deleteBtn\\$DEL"]')
        delete_btn.wait_for(state="visible", timeout=5000)
        delete_btn.click()
        print("Delete button clicked.")
        time.sleep(2)
    except Exception as e:
        print(f"Error deleting zone: {e}")


def delete_all_custom_markers(page):
    try:
        print("Looking for custom markers to delete...")
        time.sleep(2)
        while True:
            markers = page.locator("div.leaflet-marker-icon.custom-div-icon")
            count = markers.count()
            print(f"Found {count} custom markers.")
            if count == 0:
                print("All custom markers deleted.")
                break
            marker = markers.first
            box = marker.bounding_box()
            if not box:
                print("Skipping a marker — no bounding box.")
                continue
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            page.mouse.move(x, y)
            page.mouse.click(x, y)
            print("Clicked a custom marker.")
            time.sleep(1)
            def handle_dialog(dialog):
                print(f"Confirmation Dialog: {dialog.message}")
                dialog.accept()
                print("Dialog accepted.")
            page.once("dialog", handle_dialog)
            delete_btn = page.locator("button.delete-btn.delete-marker")
            delete_btn.wait_for(state="visible", timeout=5000)
            delete_btn.click()
            print("Custom marker deleted.")
            time.sleep(2)
    except Exception as e:
        print(f"Error while deleting custom markers: {e}")


def delete_circular_zone(page):
    try:
        print("Opening 'Map UI' to edit zone...")
        page.wait_for_selector(MAP_UI_BUTTON_SELECTOR, timeout=5000)
        page.click(MAP_UI_BUTTON_SELECTOR)
        page.wait_for_timeout(3000)
        time.sleep(2)
        print("Clicking on the 'automated_zone' polygon...")
        zone_paths = page.locator("path.leaflet-interactive")
        count = zone_paths.count()
        if count == 0:
            print("No zones detected on map.")
            return
        target_zone = zone_paths.nth(count - 1)
        box = target_zone.bounding_box()
        if box:
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            page.mouse.click(x, y)
            print(f"Clicked zone at approx center ({x:.0f}, {y:.0f})")
        else:
            target_zone.click()
            print("Clicked zone using fallback.")
        page.wait_for_timeout(1500)
        def handle_dialog(dialog):
            print(f"Confirmation Dialog: {dialog.message}")
            dialog.accept()
            print("Dialog accepted.")
        page.once("dialog", handle_dialog)
        delete_btn = page.locator('button[id="deleteBtn\\$DEL"]')
        delete_btn.wait_for(state="visible", timeout=5000)
        delete_btn.click()
        print("Delete button clicked.")
        time.sleep(2)
    except Exception as e:
        print(f"Error deleting zone: {e}")


def image_delete(page):
    try:
        print("Opening 'Image Options' dropdown...")
        page.wait_for_selector(DROPDOWN_TOGGLE_SELECTOR, timeout=5000)
        page.click(DROPDOWN_TOGGLE_SELECTOR)
        time.sleep(1)
        print("Clicking 'Edit' button...")
        page.wait_for_selector(IMAGE_EDIT, timeout=5000)
        page.click(IMAGE_EDIT)
        time.sleep(1)
        print("Clicking 'Delete' button...")
        page.wait_for_selector(IMAGE_DELETE, timeout=5000)
        page.click(IMAGE_DELETE)
        time.sleep(1)
    except Exception as e:
        print(f"Error deleting image: {e}")

def locations_delete(page):
    try:
        print("Opening 'Location Selector'...")
        page.wait_for_selector(LOCATION_SELECTOR, timeout=5000)
        page.click(LOCATION_SELECTOR)
        time.sleep(1)
        time.sleep(1)
    except Exception as e:
        print(f"❌ Error deleting locations: {e}")

def hnmmmm(org_block):
    try:
        time.sleep(1)
        locale_header = org_block.locator(".ls-locale-header").first
        locale_header.wait_for(timeout=5000)
        box = locale_header.bounding_box()
        if box:
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            org_block.page.mouse.move(x, y)
            org_block.page.mouse.click(x, y)
            print("Locale button clicked successfully!")
            time.sleep(1)
        else:
            print("Couldn't determine bounding box for locale.")
        page = org_block.page
        page.wait_for_selector(FLOOR_SELECTED, timeout=5000)
        page.click(FLOOR_SELECTED)
        print("Floor selected.")
    except Exception as e:
        print(f"Error clicking locale or floor: {e}")

def deleting_stuffs(page):
    try:
        page.wait_for_selector(DELETE_FLOOR_BUTTON, timeout=5000)
        delete_floor_button = page.locator(DELETE_FLOOR_BUTTON)
    except Exception as e:
        print(f"Error clicking locale or floor: {e}")

def delete_all_floors(page):
    try:
        print("Deleting all floors under the selected locale...")
        while True:
            floors = page.locator("div.ls-floor-item")
            count = floors.count()
            if count == 0:
                print("No more floors found.")
                break
            floor = floors.first
            box = floor.bounding_box()
            if not box:
                print("Skipping a floor — no bounding box.")
                continue
            delete_btn = floor.locator("button.ls-delete-btn")
            delete_btn.wait_for(state="visible", timeout=3000)
            delete_btn.click()
            print("🗑️ Floor delete button clicked.")
            time.sleep(1)
            def handle_dialog(dialog):
                print(f"Confirmation Dialog: {dialog.message}")
                dialog.accept()
                print("Dialog accepted.")
            page.once("dialog", handle_dialog)
            time.sleep(1)
    except Exception as e:
        print(f"Error deleting floors: {e}")


def delete_all_locales(page):
    try:
        print("Starting locale deletion process...")
        dialog_accept_counter = {"count": 0}
        def handle_locale_dialog(dialog):
            print(f"Locale Deletion Dialog: {dialog.message}")
            dialog.accept()
            dialog_accept_counter["count"] += 1
            print(f"Dialog accepted ({dialog_accept_counter['count']}/2)")
        page.on("dialog", handle_locale_dialog)
        while True:
            locales = page.locator(".ls-locale-item")
            if locales.count() == 0:
                print("No more locales found.")
                break
            locale = locales.first
            locale.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            floors = locale.locator("div.ls-floor-item")
            while floors.count() > 0:
                floor = floors.first
                floor.scroll_into_view_if_needed()
                page.wait_for_timeout(300)
                try:
                    floor_delete_btn = floor.locator("button.ls-delete-btn")
                    floor_delete_btn.wait_for(state="visible", timeout=5000)
                    page.once("dialog", lambda dialog: (
                        print(f"🗑️ Floor Confirmation Dialog: {dialog.message}"),
                        dialog.accept()
                    ))
                    floor_delete_btn.click()
                    print("Floor delete button clicked.")
                    time.sleep(1)
                    floors = locale.locator("div.ls-floor-item")
                except PlaywrightTimeoutError:
                    print("Floor delete button not clickable.")
                    break
            try:
                delete_btn = locale.locator("button.ls-delete-btn").first
                delete_btn.scroll_into_view_if_needed()
                delete_btn.wait_for(state="visible", timeout=5000)
                dialog_accept_counter["count"] = 0
                delete_btn.click()
                print("Locale delete button clicked.")
                timeout = 5000
                elapsed = 0
                while dialog_accept_counter["count"] < 2 and elapsed < timeout:
                    time.sleep(0.5)
                    elapsed += 500
                if dialog_accept_counter["count"] == 2:
                    print("Locale deleted after double confirmation.")
                else:
                    print("Expected two dialogs, but only handled one.")
                time.sleep(2)
            except PlaywrightTimeoutError:
                print("Locale delete button not found.")
                break
    except Exception as e:
        print(f"Error during locale deletion: {e}")


def delete_org(page):
    try:
        page.wait_for_selector(USER_DROPDOWN_SELECTOR, timeout=5000)
        page.click(USER_DROPDOWN_SELECTOR)
        page.wait_for_selector(ORG_SETTINGS_BUTTON, timeout=5000)
        page.click(ORG_SETTINGS_BUTTON)
        page.wait_for_selector(SEARCH_BAR_CLICK, timeout=5000)
        page.click(SEARCH_BAR_CLICK)
        page.wait_for_selector(ORG_SELECTOR, timeout=5000)
        page.click(ORG_SELECTOR)
        page.wait_for_selector("button.newdelete", timeout=5000)
        delete_btn = page.locator("button.newdelete")
        delete_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(500)  # small buffer time
        delete_btn.click()
        print("Clicked Delete Organization button.")
        page.once("dialog", lambda dialog: (
            print(f"Org Delete Confirm Dialog: {dialog.message}"),
            dialog.accept(),
            print("Dialog accepted.")
        ))
        page.wait_for_selector(ORG_DELETE_CONFO, timeout=5000)
        page.click(ORG_DELETE_CONFO)
        print("Organization deleted.")
    except Exception as e:
        print(f"Error deleting organization: {e}")


# --------------------------- MAIN ---------------------------
if __name__ == "__main__":
    page, browser, playwright = login_to_app()
    org_block = select_organization(page)
    if org_block:
        select_locale(org_block)
        delete_all_heatmaps(page)
        map_Stuffs(page)
        delete_polygon_zone(page)
        delete_all_custom_markers(page)
        delete_circular_zone(page)
        image_delete(page)
        locations_delete(page)
        org_block = select_organization(page, "Automation Org")
        hnmmmm(org_block)
        delete_all_floors(page)
        delete_all_locales(page)
        delete_org(page)

