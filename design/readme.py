"""Write the GitHub Profile README with theme and reduced-motion variants."""
from pathlib import Path

RAW='https://raw.githubusercontent.com/Bluuok/Bluuok/main/assets/'
def picture(name,alt,mobile=True,animated=True):
    sources=[]
    variants=[True,False] if mobile else [False]
    for small in variants:
        device='(max-width: 600px) and ' if small else ''
        prefix=f'{name}{"-mobile" if small else ""}'
        if animated:
            sources.append(f'  <source media="{device}(prefers-color-scheme: dark) and (prefers-reduced-motion: reduce)" srcset="{RAW}{prefix}-dark-still.svg" />')
            sources.append(f'  <source media="{device}(prefers-reduced-motion: reduce)" srcset="{RAW}{prefix}-light-still.svg" />')
        sources.append(f'  <source media="{device}(prefers-color-scheme: dark)" srcset="{RAW}{prefix}-dark.svg" />')
        if small:
            sources.append(f'  <source media="(max-width: 600px)" srcset="{RAW}{prefix}-light.svg" />')
    sources.append(f'  <img width="100%" alt="{alt}" src="{RAW}{name}-light.svg" />')
    return '<picture>\n'+'\n'.join(sources)+'\n</picture>'

def badge(name,label,link=None):
    image=f'<img alt="{label}" src="{RAW}badge-{name}.svg" />'
    return f'<a href="{link}">{image}</a>' if link else image

def main():
    hero=picture('hero','Bluuok：AI 应用与 Agent 工作台。金属晶格逐步移动，持续把问题变成可用工具。')
    thread=picture('threadcove','ThreadCove 架构示意：提出问题，在连续对话中按需搜索、阅读网页和协作子任务，将资料与成果保存在当前研究档案。研究工具由 Pi 后端提供。')
    claw=picture('clawtide','Clawtide 架构示意：Web、Telegram 和飞书进入数字员工工作区，执行并留下会话及记录。飞书需配置事件订阅；QQ、钉钉、微信、Discord、WhatsApp 为规划接入，灰色虚线不代表可用。')
    stats=picture('folio-stats','3 个 Folio PR 已合并、1 个上游项目、2 个重点项目。',animated=False)
    calendar=picture('contributions','Bluuok 公开贡献图，2026-10-05 快照，装饰性蛇形动画。',mobile=False)
    header='\n  '.join([badge('featured-threadcove','Featured: ThreadCove','https://github.com/Bluuok/ThreadCove'),badge('featured-clawtide','Featured: Clawtide','https://github.com/Bluuok/Clawtide'),badge('header-merged','Folio: 3 merged PRs','#open-source-contributions')])
    tech='\n  '.join(badge(n,n.title()) for n in ['typescript','react','electron','bun','node','hono','sqlite','mcp'])
    text=f'''{hero}

<p align="center">
  {header}
</p>

我是 **Bluu**，关注 AI 应用、Agent 工作流和开发者工具。喜欢把零散的问题、资料与执行过程，整理成能运行、能追溯、能继续迭代的工作台。

- 维护 [ThreadCove](https://github.com/Bluuok/ThreadCove)，让连续对话、资料检索、子任务协作与研究档案留在同一处。
- 开发 [Clawtide](https://github.com/Bluuok/Clawtide)，一个可自托管的 AI 数字员工工作台，基于 HappyClaw 的机制设计进行二次开发。
- 为 [helsome/folio](https://github.com/helsome/folio) 贡献存储并发、Markdown 解析与输入边界修复，已有 **3 个 PR 合并到上游**。

## Featured projects

重点维护与开发的两个项目，先从它们看起。

### [ThreadCove](https://github.com/Bluuok/ThreadCove) · 个人 AI 研究工作台

{thread}

从一个问题开始，在连续对话中整理资料、追问依据，让结论和文件回到当前研究档案。

- **研究工具**：Pi 后端提供公开网页搜索、网页读取与独立研究子任务；模型按需选择工具。
- **独立档案**：每项研究保留独立会话和文件目录，支持归档与继续研究。
- **桌面 + Web**：共用研究工作台与事件协议；Pi、DeepSeek、Claude 适配的能力各有差异。

<sub>动图为架构流程示意，使用合成问题；不代表每次执行都经过全部步骤。[查看项目实际界面](https://github.com/Bluuok/ThreadCove#产品预览)。</sub>

### [Clawtide](https://github.com/Bluuok/Clawtide) · 可自托管的 AI 数字员工

{claw}

将角色、独立工作区、连续会话、计划任务和执行记录组织在一起，让任务有明确入口，也有可回看的结果。

- **已接入**：Web、Telegram；飞书已验证长连接，消息事件投递需要配置事件订阅。
- **规划接入**：QQ、钉钉、微信、Discord、WhatsApp；目前为适配骨架与 mock 测试，尚不代表可用渠道。
- **执行与记录**：Claude Agent SDK 连接工作区和会话，计划任务经同一 Runtime 执行并保存结果。

<sub>动图为架构流程示意。Clawtide 基于 [HappyClaw](https://github.com/riba2534/HappyClaw) 的机制设计进行二次开发并重新实现架构，保留上游 [MIT 版权与来源声明](https://github.com/Bluuok/Clawtide/blob/main/LICENSE)。</sub>

## Open-source contributions

来自可核验的上游合并记录；开放 PR 不计入合并数量。

{stats}

| 上游项目 | 已合并 | 贡献内容 |
| :--- | :---: | :--- |
| [helsome/folio](https://github.com/helsome/folio) | **3** | 存储并发、Markdown 解析、输入边界 |

- [#109](https://github.com/helsome/folio/pull/109) · 修复并发 JSON 写入，隔离临时文件。
- [#110](https://github.com/helsome/folio/pull/110) · 修复嵌套 Markdown 代码围栏与 CRLF 解析。
- [#111](https://github.com/helsome/folio/pull/111) · 拦截报告 ID 的路径穿越。

[查看开放 PR](https://github.com/helsome/folio/pulls?q=is%3Apr+is%3Aopen+author%3ABluuok)

<sub>合并记录核对于 2026-10-05，统计范围仅为上表 Folio 项目。</sub>

## Tech

<p align="center">
  {tech}
</p>

## Contributions

{calendar}

<sub>基于 Bluuok 的公开 GitHub 贡献图，快照日期 2026-10-05；蛇形轨迹为装饰动画。深浅色和减少动态效果模式均有对应版本。[图形生成源码](design/build.py) · [素材来源与许可](NOTICE.md)</sub>

---

如果这些项目对你有帮助，欢迎留下 issue，或一起把下一个问题做成工具。

<sub>主页视觉与金属晶格动画经作者许可改编自 [sclfcz/sclfcz](https://github.com/sclfcz/sclfcz)。</sub>
'''
    (Path(__file__).resolve().parents[1]/'README.md').write_text(text,encoding='utf-8')

if __name__=='__main__':
    main()
