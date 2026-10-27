#!/usr/bin/env python3
"""Run parameterized, private mGBA smoke diagnostics and package evidence.

A living emulator process is not proof of gameplay success. This script records
what it actually observed; it does not auto-approve a build.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_gba_header(path: Path) -> dict[str, Any]:
    data = path.read_bytes()[:0xC0]
    if len(data) < 0xC0:
        raise ValueError(f"File too short to contain GBA header: {path}")
    actual = data[0xBD]
    expected = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF
    return {
        "title": data[0xA0:0xAC].split(b"\0", 1)[0].decode("ascii", errors="replace").strip(),
        "game_code": data[0xAC:0xB0].decode("ascii", errors="replace"),
        "maker_code": data[0xB0:0xB2].decode("ascii", errors="replace"),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "header_complement_actual": f"0x{actual:02X}",
        "header_complement_expected": f"0x{expected:02X}",
        "header_complement_valid": actual == expected
    }


def find_program(candidates: list[str]) -> str | None:
    for candidate in candidates:
        found = shutil.which(candidate)
        if found:
            return found
        path = Path(candidate)
        if path.is_absolute() and path.is_file() and os.access(path, os.X_OK):
            return str(path)
    return None


def run_cmd(args: list[str], timeout: float = 8.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)


def descendants_of(pid: int) -> set[int]:
    result = {pid}
    changed = True
    while changed:
        changed = False
        try:
            entries = subprocess.run(
                ["ps", "-eo", "pid=,ppid="], capture_output=True, text=True, timeout=3, check=False
            ).stdout.splitlines()
        except Exception:
            break
        for line in entries:
            parts = line.split()
            if len(parts) != 2:
                continue
            try:
                child, parent = int(parts[0]), int(parts[1])
            except ValueError:
                continue
            if parent in result and child not in result:
                result.add(child)
                changed = True
    return result


def find_window(emulator_pid: int, rom_stem: str, previous_id: str | None = None) -> str | None:
    if previous_id:
        probe = run_cmd(["xdotool", "getwindowname", previous_id], timeout=2)
        if probe.returncode == 0:
            return previous_id
    try:
        ids_result = run_cmd(["xdotool", "search", "--onlyvisible", "--name", ".*"], timeout=3)
        ids = [x.strip() for x in ids_result.stdout.splitlines() if x.strip().isdigit()]
    except Exception:
        ids = []
    pids = descendants_of(emulator_pid)
    target_id = None
    fallback_id = None
    stem = re.sub(r"[^A-Za-z0-9]+", "", rom_stem).lower()
    for wid in ids:
        pid_result = run_cmd(["xdotool", "getwindowpid", wid], timeout=2)
        try:
            wpid = int(pid_result.stdout.strip())
        except ValueError:
            wpid = -1
        title_result = run_cmd(["xdotool", "getwindowname", wid], timeout=2)
        title = title_result.stdout.strip().lower()
        normalized_title = re.sub(r"[^A-Za-z0-9]+", "", title)
        if wpid in pids:
            if stem and stem in normalized_title:
                return wid
            if "mgba" in normalized_title or "visualboy" in normalized_title:
                target_id = wid
            elif target_id is None:
                target_id = wid
        if stem and stem in normalized_title:
            fallback_id = wid
        elif fallback_id is None and ("mgba" in normalized_title or "visualboy" in normalized_title):
            fallback_id = wid
    return target_id or fallback_id


def capture_window(window_id: str | None, fallback: Path, capture_log: Path) -> tuple[bool, str]:
    candidates = []
    if window_id:
        candidates.append(["import", "-window", window_id, str(fallback)])
    candidates.append(["import", "-window", "root", str(fallback)])
    for cmd in candidates:
        try:
            with capture_log.open("a", encoding="utf-8") as log:
                proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=log, timeout=10, check=False)
            if proc.returncode == 0 and fallback.is_file() and fallback.stat().st_size > 64:
                return True, "window" if len(cmd) > 3 and cmd[2] != "root" else "desktop-fallback"
        except Exception as exc:
            with capture_log.open("a", encoding="utf-8") as log:
                log.write(f"capture command failed: {exc}\n")
    return False, "failed"


def send_key(window_id: str | None, key: str, hold_ms: int) -> dict[str, Any]:
    press = ["xdotool", "keydown"]
    release = ["xdotool", "keyup"]
    if window_id:
        press += ["--window", window_id]
        release += ["--window", window_id]
    press.append(key)
    release.append(key)
    try:
        p = run_cmd(press, timeout=3)
        time.sleep(max(0.02, hold_ms / 1000.0))
        r = run_cmd(release, timeout=3)
        if p.returncode == 0 and r.returncode == 0:
            return {"key": key, "hold_ms": hold_ms, "sent": True, "window_id": window_id}
    except Exception:
        pass
    # Fallback to normal X key events only if targeted events failed.
    try:
        p = run_cmd(["xdotool", "key", "--clearmodifiers", key], timeout=3)
        return {"key": key, "hold_ms": hold_ms, "sent": p.returncode == 0,
                "fallback": True, "window_id": window_id}
    except Exception as exc:
        return {"key": key, "hold_ms": hold_ms, "sent": False, "error": str(exc)}


def worker(args: argparse.Namespace, profile: dict[str, Any], config: dict[str, Any],
           work_rom: Path, out_dir: Path, emulator: str) -> int:
    env = os.environ.copy()
    env.update({
        "QT_QPA_PLATFORM": "xcb",
        "QT_OPENGL": "software",
        "LIBGL_ALWAYS_SOFTWARE": "1",
        "SDL_AUDIODRIVER": "dummy"
    })
    capture_log = out_dir / "capture.log"
    emulator_log = out_dir / "emulator.log"
    runtime: dict[str, Any] = {
        "emulator_path": emulator,
        "rom_copy_path": str(work_rom),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "stage_results": [],
        "limitations": [
            "A live emulator process does not prove the game is responsive.",
            "Screenshots and logs must be inspected by a person.",
            "This profile is a smoke test, not full gameplay certification."
        ]
    }
    log_stream = emulator_log.open("w", encoding="utf-8", errors="replace")
    proc: subprocess.Popen[str] | None = None
    try:
        proc = subprocess.Popen(
            [emulator, "-l", str(config.get("emulator", {}).get("log_level", 15)), str(work_rom)],
            cwd=str(work_rom.parent),
            env=env,
            stdout=log_stream,
            stderr=subprocess.STDOUT,
            text=True
        )
        runtime["emulator_pid"] = proc.pid
        display = config.get("emulator", {}).get("display", "1280x960x24")
        runtime["virtual_display"] = display
        window_timeout = float(config.get("emulator", {}).get("window_search_timeout_seconds", 15))
        deadline = time.monotonic() + window_timeout
        window_id: str | None = None
        while time.monotonic() < deadline and proc.poll() is None:
            window_id = find_window(proc.pid, work_rom.stem, window_id)
            if window_id:
                break
            time.sleep(0.25)
        runtime["window_id"] = window_id
        runtime["window_found"] = window_id is not None
        if proc.poll() is not None:
            runtime["process_exited_before_window"] = proc.returncode
        if window_id is None:
            runtime["warnings"] = ["No se pudo identificar la ventana; las capturas pueden ser del escritorio virtual completo."]
        keymap = config.get("emulator", {}).get("keyboard", {})
        stages = config.get("emulator", {}).get("stages", [])
        if not stages:
            stages = [{"name": "01-boot", "key": None, "wait_seconds": 7}]
        for idx, stage in enumerate(stages, start=1):
            result: dict[str, Any] = {
                "index": idx,
                "name": stage.get("name", f"stage-{idx:02d}"),
                "description": stage.get("description", ""),
                "key_alias": stage.get("key"),
                "started_at_utc": datetime.now(timezone.utc).isoformat()
            }
            alias = stage.get("key")
            if alias:
                key_name = keymap.get(alias, alias)
                hold_ms = int(stage.get("hold_ms", config.get("emulator", {}).get("input_hold_ms", 100)))
                result["input"] = send_key(window_id, str(key_name), hold_ms)
            wait_seconds = float(stage.get("wait_seconds", 1))
            result["wait_seconds"] = wait_seconds
            time.sleep(max(0.0, wait_seconds))
            if proc.poll() is not None:
                result["process_alive_after_wait"] = False
                result["process_exit_code"] = proc.returncode
            else:
                result["process_alive_after_wait"] = True
            window_id = find_window(proc.pid, work_rom.stem, window_id)
            out_png = out_dir / f"{idx:02d}-{result['name']}.png"
            ok, mode = capture_window(window_id, out_png, capture_log)
            result["window_id"] = window_id
            result["capture_ok"] = ok
            result["capture_mode"] = mode
            result["capture_usable"] = bool(ok and window_id is not None and mode == "window")
            result["screenshot"] = out_png.name if ok else None
            result["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
            runtime["stage_results"].append(result)
            if proc.poll() is not None:
                runtime.setdefault("warnings", []).append(
                    f"mGBA terminó durante la secuencia (código {proc.returncode}); revisar emulator.log."
                )
                break
        runtime["exit_code_before_cleanup"] = proc.poll()
        runtime["captures_succeeded"] = sum(1 for row in runtime["stage_results"] if row.get("capture_usable"))
        runtime["captures_desktop_fallback_only"] = any(
            row.get("capture_ok") and not row.get("capture_usable") for row in runtime["stage_results"]
        )
        runtime["emulator_session_started"] = bool(runtime.get("window_found") and runtime["captures_succeeded"] > 0)
        runtime["gameplay_passed"] = False
        runtime["runtime_certification"] = "NOT CERTIFIED — review screenshots/logs and test gameplay manually"
    except Exception as exc:
        runtime["fatal_error"] = f"{type(exc).__name__}: {exc}"
        return_code = 2
    else:
        return_code = 0 if runtime.get("window_found") and runtime.get("captures_succeeded", 0) > 0 else 4
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=float(config.get("emulator", {}).get("close_timeout_seconds", 3)))
            except subprocess.TimeoutExpired:
                proc.kill()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
        log_stream.close()
        runtime["ended_at_utc"] = datetime.now(timezone.utc).isoformat()
        (out_dir / "run.json").write_text(json.dumps(runtime, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return return_code


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Capture configurable GBA emulator checkpoints without packaging the ROM")
    parser.add_argument("rom", type=Path, help="ROM file located under private-roms/")
    parser.add_argument("--config", type=Path, default=root / "config" / "gba_lab.json")
    parser.add_argument("--profile", default="gba_candidate_unpinned",
                        help="ROM audit profile name for static report")
    parser.add_argument("--baseline", type=Path, help="Optional clean/reference ROM for static delta audit")
    parser.add_argument("--output-dir", type=Path, help="Output directory (must be under private-roms/diagnostics)")
    parser.add_argument("--inside-xvfb", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--_work-rom", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--_out-dir", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--_emulator", help=argparse.SUPPRESS)
    args = parser.parse_args()

    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        rom = args.rom.resolve()
        private_root = (root / "private-roms").resolve()
        diagnostics_root = (private_root / "diagnostics").resolve()
        if not rom.is_file():
            raise FileNotFoundError(rom)
        if not rom.is_relative_to(private_root):
            raise ValueError("Por seguridad, la ROM debe estar dentro de private-roms/ (excluido de Git).")
        header = parse_gba_header(rom)
        emulator_config = config.get("emulator", {})
        emulator = find_program(emulator_config.get("preferred_binary_candidates", ["mgba-qt", "mgba"]))
        if not emulator:
            raise FileNotFoundError("No se encontró mGBA. Ejecuta bash tools/install_gba_emulator.sh")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", rom.stem)[:60]
        out_dir = args.output_dir.resolve() if args.output_dir else diagnostics_root / f"{slug}-{stamp}"
        if not out_dir.is_relative_to(diagnostics_root):
            raise ValueError("La salida debe estar dentro de private-roms/diagnostics/.")
        out_dir.mkdir(parents=True, exist_ok=True)
        work_root = private_root / f".gba-diagnostic-work-{stamp}"
        work_root.mkdir(parents=True, exist_ok=False)
        work_rom = work_root / "diagnostic-copy.gba"
        shutil.copy2(rom, work_rom)
        (out_dir / "rom-header.json").write_text(json.dumps(header, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out_dir / "emulator-version.txt").write_text(
            (run_cmd([emulator, "--version"], timeout=5).stdout or run_cmd([emulator, "--version"], timeout=5).stderr).strip() + "\n",
            encoding="utf-8"
        )
        (out_dir / "rom-sha256.txt").write_text(f"{header['sha256']}  {rom.name}\n", encoding="utf-8")
        preflight = {
            "tool": "run_gba_diagnostic",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "source_rom": rom.name,
            "source_sha256": header["sha256"],
            "header": header,
            "emulator": emulator,
            "emulator_profile": emulator_config,
            "output_directory": str(out_dir),
            "save_isolation": "ROM copied to a temporary private workspace; generated save files are removed after the run.",
            "rom_included_in_zip": False
        }
        (out_dir / "preflight.json").write_text(json.dumps(preflight, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if args.baseline:
            baseline = args.baseline.resolve()
            if not baseline.is_file() or not baseline.is_relative_to(private_root):
                raise ValueError("La ROM base debe existir dentro de private-roms/.")
            audit_path = out_dir / "static-audit.json"
            audit_proc = subprocess.run(
                [sys.executable, str(root / "tools" / "gba_rom_audit.py"),
                 "--rom", str(rom), "--profile", args.profile, "--config", str(args.config),
                 "--baseline", str(baseline), "--report", str(audit_path)],
                capture_output=True, text=True, check=False
            )
            (out_dir / "static-audit.stdout.txt").write_text(audit_proc.stdout, encoding="utf-8")
            (out_dir / "static-audit.stderr.txt").write_text(audit_proc.stderr, encoding="utf-8")
            preflight["static_audit_exit_code"] = audit_proc.returncode
            preflight["static_audit_report"] = audit_path.name
            (out_dir / "preflight.json").write_text(json.dumps(preflight, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        display = emulator_config.get("display", "1280x960x24")
        worker_cmd = [
            "xvfb-run", "-a", "--server-args", f"-screen 0 {display}",
            sys.executable, str(Path(__file__).resolve()),
            str(rom), "--config", str(args.config.resolve()), "--profile", args.profile,
            "--inside-xvfb", "--_work-rom", str(work_rom), "--_out-dir", str(out_dir), "--_emulator", emulator
        ]
        # xvfb-run needs the worker command to use the isolated copy, never the original ROM.
        worker_cmd[-1] = emulator
        result = subprocess.run(worker_cmd, capture_output=True, text=True,
                                timeout=sum(float(s.get("wait_seconds", 1)) + float(s.get("hold_ms", 0))/1000
                                            for s in emulator_config.get("stages", [])) + 70, check=False)
        (out_dir / "driver.stdout.txt").write_text(result.stdout, encoding="utf-8")
        (out_dir / "driver.stderr.txt").write_text(result.stderr, encoding="utf-8")
        # The driver is invoked with explicit private paths using a hidden worker flag.
        # The return code is recorded; it is not promoted to a gameplay pass.
        summary = {
            "diagnostic_return_code": result.returncode,
            "runtime_test_status": "OBSERVATION ONLY — not a gameplay pass",
            "rom_sha256": header["sha256"],
            "rom_was_copied_to_isolated_save_workspace": True
        }
        (out_dir / "diagnostic-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        readme = (
            "mGBA diagnostic evidence package\n"
            f"ROM file: {rom.name}\nSHA-256: {header['sha256']}\n"
            "The ROM itself is NOT included in this package.\n"
            "Review the screenshots, emulator.log, run.json and static-audit.json.\n"
            "A living emulator process is not proof that the game responded correctly.\n"
            "This is a boot/menu smoke test; full gameplay is not certified.\n"
        )
        (out_dir / "README.txt").write_text(readme, encoding="utf-8")
        zip_path = out_dir.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for path in sorted(out_dir.rglob("*")):
                if path.is_file():
                    z.write(path, path.relative_to(out_dir))
        print(f"Diagnostic report: {out_dir}")
        print(f"Evidence ZIP (ROM excluded): {zip_path}")
        print(f"ROM SHA-256: {header['sha256']}")
        print("Status: observation only; inspect screenshots/logs before making any gameplay claim.")
        return result.returncode
    except subprocess.TimeoutExpired as exc:
        print(f"gba diagnostic timed out: {exc}", file=sys.stderr)
        return 5
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"gba diagnostic: ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        if "work_root" in locals():
            shutil.rmtree(work_root, ignore_errors=True)


if __name__ == "__main__":
    # The hidden worker path is intentionally explicit, to keep save files isolated from the source ROM.
    if "--inside-xvfb" in sys.argv:
        p = argparse.ArgumentParser()
        p.add_argument("rom", type=Path)
        p.add_argument("--config", type=Path, required=True)
        p.add_argument("--profile", required=True)
        p.add_argument("--inside-xvfb", action="store_true")
        p.add_argument("--_work-rom", type=Path, required=True)
        p.add_argument("--_out-dir", type=Path, required=True)
        p.add_argument("--_emulator", required=True)
        w = p.parse_args()
        c = json.loads(w.config.read_text(encoding="utf-8"))
        result = worker(w, {"name": w.profile}, c, w._work_rom, w._out_dir, w._emulator)
        raise SystemExit(result)
    raise SystemExit(main())
