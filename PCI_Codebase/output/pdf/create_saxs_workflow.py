"""Generate the manuscript's vector SAXS workflow figure (no simulated data)."""
from pathlib import Path
import math

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from pypdf import PdfReader

OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)
for name, filename in [('Arial','arial.ttf'), ('Arial-Bold','arialbd.ttf'),
                       ('Arial-Italic','ariali.ttf'), ('Arial-BoldItalic','arialbi.ttf'),
                       ('Times','times.ttf'), ('Times-Italic','timesi.ttf'),
                       ('Times-Bold','timesbd.ttf'), ('Times-BoldItalic','timesbi.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts') / filename)))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold',
                             italic='Arial-Italic', boldItalic='Arial-BoldItalic')
pdfmetrics.registerFontFamily('Times', normal='Times', bold='Times-Bold',
                             italic='Times-Italic', boldItalic='Times-BoldItalic')
pdfmetrics.registerFont(TTFont('Unicode', 'C:/Users/feng48/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/share/fonts/DejaVuSans.ttf'))
for symbol in '∗∝':
    assert ord(symbol) in pdfmetrics.getFont('Unicode').face.charToGlyph

W, H = 540, 470
PDF = OUT / '03_saxs_workflow.pdf'
c = canvas.Canvas(str(PDF), pagesize=(W,H), pageCompression=1)
c.setTitle('SAXS simulation and asymmetry-analysis workflow')
c.setAuthor('')
c.setSubject('Workflow corresponding to the SAXS methods; Gaussian icon is schematic.')
INK = HexColor('#172C3B')
MUTED = HexColor('#455665')
BLUE = HexColor('#266891')
COPPER = HexColor('#A55E29')
TEAL = HexColor('#26756E')
LINE = HexColor('#6F808C')
LIGHTBLUE = HexColor('#EDF4F8')
LIGHTCOPPER = HexColor('#FBF2E9')
LIGHTTEAL = HexColor('#EDF6F3')
LIGHTGRAY = HexColor('#F3F5F7')
TEXT_BOUNDS = []

def paragraph(text, x, top, width, size=9, font='Arial', color=INK, align=0, leading=None):
    style = ParagraphStyle('inline', fontName=font, fontSize=size,
                           leading=leading or size*1.24, textColor=color,
                           alignment=align, spaceAfter=0, spaceBefore=0)
    p = Paragraph(text, style)
    _, height = p.wrap(width, 1000)
    if top-height < 0 or x < 0 or x+width > W:
        raise ValueError(f'Out of page: {text}')
    p.drawOn(c, x, top-height)
    TEXT_BOUNDS.append((x, top-height, x+width, top, text))
    return height

def box(x, y, w, h, label, title, accent=BLUE, tint=LIGHTBLUE):
    c.setFillColor(white)
    c.setStrokeColor(accent)
    c.setLineWidth(.85)
    c.roundRect(x,y,w,h,5,stroke=1,fill=1)
    c.saveState()
    path = c.beginPath()
    path.roundRect(x,y,w,h,5)
    c.clipPath(path,stroke=0)
    c.setFillColor(tint)
    c.rect(x,y+h-25,w,25,stroke=0,fill=1)
    c.restoreState()
    paragraph(f'<b>({label})  {title}</b>',x+12,y+h-7,w-24,10,color=accent)

def arrow(points, color=LINE, head=4.7):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.1)
    p = c.beginPath()
    p.moveTo(*points[0])
    for pt in points[1:]: p.lineTo(*pt)
    c.drawPath(p)
    x,y = points[-1]
    px,py = points[-2]
    angle = math.atan2(y-py,x-px)
    tip = c.beginPath()
    tip.moveTo(x,y)
    for delta in [-.47,.47]:
        tip.lineTo(x-head*math.cos(angle+delta), y-head*math.sin(angle+delta))
    tip.close()
    c.drawPath(tip,stroke=0,fill=1)

def thin_line(x1,y1,x2,y2,color=LINE,width=.6):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1,y1,x2,y2)

c.setFillColor(white)
c.rect(0,0,W,H,stroke=0,fill=1)
c.saveState()
c.translate(0,22)

