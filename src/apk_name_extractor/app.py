from __future__ import annotations

import csv
import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import xml.etree.ElementTree as ET
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext

VALUES_DIRS = {
    "values": "Default language",
    "values-zh": "Chinese fallback",
    "values-zh-rCN": "Chinese (Mainland China)",
    "values-zh-rTW": "Chinese (Taiwan)",
    "values-zh-rHK": "Chinese (Hong Kong)",
    "values-b+zh+Hans": "Chinese (Hans, BCP 47)",
    "values-b+zh+Hant": "Chinese (Hant, BCP 47)",
}

APKTOOL_JAR_PATTERN = "apktool_*.jar"
APP_NAME_KEYS = ("app_name",)
CHINESE_VALUE_PRIORITY = (
    "values-zh-rCN",
    "values-b+zh+Hans",
    "values-zh",
    "values-zh-rHK",
    "values-zh-rTW",
    "values-b+zh+Hant",
)
DISPLAY_NAME_PRIORITY = CHINESE_VALUE_PRIORITY + ("values",)


def app_root() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def java_available() -> bool:
    java_cmd = shutil.which("java")
    if not java_cmd:
        return False
    result = subprocess.run(
        [java_cmd, "-version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def detect_apktool() -> tuple[list[str] | None, str]:
    root = app_root()
    candidates: list[Path] = []

    for base_dir in (root, root / "tools"):
        exact_files = sorted(base_dir.glob(APKTOOL_JAR_PATTERN), reverse=True)
        candidates.extend(exact_files)

    for jar_path in candidates:
        if jar_path.exists():
            if not java_available():
                return None, f"Found {jar_path}, but Java is not installed."
            return ["java", "-jar", str(jar_path)], f"Using bundled jar: {jar_path}"

    apktool_cmd = shutil.which("apktool")
    if apktool_cmd:
        return [apktool_cmd], f"Using system apktool: {apktool_cmd}"

    return None, (
        "apktool not found. Add tools/apktool_<version>.jar or install the `apktool` command."
    )


def load_string_resources(strings_path: Path) -> dict[str, str]:
    if not strings_path.exists():
        return {}
    try:
        tree = ET.parse(strings_path)
        root = tree.getroot()
        resources: dict[str, str] = {}
        for string_node in root.findall("string"):
            key = string_node.attrib.get("name")
            if key:
                resources[key] = string_node.text or ""
        return resources
    except Exception as exc:
        return {"__parse_error__": f"Parse failed: {strings_path.name} ({exc})"}


def resolve_value(raw_value: str, resources: dict[str, str], depth: int = 0) -> str:
    if not raw_value:
        return ""
    if depth > 5:
        return raw_value
    if raw_value.startswith("@string/"):
        ref_key = raw_value.split("/", 1)[1]
        ref_value = resources.get(ref_key, "")
        if not ref_value:
            return raw_value
        return resolve_value(ref_value, resources, depth + 1)
    return raw_value


def get_app_name(strings_path: Path) -> str:
    resources = load_string_resources(strings_path)
    if "__parse_error__" in resources:
        return resources["__parse_error__"]
    for key in APP_NAME_KEYS:
        if key in resources:
            return resolve_value(resources[key], resources)
    return ""


def pick_preferred_name(row_by_dir: dict[str, str], priority: tuple[str, ...]) -> str:
    for values_dir in priority:
        value = row_by_dir.get(values_dir, "").strip()
        if value:
            return value
    return ""


def extract_names(apk_dir: Path, output_csv: Path, log_func) -> None:
    apktool_base_cmd, detail = detect_apktool()
    if not apktool_base_cmd:
        raise RuntimeError(detail)

    log_func(detail)
    unpack_dir = apk_dir / "_unpacked"
    unpack_dir.mkdir(exist_ok=True)
    framework_dir = unpack_dir / "_apktool_framework"
    framework_dir.mkdir(exist_ok=True)

    apk_files = sorted(path for path in apk_dir.iterdir() if path.suffix.lower() == ".apk")
    if not apk_files:
        raise RuntimeError("No APK files found in the selected folder.")

    rows: list[list[str]] = []
    for apk_path in apk_files:
        package_name = apk_path.stem
        output_path = unpack_dir / package_name

        log_func(f"Unpacking {apk_path.name} ...")
        if not output_path.exists():
            cmd = [
                *apktool_base_cmd,
                "d",
                str(apk_path),
                "-o",
                str(output_path),
                "-f",
                "-p",
                str(framework_dir),
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if result.returncode != 0:
                log_func(f"Failed to unpack {apk_path.name}")
                rows.append([package_name] + ["<unpack failed>"] * len(VALUES_DIRS))
                continue
            log_func(f"Finished {apk_path.name}")
        else:
            log_func(f"Reuse existing unpacked folder: {output_path}")

        row = [package_name]
        row_by_dir: dict[str, str] = {}
        for values_dir in VALUES_DIRS:
            strings_file = output_path / "res" / values_dir / "strings.xml"
            app_name = get_app_name(strings_file)
            row_by_dir[values_dir] = app_name
            row.append(app_name)
        preferred_chinese_name = pick_preferred_name(row_by_dir, CHINESE_VALUE_PRIORITY)
        preferred_display_name = pick_preferred_name(row_by_dir, DISPLAY_NAME_PRIORITY)
        row.extend([preferred_chinese_name, preferred_display_name])
        rows.append(row)

    with output_csv.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.writer(file_obj)
        header = ["package_name"] + [
            f"{name} ({description})" for name, description in VALUES_DIRS.items()
        ]
        header.extend(["preferred_chinese_name", "preferred_display_name"])
        writer.writerow(header)
        writer.writerows(rows)


def start_gui() -> None:
    root = tk.Tk()
    root.title("APK Name Extractor")
    root.geometry("680x440")

    apk_dir_var = tk.StringVar()
    csv_path_var = tk.StringVar()

    tk.Label(root, text="APK Folder:").pack(pady=5)
    tk.Entry(root, textvariable=apk_dir_var, width=78).pack()

    def choose_apk_dir() -> None:
        path = filedialog.askdirectory(title="Choose a folder with APK files")
        if path:
            apk_dir_var.set(path)

    tk.Button(root, text="Browse...", command=choose_apk_dir).pack(pady=5)

    tk.Label(root, text="Output CSV:").pack(pady=5)
    tk.Entry(root, textvariable=csv_path_var, width=78).pack()

    def choose_csv_path() -> None:
        path = filedialog.asksaveasfilename(
            title="Choose the output CSV file",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if path:
            csv_path_var.set(path)

    tk.Button(root, text="Browse...", command=choose_csv_path).pack(pady=5)

    tk.Label(root, text="Log:").pack(pady=5)
    log_text = scrolledtext.ScrolledText(root, height=12, state="disabled")
    log_text.pack(fill="both", expand=True, padx=10, pady=5)

    def log(message: str) -> None:
        log_text.configure(state="normal")
        log_text.insert(tk.END, message + os.linesep)
        log_text.see(tk.END)
        log_text.configure(state="disabled")

    def run_extract() -> None:
        if not apk_dir_var.get() or not csv_path_var.get():
            messagebox.showwarning("Missing input", "Choose the APK folder and output CSV first.")
            return

        apk_dir = Path(apk_dir_var.get())
        output_csv = Path(csv_path_var.get())

        def task() -> None:
            try:
                extract_names(apk_dir, output_csv, log)
            except Exception as exc:
                messagebox.showerror("Error", str(exc))
                return
            messagebox.showinfo("Done", f"CSV created at:\n{output_csv}")

        threading.Thread(target=task, daemon=True).start()

    tk.Button(root, text="Start", command=run_extract, bg="#2e7d32", fg="white").pack(pady=10)

    apktool_cmd, detail = detect_apktool()
    status = detail if apktool_cmd else f"Dependency warning: {detail}"
    tk.Label(root, text=status, wraplength=620, justify="left", fg="#444444").pack(pady=6)

    root.mainloop()
