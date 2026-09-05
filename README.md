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

需要含中文支持的 TeX 发行版：`ctex`、Fandol、fontspec、unicode-math、fvextra、longtable、booktabs、hyperref、bookmark、xurl、latexmk 等。迁移时已在本机 WSL 的 TeX Live 2025 环境实际完成全书编译；Windows 原生执行环境尚未实测。

工程随附 DejaVu Sans Mono 的四种字形及其许可说明；中文使用 TeX 自带 Fandol，西文使用 Latin Modern。无需安装宋体、仿宋等 Windows 字体。复制或压缩整个目录即可携带书稿和全部图片，`assets/`、`fonts/` 均不是指向旧工程的符号链接。

## 文件组织

```text
main.tex                 书籍主文件、章节顺序
config/book-info.tex     书名、作者、日期、PDF 元数据
config/preamble.tex      字体、页边距、代码和图表样式
chapters/*.tex           22 份分章书稿（含前言和后记资料）
assets/                  55 个原始图片与制图源文件
fonts/                   等宽字体及许可说明
build/main.pdf           编译完成的书籍
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

**代码：** `CodeBlock` 内可以直接粘贴 Verilog、C、Shell 等原始代码，不要给 `$`、`_`、`#` 等字符加 LaTeX 转义。代码可跨页，长行自动折行；语法不执行。为方便维护，已将旧的逐词高亮宏改为统一的等宽代码排版。

```tex
\begin{CodeBlock}
make -j$(nproc)
\end{CodeBlock}
```

行内代码可写 `\texttt{reset\_n}`。Shell 命令尤其不要直接放入正文，否则 `$` 容易被当成数学定界符。网址使用 `\url{https://example.com/path}`，可以点击和自动折行。

**表格：** 现有表格使用 `longtable`，可跨页。段落型单元格中用 `\newline{}` 换行，表格行用 `\\` 结束；不要插入 HTML `<br>`。

**文献：** `chapters/30-references.tex` 保留原稿 20 条手工参考文献。当前不运行 BibTeX / Biber；若以后改成自动引用，应单独建立真实的书籍文献数据库。

**书名和样式：** 修改 `config/book-info.tex` / `config/preamble.tex`。日期默认是编译当天；需要固定版本日期时，可将 `\date{\today}` 改成具体日期。需要 A4 或出版社开本时修改 `main.tex` 的纸型选项及页边距，然后重新检查全书。

## 可选检查

Python 仅用于下面的辅助审计，**不参与 PDF 构建**：

```sh
python3 scripts/check_project.py --require-build
python3 scripts/check_project.py --baseline --require-build
```

第一条检查引用、图片、残留标记和编译日志；第二条还对照迁移基线核查原有 109 个代码块的内容与顺序、55 个资源的哈希，以及章节、图表等数量。以后主动改写内容或替换图片时，基线检查报告变化是预期行为，不能把旧基线当成写作限制。

本工程修复了迁移中确认的写法和排版问题，具体见 [迁移说明](migration/迁移说明.md)。芯片架构、寄存器定义、代码功能正确性及外部资料是否更新，需要后续按出版校审要求另行审阅。
