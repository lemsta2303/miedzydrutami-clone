from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from faker import Faker
import random
import time

chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-insecure-localhost")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--start-fullscreen")
driver = webdriver.Chrome(options=chrome_options)
driver.get("http://localhost:8080")
fake = Faker()

wait = WebDriverWait(driver, 15)

def registerNewUser():
    user_info_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "user-info")))
    user_info_element.click()
    no_account_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "no-account")))
    no_account_element.click()

    gender_value = 1

    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    password = fake.password(length=8)
    birthday = fake.date_of_birth(minimum_age=18, maximum_age=100).strftime("%Y-%m-%d")

    ganderElement = wait.until(EC.presence_of_element_located((By.ID, f"field-id_gender-{gender_value}")))
    ganderElement.click()

    firstNameElement = driver.find_element(By.ID, "field-firstname")
    firstNameElement.send_keys(first_name)

    lastNameElement = driver.find_element(By.ID, "field-lastname")
    lastNameElement.send_keys(last_name)

    emailElement = driver.find_element(By.ID, "field-email")
    emailElement.send_keys(email)

    passwordElement = driver.find_element(By.ID, "field-password")
    passwordElement.send_keys(password)

    birthdayElement = driver.find_element(By.ID, "field-birthday")
    birthdayElement.send_keys(birthday)

    optinCheckbox = wait.until(EC.presence_of_element_located((By.NAME, "optin")))
    optinCheckbox.click()

    customerPrivCheckbox = wait.until(EC.presence_of_element_located((By.NAME, "customer_privacy")))
    customerPrivCheckbox.click()

    newsletterCheckbox = wait.until(EC.presence_of_element_located((By.NAME, "newsletter")))
    newsletterCheckbox.click()

    customerCheckbox = wait.until(EC.presence_of_element_located((By.NAME, "psgdpr")))
    customerCheckbox.click()

    save_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary")))
    save_button.click()

def checkOut():
    cartElement = wait.until(EC.element_to_be_clickable((By.ID, "_desktop_cart")))
    cartElement.click()

    checkOutElement = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary")))
    checkOutElement.click()

    adressElement = wait.until(EC.element_to_be_clickable((By.ID, "field-address1")))
    adressElement.send_keys("Adress")

    zipElement = wait.until(EC.element_to_be_clickable((By.ID, "field-postcode")))
    zipElement.send_keys("12-345")

    cityElement = wait.until(EC.element_to_be_clickable((By.ID, "field-city")))
    cityElement.send_keys("City")

    continueButton = wait.until(EC.element_to_be_clickable((By.NAME, "confirm-addresses")))
    continueButton.click()

def shipping():
    radio_button = wait.until(EC.presence_of_element_located((By.XPATH, "//label[@for='delivery_option_11']")))
    radio_button.click()

    submit_button = driver.find_element(By.NAME, "confirmDeliveryOption")
    submit_button.click()

def payment():
    payment_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@for='payment-option-2']")))
    payment_label.click()
    checkbox = wait.until(EC.presence_of_element_located((By.ID, "conditions_to_approve[terms-and-conditions]")))
    checkbox.click()
    order_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    "//div[@class='ps-shown-by-js']//button[@type='submit' and contains(text(), 'Złóż zamówienie')]"))
    )

    order_button.click()

def checkShipping():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    orders_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='https://localhost/historia-zamowien']"))
    )
    orders_link.click()
    first_details_button = driver.find_element(By.XPATH, "//tbody/tr[1]//a[contains(text(), 'Szczegóły')]")
    first_details_button.click()

def downloadProduct():
    invoice_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Pobierz fakturę proforma w pliku PDF')]")
    invoice_link.click()

def addToCart():

    addQuantity = driver.find_element(By.CSS_SELECTOR, '.js-touchspin.bootstrap-touchspin-up')

    for _ in range(random.randint(0, 3)):
        addQuantity.click()

    addElement = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "add")))
    addElement.click()

    continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-dismiss='modal' and contains(text(), 'Kontynuuj zakupy')]"))
    )
    continue_button.click()

def getProduct(name):
    search_input = driver.find_element(By.CSS_SELECTOR, 'input[name="s"]')
    search_input.send_keys(name)
    search_input.send_keys(Keys.RETURN)

    products = driver.find_elements(By.CSS_SELECTOR, ".js-product")
    random_product = random.choice(products)

    quick_view_button = random_product.find_element(By.CSS_SELECTOR, ".product-title a")
    quick_view_button.click()

    addToCart()

