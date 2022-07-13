
Folder(Source) Status
=====================

1. start import: a1
2. imported: a2 未編輯

start_editing: b1 編輯中


3. start upload: b1 上傳中
4. annotation uploaded: b2 上傳中?
5. image start uploaded (but not all): b3 
6. all uploaded: b4
(
7. re-upload: b2a
8. annotation uploaded: b3a
9. image start uploaded (but not all): b3a
10. all uploaded: b4a
)
11. archive: c

image upload_status

- start upload: 100
- annotation uploaded: 110
- media uploaded: 200

.. code-block::

   digraph G {

  subgraph cluster_0 {
    style=filled;
    color=lightgrey;
    node [style=filled,color=white];
    a1 -> a2;
    label = "import folder";
  }

  subgraph cluster_1 {
    node [style=filled];
    b1 -> b2 -> b3 -> b4;
    label = "upload folder";
    color=blue
  }
  start -> a1;
  a2 -> annotate -> b1;
  a2 -> b1;
  b4 -> end;
  b4 -> annotate [label="upload again, update annotation, upload last failed files"];
  b4 -> c -> end;
  annotate [shape=rect, label="annotate"];
  c [label="c:\narchive folder"];
  b4 [label="b4:\nupload done"];
  b3 [label="b3:\nstart upload media files"];
  b2 [label="b2:\nupload annotation"];
  b1 [label="b1:\nstart upload"];
  a1 [label="a1:\nstart import"];
  a2 [label="a2:\nimport done"];
  start [shape=Mdiamond];
  end [shape=Msquare];
}
