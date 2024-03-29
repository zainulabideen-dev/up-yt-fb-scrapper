import time
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from os.path import exists

delay = 5
minDelay = 2
pgCount = 0

# fb credentials
email = "email"
password = "password"

# csv col
colPagesUrl = []
colPagesTitle = []
colPagesCat = []
colProfileName = []
colProfileUrl = []
colGender = []
colCheckedProfiles = []
colCheckedPosts = []

# final csv col
f_colPagesUrl = []
f_colPagesTitle = []
f_colPagesCat = []
f_colProfileName = []
f_colProfileUrl = []
f_colGender = []


def array_without_nan(array):
    new_array = []
    for each in array:
        if str(each) != "nan":
            new_array.append(str(each).strip())
    return new_array


def array_with_strip(array):
    new_array = []
    for each in array:
        new_array.append(str(each).strip())
    return new_array


def clear_arrays():
    # clear post arrays
    colPagesUrl.clear()
    colPagesTitle.clear()
    colPagesCat.clear()
    colProfileName.clear()
    colProfileUrl.clear()
    colGender.clear()
    colCheckedProfiles.clear()

    # clear final output arrays
    f_colProfileName.clear()
    f_colGender.clear()
    f_colProfileUrl.clear()
    f_colPagesTitle.clear()
    f_colPagesCat.clear()
    f_colPagesUrl.clear()


def _scrap_pages(url, profileUrl, profileName, gender, driver, count):
    if count > 15:
        print("=> Quiting Chrome Re Start")
        driver.quit()
        read_json()

    time.sleep(delay)
    print("=> scraping page URL: " + url.replace("https://www.facebook.com/", ""))
    pageCategory = "UnOfficialPage"
    pageTitle = "None"

    driver.get(url)

    try:
        time.sleep(delay)
        html = driver.find_element(by=By.XPATH, value='//div[@class="x1e56ztr x1xmf6yo"]').get_attribute('innerHTML')
        soup = bs(html, 'html.parser')
        pageTitle = soup.find("h1").getText()
    except:
        pass

    try:
        time.sleep(delay)
        html = driver.find_element(by=By.XPATH, value='//div[@class="x1yztbdb"]').get_attribute('innerHTML')
        soup = bs(html, 'html.parser')
        pageName = soup.find_all("span")
        for each in pageName:
            if "page" in each.getText().lower():
                pageCategory = each.getText().replace("Â", "")

    except:
        print("=> page not exist. moving on next Url..")
        pass

    f_colPagesUrl.append(url)
    f_colPagesTitle.append(pageTitle.replace("Â", ""))
    f_colPagesCat.append(pageCategory)
    f_colProfileName.append(profileName)
    f_colProfileUrl.append(profileUrl)
    f_colGender.append(gender)
    print("--- page and profile info ---")
    print("Profile Name: " + profileName)
    print("Gender: " + str(gender))
    print("Page Title: " + pageTitle.replace("Â", ""))
    print("Page Category: " + pageCategory)

    name_dict = {
        'profileName': f_colProfileName,
        'gender': f_colGender,
        'profileUrl': f_colProfileUrl,
        'Title': f_colPagesTitle,
        'Page': f_colPagesCat,
        'pageLink': f_colPagesUrl,
    }
    df = pd.DataFrame(name_dict)
    df.to_csv('output/final-output.csv')
    print('=> csv created - updated...')


def chart(driver):
    match_results = []

    # scrap pages
    profile_links_list = []
    pages_url_list = []
    profile_name_list = []
    gender_list = []

    print("== Checking peoples are interested in same page. Creating chart csv file ===")
    if exists('output/profile-pages.csv'):
        df = pd.read_csv('output/profile-pages.csv')
        for i in range(len(df['pages_url'])):
            match_page = str(df['pages_url'][i]).lower()
            current_profile_links = str(df['profile_links'][i]).lower()
            current_pages_url = str(df['pages_url'][i]).lower()
            current_profile_name = str(df['profile_name'][i]).lower()
            current_gender = str(df['gender'][i]).lower()

            # chart csv fields
            chart_pages = []
            chart_names = []
            chart_prof_links = []
            for p in range(len(df['pages_url'])):
                page = str(df['pages_url'][p]).lower()
                profile_name = df['profile_name'][p]
                profile_link = df['profile_links'][p]
                if page == match_page:
                    chart_pages.append(match_page)
                    chart_names.append(profile_name)
                    chart_prof_links.append(profile_link)

            if len(chart_pages) > 1:
                profile_links_list.append(current_profile_links)
                pages_url_list.append(current_pages_url)
                profile_name_list.append(current_profile_name)
                gender_list.append(current_gender)

                res_dict = {
                    "page": chart_pages[0],
                    "count": len(chart_names),
                    "profiles": ','.join(chart_names),
                    "profileUrl": ','.join(chart_prof_links)
                }
                match_results.append(res_dict)

        if len(match_results) > 0:
            df = pd.DataFrame(match_results)
            df.to_csv('output/chart.csv', index=False)
            print("=> Successfully find out peoples who are interested in same pages. Pleas check chart.csv file..")

            print("=> find " + str(len(match_results)) + " match results")
            print("=> find " + str(len(profile_links_list)) + " pages")

            print("=== Now scrapping those same pages and creating final output csv file ===")

            count = 0
            for i in range(len(profile_links_list)):
                page_url = pages_url_list[i]
                if page_url in f_colPagesUrl:
                    print("=> Skip post Url: "+str(pages_url_list[i]))
                else:
                    _scrap_pages(page_url, profile_links_list[i], profile_name_list[i], gender_list[i], driver, count)
                    count += 1
        else:
            print("=> No matching urls found. No same pages interested people found ...")


