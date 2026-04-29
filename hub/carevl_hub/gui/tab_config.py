"""
Tab 2: Cấu hình tải dữ liệu từ các trạm về Hub.
"""

from __future__ import annotations

import streamlit as st

from carevl_hub.gui.session import (
    SESSION_KEYS,
    local_state_path,
    mask_secret,
    save_local_state,
    try_load_local_state,
)


def render() -> None:
    """Tab 2: Cấu hình tải dữ liệu."""
    st.subheader("📊 Cấu hình tải dữ liệu")

    st.info(
        "**Tab này dùng khi nào?** Khi bạn muốn **tải dữ liệu từ các trạm về Hub**. "
        "Nếu chỉ tạo mã kích hoạt, **chưa cần vào tab này**."
    )
    st.warning(
        "⚠️ **Chức năng tải dữ liệu chưa hoạt động**. "
        "Hiện tại dùng CLI: `carevl-hub download --org <org> --output-dir ./hub_data`"
    )

    st.divider()
    st.markdown("### 🔑 Thông tin xác thực")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["hub_org"] = st.text_input(
            "GitHub org/user *",
            value=st.session_state.get("hub_org", ""),
            placeholder="carevl-bot",
            help="Tên tổ chức hoặc user (không phải URL)",
        )
        st.session_state["hub_pat"] = st.text_input(
            "GitHub PAT *",
            value=st.session_state.get("hub_pat", ""),
            type="password",
            placeholder="github_pat_...",
            help="Token với quyền đọc repo",
        )
    with col2:
        st.session_state["hub_output_dir"] = st.text_input(
            "Thư mục lưu dữ liệu",
            value=st.session_state.get("hub_output_dir", "./hub_data"),
            placeholder="./hub_data",
            help="Khuyến nghị giữ mặc định",
        )
        st.session_state["hub_encryption_key"] = st.text_input(
            "Encryption key *",
            value=st.session_state.get("hub_encryption_key", ""),
            type="password",
            placeholder="32-byte key",
            help="PHẢI TRÙNG với key đã gửi cho trạm!",
        )

    st.divider()
    st.markdown("### 💾 Lưu cấu hình")

    col_save1, col_save2 = st.columns(2)
    with col_save1:
        if st.button("💾 Lưu session", type="primary"):
            st.success("✅ Đã lưu (RAM)")
    with col_save2:
        if st.button("📁 Lưu file"):
            try:
                save_local_state()
                st.success(f"✅ Đã lưu `{local_state_path().name}`")
            except OSError as e:
                st.error(f"❌ Lỗi: {e}")

    st.caption("**Session**: Mất khi đóng tab. **File**: Lưu lâu dài (gitignored).")

    st.divider()
    st.markdown("### 📋 Tóm tắt")
    st.code(
        f"Org: {st.session_state.get('hub_org') or '(chưa điền)'}\n"
        f"Dir: {st.session_state.get('hub_output_dir') or '(chưa điền)'}\n"
        f"Key: {mask_secret(st.session_state.get('hub_encryption_key', ''))}\n"
        f"PAT: {mask_secret(st.session_state.get('hub_pat', ''))}"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Đọc từ file"):
            try_load_local_state()
            st.rerun()
    with col2:
        if st.button("🗑️ Xóa session"):
            for k in SESSION_KEYS:
                st.session_state[k] = ""
            st.rerun()

    with st.expander("❓ FAQ", expanded=False):
        st.markdown("""
**Q: Encryption key lấy ở đâu?**
→ Chính là key đã điền ở Tab 1 khi tạo invite code!

**Q: PAT cần quyền gì?**
→ **Contents: Read** (đọc repo + releases)

**Q: Nhiều trạm, mỗi trạm một key?**
→ Mỗi lần tải phải đổi key tương ứng. Hoặc dùng chung 1 key cho tất cả (đơn giản hơn).
        """)
