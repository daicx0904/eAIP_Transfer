import csv
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

RESERVED_WINDOWS_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def validate_replacement(replacement: str) -> None:
    """验证文件名替换规则。"""
    if INVALID_FILENAME_CHARS.search(replacement):
        raise ValueError("invalid_filename_replacement 包含非法文件名字符")

    if replacement.endswith((" ", ".")):
        raise ValueError("invalid_filename_replacement 不能以空格或句点结尾")


def sanitize_filename(name: str, replacement: str = "_") -> str:
    """清理文件名，兼容 Windows 文件系统。"""
    validate_replacement(replacement)

    filename = INVALID_FILENAME_CHARS.sub(replacement, name)
    filename = filename.rstrip(" .")

    if not filename:
        filename = "unnamed"

    if filename.split(".")[0].upper() in RESERVED_WINDOWS_NAMES:
        filename = f"_{filename}"

    return filename


def get_unique_path(path: Path) -> Path:
    """目标文件重名时追加编号。"""
    if not path.exists():
        return path

    index = 1

    while True:
        candidate = path.with_name(f"{path.stem} ({index}){path.suffix}")

        if not candidate.exists():
            return candidate

        index += 1


class PdfCopier:
    """根据航图记录复制 PDF 文件。"""

    def __init__(
        self,
        dir_source: Path,
        dir_target: Path,
        replacement_filename: str = "_",
    ):
        self.dir_source = dir_source.resolve()
        self.dir_target = dir_target.resolve()
        self.replacement_filename = replacement_filename

        validate_replacement(replacement_filename)

        if self.dir_source == self.dir_target:
            raise ValueError("origin 与 target 指向同一个目录，" "请检查 config.json")

    def copy_pdf(self, record: dict) -> Path:
        """复制 PDF 并返回最终目标路径。"""
        name = record.get("name_cn")
        path_pdf = record.get("pdfPath")

        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"无效的航图名称: {name!r}")

        if not isinstance(path_pdf, str) or not path_pdf.strip():
            raise ValueError(f"无效的 PDF 路径: {path_pdf!r}")

        path_relative = Path(path_pdf.lstrip("/\\").replace("\\", "/"))

        if path_relative.is_absolute() or ".." in path_relative.parts:
            raise ValueError(f"不是有效的相对路径: {path_pdf}")

        path_source = (self.dir_source / path_relative).resolve()

        try:
            path_source.relative_to(self.dir_source)
        except ValueError as exc:
            raise ValueError(f"PDF 路径超出源目录范围: {path_pdf}") from exc

        if not path_source.is_file():
            raise FileNotFoundError(f"源文件不存在: {path_source}")

        category = path_source.parent.name
        dir_destination = self.dir_target / category
        dir_destination.mkdir(parents=True, exist_ok=True)

        filename = sanitize_filename(
            name.strip(),
            self.replacement_filename,
        )

        path_destination = dir_destination / (f"{filename}{path_source.suffix}")

        path_destination = get_unique_path(path_destination)

        shutil.copy2(path_source, path_destination)

        return path_destination


class ChartCopyApp:
    """航图批量复制应用。"""

    REPORT_FIELDS = [
        "index",
        "id",
        "name_cn",
        "pdfPath",
        "status",
        "output_path",
        "error",
    ]

    def __init__(self):
        file_config = Path(__file__).resolve().parent / "config.json"

        with file_config.open("r", encoding="utf-8-sig") as file:
            config = json.load(file)

        for key in ("origin", "target"):
            value = config.get(key)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"config.json 缺少有效配置项: {key}")

        self.dir_source = Path(config["origin"]).resolve()
        self.dir_target = Path(config["target"]).resolve()

        if not self.dir_source.is_dir():
            raise NotADirectoryError(f"源目录不存在: {self.dir_source}")

        replacement = config.get("invalid_filename_replacement", "_")

        if not isinstance(replacement, str):
            raise ValueError("invalid_filename_replacement 必须是字符串")

        self.copier_pdf = PdfCopier(
            self.dir_source,
            self.dir_target,
            replacement,
        )

        path_json = self.dir_source / "Data" / "JsonPath" / "AD.json"

        with path_json.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("AD.json 的顶层数据必须是 JSON 数组")

        self.records_pdf = [
            record
            for record in data
            if isinstance(record, dict) and record.get("pdfPath")
        ]

    def create_report_path(self) -> Path:
        """生成本次运行专用的 CSV 报告路径。"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        path_report = self.dir_target / f"copy_report_{timestamp}.csv"

        return get_unique_path(path_report)

    def run(self) -> None:
        """复制航图并实时写入 CSV 报告。"""
        self.dir_target.mkdir(parents=True, exist_ok=True)

        path_report = self.create_report_path()

        count_success = 0
        count_failure = 0
        total = len(self.records_pdf)

        with path_report.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.REPORT_FIELDS,
            )
            writer.writeheader()
            file.flush()

            for index, record in enumerate(self.records_pdf, start=1):
                path_output = ""
                message_error = ""

                try:
                    destination = self.copier_pdf.copy_pdf(record)
                    path_output = str(destination)
                    status = "成功"
                    count_success += 1

                    print(f"[{index}/{total}] 成功: {destination}")

                except (OSError, ValueError, TypeError) as exc:
                    status = "失败"
                    message_error = str(exc)
                    count_failure += 1

                    print(f"[{index}/{total}] 失败: {message_error}")

                writer.writerow(
                    {
                        "index": index,
                        "id": record.get("id", ""),
                        "name_cn": record.get("name_cn", ""),
                        "pdfPath": record.get("pdfPath", ""),
                        "status": status,
                        "output_path": path_output,
                        "error": message_error,
                    }
                )

                file.flush()

        print(
            f"\n处理完成：成功 {count_success} 个，"
            f"失败 {count_failure} 个，总计 {total} 个。"
        )
        print(f"CSV 报告：{path_report}")


if __name__ == "__main__":
    app = ChartCopyApp()
    app.run()
