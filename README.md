# APK Name Extractor

一个批量拆解 APK、提取多语言 `app_name`，并导出为 CSV 表格的可视化小工具。

## 适用场景

当你手上有一批 Android APK，想快速查看它们在不同语言资源下的应用名称时，这个工具可以直接帮你把结果整理成一张表。

适合用于：

- 游戏或应用素材盘点
- APK 包名与显示名对照整理
- 多语言名称核对
- 批量审核前的信息预处理

## 功能

- 批量扫描指定文件夹中的 `.apk`
- 使用 `apktool` 自动拆包
- 提取多个 `res/values*/strings.xml` 中的 `app_name`
- 自动生成 `preferred_chinese_name` 与 `preferred_display_name` 两列，方便直接做表
- 导出为 `CSV` 表格
- 提供简单的桌面图形界面，方便非命令行使用

当前默认提取这些目录中的名称：

- `values`
- `values-zh`
- `values-zh-rCN`
- `values-zh-rTW`
- `values-zh-rHK`
- `values-b+zh+Hans`
- `values-b+zh+Hant`

## 项目结构

```text
apk-name-extractor/
  README.md
  pyproject.toml
  src/
    apk_name_extractor/
      __init__.py
      __main__.py
      app.py
      launcher.py
  tools/
    .gitkeep
  build/
    apk_name_extractor.spec
```

## 运行依赖

本项目依赖 `apktool` 才能完成 APK 拆包。

程序会按下面的顺序查找依赖：

1. 打包后的应用目录中的 `apktool_*.jar`
2. 仓库里的 `tools/apktool_*.jar`
3. 系统环境中的 `apktool` 命令

如果你使用的是 `jar` 方式，还需要本机安装 Java。

本项目调用的 APK 拆包能力来自 [Apktool](https://github.com/iBotPeaches/Apktool)。

如果你想手动下载 release 文件，可以直接参考它的官方发布页：

- [Apktool Releases](https://github.com/iBotPeaches/Apktool/releases)

## 快速开始

先进入项目目录：

```bash
cd /Users/yumeyume/Documents/Playground/apk-name-extractor
```

然后启动程序：

```bash
PYTHONPATH=src python3 -m apk_name_extractor
```

## 如何放置 apktool

如果你准备把 `apktool` 作为仓库内置依赖，建议把文件放在：

```text
tools/apktool_3.0.1.jar
```

文件名只要符合 `apktool_*.jar` 即可。

这样项目在本地运行和 PyInstaller 打包时都能优先找到它。

## 输出结果

程序会生成一份 CSV，包含：

- APK 文件名对应的包名
- 各个 `values` 目录下提取到的 `app_name`
- `preferred_chinese_name`
- `preferred_display_name`
- 未找到时的空值
- 拆包失败时的失败标记

这两个额外字段的意义是：

- `preferred_chinese_name`：优先从简体中文、中文 fallback、港澳台繁体等目录中挑一个最合适的中文名称
- `preferred_display_name`：如果没有更合适的中文值，则进一步回退到默认 `values`

## 打包为 macOS App

先安装 PyInstaller：

```bash
python3 -m pip install pyinstaller
```

再执行打包：

```bash
cd /Users/yumeyume/Documents/Playground/apk-name-extractor
PYTHONPATH=src pyinstaller build/apk_name_extractor.spec
```

生成结果会出现在 `dist/` 目录下。

## 关于 DMG

`.dmg` 只是 macOS 的分发包装，不会自动解决运行依赖问题。

如果你要发布给别人使用，推荐顺序是：

1. 先维护好 GitHub 仓库版本
2. 再构建 `.app`
3. 最后按需要封装成 `.dmg`

## 当前状态

项目代码已经完成项目化整理，但是否能真正执行拆包，取决于你本地是否提供了可用的 `apktool` 与 Java 运行环境。

## License

如需公开发布，建议你补充自己的许可证说明，例如 `MIT`。
