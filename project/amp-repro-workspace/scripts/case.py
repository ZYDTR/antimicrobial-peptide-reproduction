#!/usr/bin/env python3
"""Manage isolated protein-reproduction cases (Python 3.9+, standard library).

Run from any directory: the project root is the parent of this scripts folder.
Only `fetch` uses the network, through fetch_candidate.py. `check`/`verify` is
read-only and audits raw-data manifests; it does not mark scientific steps done.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CASE_ID_RE = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
ACCESSION_RE = re.compile(r"[A-Z0-9]{6,10}\Z")
SHA256_RE = re.compile(r"[0-9a-fA-F]{64}\Z")


class CaseError(Exception):
    pass


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def valid_case_id(value):
    if not isinstance(value, str) or not CASE_ID_RE.fullmatch(value):
        raise CaseError("Unsafe case ID. Use 1-64 lowercase letters, digits, '_' or '-', starting with a letter or digit.")
    return value


def valid_accession(value):
    if not isinstance(value, str) or not ACCESSION_RE.fullmatch(value):
        raise CaseError("Accession must be 6-10 uppercase alphanumeric characters.")
    return value


def no_symlinks(path, boundary):
    """Do not silently follow a case or evidence link into another location."""
    try:
        relative = path.relative_to(boundary)
    except ValueError as exc:
        raise CaseError("Path is outside the allowed directory: " + str(path)) from exc
    current = boundary
    if current.is_symlink():
        raise CaseError("Symbolic links are not audited: " + str(current))
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise CaseError("Symbolic links are not allowed in case paths: " + str(current))


def read_json(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CaseError("Cannot read JSON at %s: %s" % (path, exc)) from exc
    if not isinstance(data, dict):
        raise CaseError("Expected a JSON object at " + str(path))
    return data


def write_json_atomic(path, data):
    """Used only for new configuration files or the active-case pointer."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent),
                                         prefix="." + path.name + ".", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(str(temporary), str(path))
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_project():
    path = PROJECT_ROOT / "project.json"
    no_symlinks(path, PROJECT_ROOT)
    project = read_json(path)
    if type(project.get("schema_version")) is not int or project["schema_version"] != 1:
        raise CaseError("project.json must have schema_version: 1.")
    valid_case_id(project.get("active_case"))
    return project


def case_path(case_id):
    valid_case_id(case_id)
    path = PROJECT_ROOT / "cases" / case_id
    no_symlinks(path, PROJECT_ROOT)
    return path


def validate_case_config(config, case_id):
    if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        raise CaseError("case.json must have schema_version: 1.")
    if config.get("case_id") != case_id:
        raise CaseError("case.json case_id does not match its folder name.")
    valid_accession(config.get("accession"))
    created = config.get("created_at_utc")
    if not isinstance(created, str) or not created:
        raise CaseError("case.json is missing created_at_utc.")
    source = config.get("source")
    if "source" not in config or (source is not None and (
            not isinstance(source, dict) or not isinstance(source.get("id"), str)
            or not source["id"] or not isinstance(source.get("reference"), str)
            or not source["reference"])):
        raise CaseError("source must be null, or an object with nonempty id and reference.")
    fields = {
        "discovery": ("taxonomy_id", "length_min", "length_max", "annotation_source", "provenance"),
        "genome_context": ("strain", "assembly", "contig", "protein_id", "locus_tag"),
        "region": ("mode", "start", "end", "basis"),
    }
    for name, required in fields.items():
        if not isinstance(config.get(name), dict) or not all(k in config[name] for k in required):
            raise CaseError("case.json has an incomplete %s object." % name)
    if not isinstance(config["region"]["mode"], str) or not config["region"]["mode"]:
        raise CaseError("region.mode must be a nonempty string.")


