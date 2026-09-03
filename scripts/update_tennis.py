#!/usr/bin/env python3
import csv
import os
import sys

DATE = "2026-09-04"
CSV = "/home/user/Tennis-Statistics/data/tennis.csv"

CANONICAL = [
    "Дата","Турнир","Покрытие","Игрок 1","Игрок 2",
    "Моя оценка П1 (%)","Моя оценка П2 (%)","Кэф П1","Кэф П2",
    "Прогноз (ставка)","Value?","Уверенность (1-5)","Реальный исход","Краткое обоснование"
]

# Outcomes to fill: key = (date, player1, player2), value = outcome string
OUTCOMES = {
    ("2026-09-02","Carlos Alcaraz","Jaime Faria"): "П1 4-6 6-0 6-3 6-2",
    ("2026-09-02","Aryna Sabalenka","Polina Iatcenko"): "П1 6-1 6-1",
    ("2026-09-02","Iga Swiatek","Nadia Podoroska"): "П1 6-3 6-2",
    ("2026-09-02","Jessica Pegula","Sofia Kenin"): "П1 6-3 6-1",
    ("2026-09-03","Taylor Fritz","Mattia Bellucci"): "П1 6-0 6-1 6-1",
    ("2026-09-03","Naomi Osaka","Katerina Siniakova"): "П1 6-2 5-7 6-1",
    ("2026-09-03","Iga Swiatek","Nadia Podoroska"): "П1 6-3 6-2",
    ("2026-09-03","Marta Kostyuk","Sloane Stephens"): "П1 6-1 7-5",
}

