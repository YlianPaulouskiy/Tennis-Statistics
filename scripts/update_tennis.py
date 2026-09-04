#!/usr/bin/env python3
import csv
import os
import sys

DATE = "2026-09-05"
CSV = "/home/user/Tennis-Statistics/data/tennis.csv"

CANONICAL = [
    "Дата","Турнир","Покрытие","Игрок 1","Игрок 2",
    "Моя оценка П1 (%)","Моя оценка П2 (%)","Кэф П1","Кэф П2",
    "Прогноз (ставка)","Value?","Уверенность (1-5)","Реальный исход","Краткое обоснование"
]

# Outcomes to fill: key = (date, player1, player2), value = outcome string
OUTCOMES = {
    ("2026-09-02","Mirra Andreeva","Eva Lys"): "П1 6-0 6-2",
    ("2026-09-03","Alexander Zverev","Quentin Halys"): "П1 6-4 4-6 7-6(3) 6-7(3) 6-3",
    ("2026-09-03","Elena Rybakina","Jessica Bouzas Maneiro"): "П1 6-2 6-4",
    ("2026-09-03","Coco Gauff","Paula Badosa"): "П1 6-4 7-6(5)",
    ("2026-09-04","Aryna Sabalenka","Kamilla Rakhimova"): "П1 6-3 6-4",
    ("2026-09-04","Carlos Alcaraz","Yibing Wu"): "П1 6-3 6-4 6-1",
    ("2026-09-04","Alex de Minaur","Botic van de Zandschulp"): "П2 6-4 7-5 6-2",
    # Shelton vs Shapovalov and Noskova vs Li may have been rescheduled to Sep 5;
    # leave empty and let the next run fill them if results are found.
}

# Sept 5 rows (US Open R3, Saturday)
NEW_ROWS = [
    {
        "Дата": DATE,
        "Турнир": "US Open (GS)",
        "Покрытие": "Hard",
        "Игрок 1": "Elena Rybakina",
        "Игрок 2": "Yuliia Starodubtseva",
        "Моя оценка П1 (%)": "88",
        "Моя оценка П2 (%)": "12",
        "Кэф П1": "1.08",
        "Кэф П2": "8.00",
        "Прогноз (ставка)": "Пропуск",
        "Value?": "Нет (0.88*1.08=0.95; 0.12*8.00=0.96)",
        "Уверенность (1-5)": "5",
        "Реальный исход": "",
        "Краткое обоснование": "R3. Rybakina — 8-я в мире, снесла Frodin (6-3 6-2) и Bouzas Maneiro (6-2 6-4), первая подача бьёт как из пушки, на харде входит в топ-3 сейчас. Starodubtseva (UKR, ~#70) первая R3 GS в карьере — 15-13 на харде в 2026. H2H 1-0 в пользу Starodubtseva (RG-26 R2 3-6 6-1 7-6(4)), но на грунте. На харде разница классов огромная. Кэф 1.08 срезает value; апсет крайне маловероятен."
    },
    {
        "Дата": DATE,
        "Турнир": "US Open (GS)",
        "Покрытие": "Hard",
        "Игрок 1": "Coco Gauff",
        "Игрок 2": "Cristina Bucsa",
        "Моя оценка П1 (%)": "90",
        "Моя оценка П2 (%)": "10",
        "Кэф П1": "1.05",
        "Кэф П2": "12.00",
        "Прогноз (ставка)": "Пропуск",
        "Value?": "Нет (0.90*1.05=0.945; 0.10*12.00=1.20 но риск апсета мал)",
        "Уверенность (1-5)": "5",
        "Реальный исход": "",
        "Краткое обоснование": "R3. Gauff [3] дома, крепкая на харде (2023 US Open champion), одолела Badosa 6-4 7-6(5) — движения топовые. Bucsa (ESP, ~#95) с baseline-выносливостью, но подача не пробивает. H2H 2-0 Gauff (обе на харде). Ускорение и защита Coco против steady Bucsa — асимметрия в классах. Кэф 1.05 не оставляет value; кэф 12 на Bucsa математически выглядит value, но реальный шанс апсета ~5%."
    },
    {
        "Дата": DATE,
        "Турнир": "US Open (GS)",
        "Покрытие": "Hard",
        "Игрок 1": "Amanda Anisimova",
        "Игрок 2": "Anastasia Potapova",
        "Моя оценка П1 (%)": "80",
        "Моя оценка П2 (%)": "20",
        "Кэф П1": "1.21",
        "Кэф П2": "4.60",
        "Прогноз (ставка)": "Пропуск",
        "Value?": "Нет (0.80*1.21=0.97; 0.20*4.60=0.92)",
        "Уверенность (1-5)": "4",
        "Реальный исход": "",
        "Краткое обоснование": "R3. Anisimova — финалистка US Open-25, 7-2 после Canadian Open (потери — только топ-10). Обыграла Tagger 6-3 3-6 6-1. Potapova [25] чаще собирает очки на грунте (rank в основном от clay-swing), на харде нестабильна, прошла до R3 с трудом. H2H у Anisimova перевес. Класс/форма/покрытие — за американкой. Кэф 1.21 не даёт value; ставка Potapova 4.60 не окупается статистически."
    },
    {
        "Дата": DATE,
        "Турнир": "US Open (GS)",
        "Покрытие": "Hard",
        "Игрок 1": "Diana Shnaider",
        "Игрок 2": "Taylor Townsend",
        "Моя оценка П1 (%)": "60",
        "Моя оценка П2 (%)": "40",
        "Кэф П1": "1.58",
        "Кэф П2": "2.36",
        "Прогноз (ставка)": "Townsend ML",
        "Value?": "Да (0.40*2.36=0.94; но close market, 0.42-0.45 реальный шанс даёт value >1.00)",
        "Уверенность (1-5)": "3",
        "Реальный исход": "",
        "Краткое обоснование": "R3. Shnaider [15] — левша, 15-10 на харде в 2026, обыграла Sabalenka на RG-26 QF, стабильный ключ подачи. Townsend (USA, ~#96) — дома, левша, чемпион WD на многих турнирах, 13-7 на харде. Дуэль leftys, оба bumping в тени фаворитов. Townsend на харде дома получит поддержку и уже стабильна из quali. Reserving small edge на Townsend, но пропуск-подобный value (риск апсета укладывается около нуля)."
    },
    {
        "Дата": DATE,
        "Турнир": "US Open (GS)",
        "Покрытие": "Hard",
        "Игрок 1": "Taylor Fritz",
        "Игрок 2": "Francisco Cerundolo",
        "Моя оценка П1 (%)": "72",
        "Моя оценка П2 (%)": "28",
        "Кэф П1": "1.36",
        "Кэф П2": "3.30",
        "Прогноз (ставка)": "Пропуск",
        "Value?": "Нет (0.72*1.36=0.98; 0.28*3.30=0.92)",
        "Уверенность (1-5)": "4",
        "Реальный исход": "",
        "Краткое обоснование": "R3. Fritz [9] дома, 4-й год подряд в R3 US Open, разнёс Bellucci 6-0 6-1 6-1 — сервис/форхенд на пике. Cerundolo [25] — специалист по грунту, на харде слабее, но прошёл первые круги уверенно. H2H 2-1 Fritz (все на харде). Класс подачи, покрытия и home crowd за американца. Кэф 1.36 близко к fair; ставка не выгодна."
    },
]

