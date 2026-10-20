# 实现来源与参考说明

本仓库是本次人机协作中由 Codex 编写的初版实现，包含工作流 Skill、Python CLI、Canvas 运行时、演示镜头、基础程序配乐及校验脚本。它不是从某个第三方视频 Skill 直接复制、fork 或改名发布的项目。

## 参考了什么

创作方法参考了公开的「Vibe 知识大赏」教程与工程：资料核查、字幕和分镜、短样片、按时间绘制画面、逐帧导出、音频合成以及成片QA。这些是参考来源，不意味着下列作者参与本工程或对其背书。

- [六步制作教程（抖音）](https://www.douyin.com/video/7692352215482240296)：研究 → 编排 → 素材 → 风格与分镜 → 检查 → 输出。
- [HeyChengC/vibe-knowledge-film](https://github.com/HeyChengC/vibe-knowledge-film)：参考公开说明中的样片、Canvas确定性绘制、抽帧与渲染方法。
- [worlds3/vibe-knowledge](https://github.com/worlds3/vibe-knowledge)：参考公开流程中的BGM分析、分镜和关键时刻检查方法。
- [LuZhong-Li/vibe-knowledge-video-skill](https://github.com/LuZhong-Li/vibe-knowledge-video-skill)：参考公开的来源记录、制作分阶段与验收思路。
- [Jogzh/concept-reel](https://github.com/Jogzh/concept-reel)：参考公开的Canvas、Playwright、FFmpeg工具链说明。

本次没有把这些项目的 Skill 文本、引擎代码、样例字幕、图像或音频复制进本仓库；这是对本次实现过程的说明，不是对互联网全部代码进行相似度检测后的唯一性保证。确定性时间绘制等通用技术不主张为本工程首创。

## 直接依赖与文档

- [Playwright Python](https://playwright.dev/python/docs/screenshots)：浏览器运行、页面交互与截图，遵循其许可。
- [FFmpeg](https://ffmpeg.org/ffmpeg.html)：编码、混音转换与解码核验，遵循所用二进制的许可。
- [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg)：提供FFmpeg定位及媒体元数据读取。
- NumPy、Pillow：音频合成、图像接触表。
- [MDN Canvas动画](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Basic_animations)与[时间戳动画](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame)：演示片事实来源。

本工程没有集成 Remotion 或 HyperFrames；它们属于调研过的替代路线。当前实现为 Canvas + Playwright + FFmpeg。

## 素材

演示《一帧之间》的文字、布局、图形和镜头由本次协作制作；基础音轨由本地数学合成，没有使用网上流行BGM。系统字体只用于本机绘制，未随仓库分发。具体来源和素材记录见演示的 `project.json` 与 `research.md`。

本项目是经过本机短片验证的基础工具，能力和验证边界见 `VALIDATION.md`。不声称已达到某个参考作者成片的创作或美学水准。

## 2026-10-20：编辑方法补充调研

本轮进一步阅读成熟科普作者的一手方法、教学研究、第三方拆片文档及平台说明，独立整理成 `references/editorial-playbook.md` 和 `references/editorial-sources.md`。这些不是复制来的Skill文本；它们明确记录了方法来源、采纳理由及不采纳的硬性模板。第三方拆片仍是第三方观察，不能标成我们亲自观看原片后的结论。

来源登记中的出版社论文摘要和教学指南只按实际访问层级使用；正文中的归纳、操作字段与生日问题前期练习为本工程适配。原站图片、原片字幕、完整分镜及受限全文未转载。相关教育研究不能直接证明短视频流量表现。