# Sept 4 rows
NEW_ROWS = [
    {
        "Дата": DATE,
        "Турнир": "US Open (GS)",
        "Покрытие": "Hard",
        "Игрок 1": "Aryna Sabalenka",
        "Игрок 2": "Kamilla Rakhimova",
        "Моя оценка П1 (%)": "92",
        "Моя оценка П2 (%)": "8",
        "Кэф П1": "1.07",
        "Кэф П2": "8.00",
        "Прогноз (ставка)": "Пропуск",
        "Value?": "Нет (0.92*1.07=0.98)",
        "Уверенность (1-5)": "5",
        "Реальный исход": "",
        "Краткое обоснование": "R3. Sabalenka [1] — 2х действующий чемпион, 16 побед подряд в US Open, разнесла Iatcenko 6-1 6-1 за 54 мин. Rakhimova (UZB) впервые в R3 US Open с 2021, но апсетнула Krejcikova 7-6 6-2, форма растёт. H2H 3-0 Sabalenka (все страйты, включая RG-25 6-1 6-0). Класс/форма/hard-court дают Сабаленке подавляющее преимущество. Кэф 1.07 не оставляет value."
    },
    {
        "Дата": DATE,
        "Турнир": "US Open (GS)",
        "Покрытие": "Hard",
        "Игрок 1": "Carlos Alcaraz",
        "Игрок 2": "Yibing Wu",
        "Моя оценка П1 (%)": "88",
        "Моя оценка П2 (%)": "12",
        "Кэф П1": "1.06",
        "Кэф П2": "9.50",
        "Прогноз (ставка)": "Пропуск",
        "Value?": "Нет (0.88*1.06=0.93)",
        "Уверенность (1-5)": "4",
        "Реальный исход": "",
        "Краткое обоснование": "R3. Alcaraz [2] — действующий чемпион, вернулся после 4-мес травмы запястья, ещё в ржавчине (4 сета vs Faria: 4-6 6-0 6-3 6-2), но моторика и форхенд работают. Wu Yibing — экс-чемпион Даллас-23, играет через силу после длительных травм; прошёл Walton (7-6 6-2 7-5) и Duckworth. Класс/скорость Alcaraz на другом уровне, но рустиность даёт крохи Wu. Кэф 1.06 value отсекает."
    },
    {
        "Дата": DATE,
        "Турнир": "US Open (GS)",
        "Покрытие": "Hard",
        "Игрок 1": "Ben Shelton",
        "Игрок 2": "Denis Shapovalov",
        "Моя оценка П1 (%)": "70",
        "Моя оценка П2 (%)": "30",
        "Кэф П1": "1.16",
        "Кэф П2": "5.15",
        "Прогноз (ставка)": "Пропуск",
        "Value?": "Нет (0.70*1.16=0.81; Shapovalov 0.30*5.15=1.55 рискованно)",
        "Уверенность (1-5)": "3",
        "Реальный исход": "",
        "Краткое обоснование": "R3. Shelton [8] — дома, толпа, левша с топ-сервисом, разнес Hurkacz 4 сета. H2H 4-0 Shelton (2-0 на харде), последний — Dallas-26 SF (4-6 6-4 7-6(4)). Shapovalov в приличной форме (финал Los Cabos, потерял всего 1 сет здесь), но психологически проигран. Кэф 1.16 на Shelton забирает value, Shapovalov 5.15 математически даёт value, но 0-4 H2H и домашняя атмосфера снижают уверенность до пропуска."
    },
    {
        "Дата": DATE,
        "Турнир": "US Open (GS)",
        "Покрытие": "Hard",
        "Игрок 1": "Linda Noskova",
        "Игрок 2": "Ann Li",
        "Моя оценка П1 (%)": "58",
        "Моя оценка П2 (%)": "42",
        "Кэф П1": "1.55",
        "Кэф П2": "2.45",
        "Прогноз (ставка)": "Li ML",
        "Value?": "Да (0.42*2.45=1.03)",
        "Уверенность (1-5)": "2",
        "Реальный исход": "",
        "Краткое обоснование": "R3. Noskova — чемпион Wimbledon-26, 9-матчевая GS-серия, стабильна на всех покрытиях. Ann Li растянула её до 3 сетов в единственной WTA-встрече 2026 (близкое поражение), боец с надёжным baseline и цепкая на харде. Матч плотный: класс Noskova должен перевесить, но кэф 2.45 на Li даёт минимальный value. Уверенность низкая (Li дома, Noskova моложе и в форме)."
    },
    {
        "Дата": DATE,
        "Турнир": "US Open (GS)",
        "Покрытие": "Hard",
        "Игрок 1": "Alex de Minaur",
        "Игрок 2": "Botic van de Zandschulp",
        "Моя оценка П1 (%)": "75",
        "Моя оценка П2 (%)": "25",
        "Кэф П1": "1.28",
        "Кэф П2": "3.75",
        "Прогноз (ставка)": "Пропуск",
        "Value?": "Нет (0.75*1.28=0.96)",
        "Уверенность (1-5)": "3",
        "Реальный исход": "",
        "Краткое обоснование": "R3 (уточнение по данным). De Minaur [6] прошёл Guerrieri 6-2 6-2 6-4 без надрыва, идеальная baseline-хардовая машина. Van de Zandschulp — известен апсетом Alcaraz на US Open-24, но 2026 нестабилен. H2H 3-1 de Minaur. Австралиец должен решить темпом и глубиной, кэф 1.28 уже учитывает фаворитизм."
    },
]

def read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows

def normalize_header(header, rows_data):
    """Return normalized header and reordered rows_data."""
    # Build a dict of column indices
    idx_map = {h: i for i, h in enumerate(header)}

    # Ensure 'Реальный исход' exists
    if "Реальный исход" not in header:
        # Add it after 'Уверенность (1-5)'
        pos = idx_map["Уверенность (1-5)"] + 1
        new_header = header[:pos] + ["Реальный исход"] + header[pos:]
        new_rows = []
        for r in rows_data:
            new_r = r[:pos] + [""] + r[pos:]
            new_rows.append(new_r)
        header = new_header
        rows_data = new_rows
        idx_map = {h: i for i, h in enumerate(header)}

    # Reorder to canonical
    new_header = list(CANONICAL)
    new_rows = []
    for r in rows_data:
        new_r = []
        for c in CANONICAL:
            if c in idx_map:
                # Get value at old index
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

    # Normalize columns
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
    # Fill outcomes
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

    # Remove any existing today rows (idempotency)
    data = [r for r in data if r[idx_date] != DATE]

    # Add today rows
    added = 0
    for row_dict in NEW_ROWS:
        new_row = [row_dict[c] for c in CANONICAL]
        data.append(new_row)
        added += 1

    # Write out
    with open(CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(CANONICAL)
        for r in data:
            writer.writerow(r)

    print(f"OUTCOMES_FILLED={filled}")
    print(f"NEW_ROWS_ADDED={added}")

if __name__ == "__main__":
    main()