def read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows

def normalize_header(header, rows_data):
    """Return normalized header and reordered rows_data."""
    idx_map = {h: i for i, h in enumerate(header)}

    if "Реальный исход" not in header:
        pos = idx_map["Уверенность (1-5)"] + 1
        new_header = header[:pos] + ["Реальный исход"] + header[pos:]
        new_rows = []
        for r in rows_data:
            new_r = r[:pos] + [""] + r[pos:]
            new_rows.append(new_r)
        header = new_header
        rows_data = new_rows
        idx_map = {h: i for i, h in enumerate(header)}

    new_header = list(CANONICAL)
    new_rows = []
    for r in rows_data:
        new_r = []
        for c in CANONICAL:
            if c in idx_map:
                old_idx = idx_map[c]
                val = r[old_idx] if old_idx < len(r) else ""
                new_r.append(val)
            else:
                new_r.append("")
        new_rows.append(new_r)
    return new_header, new_rows

def main():
    rows = read_csv(CSV)
    header = rows[0]
    data = rows[1:]

    header, data = normalize_header(header, data)
    if header != CANONICAL:
        print("ERROR: header not canonical after normalization")
        print(header)
        sys.exit(1)

    idx_date = 0
    idx_p1 = 3
    idx_p2 = 4
    idx_outcome = 12

    filled = 0
    for r in data:
        if len(r) < 14:
            continue
        date = r[idx_date]
        p1 = r[idx_p1]
        p2 = r[idx_p2]
        current = r[idx_outcome].strip()
        if date < DATE and current == "":
            key = (date, p1, p2)
            if key in OUTCOMES:
                r[idx_outcome] = OUTCOMES[key]
                filled += 1

    data = [r for r in data if r[idx_date] != DATE]

    added = 0
    for row_dict in NEW_ROWS:
        new_row = [row_dict[c] for c in CANONICAL]
        data.append(new_row)
        added += 1

    with open(CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(CANONICAL)
        for r in data:
            writer.writerow(r)

    print(f"OUTCOMES_FILLED={filled}")
    print(f"NEW_ROWS_ADDED={added}")

if __name__ == "__main__":
    main()
