#!/usr/bin/env python3
"""
CEO Arena - Data Collection Pipeline
Run this script to collect data for all 4 CEOs.

Usage:
    python run_collection.py              # Collect all
    python run_collection.py elon_musk    # Collect one
    python run_collection.py --normalize  # Only normalize
"""
import sys
from collectors import (
    collect_elon_musk,
    collect_sam_altman,
    collect_dario_amodei,
    collect_mark_zuckerberg,
)
from normalize import normalize_all


COLLECTORS = {
    "elon_musk": collect_elon_musk,
    "sam_altman": collect_sam_altman,
    "dario_amodei": collect_dario_amodei,
    "mark_zuckerberg": collect_mark_zuckerberg,
}


def main():
    args = sys.argv[1:]

    if "--normalize" in args:
        normalize_all()
        return

    if args:
        # Run specific collectors
        for name in args:
            if name in COLLECTORS:
                COLLECTORS[name]()
            else:
                print(f"Unknown speaker: {name}")
                print(f"Available: {', '.join(COLLECTORS.keys())}")
    else:
        # Run all collectors
        for name, collector in COLLECTORS.items():
            collector()

    # Always normalize after collection
    print("\n" + "=" * 50)
    print("NORMALIZING DATA...")
    print("=" * 50)
    normalize_all()


if __name__ == "__main__":
    main()
