# 私有原声文件导入区

把你已经合法取得的《QQ自由幻想》地图音乐文件（MP3、WAV、OGG、FLAC 或 M4A）放在任意本地目录，然后执行：

```powershell
python tools/import_tracks.py "D:\your-legal-qq-fantasy-audio"
```

脚本会把文件复制到 `private_media/qq-fantasy/` 并生成 `catalog.json`。这个目录默认被 Git 忽略，不会自动上传到 GitHub。

项目中的 `data/qq_fantasy_tracklist.json` 只是地图曲目索引和章节清单，不包含官方音频文件。