def load_case(case_id=None):
    project = load_project()
    chosen = valid_case_id(case_id if case_id is not None else project["active_case"])
    directory = case_path(chosen)
    if not directory.is_dir():
        raise CaseError("Unknown case: " + chosen)
    path = directory / "case.json"
    no_symlinks(path, directory)
    config = read_json(path)
    validate_case_config(config, chosen)
    state = directory / "STATE.md"
    no_symlinks(state, directory)
    if not state.is_file():
        raise CaseError("Case is missing STATE.md: " + chosen)
    return project, directory, config


def empty_case(case_id, accession):
    return {
        "schema_version": 1,
        "case_id": case_id,
        "accession": accession,
        "created_at_utc": now_utc(),
        "source": None,
        "discovery": {"taxonomy_id": None, "length_min": None, "length_max": None,
                      "annotation_source": None, "provenance": "not_set"},
        "genome_context": {"strain": None, "assembly": None, "contig": None,
                           "protein_id": None, "locus_tag": None},
        "region": {"mode": "full_length", "start": None, "end": None, "basis": None},
    }


def initial_state(config):
    return """# 当前科学进度

Case: `{case_id}`；候选：`{accession}`；创建时间 UTC：{created_at_utc}。
这是新案例，尚无科学结果。

## 下一步

- next_action：按实际任务补充 case.json 的 source（当前为 null），核对来源或研究问题，再抓取并验证本案记录。
- next_skill：[source-sequence](../../skills/source-sequence/SKILL.md)。
- input：[case.json](case.json) 的 accession；目前没有本案 FASTA。
- first_command：配置后在项目根目录运行 `python3 scripts/case.py fetch --case {case_id}`。
- expected_output：本案新的 data 时间戳目录与 results 派生结果；核对后再更新状态。
- blockers：来源/研究问题尚未配置；远端下载尚未尝试。筛选与基因环境参数需要本案证据。

## 步骤状态

| step_id | 状态 | 最后核对 | 证据 / 结论 |
| --- | --- | --- | --- |
| source_identity | pending | — | |
| initial_search | pending | — | |
| candidate_record | pending | — | |
| processing_annotation | pending | — | |
| alphafold_confidence | pending | — | |
| blast_swissprot | pending | — | |
| foldseek_search | pending | — | |
| structure_superposition | pending | — | |
| genomic_neighborhood | pending | — | |
| candidate_literature | pending | — | |
| final_report | pending | — | |

## 交接

只根据本案产物增加结论；旧案例的结果不能迁入。没有执行的步骤保持 pending。
本案尚无后台任务、原始证据或 token 账单；湿实验活性没有被本项目验证。
""".format(**config)


def command_status(args):
    _, directory, config = load_case(args.case_id)
    print("Case configuration: " + str(directory / "case.json"))
    print("Accession: " + config["accession"])
    print("State file: " + str(directory / "STATE.md"))
    print()
    print((directory / "STATE.md").read_text(encoding="utf-8"), end="")
    return 0


def command_new(args):
    load_project()
    chosen = valid_case_id(args.case_id)
    accession = valid_accession(args.accession.strip().upper())
    directory = case_path(chosen)
    cases = directory.parent
    cases.mkdir(exist_ok=True)
    try:
        directory.mkdir(exist_ok=False)
    except FileExistsError as exc:
        raise CaseError("Case already exists; refusing to overwrite: " + chosen) from exc
    config = empty_case(chosen, accession)
    write_json_atomic(directory / "case.json", config)
    (directory / "STATE.md").write_text(initial_state(config), encoding="utf-8")
    for name in ("data", "results", "reports"):
        (directory / name).mkdir()
    print("Created case: " + chosen)
    print("Configuration: " + str(directory / "case.json"))
    print("All evidence stages are pending; source is null and needs configuration.")
    print("Active case unchanged. Switch explicitly with: python3 scripts/case.py use " + chosen)
    return 0


def command_use(args):
    project, _, config = load_case(args.case_id)
    project["active_case"] = config["case_id"]
    write_json_atomic(PROJECT_ROOT / "project.json", project)
    print("Active case: %s (%s)" % (config["case_id"], config["accession"]))
    return 0


