"""Hub operator GUI (Streamlit) — ADR 29 MVP."""

from pathlib import Path

from typer.testing import CliRunner

from carevl_hub.cli import app


def test_gui_entry_file_exists():
    pkg = Path(__file__).resolve().parents[1] / "carevl_hub"
    assert (pkg / "gui" / "app.py").is_file()


def test_gui_app_has_main():
    from carevl_hub.gui import app as gui_app

    assert callable(gui_app.main)


def test_gui_cli_help():
    runner = CliRunner()
    r = runner.invoke(app, ["gui", "--help"])
    assert r.exit_code == 0
    assert "Streamlit" in r.stdout or "8501" in r.stdout


def test_local_state_path_gitignored_filename():
    from carevl_hub.gui import app as gui_app

    assert gui_app._local_state_path().name == ".carevl_operator_local.json"


def test_config_fields_diagram_svg_shipped():
    from carevl_hub.gui import app as gui_app_mod

    p = Path(gui_app_mod.__file__).resolve().parent / "assets" / "hub_operator_config_fields.svg"
    assert p.is_file()
    assert gui_app_mod._config_fields_diagram_path() is not None
