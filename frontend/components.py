import logging
import time
from pathlib import Path
import pandas as pd
from docling.document_converter import DocumentConverter

_log = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("/Users/macbookkaanari/Downloads/2406.05409v1-2.pdf")
    _log.info(f"Conversion du document : {input_doc_path}")

    doc_converter = DocumentConverter()
    start_time = time.time()

    try:
        conv_res = doc_converter.convert(input_doc_path)
        _log.info(f"Document converti avec succès. Nombre de tables trouvées : {len(conv_res.document.tables)}")
    except Exception as e:
        _log.error(f"Erreur lors de la conversion du document : {e}")
        return

    doc_filename = conv_res.input.file.stem

    # Export tables
    output_dir = Path("/Users/macbookkaanari/Documents/kaadoc/data/out/out_csv")
    output_dir.mkdir(parents=True, exist_ok=True)

    for table_ix, table in enumerate(conv_res.document.tables):
        try:
            table_df = table.export_to_dataframe()
            _log.info(f"Table {table_ix + 1} :\n{table_df}")

            # Save the table as csv
            element_csv_filename = output_dir / f"{doc_filename}-table-{table_ix+1}.csv"
            table_df.to_csv(element_csv_filename)
            _log.info(f"Fichier de sortie sauvegardé à : {element_csv_filename}")
        except Exception as e:
            _log.error(f"Erreur lors de l'export de la table {table_ix + 1} : {e}")

    end_time = time.time() - start_time
    _log.info(f"Document converti et tables exportées en {end_time:.2f} secondes.")

if __name__ == "__main__":
    main()

