# -*- coding: utf-8 -*-
# @file : toutiao.py
import cv2
import random
import requests
from lxml import etree
from selenium import webdriver
from time import *
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options


def show(name):
    '''展示圈出来的位置'''
    cv2.imshow('Show', name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def tran_canny(image):
    """消除噪声"""
    image = cv2.GaussianBlur(image, (3, 3), 0)
    return cv2.Canny(image, 50, 150)


def detect_displacement(image_background_path, img_slider_path):
    bgRgb = cv2.imread(image_background_path)
    bgGray = cv2.cvtColor(bgRgb, cv2.COLOR_BGR2GRAY)
    slider = cv2.imread(img_slider_path, 0)
    res = cv2.matchTemplate(bgGray, slider, cv2.TM_CCOEFF)
    a, b, c, d = cv2.minMaxLoc(res)
    if abs(a) >= abs(b):
        return c[0] * 0.58
    else:
        return d[0] * 0.58

def get_track(distance):
    track = []
    current = 0
    mid = distance * 7 / 8
    t = 0.2
    v = 0
    while current < distance:  # 定义循环条件,如果为真则继续,为假则不继续
        if current < mid:
            a = 3  # 定义加速度
        else:
            a = -3
        v0 = v
        v = v0 + a * t  # 定义移动速度,哈哈哈,v = v0+at
        move = v0 * t + 1 / 2 * a * t * t  # 定义每次滑块移动的距离,也是如此.s=v0t+1/2at**2,hahha,写这个的是高手,活学活用
        current += move  # 每次遍历得到的move用current保存起来
        track.append(round(move))  # 将得到的move取整添加的列表中,每次都添加到列表尾部,可以用extend多次添加和insert添加到自己想要的位置
    return track  # 返回每次移动的轨迹列表


class TouTiaoLoginSpider():
    def __init__(self):
        opt = Options()
        opt.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
        opt.add_argument('window-size=1920x3000')  # 设置浏览器分辨率
        opt.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        opt.add_argument('--hide-scrollbars')  # 隐藏滚动条，应对一些特殊页面
        # opt.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片，提升运行速度
        opt.add_argument('--headless')
        self.driver = webdriver.Chrome(options=opt, executable_path='./chromedriver.exe')
        self.url = "https://sso.toutiao.com/login/"  # 定义需要访问的地址url
        self.driver.implicitly_wait(30)  # 设置隐式等待时间
        self.driver.set_script_timeout(45)  # 设置异步脚本加载超时时间
        self.driver.set_page_load_timeout(45)  # 设置页面加载超时时间
        # self.driver.maximize_window()  # 设置页面窗口最大化
        self.user_name = user_name
        self.password = password

    def test_first_case(self):
        driver = self.driver
        driver.get(self.url)  # 得到url打开网站
        driver.find_element_by_class_name('web-login-other-login-method__list__item__icon__account_pwd').click()
        sleep(3)
        # 传入用户账号
        driver.find_element_by_class_name("web-login-normal-input__input").send_keys(self.user_name)  # 传入用户密码
        sleep(0.3)
        driver.find_element_by_class_name("web-login-button-input__input").send_keys(self.password)
        sleep(0.2)
        driver.find_element_by_class_name("web-login-confirm-info__checkbox").click()  # 点击登录按钮
        sleep(0.1)
        driver.find_element_by_class_name("web-login-button").click()  # 点击登录按钮
        sleep(2)
        WebDriverWait(driver, 5, 0.5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "secsdk-captcha-drag-sliding"))  # 等待图片加载出来
        )
        try:
            start_position = driver.find_element_by_class_name("secsdk-captcha-drag-sliding")  # 得到滑块的初始位置,并进行异常处理
        except Exception as e:
            print("get button failed: ", e)
        sleep(2)
        response = etree.HTML(driver.page_source)
        img_url = response.xpath('//img[@id="captcha-verify-image"]/@src')
        img_slider_url = response.xpath('//img[contains(@class,"captcha_verify_img_slide")]/@src')
        if len(img_url) > 0:
            img_url = img_url[0]
            img_content = requests.get(img_url)
            with open('toutiao.jpeg', 'wb') as fp:
                fp.write(img_content.content)
            img_slider_url = img_slider_url[0]
            img_slider_content = requests.get(img_slider_url)
            with open('toutiao_slider.png', 'wb') as fp:
                fp.write(img_slider_content.content)
            distance = detect_displacement('toutiao.jpeg', 'toutiao_slider.png')
            action = ActionChains(driver)  # 定义ActionChains
            action.click_and_hold(start_position).perform()  # 点击初始滑块位置并保持不释放
            track = get_track(distance)  # 调用移动轨迹函数并传入距离distance,distance根据定位的滑块窗口大小自己设定
            while track:
                x = random.choice(track)
                ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
                track.remove(x)
            sleep(0.5)
            ActionChains(driver).release().perform()
            sleep(5)
            if '发布作品' in str(driver.page_source):
                count_res = etree.HTML(driver.page_source)
                counts = count_res.xpath('//div[@class="relate-num"]/a//text()')
                new_count = ' '.join(counts)
                return new_count
            else:
                self.test_first_case()

    def tear_close(self):
        self.driver.quit()

if __name__ == "__main__":
    tu = TouTiaoLoginSpider()
    new_count = tu.test_first_case()
    if new_count:
        tu.tear_close()
