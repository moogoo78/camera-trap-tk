# CameraTrap Desktop App Workflow


## Import Folder

![import-folder-flow](./import-folder-flow_221108.png)
[Graphviz DOT source](./import-folder-flow.dot)

## Upload Status

### Source (Folder) Upload Status

![upload-status](./upload-status-flow_220719.png)
[Graphviz DOT source](./upload-status-flow.dot)

Status Code:

```
    STATUS_START_IMPORT = 'a1'
    STATUS_DONE_IMPORT = 'a2'                # 未編輯
    STATUS_START_ANNOTATE = 'a3'             # 編輯中
    STATUS_START_UPLOAD = 'b1'
    STATUS_ANNOTATION_UPLOAD_FAILED = 'b1a'  # 上傳失敗
    STATUS_MEDIA_UPLOAD_PENDING = 'b2'       # 上傳中
    STATUS_MEDIA_UPLOADING = 'b2a'           # 上傳中
    STATUS_MEDIA_UPLOAD_FAILED = 'b2b'       # 上傳失敗 (上傳不完全)
    STATUS_DONE_UPLOAD = 'b2c'               # 完成
    STATUS_START_OVERRIDE_UPLOAD = 'b3'      # 上傳覆寫
    STATUS_OVERRIDE_ANNOTATION_UPLOAD_FAILED = 'b3a'  # 上傳失敗
    STATUS_DONE_OVERRIDE_UPLOAD = 'b3b'      # 覆寫完成
    STATUS_ARCHIVE = 'c'                     # 歸檔
```

### Image Upload Status

- imported: 10
- start upload: 100
- annotation uploaded: 110
- media uploaded: 200
