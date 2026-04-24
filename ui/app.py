from __future__ import annotations

import datetime
import threading
from typing import Any, Callable, Dict, Optional
import customtkinter as ctk

from modules import auth
from modules import config_loader
from modules import paths
from ui.design_tokens import (
    BG_APP,
    BORDER,
    PRIMARY_BLUE,
    PRIMARY_BLUE_HOVER,
    SURFACE,
    SURFACE_ALT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    font,
    primary_button_style,
    secondary_button_style,
    destructive_button_style,
)
from ui.app_shell import AppShell
from ui.terms import EDGE_LABEL, HUB_LABEL


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        paths.ensure_directories()
        
        self.title("CareVL - Khám sức khỏe Vĩnh Long")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=BG_APP)
        
        self.username: Optional[str] = None
        self.is_admin: bool = False
        self.active_branch: str = "unknown"
        self.current_screen: Optional[ctk.CTkFrame] = None
        self.current_shell: Optional[AppShell] = None
        
        self._setup_ui()
        self.after(0, self._maximize_window)
        self._check_auth()
        
        self.bind("<Configure>", self._on_resize)
    
    def _on_resize(self, event):
        pass

    def _maximize_window(self):
        try:
            self.state("zoomed")
        except Exception:
            self.attributes("-zoomed", True)

    def _setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")

    def _check_auth(self):
        result = auth.check_existing_token()
        
        if result["ok"]:
            self.username = result.get("username")
            self._refresh_user_context()
            self._show_screen_list()
        else:
            self._show_login()

    def _refresh_user_context(self):
        self.active_branch = self._get_active_branch()
        admin_usernames = config_loader.load_admin_usernames()
        self.is_admin = bool(self.username and self.username in admin_usernames)

    def _get_active_branch(self) -> str:
        from modules import sync
        branch_name = sync.get_current_branch()
        return branch_name or "unknown"

    def _show_login(self):
        self._clear_screen()
        
        wrapper = ctk.CTkFrame(self.container, fg_color="transparent")
        wrapper.pack(expand=True, fill="both", padx=24, pady=24)

        hero_card = ctk.CTkFrame(
            wrapper,
            fg_color=SURFACE,
            corner_radius=22,
            border_width=1,
            border_color=BORDER,
        )
        hero_card.pack(expand=True, ipadx=10, ipady=10)

        login_frame = ctk.CTkFrame(hero_card, fg_color="transparent")
        login_frame.pack(expand=True, fill="both", padx=56, pady=52)

        eyebrow = ctk.CTkLabel(
            login_frame,
            text="CareVL",
            font=font(14, "semibold"),
            text_color=PRIMARY_BLUE,
        )
        eyebrow.pack(pady=(0, 10))

        title = ctk.CTkLabel(
            login_frame,
            text="CareVL",
            font=font(34, "bold"),
            text_color=TEXT_PRIMARY,
        )
        title.pack(pady=(0, 10))
        
        subtitle = ctk.CTkLabel(
            login_frame,
            text="Khám sức khỏe định kỳ - Vĩnh Long",
            font=font(16),
            text_color=TEXT_MUTED,
        )
        subtitle.pack(pady=(0, 12))

        description = ctk.CTkLabel(
            login_frame,
            text=f"Ứng dụng nhập liệu offline-first cho {EDGE_LABEL}, đồng bộ về {HUB_LABEL} qua GitHub khi có mạng.",
            font=font(14),
            text_color=TEXT_MUTED,
            wraplength=520,
            justify="center",
        )
        description.pack(pady=(0, 34))
        
        login_btn = ctk.CTkButton(
            login_frame,
            text="Đăng nhập bằng GitHub",
            command=self._on_login_click,
            **primary_button_style(width=220, height=44),
        )
        login_btn.pack(pady=10)
        
        self.status_label = ctk.CTkLabel(login_frame, text="", font=font(13), text_color=TEXT_MUTED)
        self.status_label.pack(pady=20)
        
        self.code_label = ctk.CTkLabel(login_frame, text="", font=font(24, "bold"), text_color=TEXT_PRIMARY)
        self.code_label.pack(pady=10)
        
        self.copy_code_btn = ctk.CTkButton(
            login_frame,
            text="Copy mã",
            command=self._copy_user_code,
            **secondary_button_style(width=120, height=38),
        )
        self.copy_code_btn.pack_forget()

    def _copy_user_code(self):
        code = self.code_label.cget("text").replace("Mã xác thực: ", "")
        self.clipboard_clear()
        self.clipboard_append(code)
        
    def _on_login_click(self):
        self.status_label.configure(text="Đang khởi tạo xác thực...")
        self.update()
        
        flow = auth.start_device_flow()
        
        if not flow["ok"]:
            self.status_label.configure(text=f"Lỗi: {flow.get('message', '')}")
            return
        
        user_code = flow.get("user_code", "")
        device_code = flow.get("device_code", "")
        interval = flow.get("interval", 5)
        
        self.code_label.configure(text=f"Mã xác thực: {user_code}")
        self.status_label.configure(text="Vào github.com/login/device nhập mã trên, sau đó quay lại đây.")
        self.copy_code_btn.pack(pady=5)
        
        thread = threading.Thread(
            target=self._do_login_poll,
            args=(device_code, interval),
            daemon=True
        )
        thread.start()

    def _do_login_poll(self, device_code: str, interval: int):
        result = auth.poll_for_token(device_code, interval)
        self.after(0, self._handle_login_result, result)

    def _handle_login_result(self, result: Dict[str, Any]):
        if result["ok"]:
            self.username = result.get("username")
            
            config = {
                "access_token": result.get("access_token", ""),
                "username": self.username,
            }
            auth._save_user_config(config)
            self._refresh_user_context()
            
            self._show_screen_list()
        else:
            self.status_label.configure(text=f"Lỗi: {result.get('message', '')}")
            self.copy_code_btn.configure(state="disabled", fg_color="gray")

    def _show_screen_list(self):
        self._clear_screen()

        from ui import screen_list

        def on_create_record():
            self._show_screen_form(None, datetime.datetime.now().strftime("%d-%m-%Y"), None)

        def on_view_record(record_id: str, date_str: str):
            from modules import record_store as crud

            record = None
            try:
                record = crud.load_encounter(record_id)
            except Exception:
                record = None

            if record is None:
                records = []
                try:
                    records = crud.read_day(date_str)
                except Exception:
                    pass
                record = next((r for r in records if r.get("id") == record_id), None)

            package_id = record.get("package_id") if record else None

            self._show_screen_form(record_id, date_str, package_id)

        def on_sync():
            self._show_sync_screen()

        def on_switch_branch(branch_name: str):
            self._handle_branch_switch(branch_name)

        shell = self._create_authenticated_shell(active_key="records")
        screen = screen_list.render_list_screen(
            shell.content_frame,
            username=self.username or "",
            current_branch=self.active_branch,
            is_admin=self.is_admin,
            on_create_record=on_create_record,
            on_view_record=on_view_record,
            on_sync=on_sync,
            on_switch_branch=on_switch_branch,
        )
        screen.pack(fill="both", expand=True)
        self.current_screen = screen
        self.current_shell = shell

    def _show_screen_form(self, record_id: Optional[str], date_str: str, package_id: Optional[str]):
        self._clear_screen()

        from ui import screen_form

        def on_back():
            self._show_screen_list()

        def on_saved():
            self._show_screen_list()

        if not package_id:
            template = config_loader.load_template_form()
            packages = template.get("packages", [])
            if packages:
                package_id = packages[0].get("id", "nct")

        active_key = "records" if record_id else "new_record"
        shell = self._create_authenticated_shell(active_key=active_key)
        screen = screen_form.render_form_screen(
            shell.content_frame,
            record_id=record_id,
            date_str=date_str,
            package_id=package_id,
            username=self.username or "",
            branch_name=self.active_branch,
            branch_locked=self.is_admin,
            on_back=on_back,
            on_saved=on_saved,
            embedded_shell=True,
        )
        screen.pack(fill="both", expand=True)
        self.current_screen = screen
        self.current_shell = shell

    def _show_sync_screen(self):
        self._clear_screen()

        from ui import screen_sync

        def on_back():
            self._show_screen_list()

        shell = self._create_authenticated_shell(active_key="sync")
        screen = screen_sync.render_sync_screen(
            shell.content_frame,
            username=self.username or "",
            branch_name=self.active_branch,
            branch_locked=self.is_admin,
            on_back=on_back,
            embedded_shell=True,
        )
        screen.pack(fill="both", expand=True)
        self.current_screen = screen
        self.current_shell = shell

    def _show_export_screen(self):
        self._clear_screen()

        from ui import screen_export

        def on_back():
            self._show_screen_list()

        shell = self._create_authenticated_shell(active_key="export")
        screen = screen_export.render_export_screen(
            shell.content_frame,
            username=self.username or "",
            branch_name=self.active_branch,
            on_back=on_back,
        )
        screen.pack(fill="both", expand=True)
        self.current_screen = screen
        self.current_shell = shell

    def _show_import_screen(self):
        self._clear_screen()

        from ui import screen_import

        def on_back():
            self._show_screen_list()

        shell = self._create_authenticated_shell(active_key="import")
        screen = screen_import.render_import_screen(
            shell.content_frame,
            username=self.username or "",
            branch_name=self.active_branch,
            on_back=on_back,
        )
        screen.pack(fill="both", expand=True)
        self.current_screen = screen
        self.current_shell = shell

    def _show_about_screen(self):
        self._clear_screen()

        from ui import screen_about

        shell = self._create_authenticated_shell(active_key="about")
        screen = screen_about.render_about_screen(shell.content_frame)
        screen.pack(fill="both", expand=True)
        self.current_screen = screen
        self.current_shell = shell

    def _create_authenticated_shell(self, active_key: str) -> AppShell:
        shell = AppShell(
            self.container,
            username=self.username or "",
            branch_name=self.active_branch,
            is_admin=self.is_admin,
            active_key=active_key,
            on_open_records=self._show_screen_list,
            on_open_new_record=lambda: self._show_screen_form(None, datetime.datetime.now().strftime("%d-%m-%Y"), None),
            on_open_import=self._show_import_screen,
            on_open_export=self._show_export_screen,
            on_open_sync=self._show_sync_screen,
            on_open_about=self._show_about_screen,
            on_logout=self._on_logout,
        )
        shell.pack(fill="both", expand=True)
        return shell

    def _handle_branch_switch(self, branch_name: str):
        from modules import sync

        result = sync.switch_branch(branch_name)
        if result.get("ok"):
            self.active_branch = branch_name
            self.is_admin = True
            self._show_screen_list()
            return

        if self.current_screen and hasattr(self.current_screen, "show_error"):
            self.current_screen.show_error(result.get("message", "Không thể chuyển trạm."))

    def _clear_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.current_screen = None
        self.current_shell = None
    
    def _on_logout(self):
        """Handle logout action."""
        # Confirm logout
        dialog = ctk.CTkToplevel(self)
        dialog.title("Xác nhận đăng xuất")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=SURFACE_ALT)
        
        label = ctk.CTkLabel(
            dialog,
            text="Bạn có chắc muốn đăng xuất?",
            wraplength=250,
            font=font(14),
            text_color=TEXT_PRIMARY,
        )
        label.pack(padx=20, pady=20)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        def confirm_logout():
            dialog.destroy()
            auth.logout()
            self.username = None
            self._show_login()
        
        def cancel_logout():
            dialog.destroy()
        
        ctk.CTkButton(
            btn_frame,
            text="Đăng xuất",
            command=confirm_logout,
            **destructive_button_style(width=110, height=36),
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Hủy",
            command=cancel_logout,
            **secondary_button_style(width=90, height=36),
        ).pack(side="left", padx=5)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
