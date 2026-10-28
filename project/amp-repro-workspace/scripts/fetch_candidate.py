#!/usr/bin/env python3
"""Fetch a public UniProt / AlphaFold candidate and audit the downloaded evidence.

Python 3.9+; standard library only. This script performs read-only HTTP GETs.
It does not submit BLAST/Foldseek jobs, train models, or predict antimicrobial activity.

Both --accession and --out-dir are required; no candidate identity is assumed.
Use --offline only to recompute summaries from a previously downloaded snapshot.
For a read-only integrity audit, use case.py check instead.
"""

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


ALLOWED_HOSTS = {"rest.uniprot.org", "alphafold.ebi.ac.uk"}
AA3 = dict(zip(
    "ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL".split(),
    "ARNDCQEGHILKMFPSTWYV",
))
AA3.update({"SEC": "U", "PYL": "O", "ASX": "B", "GLX": "Z", "UNK": "X", "MSE": "M"})


class AuditError(Exception):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AuditError("Cannot read valid JSON from %s: %s" % (path, exc)) from exc


def validate_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise AuditError("Unexpected download URL (not an allowed public database host): " + str(url))


def download(url, filename, role, out_dir, manifest, timeout):
    validate_url(url)
    event = {"role": role, "file": filename, "requested_url": url,
             "requested_at_utc": utc_now()}
    manifest["downloads"].append(event)
    try:
        request = Request(url, headers={"User-Agent": "AMP-reproduction-audit/1.0 (read-only educational workflow)"})
        with urlopen(request, timeout=timeout) as response:
            final_url = response.geturl()
            validate_url(final_url)
            body = response.read(25 * 1024 * 1024 + 1)
            if len(body) > 25 * 1024 * 1024:
                raise AuditError("Download exceeds the 25 MiB per-file limit: " + url)
            event.update({
                "http_status": response.status,
                "final_url": final_url,
                "retrieved_at_utc": utc_now(),
                "headers": {k: response.headers[k] for k in (
                    "Content-Type", "ETag", "Last-Modified", "Date",
                    "X-UniProt-Release", "X-UniProt-Release-Date",
                ) if response.headers.get(k) is not None},
                "bytes": len(body), "sha256": sha256(body),
            })
        path = out_dir / filename
        tmp = path.with_suffix(path.suffix + ".part")
        tmp.write_bytes(body)
        tmp.replace(path)
    except HTTPError as exc:
        event.update({"http_status": exc.code, "error": str(exc), "failed_at_utc": utc_now()})
        raise AuditError("HTTP %s fetching %s. This can indicate an absent record or a temporarily unavailable API; no result has been invented."
                         % (exc.code, url)) from exc
    except (URLError, TimeoutError, OSError) as exc:
        event.update({"http_status": None, "error": str(exc), "failed_at_utc": utc_now()})
        raise AuditError("Network/download failure for %s: %s. Re-run online later, or use --offline only with a complete saved snapshot."
                         % (url, exc)) from exc
    finally:
        save_json(out_dir / "manifest.json", manifest)


def fasta_sequence(path, accession):
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines or not lines[0].startswith(">") or sum(line.startswith(">") for line in lines) != 1:
        raise AuditError("Expected exactly one FASTA record.")
    tokens = lines[0][1:].split()[0].split("|")
    if accession not in tokens:
        raise AuditError("FASTA accession does not match the requested UniProt accession.")
    return "".join(lines[1:]).upper()


def choose_model(records, accession, sequence):
    if not isinstance(records, list):
        raise AuditError("AlphaFold API schema changed: expected a list of records.")
    full = [r for r in records if r.get("uniprotAccession") == accession
            and r.get("sequence", r.get("uniprotSequence")) == sequence
            and int(r.get("sequenceStart", 1)) == 1
            and int(r.get("sequenceEnd", len(sequence))) == len(sequence)]
    if len(full) != 1:
        raise AuditError("Expected one full-length matching AlphaFold model; found %d. Fragmented/multiple models need manual review." % len(full))
    if not full[0].get("pdbUrl"):
        raise AuditError("The matching AlphaFold API record has no PDB download URL.")
    return full[0]


