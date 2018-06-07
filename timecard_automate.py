#! python3
# -*- coding: utf-8 -*-
# timecard_automate.py - クラウドタイムカード自動入力

import configparser
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def main():
    print('--main start--')
    options = Options()
    # ヘッドレスモードを有効にする（次の行をコメントアウトすると画面が表示される）。
    options.add_argument('--headless')

    # ChromeのWebDriverオブジェクトを作成する。
    driver = webdriver.Firefox(
        executable_path='./driver/geckodriver', firefox_options=options)
    wait = WebDriverWait(driver, 10)

    # クラウドタイムカードのトップ画面を開く。
    driver.get('https://cloud-timecard.appspot.com/clw/')

    # タイトルが表示されていることを確認する。
    assert 'ログインページ' in driver.title

    # 入力情報取得
    config = configparser.ConfigParser()
    config.read('config.ini')

    # 入力して送信する。
    input_id = driver.find_element_by_id('UserCorporationId')
    input_id.send_keys(config['user_info']['CorporationId'])

    ini_name = config['user_info']['Username']
    input_name = driver.find_element_by_id('UserUsername')
    input_name.send_keys(ini_name)

    input_pw = driver.find_element_by_id('UserPassword')
    input_pw.send_keys(config['user_info']['Password'])

    driver.find_element_by_class_name('btn-primary').click()   # 送信

    # ログイン後、平日を定時で入力する
    start_date = datetime.datetime.strptime(
        config['update_date_range']['Start'], "%Y-%m-%d")
    end_date = datetime.datetime.strptime(
        config['update_date_range']['End'], "%Y-%m-%d")

    tgt_date = start_date - datetime.timedelta(days=1)

    while tgt_date < end_date:
        tgt_date += datetime.timedelta(days=1)

        # 土日はskip
        if tgt_date.weekday() >= 5:
            continue
        tgt_date_str = datetime.datetime.strftime(tgt_date, '%Y-%m-%d')
        print('tgt:' + datetime.datetime.strftime(tgt_date, '%Y-%m-%d(%a)'))
        driver.get(
            'https://cloud-timecard.appspot.com/clw/works/updateTime/'
            f'{tgt_date_str}/'
            f'{ini_name}')

        # 出社
        work_in_time = driver.find_element_by_id('WorkIntime')
        work_in_time.clear()
        work_in_time.send_keys('09:00')

        # 休憩
        work_rest_time = driver.find_element_by_id('WorkResttime')
        work_rest_time.clear()
        work_rest_time.send_keys('01:00')

        # 退社
        work_out_time = driver.find_element_by_id('WorkOuttime')
        work_out_time.clear()
        work_out_time.send_keys('18:00')

        btns = driver.find_elements_by_class_name('btn-success')
        for btn in btns:
            if btn.text == '修正登録':
                btn.click()   # 送信
                break

        wait.until(EC.text_to_be_present_in_element(
            (By.CLASS_NAME, "alert-success"), '登録が正常に終了しました。'))

    # スクリーンショットを撮る。
    driver.get('https://cloud-timecard.appspot.com/clw/works/input')
    png = driver.find_element_by_id('main-container').screenshot_as_png
    with open("timecard_input_results.png", "wb") as f:
        f.write(png)

    driver.quit()  # ブラウザーを終了する。

    print('--main end--')


if __name__ == '__main__':
    main()
