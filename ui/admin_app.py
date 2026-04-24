from __future__ import annotations

import subprocess
import threading
import webbrowser
from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk
from modules import membership
from ui.design_tokens import (
    BG_APP,
    BORDER,
    BORDER_STRONG,
    DANGER_BG,
    DANGER_TEXT,
    PRIMARY_BLUE,
    PRIMARY_BLUE_SOFT,
    PRIMARY_BLUE_TEXT,
    SUCCESS_BG,
    SUCCESS_TEXT,
    SURFACE,
    SURFACE_STRONG,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    WARNING_BG,
    WARNING_TEXT,
    font,
    primary_button_style,
    secondary_button_style,
)
from ui.ui_components import add_modal_actions, add_modal_header, create_modal, status_badge


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
REPORTS_DIR = ROOT / "reports"


class TaskCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        category: str,
        title: str,
        description: str,
        command: Callable[[], None],
        button_label: str,
        secondary_command: Optional[Callable[[], None]] = None,
        secondary_label: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=SURFACE, corner_radius=18, border_width=1, border_color=BORDER, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        badge_host = ctk.CTkFrame(self, fg_color="transparent")
        badge_host.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 0))
        status_badge(badge_host, category, "info").pack(anchor="w")

        ctk.CTkLabel(
            self,
            text=title,
            font=font(18, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(10, 4))

        ctk.CTkLabel(
            self,
            text=description,
            justify="left",
            wraplength=320,
            text_color=TEXT_MUTED,
            anchor="w",
            font=font(14),
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 14))

        ctk.CTkButton(
            btn_row,
            text=button_label,
            command=command,
            **primary_button_style(height=38),
        ).pack(side="left")

        if secondary_command and secondary_label:
            ctk.CTkButton(
                btn_row,
                text=secondary_label,
                command=secondary_command,
                **secondary_button_style(height=38),
            ).pack(side="left", padx=(8, 0))


