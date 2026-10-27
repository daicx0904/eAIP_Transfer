# eAIP_Transfer

**一个用于将 eAIP 航图 PDF 文件的默认文件名转换为规范、易读且便于查找的文件名的工具。**

eAIP 是 _Electronic Aeronautical Information Publication_（电子航空情报资料汇编）的缩写。相关资料通常包括 **AIP（航行资料汇编）、SUP（补充资料）、AIC（航空情报通报）和 NOTAM（航行通告）** 等内容。

本项目主要针对 eAIP 资料中的 AIP 航图 PDF 文件，通过解析资料中的相关信息，将原本难以辨认的默认文件名转换为更符合人类阅读习惯的文件名，方便用户整理、查找和使用航图。

本项目的主要目标是：

- **规范文件命名：** 将不易识别的默认文件名转换为具有可读性的文件名。
- **便于航图管理：** 让用户能够通过文件名快速识别和查找所需航图。
- **本地处理：** 在本地读取和处理已经下载的 eAIP 资料，无须通过本项目下载资料。
- **灵活配置：** 允许用户自行指定源资料目录、转换目标目录以及非法文件名字符的替换规则。

## 注意事项

> [!WARNING]
> 本项目采用本地运行的方式，**不会在程序内提供 eAIP 资料的下载功能**。
>
> 使用前，请自行获取所需的 eAIP 资料包，并按照下文说明完成解压和配置。
>
> 本项目的处理范围为 AIP 相关 PDF 文件，不应将其视为完整的 eAIP 资料管理工具。

## 从源代码运行

> [!IMPORTANT]
> 本项目使用 [uv](https://github.com/astral-sh/uv) 管理 Python 版本、虚拟环境和项目依赖。
>
> 如果尚未安装 uv，请先完成安装。推荐使用 uv 管理运行环境，而不是手动安装和配置项目依赖。
>
> - [uv 官方仓库与安装说明](https://github.com/astral-sh/uv)
> - [uv 中文文档：安装 uv](https://uv.doczh.com/getting-started/installation/)

### 1. 准备 eAIP 资料包

1. 打开 [eAIP 官网](https://www.eaipchina.cn/)。
2. 登录 eAIP 账户；如果尚未注册，请先完成注册。
3. 在页面顶栏找到 `DOWNLOAD`，点击后选择 `Full Package`，下载完整资料包。
4. 将下载的资料包解压到本地目录。

建议将资料包解压到**路径中不包含空格、且仅使用英文字母、数字及常见路径分隔符的目录**，以减少路径兼容性问题。

解压完成后，请确认资料目录中存在 `index.html` 文件。后续配置时，需要将该文件所在的目录指定为源资料目录。

### 2. 准备 Python 环境

请先确认 uv 已正确安装，然后打开终端，执行以下命令安装项目所需的 Python 版本：

```bash
uv python install 3.12.10
```

安装完成后，执行以下命令查看 uv 已识别的 Python 版本：

```bash
uv python list
```

您应该会看到类似以下内容的输出：

```text
cpython-3.12.13-windows-x86_64-none    <download available>
cpython-3.12.10-windows-x86_64-none    C:\xxx\python.exe
cpython-3.11.15-windows-x86_64-none    <download available>
```

如果 `cpython-3.12.10` 对应的条目显示了实际的 Python 可执行文件路径，例如 `C:\xxx\python.exe`，则说明 uv 已安装并识别该版本。

如果该版本仍显示为 `<download available>`，请重新执行安装命令，并检查安装过程是否成功。

### 3. 克隆项目

```bash
git clone https://github.com/daicx0904/eAIP_Transfer.git
cd eAIP_Transfer
```

### 4. 配置项目

使用文本编辑器打开项目根目录下的 `config.json`。

根据自己的实际目录修改以下配置项：

| 配置项                         | 说明                                          |
| ------------------------------ | --------------------------------------------- |
| `origin`                       | eAIP 源资料目录，即包含 `index.html` 的目录。 |
| `target`                       | 转换后文件的目标目录，用于存放处理结果。      |
| `invalid_filename_replacement` | 用于替换 Windows 文件名中不允许使用的字符。   |

配置示例如下：

```json
{
	"origin": "D:/eAIP",
	"target": "D:/eAIP_Converted",
	"invalid_filename_replacement": "_"
}
```

> [!NOTE]
> 上述配置仅用于说明填写方式，请根据项目中实际的 `config.json` 结构修改对应字段，不要直接覆盖其他已有配置项。

#### `origin`

填写 eAIP 资料解压后的根目录，即 `index.html` 所在的目录。

例如：

```text
D:/eAIP
```

如果实际文件位于 `D:/eAIP/index.html`，则 `origin` 应填写 `D:/eAIP`，而不是 `D:/eAIP/index.html`。

#### `target`

填写转换结果的存放目录。

例如：

```text
D:/eAIP_Converted
```

目标目录不要求为空，但**不得与源资料目录相同**。建议使用独立的目标目录，以便区分原始资料与转换结果。

#### `invalid_filename_replacement`

该字段用于指定 Windows 文件名中非法字符的替代字符。

AIP 航图名称中可能包含 `/`、`:` 等不能直接用于 Windows 文件名的字符，因此需要将其替换为合法字符。

默认情况下，可以使用下划线 `_`：

```json
"invalid_filename_replacement": "_"
```

您也可以根据个人习惯更换为其他合法字符，但该字段**不能为空**。

### 5. 安装依赖并运行

在项目根目录下执行：

```bash
uv sync
uv run main.py
```

请根据程序的实际输出判断转换是否成功。首次运行前，请再次确认 `config.json` 中的源目录和目标目录填写正确。

## 作者

- **Daicx**（[@Daicx0904](https://github.com/daicx0904)）

## 特别致谢

- **ChatGPT** 帮我找出可能存在的bug并完善了代码命名规范

## 注意事项与免责声明

- 本项目仅用于对用户已经获取的 eAIP 资料进行本地文件处理，不提供资料下载服务。
- 本项目的处理范围为 AIP 相关 PDF 文件，不代表对 SUP、AIC、NOTAM 等其他资料类型提供完整支持。
- 请确保您有权获取、保存和处理所使用的 eAIP 资料，并遵守资料提供方的相关使用条款。
- 航图及其他航空情报资料可能随时间更新。文件名转换仅用于文件整理，不代表资料内容经过核验，也不保证资料的时效性、完整性或适航使用有效性。
- **本项目不能替代官方航空情报资料，也不能作为判断航行信息有效性的依据。** 实际飞行及其他航空活动应以适用的官方资料和相关运行程序为准。
- 使用本项目处理文件前，建议保留原始资料备份。对于因配置错误、文件处理或其他使用行为造成的数据丢失、文件损坏或其他损失，用户应自行承担相应风险。
- 本项目按开源许可证提供，不对其适用性、准确性或特定用途的可用性作出超出许可证规定的保证。

本项目采用 [GNU General Public License v3.0（GPL-3.0）](https://www.gnu.org/licenses/gpl-3.0.html) 许可证。详情请参阅项目根目录下的 [LICENSE](./LICENSE) 文件。

欢迎在遵守许可证条款的前提下使用、修改和分发本项目。

## 支持项目

如果您觉得 `eAIP_Transfer` 对您有所帮助，欢迎前往 [GitHub 项目页面](https://github.com/daicx0904/eAIP_Transfer) 点亮一颗 **Star**。
