"""
Helper script: prints each SQL migration in order.
Copy-paste each block into Supabase Dashboard → SQL Editor → New Query → Run.
"""
from pathlib import Path

migrations_dir = Path(__file__).parent

for sql_file in sorted(migrations_dir.glob("*.sql")):
    print(f"\n{'='*60}")
    print(f"Run in Supabase SQL Editor: {sql_file.name}")
    print('='*60)
    print(sql_file.read_text())