def check_profiles(url, driver, page):
    print("Checked profile: " + str(page))
    if page > 15:
        print("=> Quiting Chrome Re Start")
        driver.quit()
        read_json()

    cpl = str(url).split("?")[0]
    if cpl in colCheckedProfiles:
        print("=> skip profile: " + cpl)
        return

    pages_links = []
    gender = "None"
    profile_name = ""

    time.sleep(delay)
    print("=> scraping profile URL: " + cpl)
    driver.get(url)

    try:
        time.sleep(delay)
        driver.find_element(By.XPATH, "//span[text()='About']").click()
        time.sleep(minDelay)
        driver.find_element(By.XPATH, "//span[text()='Contact and basic info']").click()
        time.sleep(minDelay)
        contact_info_div = driver.find_element(by=By.XPATH, value='//div[@class="x1iyjqo2"]').get_attribute('innerHTML')
        soup = bs(contact_info_div, 'html.parser')
        gender_span = soup.find("span", {
            "class": "x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x1f6kntn xvq8zen xo1l8bm xzsf02u x1yc453h"}).getText()
        if gender_span.lower() in ["male", "female"]:
            gender = gender_span
    except:
        pass

    try:
        time.sleep(delay)
        profile_div = driver.find_element(by=By.XPATH,
                                         value='//div[@class="x6s0dn4 x78zum5 xvrxa7q x9w375v xxfedj9 x1roke11 x1es02x0"]').get_attribute(
            'innerHTML')
        soup = bs(profile_div, 'html.parser')
        profile_name = soup.find("span", {
            "class": "x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1ill7wo x1g2y4wz x579bpy xjkpybl x1xlr1w8 xzsf02u x1yc453h"}).getText()
        driver.find_element(by=By.XPATH,
                            value='//div[@class="x6s0dn4 x9f619 x78zum5 x2lah0s x1hshjfz x1n2onr6 xng8ra x1pi30zi x1swvt13"]').click()
    except Exception as error:
        print("=> more info not exist...")
        pass

    try:
        time.sleep(delay)
        driver.find_element(By.XPATH, "//span[text()='Likes']").click()
        for f in range(5):
            time.sleep(3)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

        likes_html = driver.find_element(by=By.XPATH, value='//div[@class="x78zum5 x1q0g3np x1a02dak"]').get_attribute(
            'innerHTML')
        soup = bs(likes_html, 'html.parser')
        like_div = soup.find_all("div", {"class": "x9f619 x1r8uery x1iyjqo2 x6ikm8r x10wlt62 x1n2onr6"})
        for div in like_div:
            aTag = div.find("a")["href"]
            pages_links.append(aTag)

    except Exception as error:
        print("=> likes not exist...")

    print("=> find " + str(len(pages_links)) + " pages")
    for pages in pages_links:
        cpl = str(url).split("?")[0]
        colProfileUrl.append(cpl)
        colPagesUrl.append(pages)
        colProfileName.append(profile_name)
        colGender.append(gender)

    # create or update csv
    print("=> data recorded in csv file")
    name_dict = {
        'profile_links': colProfileUrl,
        'pages_url': colPagesUrl,
        'profile_name': colProfileName,
        'gender': colGender,
    }
    df = pd.DataFrame(name_dict)
    df.to_csv('output/profile-pages.csv')


