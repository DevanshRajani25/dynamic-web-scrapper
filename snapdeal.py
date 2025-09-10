import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


user_ip = input("Enter what you want to purchase from Snapdeal: ")
min_price = input("Enter minimum budget (press Enter to skip): ")
max_price = input("Enter maximum budget (press Enter to skip): ")

print("\nSort Options:\n1. Relevance\n2. Popularity\n3. Price Low to High\n4. Price High to Low\n5. Discount\n6. Fresh Arrivals")
sort_choice = input("Choose sorting option (1-6): ")

sort_map = {
    "1": "rlvncy",   
    "2": "plrty",    
    "3": "plth",     
    "4": "phtl",     
    "5": "dhtl",     
    "6": "rec",      
}
sort_param = sort_map.get(sort_choice, "rlvncy")

if user_ip:
    driver = webdriver.Chrome()

    driver.get("https://www.snapdeal.com/")
    driver.maximize_window()

    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "searchformInput"))
    )
    search_box.send_keys(user_ip)
    search_box.send_keys(Keys.RETURN)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product-row"))
    )

    try:
        if min_price:
            min_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "fromVal"))
            )
            min_input.clear()
            min_input.send_keys(min_price)

        if max_price:
            max_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "toVal"))
            )
            max_input.clear()
            max_input.send_keys(max_price)

        go_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".price-go-arrow"))
        )
        go_btn.click()
        time.sleep(3)
    except Exception as e:
        print("Price filter not applied:", e)

    try:
        sort_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "sort-selected"))
        )
        sort_element.click()

        sort_option = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"ul.sort-value li[data-sorttype='{sort_param}']"))
        )
        driver.execute_script("arguments[0].click();", sort_option)  # JS click (more reliable)
        time.sleep(3)
    except Exception as e:
        print("Sorting not applied:", e)

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    product_cards = driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-description")
    item_list = []

    for card in product_cards:
        try:
            product_title = card.find_element(By.CLASS_NAME, "product-title").text
            product_link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            product_price = card.find_element(By.CSS_SELECTOR, "span.product-price").text
            try:
                product_reviews = card.find_element(By.CSS_SELECTOR, "p.product-rating-count").text
            except:
                product_reviews = "No reviews"

            item_list.append({
                "product_title": product_title,
                "product_link": product_link,
                "product_price": product_price,
                "product_reviews": product_reviews
            })

        except Exception as e:
            print("Skipping a card due to error:", e)
            continue

    with open(f"data_for_{user_ip}.json", "w", encoding="utf-8") as f:
        json.dump(item_list, f, indent=4, ensure_ascii=False)

    print(f"Scraping completed for '{user_ip}'! Extracted {len(item_list)} products.")
    driver.quit()

else:
    print("Please enter your choice...")
