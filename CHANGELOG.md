# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.2.4a]
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
