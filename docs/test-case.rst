Test Case
================


Landing
-----------------------
- 測試 server 連線失敗反應: config.ini 改 `[Server] host={error host address}` ，應該跳出 "連線失敗，請檢查網路連線..." 的提醒
- 桌機軟體不是最新版本: 伺服器的 Announcement 改版本，ex: `v:0.0.0` ， 應該跳出 "請至官網下載最新版本軟體" 的提醒，config.ini 的 is_outdated 應該會變成 `1`, ex: `[State] is_outdated = 1`
- 桌機軟體確定最新版本: 伺服器的 Announcement 改回原本版本，ex: `v:1.1.2` ， 沒有任何訊息跳出，config.ini 的 is_outdated 應該會變回成 `0`, ex: `[State] is_outdated = 0`

Editing/Annotation
-----------------------

DataGrid

- mouse click | 滑鼠點擊 => 看 cell 有無顯示正確，照片也要切換正確
- mouse drag & select area | 滑鼠拖拉 

  - from top-left to bottom-right => 左上到右下
  - from bottom-right to top-left => 右下到左上

- keyboard arrow up/down/left/right | 鍵盤上下左右 => 跟滑鼠點擊一樣，看顯示有無正常
- input data

  - form select/option input (listbox) | 下拉選單 => 年齡/性別/角況，下拉, 選取, 動作有無正常
  - form autocomplete input (entry/listbox widget) | 下拉 + 自動補齊 => 物種欄位，有無自動補齊 (嚴格的說是自動篩選再手動補齊)，下拉清單可否按鍵盤上下或是滑鼠 scroll 移動選項
  - form text input (entry widget) | 自由欄位 => 備註/個體 ID => 資料輸入有無正常

- copy & paste

  - Ctrl-C/Ctrl-V
  - mouse right button (Button3) copy & paste | 滑鼠右鍵的 "複製/貼上" 內容
- Selection

  - Ctrl+Mouse Left Button Click mark selection | 滑鼠+ Ctrl 鍵的跳列選取 => 目前沒綁定功能，只有視覺顯示 (綠色框)
  - Shift selection | 按住 shift 可以連續多列選取

- fill (drag fill handle to auto fill data) | cell 右下方那個藍色方型小把手

  - single value fill | 單一 cell 選取 & 補齊 => excel 的 auto fill 動作有無正常
  - multi value (pattern) fill | 多列選取 & 補齊 => 同上

- pagination

  - edit | 編輯內容 => 有無正確 (會不會改到別頁的資料)
  - image display | 照片顯示 => 是不是對的照片

- keyborad shortkey | 快捷鍵 => 輸入是否成功
- 連拍補齊

  - 顏色呈現
  - edit 有無同步
  - 換頁有無問題
  - keyboard shortkey

- 複製/刪除列 clone/ removerows

  - 只能刪複製出來的 row



Import Folder
-----------------

- 資料夾內有壞掉的照片，測試檔 https://drive.proton.me/urls/1SBH4FW02W#CJ5mIwlH3EFc

測試匯入
==============

**正常情況**

1. 按 "加入資料夾"
2. 選擇資料夾
3. 進入 "現有資料夾" 頁
4. 進度條每秒更新
5. 正在匯入時按"資料夾卡片"應該要不能進入編輯畫面
6. 正在匯入時關閉應用程式 (按視窗的 "X")，會跳出"尚有資料夾正在匯入中..." 的錯誤訊息(對話框)
7. 完成後跳出 "匯入資料夾完成" 的訊息 (對話框)
8. 可以進入資料夾編輯畫面

**測試錯誤處理 (error handling)**

模擬匯入失敗 (匯一半當機...)

1. edit config.ini, set [Mode] force_quit = 1
2. 按 "加入資料夾"
3. 選擇資料夾
4. 進入 "現有資料夾" 頁
5. 進度條每秒更新
6. 離開程式
7. 重新開啟程式
8. 可以進入匯入錯誤的資料夾, 執行"刪除資料夾"


Upload
-------------------
- 主機沒開: URLError
- API error: HTTPError 500
