from datetime import datetime
from pathlib import Path
import re

repo_root = Path(__file__).resolve().parent.parent
subpages = repo_root / 'subpages' / 'products' / 'microwave' / 'microwave_subpages'
images_root = subpages / 'images'
html_files = [p for p in subpages.rglob('*.html') if 'images' not in p.parts]
pattern = re.compile(r'images/([A-Za-z0-9_]+\.png)')
INSTRUMENTS = ('AMSR2', 'GMI')
instrument_year_dirs = {}
for instrument in INSTRUMENTS:
    year_root = images_root / instrument
    if year_root.exists():
        instrument_year_dirs[instrument] = sorted(
            [p.name for p in year_root.iterdir() if p.is_dir()]
        )
    else:
        instrument_year_dirs[instrument] = []

missing = set()
changed_files = []
log_path = Path(__file__).resolve().parent / 'update_microwave_links.log'

for html_path in html_files:
    text = html_path.read_text(encoding='utf-8')

    def replacement(match):
        file_name = match.group(1)
        instrument = 'GMI' if 'GMI' in file_name else 'AMSR2'
        available_years = instrument_year_dirs.get(instrument, [])
        year_candidates = []
        if len(file_name) >= 2 and file_name[:2].isdigit():
            year_guess = 2000 + int(file_name[:2])
            year_candidates.append(str(year_guess))
        for year in available_years:
            if year not in year_candidates:
                year_candidates.append(year)
        for year in year_candidates:
            candidate = images_root / instrument / year / file_name
            if candidate.exists():
                return f"/subpages/products/microwave/microwave_subpages/images/{instrument}/{year}/{file_name}"
        missing.add(f"{html_path}: {file_name}")
        return match.group(0)

    new_text = pattern.sub(replacement, text)
    if new_text != text:
        html_path.write_text(new_text, encoding='utf-8')
        changed_files.append(html_path)

with log_path.open('a', encoding='utf-8') as log_file:
    log_file.write(f"--- {datetime.now():%Y-%m-%d %H:%M:%S} ---\n")
    if changed_files:
        log_file.write('Updated image paths in HTML files:\n')
        for html_path in changed_files:
            log_file.write(f'  {html_path}\n')
    else:
        log_file.write('No HTML files required updates.\n')
    if missing:
        log_file.write('Missing image files not matched:\n')
        for item in sorted(missing):
            log_file.write(f'  {item}\n')
    log_file.write('\n')