# Independent inputs. The small Gaussian is schematic, not measured data.
box(12,337,247,99,'a','Fixed incident beam',BLUE,LIGHTBLUE)
box(281,337,247,99,'b','Smooth and translate the wire',COPPER,LIGHTCOPPER)
paragraph('<i>E</i><sub>in</sub>(<i>x, y</i>): spatial amplitude and phase',24,403,225,9.3,font='Times')
paragraph('8.2 keV; FWHM = 7.11 μm<br/>Sample 0.25 m downstream<br/>of the beam waist',118,383,128,8.8,leading=12)
gx, gy, gw, gh = 29,353,72,31
thin_line(gx-1,gy,gx+gw+4,gy)
thin_line(gx+gw/2,gy-2,gx+gw/2,gy+gh+2,HexColor('#B8C9D5'),.45)
p=c.beginPath()
for i in range(121):
    u=-3.2+6.4*i/120
    xx=gx+gw*i/120
    yy=gy+gh*math.exp(-u*u/2)
    if i==0: p.moveTo(xx,yy)
    else: p.lineTo(xx,yy)
c.setLineWidth(1.45)
c.setStrokeColor(BLUE)
c.drawPath(p)
paragraph('0',gx+gw/2-3,351,7,7.5,color=MUTED)
paragraph('<i>x</i>',gx+gw+3,357,9,9,font='Times')

paragraph('Cu cylinder: <i>a</i> = 5 μm; axis parallel to <i>y</i>',293,403,223,9)
paragraph('<i>t</i><sub>σ</sub> = <i>G</i><sub>σ</sub> <font name="Unicode">∗</font> <i>t</i><sub>0</sub>,   σ<sub>L</sub> = σ<sub>R</sub> = 4 nm',293,388,223,10,font='Times')
paragraph('<i>t</i><sub>n</sub>(<i>x, y</i>) = <i>t</i><sub>σ</sub>[<i>x</i> − <i>x</i><sub>0</sub><super>(n)</super>]',293,373,223,10,font='Times')
paragraph('43 offsets: −10.0 to +10.16 μm; step 0.48 μm',293,355,223,8.5)

# Merge the incident field and the translated thickness on the beam grid.
thin_line(135.5,337,135.5,324,width=1.1)
thin_line(404.5,337,404.5,324,width=1.1)
thin_line(135.5,324,404.5,324,width=1.1)
arrow([(270,324),(270,311)])

box(12,245,516,66,'c','Construct the sample-exit field',TEAL,LIGHTTEAL)
paragraph('Interpolate attenuation and phase onto the beam grid',26,283,488,8.8,align=1,color=MUTED)
paragraph('<i>E</i><sub>exit</sub><super>(n)</super>(<i>x, y</i>) = <i>E</i><sub>in</sub>(<i>x, y</i>) exp[−μ<i>t</i><sub>n</sub>(<i>x, y</i>)/2] exp[−i<i>k</i>δ<i>t</i><sub>n</sub>(<i>x, y</i>)]',26,269,488,11.3,font='Times',align=1)
arrow([(270,245),(270,227)])

box(12,143,516,84,'d','Propagate to the detector with the Fresnel approximation',BLUE,LIGHTBLUE)
paragraph('Sample-plane quadratic phase',25,194,217,8.6,align=1)
paragraph('<i>U</i><sub>n</sub> = <i>E</i><sub>exit</sub><super>(n)</super> exp[i<i>k</i>(<i>x</i><super>2</super> + <i>y</i><super>2</super>)/(2<i>Z</i>)]',25,179,217,10.4,font='Times',align=1)
arrow([(244,179),(261,179)])
paragraph('<b>2D FFT</b>',265,192,67,9.5,align=1,color=BLUE)
paragraph('Ũ<sub>n</sub>(<i>q</i><sub>x</sub>, <i>q</i><sub>y</sub>)',265,177,67,10.6,font='Times',align=1)
arrow([(335,179),(352,179)])
paragraph('Detector intensity',354,194,161,8.6,align=1)
paragraph('<i>I</i><sub>D</sub><super>(n)</super> <font name="Unicode">∝</font> |Ũ<sub>n</sub>(<i>kX/Z, kY/Z</i>)|<super>2</super>',354,179,161,10.4,font='Times',align=1)
paragraph('<i>Z</i> = 1.31 m; 4096 × 4096 grid; Δ<i>x</i> = Δ<i>y</i> = 8 nm; Δ<i>X</i> = Δ<i>Y</i> ≈ 6.04 μm',26,156,488,8.4,align=1)
arrow([(270,143),(270,127)])
c.restoreState()

