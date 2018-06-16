#! python3
# -*- coding: utf-8 -*-
# timecard_automate.py - クラウドタイムカード自動入力
import configparser
import datetime
import logging
import os
from pathlib import Path

from common import config as config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

driver = None
wait = None


def init():
    # ログ設定
    _detail_formatting = '%(relativeCreated)08d[ms] - %(name)s - %(levelname)s - %(processName)-10s - %(threadName)s -\n*** %(message)s'
    logging.basicConfig(
        level=logging.DEBUG,
        format=_detail_formatting,
        filename=str(Path('./log/timecard_automate.log')),
    )
    console = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(relativeCreated)07d[ms] : %(name)s : %(message)s')
    console.setFormatter(console_formatter)
    console.setLevel(logging.INFO)
    logging.getLogger('common').addHandler(console)
    logging.getLogger(__name__).addHandler(console)

    # WebDriver設定
    # option設定
    options = Options()
    # ヘッドレスモードを有効にする（次の行をコメントアウトすると画面が表示される）。
    options.add_argument('--headless')
    # WebDriverオブジェクトを作成する。
    global driver
    driver = webdriver.Firefox(
        executable_path=str(Path('./driver/geckodriver')),
        firefox_options=options)
    # waitオブジェクトを作成する
    global wait
    wait = WebDriverWait(driver, 10)


def main():
    logger.info('start:timecard_automate')

    try:
        top_to_home()
        input_worktime()
    finally:
        driver.quit()  # ブラウザーを終了する。

    logger.info('end:timecard_automate')


def top_to_home():
    logger.debug('start:top_to_home')

    # クラウドタイムカードのトップ画面を開く。
    driver.get('https://cloud-timecard.appspot.com/clw/')

    # タイトルが表示されていることを確認する。
    assert 'ログインページ' in driver.title

    # 入力して送信する。
    input_id = driver.find_element_by_id('UserCorporationId')
    input_id.send_keys(config.get('user_info', 'CorporationId'))

    input_name = driver.find_element_by_id('UserUsername')
    input_name.send_keys(config.get('user_info', 'Username'))

    input_pw = driver.find_element_by_id('UserPassword')
    input_pw.send_keys(config.get('user_info', 'Password'))

    driver.find_element_by_class_name('btn-primary').click()  # 送信->home画面へ

    logger.debug('end:top_to_home')


def input_worktime():
    logger.debug('start:input_worktime')
    
    # ログイン後、平日を定時で入力する
    start_date = datetime.datetime.strptime(
        config.get('update_date_range', 'Start'), "%Y-%m-%d").date()
    logger.info(f'start_date:{start_date}')
    end_date = datetime.datetime.strptime(
        config.get('update_date_range', 'End'), "%Y-%m-%d").date()
    logger.info(f'end_date:{end_date}')

    tgt_date = start_date

    while tgt_date <= end_date:
        tgt_date_str = datetime.date.strftime(tgt_date, '%Y-%m-%d')
        # 土日はskip
        if tgt_date.weekday() >= 5:
            logger.info(
                'skip -> ' + datetime.date.strftime(tgt_date, '%Y-%m-%d(%a)'))
            # 次の日付へ
            tgt_date += datetime.timedelta(days=1)
            continue

        logger.info(
            'target -> ' + datetime.date.strftime(tgt_date, '%Y-%m-%d(%a)'))

        user_name = config.get('user_info', 'Username')

        # 対象日付へ飛ぶ（url + date + user_name）
        driver.get(
            'https://cloud-timecard.appspot.com/clw/works/updateTime/'
            f'{tgt_date_str}/'
            f'{user_name}')

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
            (By.CLASS_NAME, 'alert-success'), '登録が正常に終了しました。'))

        # 次の日付へ
        tgt_date += datetime.timedelta(days=1)

    # スクリーンショットを撮る。
    driver.get('https://cloud-timecard.appspot.com/clw/works/input')
    png = driver.find_element_by_id('main-container').screenshot_as_png
    with open('timecard_input_results.png', 'wb') as f:
        f.write(png)
    
    logger.debug('end:input_worktime')


if __name__ == '__main__':
    init()
    main()
