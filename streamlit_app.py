import streamlit as st

"""
## Web scraping on Streamlit Cloud with Selenium

[![Source](https://img.shields.io/badge/View-Source-<COLOR>.svg)](https://github.com/snehankekre/streamlit-selenium-chrome/)

This is a minimal, reproducible example of how to scrape the web with Selenium and Chrome on Streamlit's Community Cloud.

Fork this repo, and edit `/streamlit_app.py` to customize this app to your heart's desire. :heart:
"""

cols = st.columns(3)
st.markdown("###")
place_progress = st.empty()

if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.mail = ""
    st.session_state.password = ""

    st.session_state.dic_player = {}
    st.session_state.player = ""
    st.session_state.id_player = ""

    st.session_state.dates = []
    st.session_state.date = ""

    st.session_state.driver, st.session_state.wait = init_setting()
    st.session_state.file_name = "temp.csv"
    st.session_state.df = pd.DataFrame()
    
with st.echo():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    @st.experimental_singleton
    def get_driver():
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')

    driver = get_driver()
    url = "https://cloud.rapsodo.com/team"
    driver.get(url)
    wait.until(EC.presence_of_all_elements_located)

    
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

        st.session_state["dic_player"] = dic_player_2
        st.session_state.step = 2

    
    st.code(driver.page_source)

    st.write("b")
