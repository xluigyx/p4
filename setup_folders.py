import os

paths = [
    'backend/ingest/pdf_actas',    # Suelta aquí los 4000 PDFs/Fotos
    'backend/ingest/csv_oficial',  # Suelta aquí los CSVs divididos
    'backend/processed',
    'backend/logs'
]

for p in paths:
    os.makedirs(p, exist_ok=True)
    with open(os.path.join(p, 'README.md'), 'w') as f:
        f.write("# Antigravity Ingest\nPon los archivos aquí para procesamiento por ráfaga.")

print("✅ Carpetas de ráfaga creadas.")