def command_fetch(args):
    _, directory, config = load_case(args.case_id)
    data = directory / "data"
    no_symlinks(data, directory)
    data.mkdir(exist_ok=True)
    # Exclusive creation plus microseconds prevents overwriting an older snapshot.
    for _ in range(10):
        snapshot = data / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        try:
            snapshot.mkdir(exist_ok=False)
            break
        except FileExistsError:
            continue
    else:
        raise CaseError("Could not allocate a unique UTC snapshot directory.")
    fetcher = PROJECT_ROOT / "scripts" / "fetch_candidate.py"
    no_symlinks(fetcher, PROJECT_ROOT)
    if not fetcher.is_file():
        raise CaseError("Missing scripts/fetch_candidate.py.")
    print("Fetching %s for case %s" % (config["accession"], config["case_id"]), flush=True)
    print("New snapshot: " + str(snapshot), flush=True)
    if config["source"] is None:
        print("Source remains unconfigured in case.json; a download does not establish the study context.", flush=True)
    result = subprocess.run([sys.executable, str(fetcher), "--accession", config["accession"],
                             "--out-dir", str(snapshot)])
    if result.returncode:
        print("Fetch failed; partial evidence is retained at " + str(snapshot), file=sys.stderr)
        print("STATE.md was not changed.", file=sys.stderr)
        return result.returncode if result.returncode > 0 else 1
    derived = directory / "results" / snapshot.name
    derived.mkdir(parents=True, exist_ok=False)
    for filename in ("summary.json", "confidence.tsv"):
        (snapshot / filename).replace(derived / filename)
    print("Raw snapshot: " + str(snapshot))
    print("Derived results: " + str(derived))
    print("Review the evidence before updating STATE.md.")
    print("BLAST, Foldseek, genomic-neighborhood validation and biological activity were not evaluated by this download.")
    return 0


def data_manifests(data):
    """Discover manifests only inside this case's data tree, without links."""
    found = []
    if not data.is_dir():
        raise CaseError("Case has no data directory: " + str(data))
    for current, directories, files in os.walk(str(data), followlinks=False):
        base = Path(current)
        for name in directories + files:
            if (base / name).is_symlink():
                raise CaseError("Symlink inside raw-data tree cannot be audited: " + str(base / name))
        for name in files:
            if name.lower().endswith("manifest.json"):
                found.append(base / name)
    return sorted(found)


def evidence_path(base, filename, data):
    if not isinstance(filename, str) or not filename or "\\" in filename or ":" in filename:
        raise CaseError("Invalid manifest filename: " + repr(filename))
    relative = PurePosixPath(filename)
    if relative.is_absolute() or ".." in relative.parts:
        raise CaseError("Unsafe manifest filename: " + filename)
    path = base.joinpath(*relative.parts)
    no_symlinks(path, data)
    if not path.is_file():
        raise CaseError("Missing raw file: " + str(path))
    if not path.resolve().is_relative_to(data.resolve()):
        raise CaseError("Raw file escapes this case's data directory: " + str(path))
    return path


def check_hash(path, expected, expected_bytes=None):
    if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
        raise CaseError("Invalid SHA-256 recorded for " + str(path))
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    if digest.hexdigest() != expected.lower():
        raise CaseError("SHA-256 mismatch: " + str(path))
    if expected_bytes is not None and (type(expected_bytes) is not int or expected_bytes != size):
        raise CaseError("Recorded byte count mismatch: " + str(path))


def check_raw_identity(path, role, accession):
    if role == "uniprot_json":
        if read_json(path).get("primaryAccession") != accession:
            raise CaseError("Raw UniProt accession does not match case: " + str(path))
    elif role == "uniprot_fasta":
        with path.open(encoding="utf-8") as handle:
            header = next((line.strip() for line in handle if line.strip()), "")
        if not header.startswith(">") or accession not in header[1:].split()[0].split("|"):
            raise CaseError("Raw FASTA accession does not match case: " + str(path))
    elif role == "alphafold_api":
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise CaseError("Invalid AlphaFold API JSON: " + str(path)) from exc
        if not isinstance(records, list) or not records or any(
                not isinstance(item, dict) or item.get("uniprotAccession") != accession for item in records):
            raise CaseError("Raw AlphaFold accession does not match case: " + str(path))


