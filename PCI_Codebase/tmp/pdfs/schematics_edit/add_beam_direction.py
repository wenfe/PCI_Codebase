from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(r"C:\Users\feng48\Downloads\schematics.pdf")
OUTPUT = ROOT / "output" / "pdf"
OUTPUT.mkdir(parents=True, exist_ok=True)

reader = PdfReader(SOURCE)
page = reader.pages[5]
width, height = float(page.mediabox.width), float(page.mediabox.height)

# Add vector artwork only. All original page content stays in the PDF.
buffer = BytesIO()
overlay = canvas.Canvas(buffer, pagesize=(width, height))
gold = HexColor("#B98424")
overlay.setStrokeColor(gold)
overlay.setFillColor(gold)
overlay.setLineWidth(1.3)
overlay.setLineCap(1)

# Panel (a): positive z is the horizontal incident-beam direction.
start_x, tip_x, beam_y = 280.0, 385.0, 395.5
overlay.line(start_x, beam_y, tip_x - 7.5, beam_y)
head = overlay.beginPath()
head.moveTo(tip_x, beam_y)
head.lineTo(tip_x - 8.5, beam_y + 3.2)
head.lineTo(tip_x - 8.5, beam_y - 3.2)
head.close()
overlay.drawPath(head, fill=1, stroke=0)
overlay.setFont("Helvetica", 9)
overlay.drawCentredString((start_x + tip_x) / 2, 376.5, "Beam direction (+z)")
overlay.save()

page.merge_page(PdfReader(BytesIO(buffer.getvalue())).pages[0])

figure_path = OUTPUT / "schematic_beam_direction.pdf"
figure = PdfWriter()
figure.add_page(page)
figure.add_metadata({"/Title": "SAXS experimental schematic with beam direction"})
with figure_path.open("wb") as stream:
    figure.write(stream)

full_path = OUTPUT / "schematics_beam_direction_full.pdf"
full = PdfWriter()
for original_page in reader.pages:
    full.add_page(original_page)
if reader.metadata:
    full.add_metadata({str(k): str(v) for k, v in reader.metadata.items() if v is not None})
with full_path.open("wb") as stream:
    full.write(stream)

for path, page_count, target_index in [(figure_path, 1, 0), (full_path, 12, 5)]:
    result = PdfReader(path)
    assert len(result.pages) == page_count
    assert "Beam direction (+z)" in result.pages[target_index].extract_text()
    print(path)

# Confirm that all other pages retain their original content streams.
original = PdfReader(SOURCE)
written = PdfReader(full_path)
for index in range(len(original.pages)):
    if index != 5:
        assert original.pages[index].get_contents().get_data() == written.pages[index].get_contents().get_data()
print("Verified page counts, added label, and unchanged content on the other 11 pages.")
