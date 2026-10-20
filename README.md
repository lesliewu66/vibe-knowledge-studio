# Vibe Studio

本地知识动画工作流：联网Agent研究与创作 → 来源/字幕/分镜 → Canvas动画 → 预览与抽帧QA → 原创基础配乐或导入音乐 → MP4。

选题、文案和分镜的方法依据、实际改进及限制见 [编辑方法调研](EDITORIAL_RESEARCH.md)；完整前期练习见 [生日问题](editorial-examples/birthday/brief.md)。新流程已写入项目Skill，尚未完成真实观众理解测试。

## 直接看成片

演示位于 `projects/frame-story/renders/final.mp4`：原创36秒《一帧之间》，1920×1080、30fps、无旁白。使用原创程序音轨，没有复用网上爆款的文案或BGM。

## 安装与预览

```sh
git clone git@github.com:lesliewu66/vibe-knowledge-studio.git
cd vibe-knowledge-studio
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python studio.py doctor
```

使用本机 Chrome/Edge；若未安装，先运行 `.venv/bin/python -m playwright install chromium`。预览：

```sh
.venv/bin/python studio.py preview projects/frame-story
```

打开命令显示的本地URL即可播放、暂停和拖动；音轨在点击播放后开始。按Ctrl+C关闭服务。

## 新一期

把本目录作为Codex项目打开，项目技能在 `.agents/skills/vibe-knowledge-studio`。也可以在对话中明确要求读取其中的SKILL.md，例如：

> 使用本项目的 vibe-knowledge-studio，制作一条讲「沉没成本为什么影响选择」的约2分钟知识动画。先查一手来源，再做字幕分镜和20秒样片；样片给我确认后再做全片。不要复用现有爆款文案和音乐。

不要求样片确认时，可以明确授权从选题做到成片。这个CLI不直接连接模型；它由对话中的编程助手驱动，不是离开Agent也能自动研究题目的服务。

```sh
python studio.py new projects/my-film --title '你的题目' --duration 120
# 由Agent完成project.json的研究、字幕和分镜，并编写scenes.js。
python studio.py validate projects/my-film
python studio.py docs projects/my-film
python studio.py audio projects/my-film
python studio.py review projects/my-film
python studio.py render projects/my-film --end 20 --width 1280
python studio.py render projects/my-film
```

## 在另一台机器配置

需要Python 3.14或与依赖版本兼容的Python。可在独立虚拟环境内安装，系统Chrome/Edge可以复用。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
# 若没有Chrome/Edge：
.venv/bin/python -m playwright install chromium
.venv/bin/python studio.py doctor
```

Windows使用 `.venv\Scripts\python`。FFmpeg优先复用PATH或VIBE_FFMPEG，找不到时使用imageio-ffmpeg随包二进制。依赖的跨平台安装未在其他系统验证。

## 交付文件与边界

- `project.json`、`research.md`：来源和主张；verified为编辑声明，代码不自动判断真假。
- `scenes.js`、`runtime.js`、`index.html`：可修改动画和本地播放器。
- `storyboard.md`、`subtitles.srt`：分镜和字幕。
- `audio.wav`、`audio-analysis.json`：基础音乐、采样峰/RMS与配置BPM网格；不是自动音乐理解或LUFS认证。
- `review/`：关键时刻接触表、封面、结构与确定性报告。不能替代全片人工审阅。
- `renders/`：H.264/AAC成片、渲染日志、解码核验和元数据。
- `publish.md`：发布草稿；不自动发布。

默认画风与音乐为工程基线；内容研究、视觉隐喻、新镜头和美学打磨依赖Agent与编辑。没有自动TTS、无人值守发布、爆款预测。当前产物验证记录见 `VALIDATION.md`。

工程代码和原创演示按MIT许可，见LICENSE；系统字体文件未随工程分发。Playwright、FFmpeg和Python依赖遵守各自许可。工作流参考与实现来源见 [PROVENANCE.md](PROVENANCE.md)。
