import pandas as pd
import time
import os
import re

from humanfriendly import format_timespan
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def Amazon_Login():
    lnk = 'https://sellercentral.amazon.com/gp/sign-in/logout.html/ref=xx_logout_dnav_xx'
    driver.get(lnk)

    lnk = f'https://sellercentral.amazon.com/signin'
    driver.get(lnk)

    email = 'dean.rusinov@gmail.com'
    password = '155793Ko!'

    css = driver.find_element_by_css_selector

    try:
        acc_field = css('input[type="email"]')
        acc_field.send_keys(str(email))
    except:
        print('Could not enter email!')

    acc_field = css('input[type="password"]')
    acc_field.send_keys(str(password))

    keep_signed = css('input[name="rememberMe"]')
    keep_signed.click()
    sign_in = css('input[id="signInSubmit"]')
    sign_in.click()

    WebDriverWait(driver, 100).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'div[class="gw-cols"]')))
    print('----- Successfully logged in Amazon Seller Central! -----')


def get_asins(upc_e, mpn, brand):
    global count
    # count = 0

    file_header = 'Link,ASIN,Item name,UPC_A,EAN_A,Sales rank,UPC_E\n'

    with open(product_links_dir, "w", encoding="ISO-8859-1") as f:
        f.write(file_header)

    lnk = (f'https://sellercentral.amazon.com/product-search/search?q={upc_e}&ref_=xx_catadd_dnav_home')
    driver.get(lnk)

    try:  # try to catch the error
        internal_error_block = WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((
            By.CLASS_NAME, 'h4')))  # driver.find_element_by_class_name('h4')
        error_text = internal_error_block.text
        print(error_text)

        if 'Internal Error' in error_text:
            print('AMAZON PAGE ERROR.. Zzz -3min-')
            time.sleep(180)
            Amazon_Login()
        else:
            print('Internal error detected: ', ('Internal Error' in error_text))
    except: pass

    WebDriverWait(driver, 15).until(EC.presence_of_element_located(    # Check for 0 found
        (By.XPATH, '//div[@class="results-header"]')))
    zero_search = driver.find_element_by_xpath('//div[@class="results-header"]')
    zero_search = zero_search.text.strip()
    zero_search = re.sub('[^A-Za-z0-9 -]+', '', zero_search).strip()

    if 'Displaying 0-0 of 0 results' in zero_search:
        zero_search = True
    else:
        zero_search = False

    if zero_search == False:  # When item was found
        try:
            search_module(upc_e)
        except:
            product_links = []

            href = asin = upc_a = ean_a = sales_rank = '----------'
            i_name = 'ZERO SEARCH UPC ERR'

            product_links.append(href)
            product_links.append(asin)
            product_links.append(i_name)
            product_links.append(upc_a)
            product_links.append(ean_a)
            product_links.append(sales_rank)
            product_links.append('?' + str(upc_e))
            product_links_write = (',').join(product_links)

            with open(product_links_dir, 'a', encoding="ISO-8859-1", newline='') as f:
                f.write(product_links_write)
                f.write('\n')

            product_links.clear()
            print('zero_search == True sequence has broken')

    else:  # Check if brand or mpn 'Does not apply'

        if 'doesnotapply' in brand.lower().replace(' ', '') or 'doesnotapply' in mpn.lower().replace(' ', ''):
            product_links = []

            href = asin = upc_a = ean_a = sales_rank = '----------'
            i_name = 'BRAND / MPN: Does not apply'

            product_links.append(href)
            product_links.append(asin)
            product_links.append(i_name)
            product_links.append(upc_a)
            product_links.append(ean_a)
            product_links.append(sales_rank)
            product_links.append('?' + str(upc_e))
            product_links_write = (',').join(product_links)

            with open(product_links_dir, 'a', encoding="ISO-8859-1", newline='') as f:
                f.write(product_links_write)
                f.write('\n')

        else:
            if '&' in brand:
                brand = brand.replace('&', '%26')
            if '&' in mpn:
                mpn = mpn.replace('&', '%26')

            lnk = f'https://sellercentral.amazon.com/product-search/search?q={brand}+{mpn}&ref_=xx_catadd_dnav_home'
            driver.get(lnk)

            if '%26' in brand:
                brand = brand.replace('%26', '&')
            if '%26' in mpn:
                mpn = mpn.replace('%26', '&')

            try:  # try to catch the error
                internal_error_block = WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((
                                                    By.CLASS_NAME, 'h4')))  # driver.find_element_by_class_name('h4')
                error_text = internal_error_block.text
                print(error_text)

                if 'Internal Error' in error_text:
                    print('AMAZON PAGE ERROR.. Zzz -3min-')
                    time.sleep(180)
                    Amazon_Login()
                else:
                    print('Internal error detected: ', ('Internal Error' in error_text))
            except: pass

            WebDriverWait(driver, 15).until(EC.presence_of_element_located(    # Check for 0 found
                (By.XPATH, '//div[@class="results-header"]')))
            zero_search = driver.find_element_by_xpath('//div[@class="results-header"]')
            zero_search = zero_search.text.strip()
            zero_search = re.sub('[^A-Za-z0-9 -]+', '', zero_search).strip()

            if 'Displaying 0-0 of 0 results' in zero_search:
                zero_search = True

                href = asin = upc_a = ean_a = sales_rank = '----------'
                i_name = 'NO RESULTS'

                product_links = [href, asin, i_name, upc_a, ean_a, sales_rank, ('?' + upc_e)]
                product_links_write = (',').join(product_links)

                with open(product_links_dir, 'a', encoding="ISO-8859-1", newline='') as f:
                    f.write(product_links_write)
                    f.write('\n')

                product_links.clear()

            else:
                zero_search = False

            if zero_search == False:  # When item was found
                try:
                    search_module(upc_e)
                except:
                    product_links = []

                    href = asin = upc_a = ean_a = sales_rank = '----------'
                    i_name = 'ZERO SEARCH BRAND/MPN ERR'

                    product_links.append(href)
                    product_links.append(asin)
                    product_links.append(i_name)
                    product_links.append(upc_a)
                    product_links.append(ean_a)
                    product_links.append(sales_rank)
                    product_links.append('?' + str(upc_e))
                    product_links_write = (',').join(product_links)

                    with open(product_links_dir, 'a', encoding="ISO-8859-1", newline='') as f:
                        f.write(product_links_write)
                        f.write('\n')

                    product_links.clear()
                    print('zero_search == True sequence has broken')


