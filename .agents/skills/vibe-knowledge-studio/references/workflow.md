# 工程接口

所有命令在工具根目录执行；Python需已安装 requirements.txt，Chrome可用系统浏览器或 `python -m playwright install chromium`。`VIBE_CHROME` 和 `VIBE_FFMPEG` 可覆盖二进制位置。

```sh
python studio.py doctor
python studio.py new projects/my-film --title '主题' --duration 120
python studio.py validate projects/my-film
python studio.py docs projects/my-film
python studio.py audio projects/my-film
python studio.py review projects/my-film
python studio.py preview projects/my-film --port 8765
python studio.py render projects/my-film --start 0 --end 20 --width 1280
python studio.py render projects/my-film
```

项目结构以 `projects/frame-story` 为完整参考。`new` 只是可运行骨架；必须继续研究和创作，不能当成成片。

- `project.json`：title、duration秒、width/height偶数、fps、scenes、subtitles、sources、claims、assets。
- scenes：id、start、end、title、visual、description。全片时间无重叠无间隙；visual对应 scenes.js 的注册名。`cards` 为基础兜底，不应代替整个短片的设计。
- subtitles：start、end、text（用换行分两行）、kind（fact或editorial）、claims（主张ID列表）。不要用editorial绕过事实查证。
- sources：id、title、url、checked_at。claims：id、text、sources、status、evidence（摘要，不复制长段原文）。
- assets：name、origin、license。素材只有记录并不保证合法，需编辑实际检查使用条件。
- audio：可配置 file（相对路径）、bpm、beat_origin；省略file时合成基础原创音轨。修改音乐设置后重新运行audio，以免沿用旧音轨。audio.wav与audio.preview供浏览器同步播放。实际拍点需要听一遍。

## 自定义镜头

```js
Vibe.register('orbit', ({ctx,t,lt,s,p,text,ball,line,box,clamp,ease}) => {
  // 坐标统一按1920×1080设计，输出分辨率由引擎缩放。
  const angle=lt*.7;
  ball(960+320*Math.cos(angle),510+150*Math.sin(angle),24);
  text('轨道示意',960,760,36);
});
```

画面内容建议在y=240–820，标题在178，字幕在950附近；顶部和底部有栏目文字。文字函数只检测宽度，不自动缩放或换行；过长时编辑短句/字号/分行。复杂画面的物体碰撞和叙事正确性仍需看图。

`review/qa.json`记录抽样数量、乱序重复绘制结果、浏览器异常、文字宽度和阅读速度提示。reading_warnings以每秒7字符为启发式参考，不是可读性认证。render在失败时不把partial文件改成final；成功后记录实际解码帧数、元数据和校验摘要。

默认引擎只提供一种深色基础外观和卡片兜底，演示另有6种镜头；新作品由Agent按主题编写新镜头和样式，不承诺任意主题自动套模板都达到演示质量。