def validate_uniprot(record, accession):
    if record.get("primaryAccession") != accession:
        raise AuditError("UniProt primary accession differs from the requested ID; resolve any merged/deleted entry explicitly.")
    seq = record.get("sequence", {}).get("value", "")
    if not seq or not re.fullmatch(r"[A-Z]+", seq):
        raise AuditError("UniProt sequence is empty or malformed.")
    if record.get("sequence", {}).get("length") != len(seq):
        raise AuditError("UniProt declared length differs from the actual sequence length.")
    return seq


def pdb_ca_values(path, chain, sequence):
    residues = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("ENDMDL"):
            break
        if line[:6].strip() not in {"ATOM", "HETATM"} or len(line) < 66:
            continue
        if line[12:16].strip() != "CA" or line[21:22] != chain or line[16:17] not in {" ", "A"}:
            continue
        key = (int(line[22:26]), line[26:27])
        aa = AA3.get(line[17:20].strip())
        if aa is None:
            raise AuditError("Unknown residue in downloaded PDB: " + line[17:20].strip())
        residues.setdefault(key, (aa, float(line[60:66])))
    ordered = sorted(residues.items())
    pdb_sequence = "".join(value[0] for _, value in ordered)
    if pdb_sequence != sequence:
        raise AuditError("PDB CA sequence differs from UniProt (or has missing residues/incorrect chain); confidence mapping is unsafe.")
    return [value[1] for _, value in ordered]


def read_confidence(path, length):
    obj = load_json(path)
    positions = obj.get("residueNumber")
    values = obj.get("confidenceScore")
    if positions != list(range(1, length + 1)) or not isinstance(values, list) or len(values) != length:
        raise AuditError("Unexpected confidence JSON schema or residue numbering; inspect the saved file.")
    return [float(x) for x in values]


def band(value):
    if value >= 90:
        return "very_high_90_to_100"
    if value >= 70:
        return "confident_70_to_90"
    if value >= 50:
        return "low_50_to_70"
    return "very_low_below_50"


def verify_snapshot(out_dir, manifest, accession):
    if manifest.get("accession") != accession:
        raise AuditError("Saved manifest accession differs from requested accession.")
    required = {"uniprot_json", "uniprot_fasta", "alphafold_api", "alphafold_pdb"}
    available = set()
    for item in manifest.get("downloads", []):
        if "sha256" not in item:
            continue
        filename = item.get("file", "")
        if Path(filename).name != filename:
            raise AuditError("Unsafe filename in manifest.")
        path = out_dir / filename
        if not path.is_file() or sha256(path.read_bytes()) != item["sha256"]:
            raise AuditError("Snapshot integrity check failed for " + filename)
        available.add(item["role"])
    if not required.issubset(available):
        raise AuditError("Incomplete snapshot; missing successful downloads for: " + ", ".join(sorted(required - available)))
    return available


