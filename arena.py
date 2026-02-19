#!/usr/bin/env python3
"""
CEO Arena - Interactive CLI
Chat with Elon Musk, Sam Altman, Dario Amodei, or Mark Zuckerberg.
Or let them debate each other!

Usage:
    python arena.py                  # Interactive mode
    python arena.py --ingest         # Ingest data into Pinecone first
"""
import sys

CEO_NAMES = {
    "1": "elon_musk",
    "2": "sam_altman",
    "3": "dario_amodei",
    "4": "mark_zuckerberg",
    "elon": "elon_musk",
    "sam": "sam_altman",
    "dario": "dario_amodei",
    "mark": "mark_zuckerberg",
    "musk": "elon_musk",
    "altman": "sam_altman",
    "amodei": "dario_amodei",
    "zuck": "mark_zuckerberg",
    "zuckerberg": "mark_zuckerberg",
}

DISPLAY_NAMES = {
    "elon_musk": "Elon Musk",
    "sam_altman": "Sam Altman",
    "dario_amodei": "Dario Amodei",
    "mark_zuckerberg": "Mark Zuckerberg",
}


def print_banner():
    print("""
╔══════════════════════════════════════════════════╗
║                  CEO ARENA                       ║
║     Chat with Tech's Most Powerful Leaders       ║
║                                                  ║
║  [1] Elon Musk      - Tesla, SpaceX, xAI        ║
║  [2] Sam Altman     - OpenAI                     ║
║  [3] Dario Amodei   - Anthropic                  ║
║  [4] Mark Zuckerberg - Meta                      ║
║                                                  ║
║  [debate] - All 4 answer the same question       ║
║  [switch] - Change CEO                           ║
║  [quit]   - Exit                                 ║
║                                                  ║
║  Fan-made simulation based on public data.       ║
║  Not affiliated with any of these individuals.   ║
╚══════════════════════════════════════════════════╝
""")


def select_ceo() -> str:
    """Let user select a CEO to chat with."""
    while True:
        choice = input("\nWho do you want to talk to? (1-4 or name): ").strip().lower()
        if choice in CEO_NAMES:
            speaker = CEO_NAMES[choice]
            print(f"\n  Connected to {DISPLAY_NAMES[speaker]}. Ask anything!\n")
            return speaker
        print("  Invalid choice. Try: 1, 2, 3, 4, elon, sam, dario, mark, or zuck")


def run_interactive():
    """Main interactive loop."""
    from rag.query_engine import CEOQueryEngine

    print("  Loading CEO Arena engine...")
    engine = CEOQueryEngine()
    print("  Ready!\n")

    print_banner()
    current_speaker = select_ceo()

    while True:
        try:
            question = input(f"  You > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Goodbye!")
            break

        if not question:
            continue

        cmd = question.lower()

        if cmd in ("quit", "exit", "q"):
            print("\n  Goodbye!")
            break

        if cmd == "switch":
            current_speaker = select_ceo()
            continue

        if cmd == "debate":
            question = input("  Debate question > ").strip()
            if not question:
                continue
            print()
            responses = engine.debate(question)
            for speaker, response in responses.items():
                name = DISPLAY_NAMES[speaker]
                print(f"  {'='*50}")
                print(f"  {name}:")
                print(f"  {'='*50}")
                print(f"  {response}\n")
            continue

        # Regular query
        print()
        response = engine.query(current_speaker, question)
        name = DISPLAY_NAMES[current_speaker]
        print(f"  {name}: {response}\n")


def run_ingest():
    """Run data ingestion into Pinecone."""
    from rag.ingest import ingest_all
    ingest_all()


if __name__ == "__main__":
    if "--ingest" in sys.argv:
        run_ingest()
    else:
        run_interactive()
