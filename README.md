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
```

## 运行依赖

本项目依赖 `apktool` 才能完成 APK 拆包。

程序会按下面的顺序查找依赖：

1. 仓库里的 `tools/apktool_*.jar`
2. 系统环境中的 `apktool` 命令

如果你使用的是 `jar` 方式，还需要本机安装 Java。

本项目调用的 APK 拆包能力来自 [Apktool](https://github.com/iBotPeaches/Apktool)。

如果你想手动下载 release 文件，可以直接参考它的官方发布页：

- [Apktool Releases](https://github.com/iBotPeaches/Apktool/releases)

## 快速开始

先进入项目目录：

```bash
cd apk-name-extractor
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

这样项目在本地运行时就能优先找到它。

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

## 当前状态

项目代码已经完成项目化整理，但是否能真正执行拆包，取决于你本地是否提供了可用的 `apktool` 与 Java 运行环境。

## License

本项目当前使用仓库内提供的非商用许可证，允许使用、修改和再发布，但不允许商用。详情见 [LICENSE](LICENSE)。

## Third-Party Notices

本项目使用了第三方工具 `Apktool` 进行 APK 拆包。

- 项目地址: [iBotPeaches/Apktool](https://github.com/iBotPeaches/Apktool)
- 发布页: [Apktool Releases](https://github.com/iBotPeaches/Apktool/releases)
- 许可协议: Apache License 2.0

更完整的第三方声明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
