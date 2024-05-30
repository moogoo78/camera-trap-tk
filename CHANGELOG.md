# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [v1.1.10]

### 修改

- 新增壞掉的照片的處理 (照片檔可以開啟, 但無法做縮圖)
- 匯入照片的進度條顯示文字 "上傳狀態" => "匯入中"
- 編輯頁的"上傳資料夾" 跟 "刪除資料夾" 按鈕不見

## [v1.1.9]

### 修改

- 匯入影片csv會沒有物種的標註資料
- 鳥類清單合併到物種清單 (有加一個 `-----` 分隔號)，所以也可以key字自動篩選
- 匯入文字資料的物種控制詞彙也要考慮鳥類 (這個應該上個版本就有加上去了)
- 拿掉右鍵鳥類清單

### 新增

- 調整字體大小
- 匯入範例檔: import-example.csv


## [v1.1.8]

### 修改

- 匯入資料夾製作縮圖後，要把file handler關閉 (解決作業系統遇到 open too many file 問題)
- 上傳未完成的資料夾，"上傳"按鈕的文字變成“上傳中”，然後讓他disable (不能按)
- 照片壞掉匯入會發生錯誤並且中斷 (v1.1.1版改過的問題，v1.1.6版後又會出現)

### 增加

- 在編輯資料頁面新增"同步上傳狀態"按鈕，從server得到has_storage狀態(有無真的在AWS S3上有檔案)，解決造成混亂的上傳狀態

## [v1.1.7] 2024-02-15

### 修改

- server回傳的錯誤訊息之前沒有跳出訊息視窗
- 上傳程式版本太舊會禁止上傳 (主要在server端設定檔控制)
- server不擋上傳程式舊版本 (恢復原本上傳邏輯)
- 匯入檔案如果有包含影片會發生錯誤
- 匯入檔案也會把鳥類清單的物種加入控制詞彙判斷條件
- 影片檔無法上傳 (調整AWS設定)
- 更新鳥類清單\物種加松鼠、飛鼠
- 更新說明頁文字(單機版 => 上傳程式)
- 匯入CSV編碼判斷 (big5, utf8)
- 計畫/樣區/相機位置選擇錯誤Bug

### 新增

- 連拍補齊可以用秒數
- 重新build exe檔(使用Pyinstaller的custom bootloader，減少防毒軟體誤判)


## [v1.1.6] 2023-10-27

### 修改

- update project options after login/logout
- post `update_upload_history` API to "finished", let server upload_history page successed if annotation override only
- import foto, exif originalDateTime broken, use last_timestamp instead, or use file's modified time

## [v1.1.5] 2023-10-05

### 新增

- 匯入文字資料(import_data)
- ORCID login (login_form)
- add app logo
- check deployment_journal
- deleted_images messagebox alert
- 連拍補齊預設打開, 設定5分鐘

### refactor

