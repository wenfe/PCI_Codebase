"""Package a code-rendered schematic PNG as a PDF without changing its pixels.

Run with a Python environment containing reportlab:
  python SAXS_asymmetry/export_schematic_pdf.py path/to/schematic.png
The PDF is written beside the PNG, at a default manuscript width of 180 mm.
"""
import argparse
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--width-mm", type=float, default=180)
    args = parser.parse_args()
    if args.width_mm <= 0:
        parser.error("PDF width must be positive")
    image = ImageReader(str(args.image))
    pixel_width, pixel_height = image.getSize()
    width = args.width_mm * mm
    height = width * pixel_height / pixel_width
    output = args.output or args.image.with_suffix(".pdf")
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output), pagesize=(width, height))
    pdf.setTitle("SAXS wire-offset schematic")
    pdf.setSubject("Generated from native Blender scenes and Gaussian profile data")
    pdf.drawImage(image, 0, 0, width=width, height=height, mask="auto")
    pdf.showPage()
    pdf.save()
    print(output.resolve())


if __name__ == "__main__":
    main()
