# Web UI & HTMX Interaction

## Status
[Active]

## Context
Sau khi roi Tkinter, he thong can UI web nhanh, nhe, mobile-first, va co tuong tac cao ma khong keo theo React hay Vue.

## Decision
- Render HTML bang Jinja2 + FastAPI.
- Dung Tailwind CSS qua CDN.
- Dung HTMX cho form, quet ma vach, va partial reload DOM.
- Tich hop `html5-qrcode` de quet ma vach bang camera dien thoai tai tram.

## Rationale
Stack nay nhe, khong can `node_modules`, khong can build step nang. HTMX giu state ben server, giam JS ben client. May cu va dien thoai cu van chay de. Toan bo UI phuc vu tu may local nen hop offline-first va LAN noi bo.

## Related Documents
- [01. FastAPI Core Architecture](01_FastAPI_Core.md)
- [12. UI/UX Data Flow: Intake to Delayed Results](12_ui_ux_flow.md)
- [18. Two-App Architecture: Edge vs Hub](18_Two_App_Architecture.md)