def analyze(out_dir, accession, manifest):
    available = verify_snapshot(out_dir, manifest, accession)
    record = load_json(out_dir / "uniprot.json")
    seq = validate_uniprot(record, accession)
    if fasta_sequence(out_dir / "candidate.fasta", accession) != seq:
        raise AuditError("UniProt FASTA and JSON sequences differ.")
    af = choose_model(load_json(out_dir / "alphafold_api.json"), accession, seq)
    values_pdb = pdb_ca_values(out_dir / "alphafold_model.pdb", af.get("chainId", "A"), seq)
    if "alphafold_confidence" in available:
        values = read_confidence(out_dir / "alphafold_confidence.json", len(seq))
        if max(abs(a - b) for a, b in zip(values, values_pdb)) > 0.11:
            raise AuditError("Confidence JSON scores and PDB CA B-factor scores disagree.")
        confidence_source = "AlphaFold confidence JSON, cross-checked against PDB CA B-factors"
    else:
        values = values_pdb
        confidence_source = "AlphaFold PDB CA B-factors (confidence-file URL absent from API)"
    if any(not math.isfinite(v) or not 0 <= v <= 100 for v in values):
        raise AuditError("pLDDT values outside 0-100 or nonfinite.")
    description = record.get("proteinDescription", {})
    full_name = description.get("recommendedName", {}).get("fullName", {})
    if not full_name.get("value"):
        full_name = next((name.get("fullName", {}) for name in description.get("submissionNames", [])
                          if name.get("fullName", {}).get("value")), {})
    counts = Counter(band(v) for v in values)
    low_positions = [i for i, v in enumerate(values, 1) if v < 70]
    warnings = [
        "pLDDT measures predicted local structural confidence; it is not an antimicrobial-activity probability.",
        "This workflow does not experimentally determine a signal-peptide cleavage site or mature-peptide sequence. Any existing UniProt features are reproduced as database annotations, with their original evidence.",
        "Current database results are a dated snapshot; they do not establish the versions used by any earlier study.",
        "BLAST, Foldseek, experimental validation and genomic-neighborhood validation are not performed by this script.",
    ]
    gene_names = [g[n][i]["value"] for g in record.get("genes", [])
                  for n in ("orfNames", "orderedLocusNames") if n in g for i in range(len(g[n]))]
    if af.get("gene") and af["gene"] not in gene_names:
        warnings.append("AlphaFold gene label differs from current UniProt locus labels. Confirm strain/contig before analyzing neighboring genes.")
    feature_confidence = []
    for feature in record.get("features", []):
        start = feature.get("location", {}).get("start", {}).get("value")
        end = feature.get("location", {}).get("end", {}).get("value")
        if feature.get("type") in {"Signal", "Chain"} and isinstance(start, int) and isinstance(end, int) and 1 <= start <= end <= len(values):
            region = values[start - 1:end]
            feature_confidence.append({
                "feature_type": feature["type"], "start_1_based": start, "end_1_based": end,
                "length": end - start + 1, "mean_plddt": round(sum(region) / len(region), 4),
                "evidences": feature.get("evidences", []),
                "interpretation": "Region boundaries are existing UniProt annotations, not inferred from pLDDT or experimentally verified by this script.",
            })
    strains = sorted({c["value"] for r in record.get("references", [])
                      for c in r.get("referenceComments", []) if c.get("type") == "STRAIN" and c.get("value")})
    summary = {
        "analysis_at_utc": utc_now(), "accession": accession,
        "sequence_length": len(seq), "sequence_sha256": sha256(seq.encode("ascii")),
        "sequence_md5": hashlib.md5(seq.encode("ascii")).hexdigest(),
        "entry_type": record.get("entryType"), "entry_audit": record.get("entryAudit"),
        "secondary_accessions": record.get("secondaryAccessions", []),
        "uniparc_id": record.get("extraAttributes", {}).get("uniParcId"),
        "protein_existence": record.get("proteinExistence"), "strains_in_references": strains,
        "caution_comments": [c for c in record.get("comments", []) if c.get("commentType") == "CAUTION"],
        "organism": record.get("organism"), "genes": record.get("genes", []),
        "protein_name": full_name.get("value"), "protein_name_evidence": full_name.get("evidences", []),
        "cross_references": record.get("uniProtKBCrossReferences", []),
        "sequence_features": record.get("features", []),
        "alphafold": {k: af.get(k) for k in (
            "entryId", "modelEntityId", "latestVersion", "modelCreatedDate", "toolUsed",
            "sequenceVersionDate", "globalMetricValue", "gene", "sequenceChecksum", "pdbUrl",
        )},
        "confidence": {
            "source": confidence_source, "count": len(values),
            "mean_plddt": round(sum(values) / len(values), 4),
            "min_plddt": min(values), "max_plddt": max(values),
            "band_boundaries": "[0,50), [50,70), [70,90), [90,100]",
            "band_counts": dict(counts), "positions_below_70": low_positions,
            "annotated_feature_regions": feature_confidence,
        },
        "checks": {
            "download_hashes_match": True, "json_fasta_sequences_match": True,
            "uniprot_alphafold_api_sequences_match": True,
            "uniprot_pdb_ca_sequences_match": True,
            "confidence_json_matches_pdb": "alphafold_confidence" in available,
        },
        "warnings": warnings,
    }
    save_json(out_dir / "summary.json", summary)
    with (out_dir / "confidence.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["position_1_based", "amino_acid", "plddt", "confidence_band"])
        writer.writerows((i, aa, "%.2f" % v, band(v)) for i, (aa, v) in enumerate(zip(seq, values), 1))
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--accession", required=True, help="UniProt accession; no default candidate")
    parser.add_argument("--out-dir", type=Path, required=True, help="Explicit snapshot directory")
    parser.add_argument("--offline", action="store_true", help="Verify hashes and re-analyze existing files; make no network requests")
    parser.add_argument("--timeout", type=float, default=30, help="Per-request timeout in seconds (default: 30)")
    args = parser.parse_args(argv)
    accession = args.accession.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{6,10}", accession):
        parser.error("accession must be a 6-10 character alphanumeric UniProt accession")
    if args.timeout <= 0:
        parser.error("timeout must be positive")
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        if args.offline:
            manifest = load_json(out_dir / "manifest.json")
        else:
            if any(out_dir.iterdir()):
                raise AuditError("The output directory is not empty. Use --offline to analyze an existing snapshot, or choose a NEW empty --out-dir for a new dated download.")
            manifest = {"schema_version": 1, "accession": accession,
                        "created_at_utc": utc_now(), "downloads": []}
            safe_id = quote(accession, safe="")
            download("https://rest.uniprot.org/uniprotkb/%s.json" % safe_id,
                     "uniprot.json", "uniprot_json", out_dir, manifest, args.timeout)
            uniprot_record = load_json(out_dir / "uniprot.json")
            sequence = validate_uniprot(uniprot_record, accession)
            manifest["record_versions"] = {"uniprot": uniprot_record.get("entryAudit", {})}
            save_json(out_dir / "manifest.json", manifest)
            download("https://rest.uniprot.org/uniprotkb/%s.fasta" % safe_id,
                     "candidate.fasta", "uniprot_fasta", out_dir, manifest, args.timeout)
            download("https://alphafold.ebi.ac.uk/api/prediction/%s" % safe_id,
                     "alphafold_api.json", "alphafold_api", out_dir, manifest, args.timeout)
            model = choose_model(load_json(out_dir / "alphafold_api.json"), accession, sequence)
            manifest["record_versions"]["alphafold"] = {k: model.get(k) for k in (
                "entryId", "modelEntityId", "latestVersion", "modelCreatedDate", "sequenceVersionDate",
            )}
            save_json(out_dir / "manifest.json", manifest)
            download(model["pdbUrl"], "alphafold_model.pdb", "alphafold_pdb", out_dir, manifest, args.timeout)
            if model.get("plddtDocUrl"):
                download(model["plddtDocUrl"], "alphafold_confidence.json", "alphafold_confidence", out_dir, manifest, args.timeout)
        summary = analyze(out_dir, accession, manifest)
        print("OK: %s; %d residues; mean pLDDT %.4f" %
              (accession, summary["sequence_length"], summary["confidence"]["mean_plddt"]))
        print("Results: %s" % out_dir)
        print("Evidence: manifest.json, summary.json, confidence.tsv and downloaded source files.")
        print("No BLAST/Foldseek searches or biological activity measurements were performed.")
        return 0
    except (AuditError, OSError, KeyError, ValueError, TypeError) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
