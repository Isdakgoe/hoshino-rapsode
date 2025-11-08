
import pandas as pd
import streamlit as st
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import datetime


cols = st.columns(3)
st.markdown("###")
place_progress = st.empty()
path_loading = "http://goe-studio.staba.jp/templates/loading2.gif"


@st.cache(hash_funcs={"_thread.RLock": lambda _: None}, allow_output_mutation=True)
def get_players(html):
    soup = BeautifulSoup(html, "lxml")
    td_list = soup.find_all("td", {"class": "td-style-highlight"})
    dic_player = {td.text: td.find("a")["href"].split("/")[-1] for td in td_list}
    return dic_player


@st.cache(hash_funcs={"_thread.RLock": lambda _: None}, allow_output_mutation=True)
def get_dates(driver, page_player):
    driver.get(page_player)
    st.session_state.wait.until(EC.presence_of_all_elements_located)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(5)
    st.session_state.wait.until(EC.presence_of_all_elements_located)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    span_list = soup.find_all("span", {"class": "session-date"})
    dates = [v.text for v in span_list]
    return dates


@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--proxy-server="direct://"')
    options.add_argument('--proxy-bypass-list=*')
    options.add_argument("window-size=1080,780")
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # options.add_argument('--headless')  # ※ヘッドレスモードを使用する場合、コメントアウトを外す
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver=driver, timeout=30)

    url = "https://cloud.rapsodo.com/team"
    driver.get(url)
    wait.until(EC.presence_of_all_elements_located)

    return driver, wait


def get_data(driver):
    driver.find_element(by=By.TAG_NAME, value="app-switch").find_elements(by=By.CLASS_NAME, value="ng-star-inserted")[1].click()
    st.session_state.wait.until(EC.presence_of_all_elements_located)
    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, "lxml")
    out_list = [td.text for td in soup.find_all("td")]
    df = pd.DataFrame(out_list[17:])
    df = pd.DataFrame(df.values.reshape(-1, 19))
    df.columns = [
        "No.", "球速", "回転数", "トゥルースピン", "回転効率", "回転方向",
        "横の変化量", "縦の変化量", "SSW VB", "SSW HB", "ストライク", "リリースの高さ", "リリースサイド",
        "縦のリリース角度", "横のリリース角度", "ジャイロ角度", "球種", "video", "memo",
    ]
    st.dataframe(df, height=300)

    return df


if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.mail = ""
    st.session_state.password = ""

    st.session_state.dic_player = {}
    st.session_state.player = ""
    st.session_state.id_player = ""

    st.session_state.dates = []
    st.session_state.date = ""

    st.session_state.driver, st.session_state.wait = get_driver()
    st.session_state.file_name = "temp.csv"
    st.session_state.df = pd.DataFrame()

mail = st.sidebar.text_input("mail", "eagles.scout.rapsodo@gmail.com")
password = st.sidebar.text_input("password", "Eagles@2021", type="password")
st.sidebar.markdown("###")
button_login = st.sidebar.button("Login")
if button_login:
    st.session_state.step = 1
    st.session_state.mail = mail
    st.session_state.password = password


# login and show players
if st.session_state.step == 1:
    place_progress.image(path_loading, width=500)
    tag_inputs = st.session_state.driver.find_elements(by=By.CLASS_NAME, value="form-control")
    tag_inputs[0].send_keys(st.session_state.mail)
    tag_inputs[1].send_keys(st.session_state.password)
    st.session_state.driver.find_elements(by=By.TAG_NAME, value="button")[0].click()
    st.session_state.driver.execute_script("document.body.style.zoom='50%'")
    st.session_state.wait.until(EC.presence_of_all_elements_located)

    time.sleep(3)
    tag_pages_box = st.session_state.driver.find_element(by=By.CLASS_NAME, value="pagination")
    button_next_page = tag_pages_box.find_elements(by=By.TAG_NAME, value="button")[1]
    num_pages = len(tag_pages_box.find_elements(by=By.TAG_NAME, value="li"))

    dic_player_2 = get_players(html=st.session_state.driver.page_source.encode('utf-8'))
    for _ in range(num_pages-1):
        # button_next_page[0].click()
        st.session_state.driver.execute_script('arguments[0].click();', button_next_page)
        time.sleep(1)
        html = st.session_state.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "lxml")
        td_list = soup.find_all("td", {"class": "td-style-highlight"})
        dic_player_2.update(get_players(html=st.session_state.driver.page_source.encode('utf-8')))

    # for _ in range(10):
    #     st.session_state.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    #     time.sleep(1)
    # st.session_state.wait.until(EC.presence_of_all_elements_located)
    # st.session_state["dic_player"] = get_players(st.session_state.driver.page_source.encode('utf-8'))

    st.session_state["dic_player"] = dic_player_2
    st.session_state.step = 2


# display players and dates
if st.session_state.step >= 2:
    player = cols[0].selectbox("選手", list(st.session_state["dic_player"].keys()))
    if player != st.session_state.player:
        st.session_state.step = 2
    st.session_state.player = player
    place_progress.empty()

if st.session_state.step == 2:
    st.session_state.id_player = st.session_state["dic_player"][st.session_state.player]
    st.session_state.page_player = f"https://cloud.rapsodo.com/team/{st.session_state.id_player}/sessions"
    st.session_state["dates"] = get_dates(st.session_state.driver, st.session_state.page_player)
    # place_progress.empty()
    st.session_state.step = 3

# get player information
if st.session_state.step >= 3:
    st.session_state.date = cols[1].selectbox("日付", st.session_state["dates"])
    cols[2].write(" ")
    cols[2].write(" ")
    button_date = cols[2].button("Load date")
    if button_date:
        date_index = st.session_state["dates"].index(st.session_state.date)
        place_progress.image(path_loading, width=600)
        st.session_state.driver.find_elements(by=By.TAG_NAME, value="td")[date_index].click()
        st.session_state.wait.until(EC.presence_of_all_elements_located)
        time.sleep(3)

        st.session_state.df = get_data(st.session_state.driver)
        st.session_state.step = 4

if st.session_state.step == 4:
    now_text = datetime.datetime.now().strftime("%Y%m%d") + f'{st.session_state.player}_{st.session_state.date}.csv'  # "%Y%m%d-%H%M%S"
    st.session_state.file_name = cols[0].text_input("file_name", now_text)

    num = st.session_state.df.shape[0]
    df_info = pd.DataFrame({
        "date": [st.session_state.date] * num,
        "id": [st.session_state.id_player] * num,
        "player": [st.session_state.player] * num,
    })
    st.session_state.df = pd.concat([df_info, st.session_state.df], axis=1)
    csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=f"{st.session_state.file_name}.csv",
        mime='text/csv',
    )

    place_progress.empty()


# streamlit run main2.py

