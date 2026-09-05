# 面向 LoongArch 国产自主指令集的 CPU 设计实践

本目录是可独立维护的 **XeLaTeX 书籍工程**。日常写作直接修改 `.tex`，生成 PDF 不需要 RStudio、R、bookdown、knitr、Pandoc、Python 或联网，也不需要原 `designpractice` 目录。

## 编译与阅读

在本目录运行：

```sh
latexmk main.tex
```

输出为 **`build/main.pdf`**。工程已配置 XeLaTeX、自动多轮编译、SyncTeX 和输出目录；不要选用 pdfLaTeX。

- Windows：也可以运行 `build.cmd`。须让选定的 TeX Live 或 MiKTeX 的 `latexmk` 在 PATH 中。
- WSL / Linux / macOS：也可以运行 `sh build.sh`。
- VS Code：打开整个目录，安装或启用 LaTeX Workshop，打开 `main.tex` 后执行 Build LaTeX project。工程配置已提供，保存时会自动编译。
- TeXworks / TeXstudio：选择 XeLaTeX 或 latexmk 构建主文件 `main.tex`。交叉引用和目录需要多轮编译，推荐 latexmk。

日常命令：

```sh
latexmk main.tex       # 生成 / 更新 PDF
latexmk -pvc main.tex  # 监听修改并自动重编译，Ctrl+C 停止
latexmk -c main.tex    # 清理中间文件，保留 PDF
```

需要含中文支持的 TeX 发行版：`ctex`、Fandol、fontspec、unicode-math、listings、xeCJK-listings、longtable、booktabs、hyperref、bookmark、xurl、latexmk 等。迁移时已在本机 WSL 的 TeX Live 2025 环境实际完成全书编译；Windows 原生执行环境尚未实测。

程序代码使用接近原稿的 Latin Modern Mono，中文注释使用 Fandol 仿宋；目录树和日志使用随附的 DejaVu Sans Mono，以覆盖线条和特殊空格。工程随附 DejaVu Sans Mono 的四种字形及其许可说明；正文使用 TeX 自带 Fandol 和 Latin Modern。无需安装宋体、仿宋等 Windows 字体。复制或压缩整个目录即可携带书稿和全部图片，`assets/`、`fonts/` 均不是指向旧工程的符号链接。

## 文件组织

```text
main.tex                 书籍主文件、章节顺序
config/book-info.tex     书名、作者、日期、PDF 元数据
config/preamble.tex      字体、页边距和图表样式
config/code-style.tex    代码配色、语言规则及代码环境
chapters/*.tex           22 份分章书稿（含前言和后记资料）
assets/                  55 个原始图片与制图源文件
fonts/                   等宽字体及许可说明
build/main.pdf           编译完成的书籍
examples/code-styles.tex 字体对照和全部语言高亮样张
latexmkrc                XeLaTeX 自动编译设置
build.sh / build.cmd     命令行便捷入口
.vscode/settings.json    LaTeX Workshop 配置
migration/               迁移变更说明、来源清单和验收记录
scripts/check_project.py 可选的结构 / 迁移完整性检查
```

前言及目录使用罗马页码，18 个正文章节使用阿拉伯页码，总结、参考文献、相关资料仍不编号。保留原书的 Letter 纸型和大致页边距，允许字体、代码自动折行及错误修复带来分页变化。

## 以后如何修改

**正文：** 修改 `chapters/` 中对应章节。每个文件第一行指定了主文件，编辑器可以从分章跳转到整书构建。以后以这里的 `.tex` 为主稿，旧 Rmd 不会自动同步。

**标题和引用：** `\chapter`、`\section`、`\subsection` 对应章、节、小节。现有标签已经整理为 ASCII。插图先写 `\caption`，再写 `\label`；正文使用 `图\ref{fig:example}`，不要再使用 bookdown 的 `\@ref(...)`。

```tex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\linewidth]{assets/01/soc.png}
  \caption{示例图标题}
  \label{fig:example}
\end{figure}
```

**代码：** `CodeBlock` 内可以直接粘贴原始代码，不要给 `$`、`_`、`#` 等字符加 LaTeX 转义。用 `language` 选择语言，`listings` 在每次 XeLaTeX 编译时自动生成语法高亮。代码可跨页，长行自动折行；代码内容不会执行。构建继续使用 `-no-shell-escape`。

```tex
\begin{CodeBlock}[language=BookShell]
make -j$(nproc)
\end{CodeBlock}
```

全书 111 个代码块均已明确标注语言，其中 106 个程序、配置和命令块启用语法配色，5 个目录树、示意图或终端输出按纯文本排版。新加代码请按下表选择；自定义语言可集中添加到 `config/code-style.tex`。

