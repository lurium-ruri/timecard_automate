# クラウドタイムカード自動入力
+ 平日の定時入力が可能。
+ 実行後の結果をスクリーンショットとして取得。

## 環境
+ python 3.6
+ pipenv
+ FireFox(gekodriver)

## 使用方法
1. clone
1. sample.config.iniをconfig.iniへ、リネーム
1. config.ini中の設定値を編集
1. 使用しているOSに合ったgekodriverを[ダウンロード](https://github.com/mozilla/geckodriver/releases)
1. ダウンロードした __geckodriver__ を、__'./driver'__ 以下へ配置
1. pipenv installで関連モジュールのインストールと仮想環境を構築
1. pipenv shellで仮想環境をアクティブに
1. python timecard_automate.pyで実行
