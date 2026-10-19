# 来源与主张

说明：verified 是编辑核查状态，不代表程序自动判断事实真伪。

## S1 · MDN · Canvas Basic animations
https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Basic_animations
核查日期：2026-10-19

## S2 · MDN · requestAnimationFrame
https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame
核查日期：2026-10-19

## S3 · FFmpeg documentation
https://ffmpeg.org/ffmpeg.html
核查日期：2026-10-19

### C1 · Canvas动画可通过更新画布内容生成一系列画面。
出处：S1
MDN Basic animations 描述清除、绘制和循环更新画布的步骤；本演示用确定性时间函数离线求值。

### C2 · 动画位置可以由时间计算，而不是单纯按回调次数递增。
出处：S2
MDN建议根据时间戳计算动画进度，并给出 elapsed × speed 的位置示例。

### C3 · 逐帧图像可由FFmpeg编码为视频；30帧每秒乘10秒为300帧。
出处：S3
FFmpeg文档说明输入帧率、媒体输入和编码过程；帧数为设定的帧率与时长之积。