| 代码内容 | `language` 值 |
|---|---|
| Verilog / SystemVerilog | `BookVerilog` / `BookSystemVerilog` |
| Scala、Chisel、SpinalHDL | `BookScala` |
| C | `BookC` |
| Shell、终端命令 | `BookShell` |
| LoongArch 汇编 | `BookLoongArch` |
| 设备树 DTS | `BookDTS` |
| EDA Tcl 脚本 | `BookTcl` |
| Makefile | `BookMake` |
| Kconfig / defconfig | `BookConfig` |
| 链接脚本 | `BookLinker` |
| 伪代码（Python 风格） | `BookPseudo` |
| Diff 补丁 | `BookDiff` |
| 目录树、文本示意图、日志 | `BookText` |

关键词使用深蓝，类型和领域标识使用紫色，注释使用绿色，字符串使用棕色，搭配浅底色和细边线。关键词另加粗，便于黑白打印时识别。不同语言只对其支持的语法类别着色；伪代码按本书示例配置。纯文本显式写 `language=BookText`，不要将终端输出当作 Shell 源码。

字体与配色对照样张可独立重编译：

```sh
latexmk examples/code-styles.tex
```

输出为 `build/code-styles.pdf`。修改 `config/preamble.tex` 中的 `\setmonofont` 可调整程序等宽字体；配色和字号位于 `config/code-style.tex`。

行内代码可写 `\texttt{reset\_n}`。Shell 命令尤其不要直接放入正文，否则 `$` 容易被当成数学定界符。网址使用 `\url{https://example.com/path}`，可以点击和自动折行。

**表格：** 现有表格使用 `longtable`，可跨页。段落型单元格中用 `\newline{}` 换行，表格行用 `\\` 结束；不要插入 HTML `<br>`。

**文献：** `chapters/30-references.tex` 保留原稿 20 条手工参考文献。当前不运行 BibTeX / Biber；若以后改成自动引用，应单独建立真实的书籍文献数据库。

**书名和样式：** 修改 `config/book-info.tex` / `config/preamble.tex`。日期默认是编译当天；需要固定版本日期时，可将 `\date{\today}` 改成具体日期。需要 A4 或出版社开本时修改 `main.tex` 的纸型选项及页边距，然后重新检查全书。

## GitHub 同步维护

远程仓库：<https://github.com/BUAA-CI-LAB/designpractice>，主分支为 `main`。
书稿、图片、字体、配置及迁移记录纳入版本管理；`build/` 下的书籍 PDF（`main.pdf`）和代码样张（`code-styles.pdf`）也同步到仓库，便于直接下载阅读。编译缓存、日志和 SyncTeX 等中间文件继续忽略。
修改书稿或代码样式后，请重新编译对应的 PDF，并与源文件一起提交。

本目录已关联远程仓库。在本目录开始修改前，先拉取远程更新（工作区应无未提交修改）：

```sh
git pull --ff-only
```

修改完成并确认编译正常后，检查改动、提交并上传：

```sh
git status
git diff
git add .
git commit -m "更新章节内容"
git push
```

提交说明应替换成这次修改的实际内容。保存文件不会自动上传，`git commit` 记录本地版本，`git push` 才会同步到 GitHub。
如果拉取或推送提示本地与远程分支分叉，先运行 `git fetch origin`，再用 `git log --oneline --graph --all` 查看双方提交，合并并解决冲突后再推送；不要直接强制推送。

换电脑时，克隆仓库即可继续维护：

```sh
git clone https://github.com/BUAA-CI-LAB/designpractice.git
cd designpractice
latexmk main.tex
```

推送需要使用具有该仓库写权限的 GitHub 账号完成 Git 身份验证。
`.gitattributes` 统一 Git 中的文本换行，并为 Shell 和 Windows 批处理脚本保留适合各自平台的换行格式。

## 可选检查

Python 仅用于下面的辅助审计，**不参与 PDF 构建**：

```sh
python3 scripts/check_project.py --require-build
python3 scripts/check_project.py --baseline --require-build
```

第一条检查引用、图片、代码语言、残留标记和编译日志；第二条还对照迁移基线核查原有 109 个代码块的内容与顺序、55 个资源的哈希，以及章节、图表等数量。以后主动改写内容或替换图片时，基线检查报告变化是预期行为，不能把旧基线当成写作限制。

本工程修复了迁移中确认的写法和排版问题，具体见 [迁移说明](migration/迁移说明.md)。芯片架构、寄存器定义、代码功能正确性及外部资料是否更新，需要后续按出版校审要求另行审阅。
