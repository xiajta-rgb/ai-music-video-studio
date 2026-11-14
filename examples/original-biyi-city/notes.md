# 开源编曲项目调研与《比翼城夜行曲》原创草稿

日期：2026-10-31

## 1. 结论先说

如果目标是“节奏丰富、乐器丰富、可以继续人工改”的古典/游戏场景配乐，当前最实用的组合不是押注单一模型，而是：

1. **MuseScore Studio**：负责打开、检查、改谱、导出 PDF / MIDI / MusicXML；
2. **music21 或 Abjad + LilyPond**：用代码生成和批量改写声部、和声、节奏与配器；
3. **MIDI-GPT**：尝试多轨续写、补写某一小节或改变声部密度；
4. **Magenta RealTime 2 / YuE2**：需要更强的本地 GPU/特定平台时，再用于音色或音频层面的探索。

本次草稿采用了第 1、2 类工具的思路，直接生成可编辑的多轨 MIDI / MusicXML，并用本地合成器做了一个可试听 WAV。没有调用原曲音频，也没有复写《比翼城》的旋律。

## 2. 值得关注的开源项目

| 项目 | 适合做什么 | 现状与限制 |
|---|---|---|
| [MuseScore Studio](https://github.com/musescore/MuseScore) | 人工作曲、总谱校对、MIDI / MusicXML / MEI 交换、回放与导出 | GPL-3.0；官方仓库列出 WYSIWYG、MusicXML、MIDI、MEI 和内置回放/合成器。2026 年仍有 4.7.x 版本发布。 |
| [music21](https://github.com/cuthbertLab/music21) | 计算音乐学、和声/曲式分析、批量生成或改写谱面 | BSD-3-Clause；Python 工具包，适合把“动机、和弦、节奏型、配器规则”写成可重复的脚本。仓库当前约 2.6k stars。 |
| [Abjad](https://github.com/Abjad/abjad) + [LilyPond](https://lilypond.org/) | 程序化作曲与高质量制谱 | Abjad 把音符、休止、和弦、连音、符杠等表示为 Python 对象，再交给 LilyPond 排版；适合复杂节奏和精细总谱，但安装链更重。 |
| [MIDI-GPT](https://www.metacreation.net/projects/midi-gpt) | 多轨 MIDI 的续写、补写、风格/密度/复音/音符时长控制 | Transformer 符号模型；支持 128 种 GM 乐器、10 条以上声部、bar/track 级 infill，并可控制乐器、音符密度、复音度等。更适合“给定草稿后续写”，不应直接当成最终总谱。 |
| [Magenta RealTime 2](https://magenta.withgoogle.com/magenta-realtime-2) | 实时、可演奏的 AI 音乐伴奏和音色实验 | 2026 年公开的 2.4B open-weights 模型，接受 MIDI、音频和文字控制；官方提供 JAX/MLX Python 库和 C++ 引擎。当前重点是低延迟现场生成，平台与硬件要求较明显。 |
| [YuE2](https://github.com/tidesea/yue) | “符号计划 → 完整音频”的生成与编辑 | 先生成可读的旋律/和弦计划，再生成音频；支持编辑计划、续写和改编。官方快速开始要求 Linux、Python 3.12、NVIDIA BF16、约 24GB 显存，且项目偏歌曲/音频生成，古典器乐需要额外约束。 |

### 选择建议

- **想要稳定写出古典总谱**：MuseScore + music21/Abjad。
- **想让模型补齐多轨**：先写 8–16 小节人工作品，再让 MIDI-GPT 做 continuation / infill，之后回到 MuseScore 修正声部进行与可演奏性。
- **想直接得到“像成品”的音频**：可以试 YuE2 或 Magenta RealTime 2，但要先确认显存、系统和模型许可；它们更适合做声音草图，不替代总谱编辑。

## 3. 这次原创草稿的设计

- **标题**：比翼城夜行曲（原创草稿）
- **时长**：约 51.4 秒
- **速度 / 拍号**：♩=112，6/8
- **调性**：D 小调，混入自然小调、Dorian 和大调借用和弦
- **声部**：长笛、独奏小提琴、双簧管、竖琴、钢片琴、弦乐铺底、大提琴/低音、打击乐
- **节奏**：6/8 的滚动竖琴、错位钢片琴、低音四拍型、框鼓/沙锤、B/C 段加密的八分音符型
- **曲式**：A（轻灵主题）— B（高八度与答句）— C（密度提升）— A'（收束）
- **氛围处理**：参考公开报道中对《QQ自由幻想》背景音乐“灵动、行云流水、轻快、浪漫”的描述，把重点放在流动感、明亮点缀和幻想城市夜景上；未提取或复写《比翼城》原曲的旋律。

## 4. 输出文件

- `biyi_cheng_original.wav`：立体声试听版；使用程序化合成音色，便于快速听结构与节奏。
- `biyi_cheng_original.mid`：8 轨 MIDI，可导入 MuseScore、Reaper、LMMS、Ableton 等继续换音源和混音。
- `biyi_cheng_original.musicxml`：可在 MuseScore 中打开的总谱交换格式。
- `biyi_cheng_original.json`：速度、调性、声部和音符数量等元数据。

## 5. 下一轮最值得做的改进

1. 在 MuseScore 中把长笛主题、双簧管答句和弦乐分层校对，并加连奏/断奏/力度记号；
2. 用真实管弦音源替换程序化 WAV，特别是木管、竖琴和打击乐；
3. 将 A' 段扩写到 90–120 秒，增加一段带转调的中段；
4. 把 8 小节主题作为 MIDI-GPT 的 continuation / infill 输入，只让模型补写背景声部，再人工筛选；
5. 如需出版级谱面，再用 Abjad/LilyPond 重排连线、符杠、力度与分页。

## 6. 版权与使用边界

本次交付是原创的旋律/和声/配器草稿，只借鉴场景气质。QQ自由幻想及其原声属于原权利人；若要公开发布“致敬/改编”版本，应另行确认原曲授权，并避免把本草稿宣传为官方曲目或原曲扒谱。
