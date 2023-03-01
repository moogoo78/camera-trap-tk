# tkdatagrid


## feature
DataGrid
  data dict: integer key
  columns


DataGrid.state (global value for MainTable, RowIndex, ColumnHeader components)

column type:

text, image listbox, entry(default)

height 設定會被 refresh() 是 用 data_visible (number of items per page) x cell_height 決定

## Layout

```
[row, col]
```

- DataGrid(tk.Frame)
  - MainTable(tk.Canvas): [1, 1]
  - ColumnHeader(tk.Canvas): [0, 1]
  - RowIndex(tk.Canvas): [1, 0]
  - scrollbar_x (tk.Canvas): [2, 1]
  - scrollbar_y (tk.Canvas): [1, 2]
  - Footer(tk.Frame) [3,1]

```
|-----|-----|-----|
| 0,0 | 0,1 | 0,2 |
|     | CH  |     |
|-----|-----|-----|
| 1,0 | 1,1 | 1,2 |
| RI  | MT  | SY  |
|-----|-----|-----|
| 2,0 | 2,1 | 2,2 |
|     | SX  |     |
|-----|-----|-----|
| 3,0 | 3,1 | 3,2 |
|     | FT  |     |
|-----|-----|-----|
```

## Actions

1: click on cell
- `render_cell_box`
- action: click


1a: click on fill handle and drag
- `render_fill_box`
- action: handle

1b: drag on cell
- `render_drag_box`
- action: drag

1a1: mouse release
- `render--`
- action: ''


1a1a: auto fill



## Notice

rc 跟 xy 的順序相反 (容易搞錯)
