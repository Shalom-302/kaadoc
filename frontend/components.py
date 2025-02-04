# import logging
# import time
# from pathlib import Path
# import pandas as pd
# from docling.document_converter import DocumentConverter

# _log = logging.getLogger(__name__)

# def main():
#     logging.basicConfig(level=logging.INFO)

#     input_doc_path = Path("/Users/macbookkaanari/Downloads/2406.05409v1-2.pdf")
#     _log.info(f"Conversion du document : {input_doc_path}")

#     doc_converter = DocumentConverter()
#     start_time = time.time()

#     try:
#         conv_res = doc_converter.convert(input_doc_path)
#         _log.info(f"Document converti avec succès. Nombre de tables trouvées : {len(conv_res.document.tables)}")
#     except Exception as e:
#         _log.error(f"Erreur lors de la conversion du document : {e}")
#         return

#     doc_filename = conv_res.input.file.stem

#     # Export tables
#     output_dir = Path("/Users/macbookkaanari/Documents/kaadoc/data/out/out_csv")
#     output_dir.mkdir(parents=True, exist_ok=True)

#     for table_ix, table in enumerate(conv_res.document.tables):
#         try:
#             table_df = table.export_to_dataframe()
#             _log.info(f"Table {table_ix + 1} :\n{table_df}")

#             # Save the table as csv
#             element_csv_filename = output_dir / f"{doc_filename}-table-{table_ix+1}.csv"
#             table_df.to_csv(element_csv_filename)
#             _log.info(f"Fichier de sortie sauvegardé à : {element_csv_filename}")
#         except Exception as e:
#             _log.error(f"Erreur lors de l'export de la table {table_ix + 1} : {e}")

#     end_time = time.time() - start_time
#     _log.info(f"Document converti et tables exportées en {end_time:.2f} secondes.")

# if __name__ == "__main__":
#     main()

import datetime
import logging
import time
from pathlib import Path

import pandas as pd

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.utils.export import generate_multimodal_pages
from docling.utils.utils import create_hash

_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0


def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("/Users/macbookkaanari/Downloads/2406.05409v1-2.pdf")
    output_dir = Path("/Users/macbookkaanari/Documents/kaadoc/data/out/out_csv")
    output_dir.mkdir(parents=True, exist_ok=True)
    # Important: For operating with page images, we must keep them, otherwise the DocumentConverter
    # will destroy them for cleaning up memory.
    # This is done by setting AssembleOptions.images_scale, which also defines the scale of images.
    # scale=1 correspond of a standard 72 DPI image
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for (
        content_text,
        content_md,
        content_dt,
        page_cells,
        page_segments,
        page,
    ) in generate_multimodal_pages(conv_res):

        dpi = page._default_image_scale * 72

        rows.append(
            {
                "document": conv_res.input.file.name,
                "hash": conv_res.input.document_hash,
                "page_hash": create_hash(
                    conv_res.input.document_hash + ":" + str(page.page_no - 1)
                ),
                "image": {
                    "width": page.image.width,
                    "height": page.image.height,
                    "bytes": page.image.tobytes(),
                },
                "cells": page_cells,
                "contents": content_text,
                "contents_md": content_md,
                "contents_dt": content_dt,
                "segments": page_segments,
                "extra": {
                    "page_num": page.page_no + 1,
                    "width_in_points": page.size.width,
                    "height_in_points": page.size.height,
                    "dpi": dpi,
                },
            }
        )

    # Generate one parquet from all documents
    df = pd.json_normalize(rows)
    now = datetime.datetime.now()
    output_filename = output_dir / f"multimodal_{now:%Y-%m-%d_%H%M%S}.parquet"
    df.to_parquet(output_filename)

    end_time = time.time() - start_time

    _log.info(
        f"Document converted and multimodal pages generated in {end_time:.2f} seconds."
    )

    # This block demonstrates how the file can be opened with the HF datasets library
    # from datasets import Dataset
    # from PIL import Image
    # multimodal_df = pd.read_parquet(output_filename)

    # # Convert pandas DataFrame to Hugging Face Dataset and load bytes into image
    # dataset = Dataset.from_pandas(multimodal_df)
    # def transforms(examples):
    #     examples["image"] = Image.frombytes('RGB', (examples["image.width"], examples["image.height"]), examples["image.bytes"], 'raw')
    #     return examples
    # dataset = dataset.map(transforms)


if __name__ == "__main__":
    main()