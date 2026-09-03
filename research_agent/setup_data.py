"""One-off script to seed sample data: a tiny doc corpus + a sqlite database.
Run once before using the agent: `python setup_data.py`
"""
import os
import sqlite3

BASE = os.path.dirname(__file__)
DOC_DIR = os.path.join(BASE, "data", "docs")
DB_PATH = os.path.join(BASE, "data", "research.db")

os.makedirs(DOC_DIR, exist_ok=True)

DOCS = {
    "internal_note_apac.txt": (
        "Internal Analyst Note — APAC EV Market (confidential)\n\n"
        "Our APAC field team estimates that domestic Chinese EV brands (BYD, "
        "NIO, Xpeng) now account for 78% of APAC EV unit sales, up from 65% "
        "two years ago. Foreign OEMs are losing share primarily on price: "
        "average domestic EV price is $24,000 vs $38,000 for foreign brands "
        "in the same segment. We recommend flagging this in the Q3 investor "
        "briefing as a structural risk for foreign automakers in the region."
    ),
    "internal_note_supply_chain.txt": (
        "Internal Analyst Note — Battery Supply Chain Risk\n\n"
        "Roughly 65% of global lithium refining capacity remains concentrated "
        "in China as of this year. Our risk model flags this as a 'high "
        "concentration' supply chain risk for any automaker without direct "
        "offtake agreements. Two clients have asked us to model a scenario "
        "where refining capacity outside China doubles by 2028."
    ),
    "internal_note_policy.txt": (
        "Internal Analyst Note — Policy Outlook\n\n"
        "We expect incremental tightening of battery sourcing requirements "
        "tied to tax credit eligibility over the next two policy cycles. "
        "Clients with supply chains outside qualifying trade-agreement "
        "countries should treat this as a near-term margin risk, not just a "
        "compliance checkbox."
    ),
}

for fname, text in DOCS.items():
    with open(os.path.join(DOC_DIR, fname), "w", encoding="utf-8") as f:
        f.write(text)

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
conn.executescript(
    """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        launch_year INTEGER
    );
    CREATE TABLE sales (
        id INTEGER PRIMARY KEY,
        region TEXT,
        quarter TEXT,
        units INTEGER,
        revenue_usd REAL
    );
    """
)
conn.executemany(
    "INSERT INTO products (name, category, launch_year) VALUES (?, ?, ?)",
    [
        ("Model A", "sedan", 2022),
        ("Model B", "suv", 2023),
        ("Model C", "compact", 2024),
    ],
)
conn.executemany(
    "INSERT INTO sales (region, quarter, units, revenue_usd) VALUES (?, ?, ?, ?)",
    [
        ("APAC", "2025-Q1", 41000, 984000000),
        ("APAC", "2025-Q2", 46500, 1116000000),
        ("Europe", "2025-Q1", 19800, 594000000),
        ("Europe", "2025-Q2", 21200, 636000000),
        ("US", "2025-Q1", 15300, 505000000),
        ("US", "2025-Q2", 16100, 531000000),
    ],
)
conn.commit()
conn.close()

print(f"Seeded {len(DOCS)} documents in {DOC_DIR}")
print(f"Seeded database at {DB_PATH}")