def search_module(upc_e):
    elements = driver.find_elements_by_class_name('row-box')
    global asin

    c = 0
    c2 = 0

    try:  # Click 'Show variations on each'
        show_var_btn = driver.find_elements_by_xpath("//div[@class='expander link flex-end']")

        for each in show_var_btn:
            each.click()
            time.sleep(0.5)

            SCROLL_PAUSE_TIME = 0.5

            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

    except:
        print('EXCEPTION TO CLICK VARIATIONS')

    product_links = []

    elements_var = driver.find_elements_by_class_name('variation-row')

    for e in elements:  # For the elements without variation

        elems = e.text

        try:
            href = e.get_attribute('innerHTML')
            href = href.split('href="')[1].split('" variant')[0].strip()
            product_links.append(href)

            asin = href.split('/dp/')[1].strip()
            product_links.append('?' + str(asin))
        except:
            print('No results')

        try:
            i_name = e.find_element_by_css_selector('kat-link[variant="link"]')
            i_name = i_name.text.replace(',', '').strip()
            i_name = re.sub('[^A-Za-z0-9 &\"\']+', '', i_name).strip()
            product_links.append(i_name)
        except:
            i_name = '----------'
            product_links.append(i_name)

        try:
            upc_a = elems.split('UPC:')[1].strip().split('\n')[0].strip()
            product_links.append('?' + str(upc_a))
        except:
            upc_a = '----------'
            product_links.append(str(upc_a))

        try:
            ean_a = elems.split('EAN:')[1].strip().split('\n')[0].strip()
            product_links.append('?' + str(ean_a))
        except:
            ean_a = '----------'
            product_links.append(str(ean_a))

        try:
            sales_rank = elems.split('Sales rank:')[1].strip().split('\n')[0].replace(',', '').strip()
            product_links.append(sales_rank)
        except:
            sales_rank = '9999999'
            product_links.append(str(sales_rank))

        product_links.append('?' + str(upc_e))
        product_links_write = (',').join(product_links)

        with open(product_links_dir, 'a', encoding="ISO-8859-1", newline='') as f:
            f.write(product_links_write)
            f.write('\n')

        product_links.clear()
        c += 1

    for e in elements_var:  # For the elements with variation

        elems = e.text

        try:

            href = e.get_attribute('innerHTML')
            href = href.split('href="')[1].split('" variant')[0].strip()

            product_links.append(href)

            asin = href.split('/dp/')[1].strip()
            product_links.append('?' + str(asin))
        except:
            print('No results')

        try:
            i_name = e.find_element_by_css_selector('kat-link[variant="link"]')
            i_name = i_name.text.replace(',', '').strip()
            i_name = re.sub('[^A-Za-z0-9 &\"\']+', '', i_name).strip()
            product_links.append(i_name)
        except:
            i_name = '----------'
            product_links.append(i_name)

        try:
            upc_a = elems.split('UPC:')[1].strip().split('\n')[0].strip()
            product_links.append('?' + str(upc_a))
        except:
            upc_a = '----------'
            product_links.append(str(upc_a))

        try:
            ean_a = elems.split('EAN:')[1].strip().split('\n')[0].strip()
            product_links.append('?' + str(ean_a))
        except:
            ean_a = '----------'
            product_links.append(str(ean_a))

        try:
            sales_rank = elems.split('Sales rank:')[1].strip().split('\n')[0].replace(',', '').strip()
            product_links.append(sales_rank)
        except:
            sales_rank = '9999999'
            product_links.append(str(sales_rank))

        product_links.append('?' + str(upc_e))
        product_links_write = (',').join(product_links)

        with open(product_links_dir, 'a', encoding="ISO-8859-1", newline='') as f:
            f.write(product_links_write)
            f.write('\n')

        product_links.clear()
        c2 += 1


