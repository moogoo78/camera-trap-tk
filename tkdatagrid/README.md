# tkdatagrid


## feature
DataGrid
  data dict: integer key
  columns


DataGrid.state (global value for MainTable, RowIndex, ColumnHeader components)

column type:

text, image listbox, entry(default)



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