def getProductFromCategory():
    sklep_link = driver.find_element(By.LINK_TEXT, "Sklep")
    sklep_link.click()

    wloczki_link = driver.find_element(By.LINK_TEXT, "Włóczki")
    wloczki_link.click()

    product_link = driver.find_element(By.XPATH,
                                       "//a[@href='https://localhost/wloczki-bambusowe/264-cumbria-pascuali-2434986380651.html']")
    product_link.click()
    addToCart()

    sklep_link = driver.find_element(By.LINK_TEXT, "Sklep")
    sklep_link.click()

    wloczki_link = driver.find_element(By.LINK_TEXT, "Włóczki")
    wloczki_link.click()

    product_link = driver.find_element(By.XPATH,
                                       "//a[@href='https://localhost/wloczki-weganskie/251-palet-isager-1277160842360.html']")
    product_link.click()
    addToCart()

    sklep_link = driver.find_element(By.LINK_TEXT, "Sklep")
    sklep_link.click()

    wloczki_link = driver.find_element(By.LINK_TEXT, "Włóczki")
    wloczki_link.click()

    product_link = driver.find_element(By.XPATH,
                                       "//a[@href='https://localhost/wloczki-fantazyjne/246-on-line-blyszczaca-wloczka-z-cekinami-linie-344-starlight-9479046905897.html']")
    product_link.click()
    addToCart()

    sklep_link = driver.find_element(By.LINK_TEXT, "Sklep")
    sklep_link.click()

    wloczki_link = driver.find_element(By.LINK_TEXT, "Włóczki")
    wloczki_link.click()

    product_link = driver.find_element(By.XPATH,
                                       "//a[@href='https://localhost/wloczki-z-wielblada/245-camel-dk-pascuali-4917899049837.html']")
    product_link.click()
    addToCart()

    wloczki_link = driver.find_element(By.LINK_TEXT, "Włóczki")
    wloczki_link.click()

    product_link = driver.find_element(By.XPATH,
                                       "//a[@href='https://localhost/wloczki-z-kaszmiru/233-organic-cashmere-lace-pascuali-2142588940524.html']")
    product_link.click()
    addToCart()

    sklep_link = driver.find_element(By.LINK_TEXT, "Sklep")
    sklep_link.click()

    druty_link = driver.find_element(By.LINK_TEXT, "Druty")
    druty_link.click()

    product_link = driver.find_element(By.XPATH,
                                       "//a[@href='https://localhost/szydelka/315-knitpro-oasis-szydelka-wymienne-2475626889507.html']")
    product_link.click()
    addToCart()

    druty_link = driver.find_element(By.LINK_TEXT, "Druty")
    druty_link.click()

    product_link = driver.find_element(By.XPATH,
                                       "//a[@href='https://localhost/druty-do-warkoczy/314-drut-pomocniczy-knitpro-5910408525627.html']")
    product_link.click()
    addToCart()

    druty_link = driver.find_element(By.LINK_TEXT, "Druty")
    druty_link.click()

    product_link = driver.find_element(By.XPATH,
                                       "//a[@href='https://localhost/zestawy-drutow-wymiennych/286-seeknit-koshitsu-curve-60249-8-par-125-cm-5519519728058.html']")
    product_link.click()
    addToCart()

    druty_link = driver.find_element(By.LINK_TEXT, "Druty")
    druty_link.click()

    product_link = driver.find_element(By.XPATH,
                                       "//a[@href='https://localhost/druty-skarpetkowe/281-druty-addi-crasytrio-bamboo-6666154819347.html']")
    product_link.click()
    addToCart()

    druty_link = driver.find_element(By.LINK_TEXT, "Druty")
    druty_link.click()

    product_link = driver.find_element(By.XPATH,
                                       "//a[@href='https://localhost/szydelka/316-knitpro-oasis-raczka-do-szydelka-2568435590788.html']")
    product_link.click()
    addToCart()

def deleteProductFromCart():
    cartElement = wait.until(EC.element_to_be_clickable((By.ID, "_desktop_cart")))
    cartElement.click()
    for _ in range(3):
        remove_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@data-link-action='delete-from-cart']"))
        )
        remove_button.click()
        time.sleep(1)

def main():
    start = time.time()
    getProductFromCategory()
    time.sleep(2)
    getProduct("wloczka")
    time.sleep(2)
    deleteProductFromCart()
    time.sleep(2)
    registerNewUser()
    time.sleep(2)
    checkOut()
    time.sleep(2)
    shipping()
    time.sleep(2)
    payment()
    time.sleep(2)
    checkShipping()
    time.sleep(2)
    downloadProduct()
    time.sleep(2)
    print("Time: ", time.time() - start)

if __name__ == "__main__":
    main()
