from pathlib import Path
import re
from sqlalchemy import text
from src.database import engine

COUNTRY_SQL = Path("src/models/country.sql")
REGION_SQL  = Path("src/models/region.sql")

async def run_sql_file_line_by_line(conn, path: Path):
    if not path.exists():
        print(f"[seed] Файл не найден: {path}")
        return

    needs_on_conflict = re.compile(r";\s*$", re.IGNORECASE)
    has_on_conflict = re.compile(r"\bon\s+conflict\b", re.IGNORECASE)

    count = 0
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        async with conn.begin():
            for line in f:
                ln = line.strip()
                if not ln or not ln.lower().startswith("insert into"):
                    continue
                if not has_on_conflict.search(ln):
                    if needs_on_conflict.search(ln):
                        ln = needs_on_conflict.sub(" ON CONFLICT DO NOTHING;", ln)
                    else:
                        ln = ln + " ON CONFLICT DO NOTHING;"
                await conn.execute(text(ln))
                count += 1
    print(f"[seed] {path.name}: вставлено (или пропущено из-за конфликта) строк: {count}")

async def set_countries_to_base_with_file():
    async with engine.connect() as conn:
        await run_sql_file_line_by_line(conn, COUNTRY_SQL)
        await run_sql_file_line_by_line(conn, REGION_SQL)