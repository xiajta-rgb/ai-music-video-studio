# 谱境 / AI Music Video Studio

一个面向“AI 音乐 + 音乐知识可视化 + 音乐视频”的本地原型。它参考 B 站视频 [BV1Rpxb6gEVH](https://www.bilibili.com/video/BV1Rpxb6gEVH) 的表达方式，把风格、音阶、旋律、节拍、章节字幕和视觉时间线放到同一份 composition JSON 里。

## 当前能力

- 输入场景与创作意图，选择中国风五声、都节调式或幻想管弦风格。
- 生成一份可编辑的编曲蓝图：旋律、答句、和声、点彩、低音和节拍声部。
- 在浏览器里展示音高轨迹、钢琴键盘、章节字幕、粒子数量和多轨时间线。
- 后端使用 Python 标准库，无需安装第三方依赖。
- `public/demo/` 中包含上一轮原创草稿的 WAV、MIDI 与 MusicXML，可作为后续音源和视频渲染的输入。

## 启动

```powershell
cd C:\Users\xiajt\Documents\trae-project\ai-music-video-studio
python server.py
```

打开 <http://localhost:4173>。

## 项目结构

```text
server.py                 # 本地 HTTP 服务与 /api/compose 生成接口
data/style_profiles.json  # 调式、音阶、配器、颜色和章节字幕配置
public/index.html         # 工作台界面
public/styles.css         # 暗色蓝黑、发光轨道和响应式布局
public/app.js             # 生成、渲染和交互逻辑
public/demo/              # 可试听和继续编辑的示例资产
docs/video-reference.md   # 参考视频拆解和产品路线
```

## 下一阶段

1. 用 music21 / MIDIUtil 把 composition JSON 真正导出为 MIDI 和 MusicXML。
2. 接入 MIDI-GPT 做多轨 continuation / infill，再回到 MuseScore 人工修谱。
3. 用 Remotion、Blender 或 FFmpeg 根据同一时间线生成 MP4：音符轨迹、钢琴键、节拍闪光、粒子和章节字幕共用时间轴。
4. 接入真实音源或 YuE2 / Magenta RealTime 2，增加音频渲染与实时伴奏。
5. 加入项目保存、版本对比、导出队列和登录后的云端任务。

## 许可

代码采用 MIT License。`public/demo/` 中的原创草稿由本项目生成；参考视频只用于研究其公开的视觉与音乐可视化方法。