def verify_manifest(path, data, accession):
    manifest = read_json(path)
    if "accession" in manifest and manifest["accession"] != accession:
        raise CaseError("Manifest accession %r differs from case accession %s: %s" %
                        (manifest["accession"], accession, path))
    if "downloads" in manifest:
        if manifest.get("accession") != accession:
            raise CaseError("A download manifest must explicitly identify this case's accession: " + str(path))
        if not isinstance(manifest["downloads"], list):
            raise CaseError("Manifest downloads must be an array: " + str(path))
        if not manifest["downloads"]:
            raise CaseError("Empty download manifest has no raw hashes to verify: " + str(path))
        count = 0
        for item in manifest["downloads"]:
            if not isinstance(item, dict) or "sha256" not in item:
                raise CaseError("Incomplete download record without a saved SHA-256: " + str(path))
            raw = evidence_path(path.parent, item.get("file"), data)
            check_hash(raw, item["sha256"], item.get("bytes"))
            check_raw_identity(raw, item.get("role"), accession)
            count += 1
        return count
    if "raw_file" in manifest and "sha256" in manifest:
        raw = evidence_path(path.parent, manifest["raw_file"], data)
        check_hash(raw, manifest["sha256"])
        # Discovery tables can legitimately contain several different accessions.
        return 1
    raise CaseError("Unsupported manifest format: " + str(path))


def command_check(args):
    _, directory, config = load_case(args.case_id)
    data = directory / "data"
    no_symlinks(data, directory)
    manifests = data_manifests(data)
    print("Case identity: %s / %s" % (config["case_id"], config["accession"]))
    print("Audit scope: " + str(data))
    if not manifests:
        print("No raw-data manifests found. Configuration is valid; there is no raw evidence to verify yet.")
        return 0
    failures = 0
    files = 0
    for manifest in manifests:
        try:
            count = verify_manifest(manifest, data, config["accession"])
            files += count
            print("OK: %s (%d file hashes)" % (manifest.relative_to(data), count))
        except (CaseError, OSError, ValueError, TypeError, IndexError) as exc:
            failures += 1
            print("FAIL: " + str(exc), file=sys.stderr)
    if failures:
        print("FAILED: %d manifest(s) could not be verified; no files were changed." % failures, file=sys.stderr)
        return 1
    print("Verified %d raw-file hash records across %d manifests. No files were changed." % (files, len(manifests)))
    print("This is a case-identity and file-integrity audit; scientific step status is unchanged.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status", help="Read case configuration and the full STATE.md; never inspect raw data")
    status.add_argument("--case", dest="case_id", help="Case ID; defaults to project.json active_case")
    status.set_defaults(action=command_status)
    new = commands.add_parser("new", help="Create an empty, pending case without changing the active case")
    new.add_argument("--id", dest="case_id", required=True)
    new.add_argument("--accession", required=True)
    new.set_defaults(action=command_new)
    use = commands.add_parser("use", help="Validate a case and switch the active-case pointer")
    use.add_argument("case_id")
    use.set_defaults(action=command_use)
    fetch = commands.add_parser("fetch", help="Download a new uniquely named raw snapshot for this case")
    fetch.add_argument("--case", dest="case_id", help="Case ID; defaults to active case")
    fetch.set_defaults(action=command_fetch)
    check = commands.add_parser("check", aliases=["verify"], help="Offline, read-only audit of this case's data manifests")
    check.add_argument("--case", dest="case_id", help="Case ID; defaults to active case")
    check.set_defaults(action=command_check)
    args = parser.parse_args(argv)
    try:
        return args.action(args)
    except (CaseError, OSError, ValueError, TypeError, KeyError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
