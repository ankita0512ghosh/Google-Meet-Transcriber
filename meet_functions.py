from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as soup
import undetected_chromedriver as uc
import time
import tts
from get_credentials import get_email, get_pwd
import sys
from playsound import playsound  

# initialize WebDriver
def initialize_driver():
    opt = Options()
    opt.add_argument("--disable-infobars")
    opt.add_argument("start-maximised")
    opt.add_argument("--disable-extensions")
    opt.add_argument("--use-fake-ui-for-media-stream")  # disables permission popup
    opt.add_experimental_option("prefs", { \
        "profile.default_content_setting_values.media_stream_mic": 2, 
        "profile.default_content_setting_values.media_stream_camera": 2,
        "profile.default_content_setting_values.geolocation": 1, 
        "profile.default_content_setting_values.notifications": 1 
    })

    driver = uc.Chrome(chrome_options = opt, driver_executable_path = "Path to chrome driver exe file")
    driver.implicitly_wait(440)

    #enable mic and camera
    driver.execute_cdp_cmd(
        "Browser.grantPermissions",
        {
            "origin": "https://meet.google.com"  , 
            "permissions": ["geolocation"]
        },
    )
    return driver

# close Web Driver
def close_driver(driver):
    driver.close()

# Sign in to Google
def sign_in_to_google(driver):
    url = 'https://accounts.google.com/signin/v2/identifier?ltmpl=meet&continue=https%3A%2F%2Fmeet.google.com%3Fhs%3D193&&flowName=GlifWebSignIn&flowEntry=ServiceLogin'
    driver.get(url)
    # email ID field 
    SignIn = driver.find_element("id","identifierId") 

    # clicking on the button 
    # get email from encrypted file
    SignIn.send_keys(str(get_email()))
    SignIn.send_keys(Keys.ENTER)

    driver.implicitly_wait(10)

    # password field
    # get password from encrypted file
    EnterPass = driver.find_element("xpath","//*[@id='password']/div[1]/div/div[1]/input")
    EnterPass.send_keys(str(get_pwd()))
    EnterPass.send_keys(Keys.ENTER)

# Enter meeting code 
def enter_meet_code(driver, meet_code):
    try:
        # Wait for input box to appear up to 15 seconds
        input_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Enter a code or link']"))
        )
        input_box.clear()
        input_box.send_keys(meet_code)
        input_box.send_keys(Keys.ENTER)
    except Exception as e:
        print("[ERROR] Could not enter Meet code:", e)

# Press on join meeting button
def join_meeting(driver):
    try:
        join_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((
                By.XPATH, "//button[.//span[contains(text(), 'Join now') or contains(text(), 'Ask to join') or contains(text(), 'Join')]]"
            ))
        )
        join_btn.click()
        print("[INFO] Successfully clicked Join button.")
    except Exception as e:
        print("[ERROR] Could not find or click Join button:", e)

# Close a pop up
def close_pop_up(driver):
    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH, "//div[@role='dialog']//button[.='Dismiss' or .='Close']"
            ))
        )
        close_button.click()
        print("[INFO] Dismissed popup.")
    except Exception as e:
        print("[INFO] No popup to dismiss or already closed.")

def initial_stuff(meet_code):
    # initialize selenium driver
    driver = initialize_driver()

    # sign in to google
    sign_in_to_google(driver)
    time.sleep(2)

    # entering google meet code
    enter_meet_code(driver, meet_code)
    time.sleep(4)

    # join the meeting
    join_meeting(driver)

    time.sleep(2)

    # close a pop up
    close_pop_up(driver)

    return driver
    
def scrape(driver, chat_dic):
    html = driver.page_source
    page_soup = soup(html, "html.parser")
    x = page_soup.find_all("div", {"class":"GDhqjd"})
    
    new_msg = []
    try:
        for y in x:
            sender = y.find("div", {"class":"YTbUzc"}).get_text()
            time_stamp = ' '.join(y.find("div",{"class":"MuzmKe"}).get_text().split('\u202f'))
            msgs = y.find_all("div",{"class":"oIy2qc"})
            msgs_list = []

            for msg in msgs:
                msgs_list.append(msg.get_text())
            
            # append only new messages to ensure that messages sent to the user are not sent again
            if (sender, time_stamp) not in chat_dic:
                new_msg.append((sender, msgs_list))

            elif chat_dic[(sender, time_stamp)] != msgs_list:
                new_msg.append((sender, [msg for msg in msgs_list if msg not in chat_dic[(sender, time_stamp)]]))
            
            chat_dic[(sender, time_stamp)] = msgs_list
    except:
        pass
    return new_msg

def is_element_appeared(element_Xpath, driver, timeout = 2):
    try:
        wait = WebDriverWait(driver, timeout=timeout)
        driver.implicitly_wait(timeout)
        driver.find_element(By.XPATH,element_Xpath)
        return True
    except Exception as ex:
        return False

# check if meeting has ended yet 
def check_meeting(driver):

    # check if return to home screen button is present
    try:
        if is_element_appeared("/html/body/div[1]/c-wiz/div/div/div[1]/div[2]/div/button",driver):
            # found, so exit meeting
            return False
    except:
        pass
    
    # check if home screen present
    try:
        if is_element_appeared("/html/body/c-wiz/div/div[2]/div/div[1]/div[3]/div/div[1]/div[1]/div/button",driver):
            # found, so exit meeting
            return False
    except:
        pass

    # the meeting has not ended 
    return True