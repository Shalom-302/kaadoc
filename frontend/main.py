import json
import logging
import time
import logging
from pathlib import Path
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat

from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
_log = logging.getLogger(__name__)

def main():
    input_paths = [
        Path("/Users/macbookkaanari/Downloads/645e0b3c0d6f365e0a214809_exemple-nouveau-permis-francais.jpg"),
    ]

    doc_converter = (
        DocumentConverter(  # all of the below is optional, has internal defaults.
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.IMAGE,
                InputFormat.DOCX,
                InputFormat.HTML,
                InputFormat.PPTX,
                InputFormat.ASCIIDOC,
                InputFormat.MD,
            ],  # whitelist formats, non-matching files are ignored.
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=StandardPdfPipeline, backend=PyPdfiumDocumentBackend
                ),
                InputFormat.DOCX: WordFormatOption(
                    pipeline_cls=SimplePipeline  # , backend=MsWordDocumentBackend
                ),
            },
        )
    )
    start_time = time.time()
    conv_results = doc_converter.convert_all(input_paths)


    for res in conv_results:
        out_path = Path("/Users/macbookkaanari/Documents/kaadoc/data/out/out_json")
        print(
            f"Document {res.input.file.name} converted."
            f"\nSaved JSON output to: {str(out_path)}"
        )
        _log.debug(f"Exported text:\n{res.document._export_to_indented_text(max_text_len=16)}")
        
        with (out_path / f"{res.input.file.stem}.json").open("w") as fp:
            fp.write(json.dumps(res.document.export_to_dict(), indent=4))  # Indentation de 4 espaces

    end_time = time.time() - start_time

    _log.info(f"Documents converted in {end_time:.2f} seconds.")

if __name__ == "__main__":
    main()



