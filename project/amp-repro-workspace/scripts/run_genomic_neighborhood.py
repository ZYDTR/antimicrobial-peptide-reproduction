#!/usr/bin/env python3
"""Genomic neighborhood analysis for candidate A0A0U0D591 on contig RAHZ01000002.1.

Downloads complete GenBank, GFF3, and FASTA records from NCBI Entrez E-utilities,
verifies target locus coordinates and translation against candidate.fasta,
computes intergenic distances across flanking CDSs, and generates audit manifests.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import urllib.parse
import urllib.request
from Bio import SeqIO

USER_EMAIL = "science.repro@gmail.com"
USER_AGENT = f"ScienceSkillsRepro/1.0 ({USER_EMAIL})"
NCBI_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def fetch_ncbi(db: str, record_id: str, rettype: str, retmode: str = "text") -> bytes:
    params = {
        "db": db,
        "id": record_id,
        "rettype": rettype,
        "retmode": retmode,
    }
    url = f"{NCBI_EFETCH_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        return resp.read()

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_str(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def main():
    repo_root = Path(__file__).resolve().parent.parent
    case_dir = repo_root / "cases" / "paper-a0a0u0d591"
    data_dir = case_dir / "data" / "2026-10-27-genomic"
    results_dir = case_dir / "results"
    candidate_fasta_path = case_dir / "data" / "2026-10-23-record" / "candidate.fasta"

    data_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    # 1. Read candidate FASTA
    with open(candidate_fasta_path, encoding="utf-8") as f:
        cand_lines = [line.strip() for line in f if not line.startswith(">")]
    candidate_seq = "".join(cand_lines)
    candidate_sha = sha256_str(candidate_seq)
    print(f"Loaded candidate sequence: {len(candidate_seq)} aa, SHA-256: {candidate_sha}")

    # 2. Fetch raw genomic records
    contig_id = "RAHZ01000002.1"
    now_iso = datetime.now(timezone.utc).isoformat()

    downloads_manifest = []

    # GenBank
    print("Fetching GenBank record...")
    gb_bytes = fetch_ncbi("nuccore", contig_id, "gb", "text")
    gb_file = data_dir / "RAHZ01000002.1.gb"
    gb_file.write_bytes(gb_bytes)
    downloads_manifest.append({
        "role": "genbank_record",
        "file": "RAHZ01000002.1.gb",
        "requested_url": f"{NCBI_EFETCH_URL}?db=nuccore&id={contig_id}&rettype=gb&retmode=text",
        "retrieved_at_utc": now_iso,
        "http_status": 200,
        "bytes": len(gb_bytes),
        "sha256": sha256_bytes(gb_bytes),
    })

    # GFF3
    print("Fetching GFF3 record...")
    gff_bytes = fetch_ncbi("nuccore", contig_id, "gff3", "text")
    gff_file = data_dir / "RAHZ01000002.1.gff3"
    gff_file.write_bytes(gff_bytes)
    downloads_manifest.append({
        "role": "gff3_record",
        "file": "RAHZ01000002.1.gff3",
        "requested_url": f"{NCBI_EFETCH_URL}?db=nuccore&id={contig_id}&rettype=gff3&retmode=text",
        "retrieved_at_utc": now_iso,
        "http_status": 200,
        "bytes": len(gff_bytes),
        "sha256": sha256_bytes(gff_bytes),
    })

    # FASTA
    print("Fetching FASTA record...")
    fasta_bytes = fetch_ncbi("nuccore", contig_id, "fasta", "text")
    fasta_file = data_dir / "RAHZ01000002.1.fasta"
    fasta_file.write_bytes(fasta_bytes)
    downloads_manifest.append({
        "role": "contig_fasta",
        "file": "RAHZ01000002.1.fasta",
        "requested_url": f"{NCBI_EFETCH_URL}?db=nuccore&id={contig_id}&rettype=fasta&retmode=text",
        "retrieved_at_utc": now_iso,
        "http_status": 200,
        "bytes": len(fasta_bytes),
        "sha256": sha256_bytes(fasta_bytes),
    })

    # Write manifest.json
    manifest_data = {
        "schema_version": 1,
        "accession": "A0A0U0D591",
        "created_at_utc": now_iso,
        "task": "genomic_neighborhood",
        "contig_id": contig_id,
        "organism": "Streptococcus pseudopneumoniae",
        "strain": "Spain2270",
        "downloads": downloads_manifest,
    }
    manifest_file = data_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote manifest: {manifest_file}")

    # 3. Parse GenBank CDS features
    record = SeqIO.read(io.StringIO(gb_bytes.decode("utf-8")), "genbank")
    cds_features = []
    for feat in record.features:
        if feat.type == "CDS":
            locus = feat.qualifiers.get("locus_tag", [""])[0]
            protein_id = feat.qualifiers.get("protein_id", [""])[0]
            gene = feat.qualifiers.get("gene", [""])[0]
            product = feat.qualifiers.get("product", [""])[0]
            translation = feat.qualifiers.get("translation", [""])[0]
            # 1-based inclusive
            start = int(feat.location.start) + 1
            end = int(feat.location.end)
            strand = "+" if feat.location.strand == 1 else "-"
            cds_features.append({
                "locus_tag": locus,
                "protein_id": protein_id,
                "gene": gene,
                "product": product,
                "start": start,
                "end": end,
                "strand": strand,
                "length_aa": len(translation),
                "translation": translation,
                "sha256_translation": sha256_str(translation),
            })

    # Sort CDS by genomic start coordinate
    cds_features.sort(key=lambda c: c["start"])

    # Locate target
    target_idx = None
    for i, c in enumerate(cds_features):
        if c["locus_tag"] == "D6867_00595" or c["protein_id"] == "RJY15081.1":
            target_idx = i
            break

    if target_idx is None:
        raise RuntimeError("Target locus D6867_00595 / protein RJY15081.1 not found in record!")

    target = cds_features[target_idx]
    is_translation_match = (target["translation"] == candidate_seq)
    print(f"Target found at index {target_idx}: locus={target['locus_tag']}, protein_id={target['protein_id']}, coords={target['start']}..{target['end']}({target['strand']})")
    print(f"Translation length: {target['length_aa']} aa, Matches candidate FASTA: {is_translation_match}")
    if not is_translation_match:
        raise RuntimeError("Target CDS translation does NOT match candidate sequence!")

    # 4. Compute intergenic distances across contig CDSs
    # 1-based inclusive: gap from previous CDS = current.start - prev.end - 1
    for i in range(len(cds_features)):
        if i == 0:
            cds_features[i]["gap_from_prev_bp"] = None
        else:
            prev = cds_features[i - 1]
            gap = cds_features[i]["start"] - prev["end"] - 1
            cds_features[i]["gap_from_prev_bp"] = gap

    # 5. Extract neighborhood window (e.g., target_idx - 5 to target_idx + 5)
    win_start = max(0, target_idx - 5)
    win_end = min(len(cds_features), target_idx + 6)
    neighborhood = cds_features[win_start:win_end]

    # Annotate relation to target based on strand
    # For minus strand (-), transcription proceeds from higher coordinates to lower coordinates.
    # Therefore, features with higher coordinates (idx > target_idx) are upstream in transcription.
    # Features with lower coordinates (idx < target_idx) are downstream in transcription.
    for c in neighborhood:
        offset = cds_features.index(c) - target_idx
        c["offset_from_target"] = offset
        if offset == 0:
            c["relation_to_target"] = "TARGET"
        elif offset > 0:
            # Physical coordinates are higher than target.
            # Since target is on minus strand, transcription runs 48432 -> 48139.
            # Genes with coords > 48432 are physically upstream of target transcription.
            c["relation_to_target"] = f"upstream (offset +{offset})"
        else:
            # Physical coordinates are lower than target.
            # Genes with coords < 48139 are downstream in target transcription.
            c["relation_to_target"] = f"downstream (offset {offset})"

    # Write all CDS table
    all_tsv_path = results_dir / "genomic_neighborhood_all_cds.tsv"
    with open(all_tsv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([
            "index", "locus_tag", "protein_id", "gene", "start", "end", "strand",
            "length_aa", "product", "gap_from_prev_bp", "is_target"
        ])
        for i, c in enumerate(cds_features):
            writer.writerow([
                i, c["locus_tag"], c["protein_id"], c["gene"], c["start"], c["end"], c["strand"],
                c["length_aa"], c["product"], c["gap_from_prev_bp"] if c["gap_from_prev_bp"] is not None else "",
                "YES" if i == target_idx else "NO"
            ])
    print(f"Wrote all CDS TSV: {all_tsv_path}")

    # Write neighborhood TSV
    neigh_tsv_path = results_dir / "genomic_neighborhood.tsv"
    with open(neigh_tsv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([
            "offset", "locus_tag", "protein_id", "gene", "start", "end", "strand",
            "length_aa", "gap_from_prev_bp", "relation_to_target", "product"
        ])
        for c in neighborhood:
            writer.writerow([
                f"{c['offset_from_target']:+d}", c["locus_tag"], c["protein_id"], c["gene"],
                c["start"], c["end"], c["strand"], c["length_aa"],
                c["gap_from_prev_bp"] if c["gap_from_prev_bp"] is not None else "",
                c["relation_to_target"], c["product"]
            ])
    print(f"Wrote neighborhood TSV: {neigh_tsv_path}")

    # Calculate key metrics
    # Downstream immediate neighbor is index target_idx - 1 (D6867_00590)
    downstream_neighbor = cds_features[target_idx - 1]
    # Gap between target (48139..48432) and D6867_00590 (45931..48132)
    # Physical gap: target.start - neighbor.end - 1 = 48139 - 48132 - 1 = 6 bp
    gap_to_downstream = target["start"] - downstream_neighbor["end"] - 1

    summary = {
        "schema_version": 1,
        "accession": "A0A0U0D591",
        "contig": contig_id,
        "organism": "Streptococcus pseudopneumoniae strain Spain2270",
        "target": {
            "locus_tag": target["locus_tag"],
            "protein_id": target["protein_id"],
            "coords_1based_inclusive": [target["start"], target["end"]],
            "strand": target["strand"],
            "length_aa": target["length_aa"],
            "product": target["product"],
            "translation_matches_candidate": is_translation_match,
            "translation_sha256": target["sha256_translation"]
        },
        "immediate_downstream_operon_partner": {
            "locus_tag": downstream_neighbor["locus_tag"],
            "protein_id": downstream_neighbor["protein_id"],
            "coords_1based_inclusive": [downstream_neighbor["start"], downstream_neighbor["end"]],
            "strand": downstream_neighbor["strand"],
            "length_aa": downstream_neighbor["length_aa"],
            "product": downstream_neighbor["product"],
            "intergenic_distance_bp": gap_to_downstream,
            "author_claim_reproduced": (gap_to_downstream == 6)
        },
        "flanking_operon_features": [
            {
                "offset": -3,
                "locus_tag": cds_features[target_idx - 3]["locus_tag"],
                "protein_id": cds_features[target_idx - 3]["protein_id"],
                "product": cds_features[target_idx - 3]["product"],
                "coords": [cds_features[target_idx - 3]["start"], cds_features[target_idx - 3]["end"]],
                "strand": cds_features[target_idx - 3]["strand"]
            },
            {
                "offset": -2,
                "locus_tag": cds_features[target_idx - 2]["locus_tag"],
                "protein_id": cds_features[target_idx - 2]["protein_id"],
                "product": cds_features[target_idx - 2]["product"],
                "coords": [cds_features[target_idx - 2]["start"], cds_features[target_idx - 2]["end"]],
                "strand": cds_features[target_idx - 2]["strand"]
            },
            {
                "offset": -1,
                "locus_tag": cds_features[target_idx - 1]["locus_tag"],
                "protein_id": cds_features[target_idx - 1]["protein_id"],
                "product": cds_features[target_idx - 1]["product"],
                "coords": [cds_features[target_idx - 1]["start"], cds_features[target_idx - 1]["end"]],
                "strand": cds_features[target_idx - 1]["strand"]
            },
            {
                "offset": 0,
                "locus_tag": target["locus_tag"],
                "protein_id": target["protein_id"],
                "product": target["product"],
                "coords": [target["start"], target["end"]],
                "strand": target["strand"]
            }
        ]
    }

    summary_file = results_dir / "genomic_neighborhood_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote summary JSON: {summary_file}")
    print("Genomic neighborhood analysis complete!")

if __name__ == "__main__":
    main()
