import os
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request


username = input("스크래핑 할 인스타그램 계정의 아이디를 입력하세요\n→ ")
password = input("비밀번호를 입력하세요\n→ ")
dir_name1 = input("다운받은 파일을 저장할 폴더명을 입력하세요\n→ ")
dir_name = dir_name1+'/'
# dir_name = 'downloaded/'
driver = webdriver.Chrome(r'.\chromedriver_win32\chromedriver.exe')
url1 = 'https://www.instagram.com/accounts/login/?next=%2F'
url2 = '%2Fsaved%2F&source=desktop_nav'
url = url1 + username + url2
print(url)

SCROLL_PAUSE_TIME = 1
ArrHref = []

total_num = 1
id_num = 1
id_li_num = 1


def getData(el):
    # 이미지el
    imgs = el.find_elements_by_css_selector('.FFVAD')
    if len(imgs) != 0:
        print('이미지네')
        # 이미지면
        img = el.find_element_by_css_selector('.FFVAD')
        # 이미지경로추출
        imgSrc = img.get_attribute('srcset').split('750w,')[
            1].split('1080w')[0]
        # 파일저장
        urllib.request.urlretrieve(
            imgSrc, dir_name+'%s(%s)_%.0f.jpg' % (username, id_, id_li_num))
    else:
        print('비디오네')
        # 이미지가아니면
        video = el.find_element_by_css_selector('.tWeCl')
        # 비디오경로추출
        videoSrc = video.get_attribute('src')
        # 파일저장
        urllib.request.urlretrieve(
            videoSrc, dir_name+'%s(%s)_%.0f.mp4' % (username, id_, id_li_num))


def getThums():
    thums = driver.find_elements_by_css_selector('.v1Nh3.kIKUG._bz0w')
    for thum in thums:
        href = thum.find_element_by_css_selector('a').get_attribute('href')
        print(href)
        if href in ArrHref:
            pass
        else:
            ArrHref.append(href)


try:
    # 접속
    print('브라우저 열기 시도')
    driver.get(url)
    driver.implicitly_wait(1)
    print('브라우저 접속 완료')

    # 로그인
    print('사용자 정보 입력')
    driver.find_element_by_name('username').send_keys(username)
    driver.find_element_by_name('password').send_keys(password)
    driver.find_element_by_xpath(
        '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button').click()
    print('로그인 접속 시도')
    driver.implicitly_wait(5)

    # 자동 스크롤
    while True:
        getThums()

        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                print(len(ArrHref), ArrHref)
                print('전체 스캔 완료(■스크롤 끝■)')
                break

            else:
                last_height = new_height
                print('전체 스캔 (▼스크롤중▼)')
                continue

    try:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    except OSError as e:
        print('폴더를 생성하는데 실패했습니다.', e)

    for href in ArrHref:
        driver.get(href)
        driver.implicitly_wait(1)

        thum_next = driver.find_elements_by_css_selector('._6CZji')
        container = driver.find_element_by_css_selector('._97aPb.wKWK0')
        ArrLi = container.find_elements_by_css_selector('._-1_m6')
        username = driver.find_element_by_css_selector(
            '.FPmhX.notranslate.nJAzx').get_attribute('title')

        id_ = href.split('/p/')[1].split('/')[0]

        if len(ArrLi) == 0:
            print('게시물 하나네요')
            getData(container)
            print('다운했어요')
            driver.implicitly_wait(1)
        else:
            print('게시물 여러개네요')
            for li in ArrLi:
                if len(thum_next) != 0:
                    print('다음버튼이 있네요')
                    getData(li)
                    print('다운했어요')
                    try:
                        thum_next[0].click()
                        print('다음게시물버튼 눌렀어요')
                    except Exception:
                        print('다음버튼이 없네요')
                        id_li_num = 1
                        break
                    driver.implicitly_wait(1)
                    id_li_num = id_li_num+1
                    total_num = total_num+1
                    continue
        id_num = id_num+1
        total_num = total_num+1

        # 저장해제
        btn_like = driver.find_element_by_css_selector('.fr66n')
        btn_save = driver.find_element_by_css_selector('.wmtNn')
        # btn_save.click()

except Exception as e:
    print(e)

finally:
    print('▶▶▶ 작업종료')
    print('%s개의 게시물링크에서 %s개의 파일저장을 완료했습니다' % (id_num-1, total_num-1))
    driver.close()