- `check_import_folder` combine all import folder check rules
- rewrite main edit window`s project/studyarea/deployment option choose, consider to login process has new user_info data structure

## [v1.1.4] 2023-09-05

### 修改

- remove imageio, imageio-ffmpeg (will cause run error on certain labtop)
- 連拍分組輸入如果不是數字會跳出錯誤
- 大分頁速度慢

## [v1.1.3] 2023-08-17

### 修改

- 資料夾狀態卡住，無法繼續上傳的問題
- python 套件更新，棄 PyInstaller 改用 nuitka 產生 exe 檔
- AWS 的 secret key 改用 module import (不會留在 config 或外部讀取的 credentials 檔案)
- ct-log.txt 改成 ct-app.log (超過10MB 會自動輪替, rotate)


## [v1.1.2] 2023-06-20

### 修改

- 影像匯入中，點擊資料夾會當掉
- 複製內容 drag handle (小藍方塊) 上下拉時，scrollbar 要跟著動
- 編輯表單的 drag handle (小藍方塊) 拉超出表表格會出現錯誤訊息
- 上傳進度頁加上 scrollbar
- 現有目錄頁篩選某些狀態會造成爆框問題 (一欄超過 3 個項目)
- 上傳中，現有資料夾還是可以點進去編輯 (要擋掉)

## [v1.1.1] 2023-05-09

### Added

- 檢查 App是否最新版
- 資料夾上傳時不能編輯 (鎖住無法進入編輯畫面)
- 上傳檔案如果有壞掉，會回傳錯誤對話框，並重新計算正確的照片數量
- 匯入資料夾前先檢查伺服器上有無存在
- 匯入資料集前先檢查網路 [rc2]
- 匯入資料夾還沒處理晚離開 App 會跳出通知 (不能離開) [rc3]
- 照片標註完狀態要馬上顯示 "已標"

## [v1.0.2/v1.1.0] 2023-05-01

### Changed

- 連拍補齊畫面沒有 refresh
- 文字上傳改流程 (上傳大資料不會 timeout)
- 說明畫面更用 toplevel (節省記憶體)
- 匯入資料夾處理中時，不能同時匯入其他資料夾 (對話框阻擋)
- 影片無法播放 (測試站跟正式站在 AWS 的設定不同造成)

## [v1.0.1]

### Changed

- 匯入失敗後，可以進去編輯畫面刪除
- 匯出 csv 遇到物種填 食蟹獴 會導致 app 錯誤
- 大圖畫面按上下鍵標題 (檔案名稱) 也會跟著改

### Added

- 增加 debug 看問題使用的設定
  - skip_media_upload (忽略照片檔案上傳)
  - skip_media_display (忽略照片顯示) => 拿到別人的 ct.db 檔案，測試環境狀態用

## [v1.0.0] 2022-12-13

### Added:

- QRCode 說明頁

## [v0.2.6]

- 物種下拉選單選定後，鍵盤上下鍵失效
- 資料少 (比顯示範圍高度小)，鍵盤上下鍵會造成 vertical scroll 把資料排到中間

## [v0.2.5c1]

- 改相機命名警告文字

## [v0.2.5c]

- 相機位置排序
- 測試照清空 bug
- 拿掉沒網路時的提醒
- 照片放大按鈕消失 (有影片檔時才會發生)

## [v0.2.5b]

- 影片匯入問題
- 表格上按左右鍵移動，horizontal scroll bar 也要跟著捲動
- 原本上下鍵移動感覺 highlight 跑出去了，vertical scrollbar 也沒有捲動

## [v0.2.5]

### Changed:
- many UI after 教育訓練
- 改下拉選單邏輯 (避免相機位置同名)

### Added:
- 檢查資料夾匯入格式

## [v0.2.4b]

### Changed:
fix:
- if upload_progress has multiple folder to upload, pause not work
- update annotation will let server send notification like upload finish

## [v0.2.4a]

### Changed:
fix:
- server.make_request use requests package
- config.ini add ssl_verify

## [v0.2.3a]

### Changed:

fix:
- 更新文字，上傳進度要變綠勾勾
- 上下鍵要到第28列畫面才會跳過去
- SSL 網路問題

### Added:

- 輸入資料的原則與影像定義附掛於介面上

## [v0.2.2a]

### Changed:

fix:
- 放大圖的比例跟顯示範圍調整，不然會被遮住
- 編輯表格區域可以調整高度 (解析度太低的電腦也可以用)

### Added: 

feat:
- 放大圖可以商上下左右鍵控制

style:
- landing, panel, appbar 的按鈕換設計的 icon

## [v0.2.1b]

### Changed:
fix:
- 連拍分組換資料夾不會跟著 reset
- 影片播放改用系統的 Windows Media Player 播放影片 (目前只有測 Windows 11，不知道 Windows 7、Windows 10 路徑是不是一樣，需要再確認)
- 上傳影片後自動觸發 AWS Media Convert 轉檔，網頁前台可以看到轉檔後的結果
- 現有資料夾很難點進去的問題
- [網頁] 棄用的相機位置在桌機版的下拉選單要拿掉

style:
- 放大圖/播放影片的按鈕位置調整 (之前是固定，現在會因為圖片的寬度跟著移動到右下角)

## [v0.2.1a]

### Changed:
fix:
- 分頁
- 上傳流程 (暫停/重新上傳)
- 狀態相關 bugs
- 鍵盤上下左右鍵失靈
- 分頁造成連拍補齊顯示錯誤

style:
- 連拍補齊套新配色

### Added:
- 影片上傳/播放
- 快捷鍵設定視窗

## [v0.2.0a] - 2022-07-20

### Changed

- 套新的 Figma 版面
- 重寫 source.status (上傳狀態) 的流程
- 重寫 upload_progress.py 的 threading, event (不用 tk.after 的 polling機制)


## [v0.1.7c] - 2022-05-03

### Changed

- fixed many bugs
- upload payload add "行程" & "測試照時間"

## [v0.1.7b] - 2022-04-29

### Changed

- 可選取多列刪除，但選取到的最後一列還是無法刪掉
- 地棲性鳥類清單名稱未改成「鳥類清單」
- 連拍補齊時還是會補齊已經被自動標註為測試照的原始照片
- 上傳一個名稱包含行程的資料夾之後，「先前已上傳但資料夾名稱沒有行程」以及「後來才上傳但資料夾名稱沒有行程」的資料夾行程皆會自動變成相同行程（但我抓不太到規律，請見圖片們）
- 下拉選單可以上下鍵選擇選項，但無法按enter選定
- 下拉選單輸入「熊」，無法自動篩選出「黑熊」，要輸入第一個字「黑」才有結果


## [v0.1.7a] - 2022-04-28

編輯 UI 大修改

### Changed

- 滑鼠拖拉區域可以往上拉
- 只能刪除 "複製出來的列"
- 更新鳥類選單


### Added

- 物種欄位有自動補齊功能 (其實是自動篩選+手動補齊)
- 跟 excel 一樣的 auto fill handle (右下角那個藍色小方方)
- Ctrl-C/Ctrl-V

## [v0.1.6b] - 2022-02-11

### Changed

- 複製/貼上內容 不會即時更新頁面

## [v0.1.6a] - 2022-02-10

### Added

- 加上分頁 (config.ini  的 [DataGrid] 的 num_per_page 可以控制一頁的筆數)

### Changed

- 改善效能 (連拍補齊的批次修改, 還有照片數多是不會動作很慢)

### WIP

- macOS 版本 (大致上可以用，但是有幾個 UI 還需要調整)

## [v0.1.5] - 20221-10-25

### Added

- 更新快速鍵