class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("CareVL Admin")
        self.geometry("1200x780")
        self.minsize(1000, 680)
        self.configure(fg_color=BG_APP)

        self.is_running = False
        self._setup_ui()
        self.after(0, self._maximize_window)
        self._refresh_summary()

    def _maximize_window(self):
        try:
            self.state("zoomed")
        except Exception:
            self.attributes("-zoomed", True)

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(
            self,
            fg_color=SURFACE,
            corner_radius=24,
            border_width=1,
            border_color=BORDER,
        )
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 12))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(
            header,
            text="CareVL Admin",
            font=font(30, "bold"),
            text_color=TEXT_PRIMARY,
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(20, 0))

        ctk.CTkLabel(
            header,
            text="Quản lý danh sách trạm, tạo snapshot SQLite toàn hệ thống và build Hub DuckDB phục vụ thống kê.",
            text_color=TEXT_MUTED,
            font=font(14),
            wraplength=560,
            justify="left",
        ).grid(row=1, column=0, sticky="w", padx=22, pady=(6, 0))

        quick_meta = ctk.CTkFrame(header, fg_color="transparent")
        quick_meta.grid(row=2, column=0, sticky="w", padx=22, pady=(14, 20))
        status_badge(quick_meta, "Hub / Admin", "info").pack(side="left")
        status_badge(quick_meta, "Vận hành nội bộ", "success").pack(side="left", padx=(8, 0))

        top_actions = ctk.CTkFrame(header, fg_color="transparent")
        top_actions.grid(row=0, column=1, rowspan=3, sticky="e", padx=22)

        ctk.CTkButton(
            top_actions,
            text="Mở stations.csv",
            command=lambda: self._open_path(CONFIG_DIR / "stations.csv"),
            **secondary_button_style(height=38),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            top_actions,
            text="Làm mới",
            command=self._refresh_summary,
            **secondary_button_style(height=38),
        ).pack(side="left")

        ctk.CTkButton(
            top_actions,
            text="Duyệt user",
            command=self._open_user_registry_modal,
            **secondary_button_style(height=38),
        ).pack(side="left", padx=(8, 0))

        summary = ctk.CTkFrame(self, fg_color="transparent")
        summary.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))
        for col in range(4):
            summary.grid_columnconfigure(col, weight=1)

        self.csv_summary = self._build_summary_card(summary, "Stations CSV", "Đang đọc...", "Nguồn gốc", 0)
        self.json_summary = self._build_summary_card(summary, "stations.json", "Đang đọc...", "App config", 1)
        self.report_summary = self._build_summary_card(summary, "Checklist", "Đang đọc...", "Onboarding", 2)
        self.aggregate_summary = self._build_summary_card(summary, "Hub Data", "Đang đọc...", "Snapshot / DuckDB", 3)

        utility_row = ctk.CTkFrame(
            self,
            fg_color=SURFACE,
            corner_radius=18,
            border_width=1,
            border_color=BORDER,
        )
        utility_row.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 12))
        utility_row.grid_columnconfigure(0, weight=1)
        utility_row.grid_columnconfigure(1, weight=1)
        utility_row.grid_columnconfigure(2, weight=1)
        utility_row.grid_columnconfigure(3, weight=1)

        self._build_quick_link(utility_row, "Mở JSON", "Kiểm tra metadata branch đang dùng", lambda: self._open_path(CONFIG_DIR / "stations.json"), 0)
        self._build_quick_link(utility_row, "Mở Checklist", "Rà nhanh trạng thái onboarding", lambda: self._open_path(REPORTS_DIR / "onboarding_checklist.md"), 1)
        self._build_quick_link(utility_row, "Mở Hub", "Đi tới thư mục reports/hub", lambda: self._open_path(REPORTS_DIR / "hub"), 2)
        self._build_quick_link(utility_row, "Mở User Registry", "Duyệt user mới bằng config/user_registry.json", lambda: self._open_path(CONFIG_DIR / "user_registry.json"), 3)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 16))
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)

        self._build_section_header(
            left,
            row=0,
            title="Tác vụ hệ thống",
            body="Các thao tác chính để cập nhật cấu hình trạm, gom dữ liệu SQLite và dựng lớp báo cáo cho Hub.",
        )

        TaskCard(
            left,
            category="Validate",
            title="Kiểm tra danh sách trạm",
            description="Validate stations.csv, phát hiện thiếu dữ liệu, branch trùng, station_id trùng hoặc username không đúng quy ước.",
            command=lambda: self._run_script("scripts/check_station_registry.py"),
            button_label="Chạy kiểm tra",
            secondary_command=lambda: self._open_path(CONFIG_DIR / "stations.csv"),
            secondary_label="Mở CSV",
        ).grid(row=1, column=0, sticky="ew", pady=(0, 12))

        TaskCard(
            left,
            category="Build",
            title="Build stations.json",
            description="Sinh config/stations.json từ stations.csv để app user và Hub đọc được metadata branch, station_id và commune_code.",
            command=lambda: self._run_script("scripts/build_stations_json.py"),
            button_label="Build JSON",
            secondary_command=lambda: self._open_path(CONFIG_DIR / "stations.json"),
            secondary_label="Mở JSON",
        ).grid(row=2, column=0, sticky="ew", pady=(0, 12))

        self._build_section_header(
            left,
            row=3,
            title="Tổng hợp và đối soát",
            body="Dành cho checklist bàn giao, snapshot backup và chuẩn bị dữ liệu tổng hợp.",
        )

        TaskCard(
            left,
            category="Onboarding",
            title="Export onboarding checklist",
            description="Xuất checklist để Hub theo dõi onboarding từng trạm, gồm CSV và Markdown trong thư mục reports.",
            command=lambda: self._run_script("scripts/export_onboarding_checklist.py"),
            button_label="Xuất checklist",
            secondary_command=lambda: self._open_path(REPORTS_DIR / "onboarding_checklist.md"),
            secondary_label="Mở file",
        ).grid(row=4, column=0, sticky="ew", pady=(0, 12))

        TaskCard(
            left,
            category="Snapshot",
            title="Aggregate snapshot toàn hệ thống",
            description="Đọc SQLite DB từ main và các branch trạm, xuất manifest cùng bảng encounter phẳng để Hub backup hoặc đối soát.",
            command=lambda: self._run_script("scripts/aggregate_station_data.py"),
            button_label="Chạy aggregate",
            secondary_command=lambda: self._open_path(REPORTS_DIR / "aggregate"),
            secondary_label="Mở thư mục",
        ).grid(row=5, column=0, sticky="ew", pady=(0, 12))

        TaskCard(
            left,
            category="Hub",
            title="Build Hub DuckDB",
            description="Dựng reports/hub/carevl_hub.duckdb từ snapshot aggregate mới nhất và xuất các bảng summary cho thống kê, dashboard.",
            command=lambda: self._run_script("scripts/build_hub_duckdb.py"),
            button_label="Build DuckDB",
            secondary_command=lambda: self._open_path(REPORTS_DIR / "hub"),
            secondary_label="Mở Hub",
        ).grid(row=6, column=0, sticky="ew", pady=(0, 12))

        right = ctk.CTkFrame(content, fg_color=SURFACE, corner_radius=18, border_width=1, border_color=BORDER)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            right,
            text="Bảng điều phối",
            font=font(18, "bold"),
            text_color=TEXT_PRIMARY,
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            right,
            text="Theo dõi trạng thái tác vụ, đọc hướng dẫn nhanh và xem log chạy script tại đây.",
            font=font(13),
            text_color=TEXT_MUTED,
            wraplength=320,
            justify="left",
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 10))

        self.status_badge = ctk.CTkLabel(
            right,
            text="Sẵn sàng",
            fg_color=PRIMARY_BLUE_SOFT,
            text_color=PRIMARY_BLUE_TEXT,
            corner_radius=10,
            padx=10,
            pady=4,
            font=font(12, "semibold"),
        )
        self.status_badge.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 10))

        tip_panel = ctk.CTkFrame(right, fg_color=SURFACE_STRONG, corner_radius=14, border_width=1, border_color=BORDER_STRONG)
        tip_panel.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 12))
        ctk.CTkLabel(
            tip_panel,
            text="Quy trình khuyến nghị",
            font=font(13, "semibold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkLabel(
            tip_panel,
            text="1. Kiểm tra CSV\n2. Build JSON\n3. Xuất checklist\n4. Chạy aggregate SQLite\n5. Build Hub DuckDB",
            font=font(13),
            text_color=TEXT_SECONDARY,
            justify="left",
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(0, 12))

        log_header = ctk.CTkFrame(right, fg_color="transparent")
        log_header.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 6))
        log_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            log_header,
            text="Nhật ký tác vụ",
            font=font(16, "bold"),
            text_color=TEXT_PRIMARY,
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            log_header,
            text="Xóa log",
            command=self._clear_log,
            **secondary_button_style(width=90, height=30),
        ).grid(row=0, column=1, sticky="e")

        self.log_text = ctk.CTkTextbox(right, wrap="word")
        self.log_text.grid(row=5, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.log_text.insert(
            "end",
            "Admin App v1\n\n"
            "- Dùng để chạy tool quản trị, không dùng để nhập liệu như trạm.\n"
            "- Sửa nguồn dữ liệu tại config/stations.csv rồi chạy các tác vụ tương ứng.\n"
            "- Kết quả sẽ hiện tại đây và có thể mở file/folder ngay từ giao diện.\n",
        )
        self.log_text.configure(state="disabled")

    def _build_summary_card(self, master, title: str, value: str, subtitle: str, column: int) -> ctk.CTkLabel:
        card = ctk.CTkFrame(master, fg_color=SURFACE, corner_radius=18, border_width=1, border_color=BORDER)
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=title,
            text_color=TEXT_MUTED,
            anchor="w",
            font=font(13, "semibold"),
        ).grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))

        ctk.CTkLabel(
            card,
            text=subtitle,
            text_color=TEXT_SECONDARY,
            anchor="w",
            font=font(12),
        ).grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 4))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=font(22, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        value_label.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))
        return value_label

    def _build_quick_link(self, master, title: str, body: str, command: Callable[[], None], column: int) -> None:
        panel = ctk.CTkFrame(master, fg_color="transparent")
        panel.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 10, 0))
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text=title,
            font=font(13, "semibold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(
            panel,
            text=body,
            font=font(12),
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=240,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))
        ctk.CTkButton(
            panel,
            text="Mở",
            command=command,
            **secondary_button_style(width=84, height=30),
        ).grid(row=2, column=0, sticky="w", padx=14, pady=(0, 12))

    def _build_section_header(self, master, row: int, title: str, body: str) -> None:
        block = ctk.CTkFrame(master, fg_color="transparent")
        block.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(
            block,
            text=title,
            font=font(20, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            block,
            text=body,
            font=font(13),
            text_color=TEXT_MUTED,
            justify="left",
            anchor="w",
            wraplength=640,
        ).pack(anchor="w", pady=(4, 0))

    def _set_status(self, text: str, *, fg: str = PRIMARY_BLUE_SOFT, text_color: str = PRIMARY_BLUE_TEXT):
        self.status_badge.configure(text=text, fg_color=fg, text_color=text_color)

    def _append_log(self, text: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text.rstrip() + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", "Log đã được xóa.\n")
        self.log_text.configure(state="disabled")

    def _run_script(self, script_path: str):
        if self.is_running:
            self._append_log("\n[Busy] Đang có tác vụ khác chạy.\n")
            return

        self.is_running = True
        self._set_status("Đang chạy...", fg=WARNING_BG, text_color=WARNING_TEXT)
        self._append_log(f"\n> uv run python {script_path}\n")
        thread = threading.Thread(target=self._run_script_task, args=(script_path,), daemon=True)
        thread.start()

    def _run_script_task(self, script_path: str):
        try:
            completed = subprocess.run(
                ["uv", "run", "python", script_path],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=300,
                check=False,
            )
            output = (completed.stdout or "") + (completed.stderr or "")
            self.after(0, self._handle_script_result, script_path, completed.returncode, output)
        except Exception as exc:
            self.after(0, self._handle_script_result, script_path, 1, str(exc))

    def _handle_script_result(self, script_path: str, returncode: int, output: str):
        self.is_running = False
        if output.strip():
            self._append_log(output.strip() + "\n")

        if returncode == 0:
            self._set_status("Thành công", fg=SUCCESS_BG, text_color=SUCCESS_TEXT)
            self._append_log(f"[OK] Hoàn tất: {script_path}\n")
        else:
            self._set_status("Thất bại", fg=DANGER_BG, text_color=DANGER_TEXT)
            self._append_log(f"[ERROR] Tác vụ lỗi: {script_path}\n")

        self._refresh_summary()

    def _refresh_summary(self):
        self.csv_summary.configure(text=self._summarize_csv())
        self.json_summary.configure(text=self._summarize_json())
        self.report_summary.configure(text=self._summarize_checklist())
        self.aggregate_summary.configure(text=self._summarize_aggregate())

    def _open_user_registry_modal(self):
        dialog = create_modal(self, "Duyệt user mới", "1020x720")
        dialog.resizable(True, True)
        dialog.update_idletasks()
        screen_w = dialog.winfo_screenwidth()
        screen_h = dialog.winfo_screenheight()
        width = min(1020, max(880, screen_w - 120))
        height = min(720, max(620, screen_h - 140))
        pos_x = max(40, (screen_w - width) // 2)
        pos_y = max(40, (screen_h - height) // 2)
        dialog.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        dialog.minsize(880, 620)

        add_modal_header(
            dialog,
            "Duyệt user trong app",
            "Luồng gọn nhất là: chọn request ở tab Chờ duyệt, sang tab Duyệt để lưu quyền, rồi xem lại tab Registry nếu cần.",
        )

        body = ctk.CTkFrame(dialog, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        tabview = ctk.CTkTabview(
            body,
            fg_color="transparent",
            segmented_button_fg_color=SURFACE_STRONG,
            segmented_button_selected_color=PRIMARY_BLUE,
            segmented_button_selected_hover_color=PRIMARY_BLUE,
            segmented_button_unselected_color=SURFACE,
            segmented_button_unselected_hover_color=PRIMARY_BLUE_SOFT,
            text_color=TEXT_PRIMARY,
        )
        tabview.pack(fill="both", expand=True)

        pending_tab = tabview.add("Chờ duyệt")
        approve_tab = tabview.add("Duyệt")
        registry_tab = tabview.add("Registry")

        for tab in (pending_tab, approve_tab, registry_tab):
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(1, weight=1)

        selected_issue = {"value": ""}
        selected_registry_username = {"value": ""}
        pending_requests = {"items": []}
        registry_entries = {"items": []}
        pending_card_host = {"widget": None}
        registry_card_host = {"widget": None}

        def status_palette(level: str) -> tuple[str, str]:
            mapping = {
                "success": (SUCCESS_TEXT, SUCCESS_BG),
                "error": (DANGER_TEXT, DANGER_BG),
                "warning": (WARNING_TEXT, WARNING_BG),
                "info": (TEXT_SECONDARY, PRIMARY_BLUE_SOFT),
            }
            return mapping.get(level, (TEXT_SECONDARY, PRIMARY_BLUE_SOFT))

        def set_status(message: str, level: str = "info") -> None:
            text_color, bg_color = status_palette(level)
            status_label.configure(text=message, text_color=text_color, fg_color=bg_color)

        def suggest_branch(username: str) -> str:
            clean = str(username or "").strip()
            return f"user/{clean}" if clean else ""

        def suggest_title(username: str, branch_name: str, fallback: str = "") -> str:
            if fallback:
                return fallback
            clean_branch = str(branch_name or "").strip()
            clean_username = str(username or "").strip()
            station_title = membership.sync.get_station_title(clean_branch) if clean_branch else ""
            return station_title or clean_username or clean_branch

        def set_entry_value(entry: ctk.CTkEntry, value: str) -> None:
            entry.delete(0, "end")
            if value:
                entry.insert(0, value)

        def clear_preview() -> None:
            issue_preview.configure(state="normal")
            issue_preview.delete("1.0", "end")
            issue_preview.configure(state="disabled")

        def render_preview(issue: dict | None) -> None:
            issue_preview.configure(state="normal")
            issue_preview.delete("1.0", "end")
            if not issue:
                issue_preview.insert("end", "Chưa có request nào được nạp.")
            else:
                lines = [
                    f"Issue #{issue.get('issue_number') or '?'}",
                    issue.get("title", "") or "(không có tiêu đề)",
                ]
                if issue.get("username"):
                    lines.append(f"GitHub username: {issue.get('username')}")
                if issue.get("branch_name"):
                    lines.append(f"Branch: {issue.get('branch_name')}")
                if issue.get("display_title"):
                    lines.append(f"Tiêu đề hiển thị: {issue.get('display_title')}")
                body_text = str(issue.get("body", "") or "").strip()
                if body_text:
                    preview_text = body_text[:280]
                    if len(body_text) > 280:
                        preview_text += "..."
                    lines.append("")
                    lines.append(preview_text)
                issue_preview.insert("end", "\n".join(lines))
            issue_preview.configure(state="disabled")

        def apply_issue_data(issue: dict, *, switch_tab: bool = True, message: str = "") -> None:
            selected_issue["value"] = str(issue.get("issue_url", "") or "").strip()
            set_entry_value(issue_link_entry, selected_issue["value"])
            set_entry_value(username_entry, issue.get("username", ""))
            branch_name = str(issue.get("branch_name", "") or "").strip() or suggest_branch(issue.get("username", ""))
            set_entry_value(branch_entry, branch_name)
            title_value = suggest_title(issue.get("username", ""), branch_name, issue.get("display_title", ""))
            set_entry_value(title_entry, title_value)
            approved_var.set(True)
            render_preview(issue)
            if switch_tab:
                tabview.set("Duyệt")
            if message:
                set_status(message, "success")

        def open_issue_link() -> None:
            issue_url = issue_link_entry.get().strip() or selected_issue["value"]
            if not issue_url:
                set_status("Chưa có link issue để mở.", "warning")
                return
            try:
                webbrowser.open(issue_url)
                set_status("Đã mở issue trên GitHub.", "info")
            except Exception as exc:
                set_status(f"Không mở được issue: {exc}", "error")

        def fetch_issue_from_input(*, switch_tab: bool = True) -> bool:
            issue_url = issue_link_entry.get().strip()
            if not issue_url:
                set_status("Dán link issue GitHub trước khi nạp.", "warning")
                return False
            result = membership.fetch_join_request_issue(issue_url)
            if not result.get("ok"):
                set_status(result.get("message", "Không tải được issue."), "error")
                return False
            issue = result.get("issue") or {}
            apply_issue_data(issue, switch_tab=switch_tab, message=f"Đã nạp request từ issue #{issue.get('issue_number')}.")
            refresh_pending_requests(keep_selection=True)
            return True

        pending_summary = ctk.CTkLabel(
            pending_tab,
            text="Chọn một request ở đây rồi sang tab Duyệt để lưu quyền. Issue sẽ không còn bị chìm trong một modal dài.",
            font=font(12),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=780,
        )
        pending_summary.grid(row=0, column=0, sticky="ew", pady=(6, 10))

        pending_list_panel = ctk.CTkFrame(
            pending_tab,
            fg_color=SURFACE,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        pending_list_panel.grid(row=1, column=0, sticky="nsew")
        pending_list_panel.grid_columnconfigure(0, weight=1)
        pending_list_panel.grid_rowconfigure(1, weight=1)

        pending_toolbar = ctk.CTkFrame(pending_list_panel, fg_color="transparent")
        pending_toolbar.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        pending_toolbar.grid_columnconfigure(0, weight=1)
        pending_toolbar.grid_columnconfigure((1, 2, 3, 4), weight=0)

        pending_count_label = ctk.CTkLabel(
            pending_toolbar,
            text="Đang tải request...",
            font=font(13, "semibold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        pending_count_label.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            pending_toolbar,
            text="Làm mới",
            command=lambda: refresh_pending_requests(keep_selection=True),
            width=110,
            **secondary_button_style(height=34),
        ).grid(row=0, column=1, padx=(8, 0))

        ctk.CTkButton(
            pending_toolbar,
            text="Nạp issue",
            command=lambda: load_selected_request(select_tab=True),
            width=110,
            **secondary_button_style(height=34),
        ).grid(row=0, column=2, padx=(8, 0))

        ctk.CTkButton(
            pending_toolbar,
            text="Mở issue",
            command=open_issue_link,
            width=110,
            **secondary_button_style(height=34),
        ).grid(row=0, column=3, padx=(8, 0))

        ctk.CTkButton(
            pending_toolbar,
            text="Đóng issue",
            command=lambda: close_selected_issue(with_comment=False),
            width=110,
            **secondary_button_style(height=34),
        ).grid(row=0, column=4, padx=(8, 0))

        pending_card_frame = ctk.CTkScrollableFrame(
            pending_list_panel,
            fg_color="transparent",
            corner_radius=0,
        )
        pending_card_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        pending_card_frame.grid_columnconfigure(0, weight=1)
        pending_card_host["widget"] = pending_card_frame

        approve_summary = ctk.CTkLabel(
            approve_tab,
            text="Tab này chỉ lo duyệt quyền. Từ link issue, app tự điền thông tin cơ bản để bạn lưu nhanh.",
            font=font(12),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=780,
        )
        approve_summary.grid(row=0, column=0, sticky="ew", pady=(6, 10))

        approve_panel = ctk.CTkFrame(
            approve_tab,
            fg_color=SURFACE,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        approve_panel.grid(row=1, column=0, sticky="nsew")
        approve_panel.grid_columnconfigure(1, weight=1)
        approve_panel.grid_rowconfigure(6, weight=1)

        issue_link_entry = self._registry_input(
            approve_panel,
            0,
            "Link issue",
            "https://github.com/kanazawahere/carevl/issues/1",
        )

        issue_button_row = ctk.CTkFrame(approve_panel, fg_color="transparent")
        issue_button_row.grid(row=1, column=1, sticky="w", padx=(0, 16), pady=(8, 0))

        ctk.CTkButton(
            issue_button_row,
            text="Nạp từ link",
            command=fetch_issue_from_input,
            width=120,
            **secondary_button_style(height=34),
        ).pack(side="left")

        ctk.CTkButton(
            issue_button_row,
            text="Mở issue",
            command=open_issue_link,
            width=110,
            **secondary_button_style(height=34),
        ).pack(side="left", padx=(8, 0))

        username_entry = self._registry_input(approve_panel, 2, "GitHub username", "Ví dụ: bacsi-nguyen")
        branch_entry = self._registry_input(approve_panel, 3, "Branch", "Ví dụ: user/<github-username>")
        title_entry = self._registry_input(approve_panel, 4, "Tiêu đề hiển thị", "Ví dụ: Trạm Y Tế Phường 1")

        ctk.CTkLabel(
            approve_panel,
            text="Cho phép vào app",
            font=font(13, "semibold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).grid(row=5, column=0, sticky="w", padx=(16, 12), pady=(12, 0))

        approved_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            approve_panel,
            text="Bật quyền ngay sau khi lưu",
            variable=approved_var,
            onvalue=True,
            offvalue=False,
        ).grid(row=5, column=1, sticky="w", pady=(12, 0))

        ctk.CTkLabel(
            approve_panel,
            text="Xem nhanh request",
            font=font(13, "semibold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).grid(row=6, column=0, sticky="nw", padx=(16, 12), pady=(12, 0))

        issue_preview = ctk.CTkTextbox(
            approve_panel,
            height=120,
            wrap="word",
            fg_color=SURFACE_STRONG,
            border_color=BORDER_STRONG,
            text_color=TEXT_PRIMARY,
        )
        issue_preview.grid(row=6, column=1, sticky="nsew", padx=(0, 16), pady=(12, 0))
        issue_preview.configure(state="disabled")

        approve_actions = ctk.CTkFrame(approve_panel, fg_color="transparent")
        approve_actions.grid(row=7, column=0, columnspan=2, sticky="ew", padx=16, pady=(12, 0))
        approve_actions.grid_columnconfigure((0, 1), weight=1)

        registry_summary = ctk.CTkLabel(
            registry_tab,
            text="Tab này dành cho danh sách local hiện có. Chọn user đã có để nạp lại form hoặc xóa quyền khi cần.",
            font=font(12),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=780,
        )
        registry_summary.grid(row=0, column=0, sticky="ew", pady=(6, 10))

        registry_panel = ctk.CTkFrame(
            registry_tab,
            fg_color=SURFACE,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        registry_panel.grid(row=1, column=0, sticky="nsew")
        registry_panel.grid_columnconfigure(0, weight=1)
        registry_panel.grid_rowconfigure(1, weight=1)

        registry_toolbar = ctk.CTkFrame(registry_panel, fg_color="transparent")
        registry_toolbar.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        registry_toolbar.grid_columnconfigure(0, weight=1)
        registry_toolbar.grid_columnconfigure((1, 2, 3), weight=0)

        registry_count_label = ctk.CTkLabel(
            registry_toolbar,
            text="Đang tải registry...",
            font=font(13, "semibold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        registry_count_label.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            registry_toolbar,
            text="Làm mới",
            command=lambda: refresh_registry_list(keep_selection=True),
            width=110,
            **secondary_button_style(height=34),
        ).grid(row=0, column=1, padx=(8, 0))

        ctk.CTkButton(
            registry_toolbar,
            text="Nạp user",
            command=lambda: load_selected_registry(select_tab=True),
            width=110,
            **secondary_button_style(height=34),
        ).grid(row=0, column=2, padx=(8, 0))

        ctk.CTkButton(
            registry_toolbar,
            text="Mở file",
            command=lambda: self._open_path(CONFIG_DIR / "user_registry.json"),
            width=110,
            **secondary_button_style(height=34),
        ).grid(row=0, column=3, padx=(8, 0))

        registry_card_frame = ctk.CTkScrollableFrame(
            registry_panel,
            fg_color="transparent",
            corner_radius=0,
        )
        registry_card_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        registry_card_frame.grid_columnconfigure(0, weight=1)
        registry_card_host["widget"] = registry_card_frame

        status_label = ctk.CTkLabel(
            dialog,
            text="Chọn request ở tab Chờ duyệt hoặc nhập tay ở tab Duyệt.",
            font=font(12),
            text_color=TEXT_SECONDARY,
            fg_color=PRIMARY_BLUE_SOFT,
            corner_radius=10,
            anchor="w",
            justify="left",
            wraplength=900,
            padx=12,
            pady=8,
        )
        status_label.pack(fill="x", padx=18, pady=(0, 10))

        def render_pending_request_cards() -> None:
            host = pending_card_host["widget"]
            for child in host.winfo_children():
                child.destroy()

            items = pending_requests["items"]
            if not items:
                ctk.CTkLabel(
                    host,
                    text="Không có request chờ duyệt nào đang mở trên GitHub.",
                    font=font(13),
                    text_color=TEXT_MUTED,
                    anchor="w",
                    justify="left",
                    wraplength=780,
                ).grid(row=0, column=0, sticky="ew", padx=6, pady=6)
                return

            for index, item in enumerate(items):
                is_selected = selected_issue["value"] == str(item.get("issue_url", "") or "").strip()
                card = ctk.CTkFrame(
                    host,
                    fg_color=PRIMARY_BLUE_SOFT if is_selected else SURFACE_STRONG,
                    corner_radius=12,
                    border_width=1,
                    border_color=PRIMARY_BLUE if is_selected else BORDER,
                )
                card.grid(row=index, column=0, sticky="ew", padx=4, pady=4)
                card.grid_columnconfigure(0, weight=1)

                header = f"#{item.get('issue_number') or '?'}  {item.get('username') or '(chưa rõ username)'}"
                subtitle_bits = []
                if item.get("display_title"):
                    subtitle_bits.append(item.get("display_title"))
                if item.get("branch_name"):
                    subtitle_bits.append(item.get("branch_name"))
                subtitle = " | ".join(subtitle_bits) if subtitle_bits else item.get("title", "")

                ctk.CTkLabel(
                    card,
                    text=header,
                    font=font(14, "bold"),
                    text_color=TEXT_PRIMARY,
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))

                ctk.CTkLabel(
                    card,
                    text=subtitle or "(không có mô tả thêm)",
                    font=font(12),
                    text_color=TEXT_MUTED,
                    anchor="w",
                    justify="left",
                    wraplength=620,
                ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))

                ctk.CTkButton(
                    card,
                    text="Chọn",
                    width=88,
                    command=lambda issue=item: select_pending_request(issue, auto_load=False),
                    **secondary_button_style(height=30),
                ).grid(row=0, column=1, rowspan=2, sticky="e", padx=12, pady=10)

        def render_registry_cards() -> None:
            host = registry_card_host["widget"]
            for child in host.winfo_children():
                child.destroy()

            items = registry_entries["items"]
            if not items:
                ctk.CTkLabel(
                    host,
                    text="Chưa có user nào trong registry local.",
                    font=font(13),
                    text_color=TEXT_MUTED,
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew", padx=6, pady=6)
                return

            for index, item in enumerate(items):
                username = str(item.get("username", "") or "").strip()
                is_selected = selected_registry_username["value"] == username
                badge = "Đã duyệt" if item.get("approved") else "Tạm khóa"
                card = ctk.CTkFrame(
                    host,
                    fg_color=PRIMARY_BLUE_SOFT if is_selected else SURFACE_STRONG,
                    corner_radius=12,
                    border_width=1,
                    border_color=PRIMARY_BLUE if is_selected else BORDER,
                )
                card.grid(row=index, column=0, sticky="ew", padx=4, pady=4)
                card.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(
                    card,
                    text=username,
                    font=font(14, "bold"),
                    text_color=TEXT_PRIMARY,
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))

                ctk.CTkLabel(
                    card,
                    text=f"{item.get('branch_name', '')} | {item.get('title', '')} | {badge}",
                    font=font(12),
                    text_color=TEXT_MUTED,
                    anchor="w",
                    justify="left",
                    wraplength=620,
                ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))

                ctk.CTkButton(
                    card,
                    text="Chọn",
                    width=88,
                    command=lambda entry=item: select_registry_entry(entry, auto_load=False),
                    **secondary_button_style(height=30),
                ).grid(row=0, column=1, rowspan=2, sticky="e", padx=12, pady=10)

        def refresh_pending_requests(*, keep_selection: bool = False) -> None:
            current_issue = selected_issue["value"] if keep_selection else ""
            result = membership.list_pending_join_requests()
            if not result.get("ok"):
                pending_requests["items"] = []
                selected_issue["value"] = ""
                pending_count_label.configure(text="Không tải được request chờ duyệt")
                render_pending_request_cards()
                set_status(result.get("message", "Không tải được request chờ duyệt."), "error")
                return

            pending_requests["items"] = result.get("items") or []
            issue_urls = {str(item.get("issue_url", "") or "").strip() for item in pending_requests["items"]}
            selected_issue["value"] = current_issue if current_issue in issue_urls else ""
            pending_count_label.configure(text=f"{len(pending_requests['items'])} request chờ duyệt")
            render_pending_request_cards()

        def refresh_registry_list(*, keep_selection: bool = False) -> None:
            current_username = selected_registry_username["value"] if keep_selection else ""
            registry_entries["items"] = membership.list_local_registry_entries()
            usernames = {str(item.get("username", "") or "").strip() for item in registry_entries["items"]}
            selected_registry_username["value"] = current_username if current_username in usernames else ""
            registry_count_label.configure(text=f"{len(registry_entries['items'])} user trong registry local")
            render_registry_cards()

        def select_pending_request(issue: dict, *, auto_load: bool) -> None:
            selected_issue["value"] = str(issue.get("issue_url", "") or "").strip()
            set_entry_value(issue_link_entry, selected_issue["value"])
            render_pending_request_cards()
            render_preview(issue)
            set_status(f"Đã chọn request #{issue.get('issue_number')} cho {issue.get('username') or 'user'}.", "info")
            if auto_load:
                apply_issue_data(issue, switch_tab=True, message=f"Đã nạp request #{issue.get('issue_number')} sang tab Duyệt.")

        def load_selected_request(*, select_tab: bool) -> None:
            issue_url = selected_issue["value"] or issue_link_entry.get().strip()
            if not issue_url:
                set_status("Chọn request ở tab Chờ duyệt hoặc dán link issue trước.", "warning")
                return

            for item in pending_requests["items"]:
                if str(item.get("issue_url", "") or "").strip() == issue_url:
                    apply_issue_data(item, switch_tab=select_tab, message=f"Đã nạp request #{item.get('issue_number')} sang tab Duyệt.")
                    return

            if fetch_issue_from_input(switch_tab=select_tab):
                render_pending_request_cards()

        def select_registry_entry(entry: dict, *, auto_load: bool) -> None:
            selected_registry_username["value"] = str(entry.get("username", "") or "").strip()
            render_registry_cards()
            set_status(f"Đã chọn user {selected_registry_username['value']} trong registry.", "info")
            if auto_load:
                load_selected_registry(select_tab=True)

        def load_selected_registry(*, select_tab: bool) -> None:
            username = selected_registry_username["value"] or username_entry.get().strip()
            if not username:
                set_status("Chọn user ở tab Registry hoặc nhập GitHub username trước.", "warning")
                return

            entries = {item["username"]: item for item in membership.list_local_registry_entries()}
            entry = entries.get(username)
            if not entry:
                set_status(f"Chưa tìm thấy {username} trong registry local.", "error")
                return

            selected_registry_username["value"] = username
            set_entry_value(username_entry, username)
            set_entry_value(branch_entry, entry.get("branch_name", ""))
            set_entry_value(title_entry, entry.get("title", ""))
            approved_var.set(bool(entry.get("approved")))
            render_registry_cards()
            if select_tab:
                tabview.set("Duyệt")
            set_status(f"Đã nạp user {username} từ registry sang tab Duyệt.", "success")

        def clear_form() -> None:
            selected_issue["value"] = ""
            set_entry_value(issue_link_entry, "")
            set_entry_value(username_entry, "")
            set_entry_value(branch_entry, "")
            set_entry_value(title_entry, "")
            approved_var.set(True)
            clear_preview()
            render_pending_request_cards()
            set_status("Đã xóa nội dung form duyệt.", "info")

        def save_entry(*, close_issue_after_save: bool) -> None:
            username = username_entry.get().strip()
            branch_name = branch_entry.get().strip() or suggest_branch(username)
            title = title_entry.get().strip() or suggest_title(username, branch_name)
            result = membership.upsert_local_registry_entry(
                username=username,
                branch_name=branch_name,
                title=title,
                approved=approved_var.get(),
            )
            if not result.get("ok"):
                set_status(result.get("message", "Không thể lưu entry."), "error")
                return

            set_entry_value(branch_entry, branch_name)
            set_entry_value(title_entry, title)
            selected_registry_username["value"] = username
            refresh_registry_list(keep_selection=True)
            self._refresh_summary()
            if close_issue_after_save and selected_issue["value"]:
                close_selected_issue(with_comment=True, success_message=result.get("message", "Đã lưu quyền truy cập."))
                return
            set_status(result.get("message", "Đã lưu quyền truy cập."), "success")

        def close_selected_issue(*, with_comment: bool, success_message: str = "") -> None:
            issue_url = selected_issue["value"] or issue_link_entry.get().strip()
            if not issue_url:
                set_status("Chưa có issue nào được chọn để đóng.", "warning")
                return

            comment = ""
            if with_comment:
                comment = (
                    "Đã duyệt trong registry. Vui lòng mở app CareVL và bấm "
                    "`Kiểm tra lại quyền truy cập` để nhận quyền mới."
                )
            result = membership.close_join_request_issue(issue_url, comment=comment)
            if not result.get("ok"):
                set_status(result.get("message", "Không đóng được issue."), "error")
                return

            previous_issue = selected_issue["value"]
            selected_issue["value"] = ""
            if issue_link_entry.get().strip() == previous_issue:
                set_entry_value(issue_link_entry, "")
            refresh_pending_requests()
            render_pending_request_cards()
            if success_message:
                set_status(f"{success_message} Đồng thời đã đóng issue GitHub.", "success")
            else:
                set_status(result.get("message", "Đã đóng issue."), "success")

        def delete_entry() -> None:
            username = username_entry.get().strip() or selected_registry_username["value"]
            result = membership.delete_local_registry_entry(username)
            if not result.get("ok"):
                set_status(result.get("message", "Không thể xóa entry."), "error")
                return

            selected_registry_username["value"] = ""
            refresh_registry_list()
            self._refresh_summary()
            clear_form()
            set_status(result.get("message", "Đã xóa entry."), "success")

        ctk.CTkButton(
            approve_actions,
            text="Lưu duyệt",
            command=lambda: save_entry(close_issue_after_save=False),
            **primary_button_style(height=36),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=(0, 8))

        ctk.CTkButton(
            approve_actions,
            text="Duyệt + đóng issue",
            command=lambda: save_entry(close_issue_after_save=True),
            **secondary_button_style(height=36),
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=(0, 8))

        ctk.CTkButton(
            approve_actions,
            text="Nạp user từ registry",
            command=lambda: load_selected_registry(select_tab=False),
            **secondary_button_style(height=36),
        ).grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            approve_actions,
            text="Xóa user khỏi registry",
            command=delete_entry,
            **secondary_button_style(height=36),
        ).grid(row=1, column=1, sticky="ew", padx=(6, 0))

        ctk.CTkButton(
            approve_actions,
            text="Làm trống form",
            command=clear_form,
            **secondary_button_style(height=36),
        ).grid(row=2, column=0, sticky="ew", padx=(0, 6), pady=(8, 0))

        ctk.CTkButton(
            approve_actions,
            text="Mở file registry",
            command=lambda: self._open_path(CONFIG_DIR / "user_registry.json"),
            **secondary_button_style(height=36),
        ).grid(row=2, column=1, sticky="ew", padx=(6, 0), pady=(8, 0))

        clear_preview()
        refresh_pending_requests()
        refresh_registry_list()
        add_modal_actions(dialog, "Đóng", dialog.destroy)

    def _registry_input(self, master, row: int, label: str, placeholder: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            master,
            text=label,
            font=font(13, "semibold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).grid(row=row, column=0, sticky="w", padx=(16, 12), pady=(14 if row == 0 else 10, 0))

        entry = ctk.CTkEntry(
            master,
            placeholder_text=placeholder,
            height=38,
            corner_radius=10,
            fg_color=SURFACE_STRONG,
            border_color=BORDER_STRONG,
            text_color=TEXT_PRIMARY,
        )
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 16), pady=(14 if row == 0 else 10, 0))
        return entry

    def _summarize_csv(self) -> str:
        csv_path = CONFIG_DIR / "stations.csv"
        if not csv_path.exists():
            return "Chưa có file"

        count = 0
        try:
            import csv

            with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    active = str((row.get("active") or "")).strip().lower()
                    if active in {"0", "false", "no", "n", "off"}:
                        continue
                    count += 1
            return f"{count} dòng active"
        except Exception:
            return "Đọc lỗi"

    def _summarize_json(self) -> str:
        json_path = CONFIG_DIR / "stations.json"
        if not json_path.exists():
            return "Chưa build"

        try:
            import json

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return f"{len(data)} branch"
        except Exception:
            return "JSON lỗi"

    def _summarize_checklist(self) -> str:
        csv_path = REPORTS_DIR / "onboarding_checklist.csv"
        md_path = REPORTS_DIR / "onboarding_checklist.md"
        if csv_path.exists() and md_path.exists():
            return "Đã xuất"
        return "Chưa xuất"

    def _summarize_aggregate(self) -> str:
        aggregate_dir = REPORTS_DIR / "aggregate"
        hub_dir = REPORTS_DIR / "hub"
        hub_db = hub_dir / "carevl_hub.duckdb"
        if hub_db.exists():
            return "DuckDB sẵn sàng"

        if not aggregate_dir.exists():
            return "Chưa có snapshot"

        snapshots = [item for item in aggregate_dir.iterdir() if item.is_dir()]
        if not snapshots:
            return "Chưa có snapshot"

        latest = sorted(snapshots)[-1].name
        return latest

    def _open_path(self, path: Path):
        target = path if path.exists() else path.parent
        try:
            subprocess.Popen(["explorer", str(target)])
        except Exception as exc:
            self._append_log(f"[ERROR] Không mở được: {target}\n{exc}\n")


def main():
    app = AdminApp()
    app.mainloop()


if __name__ == "__main__":
    main()
