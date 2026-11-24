#!/usr/bin/env python3
"""Antigravity PostToolUse hook for C/H files: format with clang-format and lint with cppcheck/compiler."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def _configure_stdio_utf8() -> None:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _emit_ok_json() -> None:
    # Antigravity PostToolUse contract expects an empty JSON object on stdout.
    sys.stdout.write("{}\n")
    sys.stdout.flush()


def _extract_target_path(payload: dict[str, Any]) -> str:
    candidate_keys = ("Path", "TargetFile", "AbsolutePath", "file_path", "path")

    tool_call = payload.get("toolCall")
    if isinstance(tool_call, dict):
        args = tool_call.get("args")
        if isinstance(args, dict):
            for key in candidate_keys:
                val = args.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()

    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        for key in candidate_keys:
            val = tool_input.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()

    for key in candidate_keys:
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()

    return ""


def _resolve_workspace_root(payload: dict[str, Any]) -> Path:
    # Default: <workspace>/.agents/hooks/c-check.py -> parents[2] is <workspace>.
    script_workspace = Path(__file__).resolve().parents[2]
    workspace_paths = payload.get("workspacePaths")
    if isinstance(workspace_paths, list) and workspace_paths:
        first = workspace_paths[0]
        if isinstance(first, str) and first.strip():
            p = Path(first).resolve()
            if p.is_dir():
                return p
    return script_workspace


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _run_subprocess(cmd: list[str], cwd: Path, timeout_sec: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_sec,
        check=False,
    )


def _run_static_check(target: Path, workspace_root: Path) -> tuple[bool, str]:
    include_dir = workspace_root / "include"
    include_args = ["-I", str(include_dir)] if include_dir.is_dir() else []

    cppcheck = shutil.which("cppcheck")
    if cppcheck:
        cmd = [
            cppcheck,
            "--enable=warning,performance,portability",
            "--error-exitcode=1",
            "--inline-suppr",
            *include_args,
            str(target),
        ]
        result = _run_subprocess(cmd, workspace_root)
        if result.returncode != 0:
            output = "\n".join(s for s in (result.stderr.strip(), result.stdout.strip()) if s)
            return False, f"[c-check] cppcheck issues in {target}:\n{output}"
        return True, ""

    for compiler_name in ("clang", "gcc"):
        compiler = shutil.which(compiler_name)
        if compiler:
            cmd = [
                compiler,
                "-std=c11",
                "-fsyntax-only",
                "-Wall",
                "-Wextra",
            ]
            if target.suffix.lower() == ".h":
                cmd.extend(["-x", "c-header"])
            cmd.extend([*include_args, str(target)])
            result = _run_subprocess(cmd, workspace_root)
            if result.returncode != 0:
                output = "\n".join(s for s in (result.stderr.strip(), result.stdout.strip()) if s)
                return False, f"[c-check] {compiler_name} syntax/warning issues in {target}:\n{output}"
            return True, ""

    msvc_cl = shutil.which("cl")
    if msvc_cl and target.suffix.lower() == ".c":
        cmd = [msvc_cl, "/nologo", "/Zs", "/W4", "/std:c11"]
        if include_dir.is_dir():
            cmd.append(f"/I{include_dir}")
        cmd.append(str(target))
        result = _run_subprocess(cmd, workspace_root)
        if result.returncode != 0:
            output = "\n".join(s for s in (result.stderr.strip(), result.stdout.strip()) if s)
            return False, f"[c-check] cl syntax/warning issues in {target}:\n{output}"
        return True, ""

    # No analyzer/compiler found in PATH: skip gracefully so editing is not blocked.
    return True, ""


def main() -> int:
    _configure_stdio_utf8()

    raw = sys.stdin.read()
    if not raw.strip():
        _emit_ok_json()
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        _emit_ok_json()
        return 0

    if not isinstance(payload, dict):
        _emit_ok_json()
        return 0

    raw_path = _extract_target_path(payload)
    if not raw_path:
        _emit_ok_json()
        return 0

    workspace_root = _resolve_workspace_root(payload)
    base_dir = Path(payload["cwd"]).resolve() if isinstance(payload.get("cwd"), str) and payload["cwd"].strip() else workspace_root

    target = Path(raw_path)
    if not target.is_absolute():
        target = (base_dir / target).resolve()
    else:
        target = target.resolve()

    if not _is_within(target, workspace_root):
        _emit_ok_json()
        return 0

    if target.suffix.lower() not in {".c", ".h"} or not target.is_file():
        _emit_ok_json()
        return 0

    try:
        clang_format = shutil.which("clang-format")
        if clang_format:
            fmt_res = _run_subprocess([clang_format, "-i", str(target)], workspace_root, timeout_sec=10)
            if fmt_res.returncode != 0:
                sys.stderr.write(f"[c-check] clang-format failed for {target}:\n{fmt_res.stderr}\n")

        ok, diag = _run_static_check(target, workspace_root)
    except subprocess.TimeoutExpired as exc:
        sys.stderr.write(f"[c-check] timed out while checking {target}: {exc}\n")
        _emit_ok_json()
        return 2

    _emit_ok_json()
    if not ok:
        sys.stderr.write(f"{diag}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
