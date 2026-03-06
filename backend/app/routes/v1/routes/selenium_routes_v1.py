from enum import Enum
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options # Ignoring SSL Hanshake Logs
import chromedriver_autoinstaller
import asyncio
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

router = APIRouter()


# =========================================================
# Settings
# =========================================================

# Chrom driver Setup
chromedriver_autoinstaller.install()

# To ignore SSL Handshake Logs
options = Options()
options.add_argument("--log-level=3")
options.add_argument("--disable-logging")
options.add_argument("--ignore-certificate-errors")

# CssSelectorValue
class CssSelectorValue(Enum):
    CSS_SELECTOR_SEARCH_BUTTON1 = "#MainSearch" # Dev Mode (F12) -> Click the element -> Copy -> Copy selector
    CSS_SELECTOR_SEARCH_BUTTON2 = "#shopify-section-sections--21066908368943__header > m-header > div.m-header__wrapper.header__wrapper > header.sf-header__mobile.m-header__mobile.container-fluid.m\:flex.m\:items-center.m-gradient.m-color-default > div.m-header__mobile-right.m\:w-3\/12.m\:flex.m\:flex-1.m\:justify-end > m-search-popup"
    CSS_SELECTOR_TABS = '#MainMenu'
    CSS_SELECTOR_SHOP_BY_CATEGORY = '#shopify-section-template--21066907320367__spg_shop_by_slides_LrApww > section > div > div.sq--section__header.sq--section__header--desktop-theme-header__dark.sq--section__header--desktop-alignment-header__left.sq--section__header--mobile-theme-header__dark.sq--section__header--mobile-alignment-header__center > div'
    CSS_SELECTOR_SEARCH_TAB = "#m-form-search > input.form-field.form-field--input"
    CSS_SELECTOR_SEARCH_MAIN = '#shopify-section-template--21066908303407__main > section > div:nth-child(2) > div > form > input.form-field.form-field--input.m-search--form-input'


# =========================================================
# API Response
# =========================================================

class SeleniumDemonstrateResponse(BaseModel):
    status: str


@router.get("/demonstrate", response_model=SeleniumDemonstrateResponse)
async def demonstrate():
    try:
        browser_close_timeout = 10
        driver = webdriver.Chrome(options=options)

        # Step 1 - Open the page (Browser Navigation Tool)
        driver.get('https://www.google.com/')
        page_title = driver.title
        current_url = driver.current_url
        print(f'>>> Entered Page: Title: {page_title}, Current Url: {current_url}')

        await asyncio.sleep(2) # Delay
        driver.get("https://www.spigen.com/")
        page_title = driver.title
        current_url = driver.current_url
        print(f'>>> Entered Page: Title: {page_title}, Current Url: {current_url}')

        await asyncio.sleep(2) # Delay
        driver.back() # Backward
        page_title = driver.title
        current_url = driver.current_url
        print(f'>>> Backward Page: Title: {page_title}, Current Url: {current_url}')

        await asyncio.sleep(2) # Delay
        driver.forward() # Forward
        page_title = driver.title
        current_url = driver.current_url
        print(f'>>> Forward Page: Title: {page_title}, Current Url: {current_url}')

        await asyncio.sleep(2) # Delay
        driver.refresh() # Refresh
        page_title = driver.title
        current_url = driver.current_url
        print(f'>>> Refresh Page: Title: {page_title}, Current Url: {current_url}')


        # Step 2 - Get CSS Selector
        item_search_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, CssSelectorValue.CSS_SELECTOR_SEARCH_BUTTON1.value))
        ) # Wait til the page comes out
        if not (item_search_button.is_displayed() and item_search_button.is_enabled()):
            item_search_button = driver.find_element(By.CSS_SELECTOR, CssSelectorValue.CSS_SELECTOR_SEARCH_BUTTON2.value)

        item_tabs = driver.find_element(By.CSS_SELECTOR, CssSelectorValue.CSS_SELECTOR_TABS.value)
        item_shop_by_category = driver.find_element(By.CSS_SELECTOR, CssSelectorValue.CSS_SELECTOR_SHOP_BY_CATEGORY.value)


        # Action (Get Text, Scroll, Button Click)
        await asyncio.sleep(1) # Delay
        print(f'>> item_tabs: {item_tabs.text if item_tabs and item_tabs.text else "Nothing due to the responsible web"}')
        driver.execute_script("arguments[0].scrollIntoView();", item_shop_by_category)
        print(f'>> item_shop_by_category: {item_shop_by_category.text}')


        # Click Button
        await asyncio.sleep(1) # Delay
        driver.execute_script("window.scrollTo(0, 0);")
        await asyncio.sleep(1) # Delay
        if item_search_button.is_displayed() and item_search_button.is_enabled():
            item_search_button.click()

        # Step 3 - Search
        await asyncio.sleep(1) # Delay
        item_search_tab = driver.find_element(By.CSS_SELECTOR, CssSelectorValue.CSS_SELECTOR_SEARCH_TAB.value)
        item_search_tab.send_keys("Tesla")
        print(f'>> Searched for Tesla')
        await asyncio.sleep(1)
        item_search_tab.send_keys(Keys.ENTER) # Enter button
        
        item_search_main = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, CssSelectorValue.CSS_SELECTOR_SEARCH_MAIN.value))
        ) # Wait til the page comes out
        message_developer_info = 'Developed By Kyungtaek Lim a.k.a Jonas'
        print(f'>> Developer Info')
        for char in message_developer_info:
            item_search_main.send_keys(char)
            await asyncio.sleep(0.1)  # 0.1s interval
        await asyncio.sleep(2)
        item_search_main.clear()

        # Step 4 - Browser closing notice
        await asyncio.sleep(1)
        print(f'>> Browser closing notice')
        item_search_main.send_keys(f"The browser will automatically close in {browser_close_timeout} seconds.")

        await asyncio.sleep(browser_close_timeout)
        # input() # Pause

        print(f'>> Closing browser')
        # driver.close() # Close Tab    
        driver.quit() # Close Browser

        return SeleniumDemonstrateResponse(
            status="Selenium demonstated successfully"
        )
    
    except:
        raise HTTPException(status_code=500, detail="Internal error!")