def _check_post(url, data, driver):
    interested_peoples = []
    print("=> scraping post URL: " + url.replace("https://www.facebook.com/", ""))
    time.sleep(delay)
    driver.get(url)

    try:
        time.sleep(delay)
        driver.find_element(by=By.XPATH, value='//div[@aria-label="Comment"]').click()
    except Exception as error:
        pass

    time.sleep(delay)
    driver.find_element(by=By.XPATH, value='//div[@class="x9f619 x1n2onr6 x1ja2u2z x6s0dn4 x3nfvp2 xxymvpz"]').click()
    time.sleep(delay)
    driver.find_element(By.XPATH, "//span[text()='All comments']").click()
    time.sleep(delay)

    load_more_comments = True
    while load_more_comments:
        try:
            time.sleep(delay)
            driver.find_element(By.XPATH, "//span[text()='View more comments']").click()
            print("=> loading more comments...")
        except Exception as error:
            load_more_comments = False
            print("=> all comments loaded...")

    comments = None
    try:
        comments = driver.find_element(by=By.XPATH, value='//div[@class="x1gslohp"]').get_attribute('innerHTML')
    except Exception as error:
        comments = driver.find_element(by=By.XPATH, value='//div[@class="x1pi30zi x1swvt13"]').get_attribute(
            'innerHTML')

    soup = bs(comments, 'html.parser')
    com_div = soup.find_all("div", {"class": "x1n2onr6 x1swvt13 x1iorvi4 x78zum5 x1q0g3np x1a2a7pz"})

    for each in com_div:
        try:
            com_div = each.find("div", {"class": "xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs"}).getText()
            exist = False
            for key in data["keywords"]:
                if key.lower() in str(com_div).lower():
                    exist = True

            if exist:
                prof_div = each.find("div", {
                    "class": "xqcrz7y x14yjl9h xudhj91 x18nykt9 xww2gxu x1lliihq x1w0mnb xr9ek0c x1n2onr6"})
                prof_link = prof_div.find("a")["href"]
                if prof_link not in interested_peoples:
                    interested_peoples.append(prof_link)
        except Exception as e:
            pass

    print("=> find " + str(len(interested_peoples)) + " interested peoples")
    filter_peoples = []
    for ppl in interested_peoples:
        cpl = str(ppl).split("?")[0]
        if cpl in colCheckedProfiles:
            print("=> skip: " + str(cpl))
            colCheckedProfiles.append(cpl)
        else:
            filter_peoples.append(ppl)

    print("=> " + str(len(filter_peoples)) + " filter peoples")

    page = 0
    for filterPpl in filter_peoples:
        cpl = str(filterPpl).split("?")[0]
        check_profiles(cpl, driver, page)
        # create checked profile
        colCheckedProfiles.append(cpl)
        name_dict = {'link': colCheckedProfiles}
        df = pd.DataFrame(name_dict)
        df.to_csv('output/checked-profile.csv')
        page += 1


def _login(data, driver):
    print("=> signing into facebook...")
    time.sleep(delay)
    (driver.find_element(by=By.XPATH, value='//input[@placeholder="Email address or phone number"]')
     .send_keys(data["email"]))
    driver.find_element(by=By.XPATH, value='//input[@placeholder="Password"]').send_keys(data["password"])
    driver.find_element(by=By.XPATH, value='//button[@data-testid="royal_login_button"]').click()

    for post in data["postList"]:
        _check_post(post, data, driver)

    print("=== All Posts are scrapped successfully ===")
    chart(driver)


def read_json():
    clear_arrays()
    df = pd.read_csv('config.csv')
    data = {
        "email": email,
        "password": password,
        "keywords": array_without_nan(df["keywords"]),
        "postList": array_without_nan(df["postList"]),
        "profile": array_without_nan(df["profile"])
    }

    if exists('output/final-output.csv'):
        df = pd.read_csv('output/final-output.csv')
        f_colProfileName.extend(array_with_strip(df["profileName"]))
        f_colGender.extend(array_with_strip(df["gender"]))
        f_colProfileUrl.extend(array_with_strip(df["profileUrl"]))
        f_colPagesTitle.extend(array_with_strip(df["Title"]))
        f_colPagesCat.extend(array_with_strip(df["Page"]))
        f_colPagesUrl.extend(array_with_strip(df["pageLink"]))

    if exists('output/checked-profile.csv'):
        df = pd.read_csv('output/checked-profile.csv')
        colCheckedProfiles.extend(array_with_strip(df["link"]))

    if exists('output/profile-pages.csv'):
        df = pd.read_csv('output/profile-pages.csv')
        colProfileUrl.extend(array_with_strip(df["profile_links"]))
        colPagesUrl.extend(array_with_strip(df["pages_url"]))
        colProfileName.extend(array_with_strip(df["profile_name"]))
        colGender.extend(array_with_strip(df["gender"]))

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-notifications')
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.facebook.com/")
    _login(data, driver)

    print("=== script completed successfully ===")


if __name__ == '__main__':
    if email == "fb_email" and password == "fb_password":
        print("=> Please provide your facebook credentials on the top of the script")
    else:
        read_json()