def top_asinTABLE(upc_e):
    count = 0
    file_w = []
    perm_req = True

    with open(product_links_dir, 'r', encoding="ISO-8859-1") as f:
        data = [line.replace('\n', '') for line in f]

        for line in data:
            if count == 0:
                count += 1
            else:
                while perm_req == True:

                    # print('My line is: ',line,'------\n')
                    row_values = line.strip().split(',')

                    print('Link: ' + row_values[0])
                    print('ASIN: ' + row_values[1].replace('?', '').replace(' ', ''))
                    print('Item name: ' + row_values[2])
                    print('UPC_A: ' + row_values[3].replace('?', ''))
                    print('EAN_A: ' + row_values[4].replace('?', ''))
                    print('Sales rank: ' + row_values[5])

                    link_w = row_values[0].strip()
                    asin_w = row_values[1].replace('?', '').replace(' ', '').strip()
                    iName_w = row_values[2].strip()
                    upc_w = row_values[3].strip()
                    ean_w = row_values[4].strip()
                    salesRnk_w = row_values[5].strip()

                    if 'NO RESULTS' in str(iName_w) or 'BRAND / MPN: Does not apply' in str(iName_w) or 'ZERO SEARCH BRAND/MPN ERR' in str(iName_w):
                        if count == len(data) - 1:
                            file_w = [link_w, asin_w, iName_w, upc_w, ean_w, salesRnk_w, (store_e + '?' + upc_e)]
                            file_w_clear = (',').join(file_w)

                            with open(top_asins_dir, "a", encoding="ISO-8859-1", newline='') as w:
                                w.write(file_w_clear)
                                w.write('\n')

                            file_w.clear()
                            break
                        else:
                            count += 1
                            break

                    else:
                        # ------------- CHECK FOR PERM REQ ------------------ #

                        lnk = (f'https://sellercentral.amazon.com/abis/listing/syh?asin={asin_w}&ref_=xx_catadd_dnav_xx#offer')
                        lnk = lnk.replace('\n', '')

                        driver.get(lnk)

                        try:  # try to catch the error
                            internal_error_block = WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((
                                By.CLASS_NAME, 'h4')))  # driver.find_element_by_class_name('h4')
                            error_text = internal_error_block.text
                            print(error_text)

                            if 'Internal Error' in error_text:
                                print('AMAZON PAGE ERROR.. Zzz -3min-')
                                time.sleep(180)
                                Amazon_Login()
                            else:
                                print('Internal error detected: ', ('Internal Error' in error_text))

                        except: pass

                        try:
                            perm_req = WebDriverWait(driver, 0.25).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, '//div[@class="eight wide column no-vertical-margin menu-tab-sctn"]')))

                            perm_req = perm_req.text

                            if 'You need approval to list in this brand.' in perm_req or \
                                    'Sorry, this product is ineligible for Amazon Marketplace selling at this time.' in perm_req or \
                                    'This product has other listing limitations.' in perm_req or \
                                    'You need approval to list in the Video, DVD & Blu-ray category.' in perm_req or \
                                    'You are not approved to list in this product category.' in perm_req or \
                                    'Collectible, Refurbished conditions' in perm_req or \
                                    'You need approval to list in' in perm_req:

                                perm_req = True
                                print('>>>Permission required for this item!<<<\n')

                                if count == len(data) - 1:
                                    iName_w = 'You need approval to list in this brand.'
                                    file_w = ['----------'.strip(), ('?' + str(asin_w)).strip(), iName_w.strip(),
                                              '----------'.strip(), '----------'.strip(), '----------'.strip(),
                                              (store_e + '?' + upc_e).strip()]
                                    file_w_clear = (',').join(file_w)

                                    with open(top_asins_dir, "a", encoding="ISO-8859-1", newline='') as w:
                                        w.write(file_w_clear)
                                        w.write('\n')

                                    file_w.clear()
                                    break
                                else:
                                    count += 1
                                    break

                            else:
                                perm_req = False
                                print('>>>Maybe not allowed?<<<\n')

                        except:
                            perm_req = False
                            print('>>>Allowed to list!<<<\n')

                        # ------------- CHECK FOR PERM REQ ------------------ #

                        if perm_req == False:

                            try:
                                # Item Condition
                                cond_dd = WebDriverWait(driver, 1).until(
                                    EC.presence_of_element_located(
                                        (By.XPATH, ('//kat-dropdown[@id="condition_type"]'))))

                                opt = cond_dd.get_attribute('options')
                                opt = opt.strip()

                                # check if asin is already listed---------------
                                if str(asin_w) in listed_asin_list:
                                    opt = 'Already Listed!'
                                # check if asin is already listed---------------

                                if '{"name":"New","value":"new, new"}' in opt:
                                    # print('There is New condition')

                                    file_w = [link_w, ('?' + str(asin_w)), iName_w, upc_w, ean_w, salesRnk_w,
                                              (store_e + '?' + upc_e)]
                                    file_w_clear = (',').join(file_w)

                                    with open(top_asins_dir, "a", encoding="ISO-8859-1", newline='') as w:
                                        w.write(file_w_clear)
                                        w.write('\n')

                                    file_w.clear()
                                    count += 1
                                    break

                                else:

                                    if opt == 'Already Listed!':
                                        print('----------Already Listed!----------\n')
                                        iName_w = opt  # end of asin listed check
                                        file_w = ['----------'.strip(), ('?' + str(asin_w)).strip(), iName_w.strip(),
                                                  '----------'.strip(), '----------'.strip(), '----------'.strip(),
                                                  (store_e + '?' + upc_e).strip()]
                                        file_w_clear = (',').join(file_w)

                                        with open(top_asins_dir, "a", encoding="ISO-8859-1", newline='') as w:
                                            w.write(file_w_clear)
                                            w.write('\n')

                                        file_w.clear()
                                        break

                                    else:
                                        opt = 'No New condition!'
                                        print('No New condition!\n')

                                    if count == len(data) - 1:
                                        iName_w = opt  # end of asin listed check
                                        file_w = ['----------'.strip(), ('?' + str(asin_w)).strip(), iName_w.strip(),
                                                  '----------'.strip(), '----------'.strip(), '----------'.strip(),
                                                  (store_e + '?' + upc_e).strip()]
                                        file_w_clear = (',').join(file_w)

                                        with open(top_asins_dir, "a", encoding="ISO-8859-1", newline='') as w:
                                            w.write(file_w_clear)
                                            w.write('\n')

                                        file_w.clear()
                                        break
                                    else:
                                        count += 1
                                        perm_req = True
                                        break

                            except:
                                iName_w = 'Maybe not allowed? (No condition drop-down menu!)'
                                file_w = ['----------'.strip(), ('?' + str(asin_w)).strip(), iName_w.strip(),
                                          '----------'.strip(), '----------'.strip(), '----------'.strip(),
                                          (store_e + '?' + upc_e).strip()]
                                file_w_clear = (',').join(file_w)

                                with open(top_asins_dir, "a", encoding="ISO-8859-1", newline='') as w:
                                    w.write(file_w_clear)
                                    w.write('\n')
                                continue

                        else:
                            print('Listing NOT possible...')
                            if count == len(data) - 1:
                                iName_w = 'Listing NOT possible...'
                                file_w = ['----------'.strip(), ('?' + str(asin_w)).strip(), iName_w.strip(),
                                          '----------'.strip(), '----------'.strip(), '----------'.strip(),
                                          (store_e + '?' + upc_e).strip()]
                                file_w_clear = (',').join(file_w)

                                with open(top_asins_dir, "a", encoding="ISO-8859-1", newline='') as w:
                                    w.write(file_w_clear)
                                    w.write('\n')

                                file_w.clear()
                                break
                            else:
                                count += 1
                                break