box(12,12,516,137,'e','Extract the SAXS profile and quantify asymmetry',TEAL,LIGHTTEAL)
paragraph('<b>Average 10 central rows:</b> <font name="Times">Ī<sub>n</sub>(<i>q</i><sub>x</sub>)</font>',26,117,249,9)
paragraph('Use <i>q</i><sub>x</sub> = <i>kX/Z</i>; exclude |<i>q</i><sub>x</sub> − <i>q</i><sub>c</sub>| ≤ <i>q</i><sub>min</sub>',26,97,249,9.4,font='Times')
paragraph('<i>q</i><sub>min</sub> = 0.10 nm<super>−1</super>; <i>q</i><sub>c</sub> = 0 or +0.005 nm<super>−1</super>',26,78,249,9.2,font='Times')
# Only integration regions are depicted: the strip is not a SAXS data curve.
for x,w,fill,label in [(26,68,LIGHTBLUE,'LEFT'),(94,79,LIGHTGRAY,'EXCLUDED'),(173,68,LIGHTCOPPER,'RIGHT')]:
    c.setFillColor(fill)
    c.setStrokeColor(HexColor('#C7D0D6'))
    c.setLineWidth(.45)
    c.rect(x,39,w,15,stroke=1,fill=1)
    paragraph(label,x,50,w,7.2,align=1,color=MUTED)
arrow([(247,47),(274,47)])

thin_line(286,28,286,118,HexColor('#D4DFDA'),.65)
paragraph('<b>Integrate left and right regions</b>',300,117,214,9)
paragraph('<i>S</i><sub>L</sub> = Σ<sub>left</sub> Ī<sub>n</sub>,   <i>S</i><sub>R</sub> = Σ<sub>right</sub> Ī<sub>n</sub>',300,100,214,10.5,font='Times',align=1)
paragraph('<i>f</i><sub>L</sub><super>(n)</super>(<i>q</i><sub>c</sub>) =',312,61,70,12,font='Times')
paragraph('<i>S</i><sub>L</sub><super>(n)</super>(<i>q</i><sub>c</sub>)',384,75,121,10.6,font='Times',align=1)
thin_line(384,55,505,55,INK,.6)
paragraph('<i>S</i><sub>L</sub><super>(n)</super>(<i>q</i><sub>c</sub>) + <i>S</i><sub>R</sub><super>(n)</super>(<i>q</i><sub>c</sub>)',384,52,121,10.6,font='Times',align=1)
paragraph('Repeat for every wire offset',300,25,214,8.3,align=1,color=MUTED)

c.showPage()
c.save()
reader=PdfReader(PDF)
assert len(reader.pages)==1
text=reader.pages[0].extract_text()
for expected in ['Fixed incident beam','Smooth and translate','4 nm','2D FFT','0.005','6.04']:
    assert expected in text, expected
assert not reader.pages[0].images, 'Expected a pure-vector diagram'
assert abs(float(reader.pages[0].mediabox.width)-W)<.01
print(f'Created {PDF}; 1 page, {W} x {H} pt, vector-only, embedded fonts.')

SNIPPET = r'''% Requires graphicx (already loaded in the manuscript).
\begin{figure*}[t]
    \centering
    \includegraphics[width=0.96\textwidth]{03_saxs_workflow.pdf}
    \caption{Workflow for the SAXS simulation and asymmetry analysis. The fixed incident field and the Gaussian-smoothed, translated wire thickness are combined to form the sample-exit field. Fresnel propagation is evaluated by applying the sample-plane quadratic phase, performing a two-dimensional Fourier transform, and taking the squared magnitude of the propagated field. The ten central detector rows are averaged to obtain a one-dimensional SAXS profile. Left and right intensity sums are evaluated outside a central exclusion window for $q_c=0$ and $q_c=+0.005\,\mathrm{nm}^{-1}$, and the left-side fraction $f_L$ is calculated at each wire offset. The Gaussian icon is schematic; the colored strip denotes integration regions.}
    \label{fig:saxs_workflow}
\end{figure*}
'''
(OUT/'saxs_workflow_figure.tex').write_text(SNIPPET,encoding='utf-8')
