"""Fixtures of the pnm regression tests (pytest). Needs: pytest, pnmkit and the pnextract/pnflow executables ($MS_INST/bin)."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent

_ms_inst = os.environ.get("MS_INST") or os.environ.get("msInst")
if _ms_inst:  # executables and libraries of the installation
    os.environ["PATH"] = f"{_ms_inst}/bin:{os.environ.get('PATH', '')}"
    os.environ["LD_LIBRARY_PATH"] = f"{_ms_inst}/lib:{os.environ.get('LD_LIBRARY_PATH', '')}"


def require_exe(name: str) -> str:
    """Skip the test if the executable is not found."""
    exe = shutil.which(name)
    if not exe:
        pytest.skip(f"Required executable '{name}' not found on PATH (MS_INST={_ms_inst})")
    return exe


def case_dir(case: str, tmp_path: Path | None = None) -> Path:
    """Work folder of a test case: $MS_TEST_DIR/pnm/<case> (kept after the run), else a temporary folder."""
    env_test_dir = os.environ.get("MS_TEST_DIR")
    if env_test_dir:
        work_dir = Path(env_test_dir) / "pnm" / case
    else:
        assert tmp_path is not None, "Either MS_TEST_DIR or tmp_path must be provided"
        work_dir = tmp_path / case
    work_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(work_dir)
    return work_dir


def pytest_configure(config):
    config.addinivalue_line("markers", "regression: compares results with the reference values")