# --------------------------------- END FUNCTION -----------------------------#


# --------------------------------- START CODE -------------------------------#
sys_username = str(os.getenv('username'))
input_id_dir = r'C:\Users\{0}\Google Drive\Python_Shared\In_Out_{0}\ASIN_grabber\Input IDs.csv'.format(sys_username)
top_asins_dir = r'C:\Users\{0}\Google Drive\Python_Shared\In_Out_{0}\ASIN_grabber\TOP_ASINs.csv'.format(sys_username)
ta_no_dupl_dir = r'C:\Users\{0}\Google Drive\Python_Shared\In_Out_{0}\ASIN_grabber\TOP_ASINs_NO_Duplicates.csv'.format(
                                                                                                        sys_username)
product_links_dir = r'C:\Users\{0}\Google Drive\Python_Shared\In_Out_{0}\ASIN_grabber\Product links.csv'.format(
                                                                                                        sys_username)

options = webdriver.ChromeOptions()
options.add_argument(r'user-data-dir=C:\\Users\\{0}\\AppData\\Local\\Google\\Chrome\\User Data\\Profile {0}'.format(
                                                                                                        sys_username))

driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
driver.implicitly_wait(1)

driver.set_window_size(960, 1080)
driver.set_window_position(960, 0, windowHandle='current')

