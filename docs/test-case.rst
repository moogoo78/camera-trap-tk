Test Case
================


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




Upload
-------------------
- 主機沒開: URLError
- API error: HTTPError 500
