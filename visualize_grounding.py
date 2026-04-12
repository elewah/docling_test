import logging
import time
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

IMAGE_RESOLUTION_SCALE = 2.0

data_folder = Path("data")
output_dir = Path("output")
output_dir.mkdir(parents=True, exist_ok=True)

# Pick PDF
input_doc_path = data_folder / "paper.pdf"
if not input_doc_path.exists():
    pdf_candidates = sorted(data_folder.glob("*.pdf"))
    if not pdf_candidates:
        raise FileNotFoundError(f"No PDF found in '{data_folder}'")
    input_doc_path = pdf_candidates[0]

_log.info("Using: %s", input_doc_path)

# Pipeline — generate_page_images=True is required for visualization
pipeline_options = PdfPipelineOptions()
pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
pipeline_options.generate_page_images = True
pipeline_options.generate_picture_images = True

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

start_time = time.time()
conv_res = doc_converter.convert(input_doc_path)
_log.info("Converted in %.2fs", time.time() - start_time)

doc_filename = conv_res.input.file.stem
doc = conv_res.document

def save_grounded_pdf(doc, output_dir: Path) -> Path:
    """Render bounding-box grounding for every page and save as a single PDF.

    Args:
        doc: A DoclingDocument (conv_res.document).
        output_dir: Directory where docling_output.pdf will be written.

    Returns:
        Path to the saved PDF.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    viz_images = doc.get_visualization(
        show_label=True,
        show_branch_numbering=False,
        viz_mode="reading_order",
    )

    pages = [img.convert("RGB") for img in viz_images.values()]
    out_path = output_dir / "docling_output.pdf"
    pages[0].save(out_path, save_all=True, append_images=pages[1:])
    _log.info("Saved grounded PDF (%d page(s)): %s", len(pages), out_path)
    return out_path


save_grounded_pdf(doc, output_dir)