output_del = input('Do you want to delete the output file? [y/n]:   ')
print('\n')

file_header = 'Link,ASIN,Item name,UPC_A,EAN_A,Sales rank,UPC_E\n'

if 'y' in str(output_del) or 'Y' in str(output_del):
    with open(top_asins_dir, "w", encoding="ISO-8859-1") as f:
        f.write(file_header)

Amazon_Login()

timeout = 10
l_count = 0

global count
count = 0

# ------------LISTED ASINS FILE------------#
listed_dir = str(r'C:\Users\{}\Google Drive\Python_Shared\DO_NOT_DELETE\Listed.csv'.format(sys_username))

listed_data_frame = pd.read_csv(listed_dir, 'r', encoding="ISO-8859-1")
listed_data = listed_data_frame.values

global listed_asin_list
listed_asin_list = []

for row in listed_data:
    asin = str(row[0])
    listed_asin_list.append(asin)
# ------------LISTED ASINS FILE------------#

with open(top_asins_dir, 'r', encoding="ISO-8859-1") as f:
    data_out = [line for line in f]
    data_out = len(data_out)

with open(input_id_dir, 'r', encoding="ISO-8859-1") as f:
    data = [line.replace('\n', '') for line in f]
    for line in data:
        if l_count == 0 or l_count < data_out:
            t0 = time.time()
            l_count += 1
        else:
            try:  # try to catch the error
                internal_error_block = WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((
                                                    By.CLASS_NAME, 'h4')))  # driver.find_element_by_class_name('h4')
                error_text = internal_error_block.text
                print(error_text)
                if 'Internal Error' in error_text:
                    print('AMAZON PAGE ERROR.. Zzz -3min-')
                    time.sleep(180)
                    Amazon_Login()
                else:
                    print('Internal error detected: ', ('Internal Error' in error_text))
            except: pass

            if l_count % 100 == 0:  # After how many checks you want to re-log ?
                print('Amazon re-log initiated!')
                Amazon_Login()
            else: pass

            print('Row: ' + str(l_count) + ' of ' + str(len(data) - 1))
            row_values = line.strip().split(',')

            upc_e = row_values[0].split('?')[1]
            store_e = row_values[0].split('?')[0]

            try:
                brand_mpn = row_values[1].split('?')
                brand = brand_mpn[1]
                mpn = brand_mpn[2]
            except:
                brand = ''
                mpn = ''

            print('Item with: ')
            print('UPC_E: ' + upc_e)
            print('MPN: ' + mpn)
            print('BRAND: ' + brand)

            get_asins(upc_e, mpn, brand)

            df = pd.read_csv(product_links_dir, encoding="ISO-8859-1")
            df_sorted = df.sort_values(by=['Sales rank'])
            df_sorted.to_csv(product_links_dir, index=False)

            top_asinTABLE(upc_e)

            l_count += 1
            t1 = time.time()

            total_n = t1 - t0

            print('Time running so far: ' + str(
                format_timespan(round(total_n, 0))))  # str(round(total_n, 2)))
            print('---------------NEXT ITEM---------------')

data_frame = pd.read_csv(top_asins_dir, encoding="ISO-8859-1").drop_duplicates(subset='UPC_E', keep='first',
                                                                               inplace=False)
data_frame.to_csv(ta_no_dupl_dir, index=False, encoding='ISO-8859-1')

time.sleep(5)
driver.quit()

try:
    os.remove(top_asins_dir)
    os.remove(product_links_dir)
    time.sleep(1)
    os.rename(ta_no_dupl_dir, top_asins_dir)
except:
    pass

    # --------------------------------- END CODE ---------------------------------#
