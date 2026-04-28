# FastAPI Core Architecture

## Status
[Active]

## Context
Ban dau CareVL dung CustomTkinter desktop. Cach nay vuong mobile responsive, vuong quet ma vach bang dien thoai, va vuong mo rong API.

## Decision
Chuyen backend sang FastAPI.

- API va HTML cung do FastAPI phuc vu.
- Template dung Jinja2.
- Code tach module `core`, `api`, `models`, `services`.

## Rationale
FastAPI nhanh, ro, va hop web-first hon stack cu. Async/Await san co. Pydantic giup validation. UI/Backend tach lop de ghep HTMX, Tailwind, va route API de hon. Cau truc module cung de khoanh loi va de bao tri.

## Related Documents
- [03. Web UI & HTMX Interaction](03_Web_UI_HTMX.md)
- [04. Development Guidelines & Troubleshooting](04_Development_Guidelines.md)
- [18. Two-App Architecture: Edge vs Hub](18_Two_App_Architecture.md)
