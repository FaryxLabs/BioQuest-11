import asyncio, json, math, os, subprocess, textwrap, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether, Flowable
from reportlab.lib.enums import TA_LEFT
from xml.sax.saxutils import escape
import fitz
ROOT=Path(__file__).parent
D=json.loads((ROOT/'data.json').read_text())
E=json.loads((ROOT/'exam.json').read_text())
assert sum(q[1] for s in E for q in s['items'])==60
assert len(D['questions'])==64
assert all(len(q['options'])==4 and q['correct']==0 for q in D['questions'])
OUT=ROOT
TMP=ROOT/'build'
TMP.mkdir(exist_ok=True)
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyQ',fontName='Helvetica',fontSize=10.5,leading=15,spaceAfter=9,textColor=HexColor('#173047')))
styles.add(ParagraphStyle(name='TitleQ',fontName='Helvetica-Bold',fontSize=26,leading=31,spaceAfter=20,textColor=HexColor('#0a645d')))
styles.add(ParagraphStyle(name='HeadQ',fontName='Helvetica-Bold',fontSize=15,leading=20,spaceAfter=10,textColor=HexColor('#0a645d')))
styles.add(ParagraphStyle(name='SmallQ',fontSize=9,leading=13,spaceAfter=8))
story=[]
def p(t,sty='BodyQ'):return Paragraph(escape(t).replace('\n','<br/>'),styles[sty])
def add(t,sty='BodyQ'):story.append(p(t,sty))
def new(title):story.append(PageBreak());add(title,'TitleQ')
def foot(c,doc):
 c.setStrokeColor(HexColor('#0a645d'));c.line(42,40,553,40)
 c.setFont('Helvetica',8);c.drawString(42,27,'ChemQuest 11 | Practice prediction, not the actual exam');c.drawRightString(553,27,str(doc.page))
add('CHEMISTRY\nExam + revision pack','TitleQ')
add('GRADE 11 | UNITS 1 AND 2','HeadQ')
add('Prepared from your shared revision booklet, Chapter 1 quiz, lesson PPTs and photographed homework. The format follows those materials. The teacher has not supplied the actual exam; the selection, marks and 60-minute timing below are practice assumptions.')
add('Your fastest route tonight','HeadQ')
for t in ['1. Learn the rules and worked examples in the revision section.',
'2. Attempt the 60-mark paper with the answers covered. Allow about 60 minutes.',
'3. Mark it, then practise the questions you missed in the game.',
'4. Before bed and tomorrow, recall the definitions and redo missed calculations without notes.']:
 add(t)
add('Most strongly supported question types','HeadQ')
add('Particle counts; isotope weighted averages; atomic models; definitions; periodic comparisons with reasons; ionic formulas and names; molecular prefixes; Lewis structures and lone pairs; conductivity and bond polarity.')
add('Also revise','HeadQ')
add('Radiation and isotope uses, flame tests, scientific knowledge, green chemistry, and sweetener-selection criteria. These appear in the lesson material even when less prominent in the quiz.')
add('Notation','HeadQ')
add('Plain-text formulas use digits as subscripts: Al2O3 means two aluminium and three oxygen atoms. A charge such as SO4^2- is the overall ion charge. A dot in CoCl2.6H2O separates water of crystallization.')
new('Predicted exam | 60 marks')
add('Name: ____________________  Date: __________  Suggested time: 60 minutes')
add('Use a periodic table and calculator for practice. Check your teacher\'s permitted equipment for the real exam. Show working and units. Draw Lewis diagrams in pencil.')
for si,s in enumerate(E):
 if si and si in [1,2,4,5,6]:new(s['section'])
 else:add(s['section'],'HeadQ')
 add(s['intro'])
 for question,marks,ans in s['items']:
  story.append(KeepTogether([p(question+' ['+str(marks)+' marks]'),Spacer(1,24 if marks<3 else (80 if marks==9 else 42))]))
new('Marking guide | Sections A-D')
for si,s in enumerate(E):
 if si==4:new('Marking guide | Sections E-G')
 add(s['section'],'HeadQ')
 for question,marks,ans in s['items']:add(question.split('.')[0]+'. '+ans)
new('Revision | Learn, cover, recall')
add('A correct answer from memory is more useful than recognizing an answer on the page. Study each box, cover it, and explain the rule with an example.')
for i,l in enumerate(D['lessons'][1:-1]):
 if i and i%4==0:new('Revision | Continued')
 add(l['title'],'HeadQ')
 for point in l['points']:add(point)
class Lewis(Flowable):
 def __init__(self,kind):Flowable.__init__(self);self.kind=kind;self.width=490;self.height=160
 def draw(self):
  c=self.canv;c.setStrokeColor(HexColor('#173047'));c.setFillColor(HexColor('#173047'));c.setLineWidth(1.4)
  def atom(x,y,label):c.setFont('Helvetica-Bold',16);c.drawCentredString(x,y-5,label)
  def pair(x,y,vertical=False):
   for a in [-3,3]:c.circle(x if vertical else x+a,y+a if vertical else y,1.5,fill=1,stroke=0)
  def bond(x1,y1,x2,y2,double=False):
   if double:
    c.line(x1,y1-3,x2,y2-3);c.line(x1,y1+3,x2,y2+3)
   else:c.line(x1,y1,x2,y2)
  if self.kind=='water':
   atom(245,80,'O');atom(180,80,'H');atom(310,80,'H');bond(191,80,232,80);bond(258,80,299,80);pair(245,106);pair(245,54)
  elif self.kind=='ammonia':
   atom(245,80,'N');atom(180,80,'H');atom(310,80,'H');atom(245,26,'H');bond(191,80,232,80);bond(258,80,299,80);bond(245,66,245,39);pair(245,106)
  elif self.kind=='carbonate':
   atom(245,80,'C');atom(160,80,'O');atom(330,80,'O');atom(245,25,'O')
   bond(174,80,231,80,True);bond(259,80,316,80);bond(245,66,245,39)
   pair(160,103);pair(160,57)
   pair(330,103);pair(330,57);pair(352,80,True)
   pair(222,25,True);pair(268,25,True);pair(245,4)
   c.setFont('Helvetica',12);c.drawString(340,96,'-');c.drawString(261,39,'-')
   c.line(130,0,130,126);c.line(130,126,140,126);c.line(130,0,140,0)
   c.line(370,0,370,126);c.line(360,126,370,126);c.line(360,0,370,0)
   c.drawString(377,124,'2-')
  elif self.kind=='hydronium':
   atom(245,80,'O');atom(180,80,'H');atom(310,80,'H');atom(245,26,'H')
   bond(191,80,232,80);bond(258,80,299,80);bond(245,66,245,39);pair(245,106)
   c.line(150,5,150,128);c.line(150,128,160,128);c.line(150,5,160,5)
   c.line(340,5,340,128);c.line(330,128,340,128);c.line(330,5,340,5)
   c.setFont('Helvetica',12);c.drawString(347,125,'+')
new('Lewis drawing practice')
add('Each line is one shared pair; each pair of dots is a lone pair. Copy once, then redraw without looking.')
for name,k in [('Water H2O: 8 electrons; 2 bonds and 2 oxygen lone pairs.','water'),('Ammonia NH3: 8 electrons; 3 bonds and 1 nitrogen lone pair.','ammonia'),('Hydronium H3O+: 8 electrons; 3 bonds and 1 oxygen lone pair.','hydronium')]:
 story.append(KeepTogether([p(name),Lewis(k)]))
new('Carbonate and homework corrections')
add('One valid CO3^2- resonance contributor','HeadQ');story.append(Lewis('carbonate'))
add('Count 24 electrons: 8 in bonds, 16 in lone pairs. Carbon has an octet. The double-bond position has three equivalent choices. Actual bonding is delocalized; a Lewis drawing is a model.')
add('Corrections to memorize','HeadQ')
for t in ['FeS is iron(II) sulfide, NOT sulfate. Sulfate contains SO4^2-.',
'Mg(ClO3)2 is magnesium chlorate, NOT chloride.',
'Your printed Q4(a) is PCl5: phosphorus pentachloride. The notebook copied PCl3.',
'CCl4 is carbon tetrachloride, NOT trichloride.',
'A full Lewis diagram needs lone pairs and charges, not just bond lines.',
'Your electronegativity PPT uses 0 / 1.7 boundaries, but actual bonding is not decided by a universal cutoff. HF is polar covalent; CaS is ionic. Use the supplied values and the convention explicitly requested.',
'Your Chapter 1 quiz Q22 is incomplete: it says \"Na or\" without the second element. Do not invent the missing element. Practise a complete comparison such as Na versus Mg (Mg has higher first ionization energy).']:
 add(t)
new('Additional homework answers | Naming')
for t in ['2.4 Q1: LiCl; K2S; FeCl2; Al2O3; Na2SO4; SnO2.',
'Q2: Name cation first; use Roman numeral for a variable-charge metal; name the anion, retaining a polyatomic name or using -ide for a monatomic anion.',
'Q3: magnesium chloride; cesium oxide; iron(II) sulfide; sodium phosphate; ammonium nitrate; aluminium sulfate; magnesium chlorate; lead(II) bromate; zinc hydrogen phosphate; sodium cyanide.',
'Q4: phosphorus pentachloride; dinitrogen pentoxide; carbon tetrafluoride; sulfur dioxide.',
'Q5: CoCl2.6H2O (hydrated); CoCl2 (anhydrous).',
'Q6: PCl3; CCl4; NO; S2Cl2.',
'Q7: potassium hydroxide; sodium nitrite; copper(I) chloride; sodium hydroxide; calcium carbonate.',
'Q8: Standardized IUPAC nomenclature prevents ambiguity and supports clear worldwide communication.']:add(t)
add('Additional homework answers | Polarity','HeadQ')
for t in ['Increasing electronegativity: Cs < K < Ca < Fe < Br < Cl < F. Use tabulated values for close or transition-metal comparisons.',
'More polar bonds: H-F, O-H, C-N.',
'N2 non-polar covalent; NH3 and H2O polar covalent bonds; FeO and MgCl2 ionic.',
'Homework approximate differences: Ca-S 1.6; H-F 1.8; P-H about 0; C-Cl 0.6; C-O 0.9; Li-Cl 2.2. The PPT uses slightly different rounded values (C-O 0.8). Use the values provided in each question.']:add(t)
new('Last-hour recall checklist')
for t in ['Can I define atomic number, isotope, ionization energy, electron affinity, electronegativity, cation, anion, ionic bond, covalent bond, polyatomic ion and radioisotope?',
'Can I calculate p, n, e, charge and an isotope weighted average?',
'Can I explain trends using shells, shielding and nuclear attraction?',
'Can I write neutral formulas with parentheses and name variable-charge metals?',
'Can I draw all lone pairs in H2O, NH3, H3O+ and carbonate?',
'Can I explain conductivity using mobile ions, not electrons flowing through salt?',
'Can I recognize alpha, beta and gamma and match flame-test colours?',
'Can I correct the homework errors without looking?']:add('[ ] '+t)
add('Source scope','HeadQ')
add('Based on Grade_11_Chemistry_Chapters_1_2_Revision.docx, Grade_11Quiz.docx, ANSWER KEY.pdf, the supplied lesson PPT text on atomic structure, periodic table/trends, isotopes/radiation, ionic/molecular compounds, electronegativity, nomenclature, nature of chemistry and sweeteners, plus homework photos. Image-only slide details may not be captured by text extraction. This pack prioritizes the repeated assessable concepts.')
pdf=OUT/'Chemistry_Exam_and_Revision.pdf'
SimpleDocTemplate(str(pdf),pagesize=(595.28,841.89),rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=52).build(story,onFirstPage=foot,onLaterPages=foot)
doc=fitz.open(pdf)
thumbs=[]
for i,page in enumerate(doc):
 for b in page.get_text('blocks'):
  assert b[0]>=15 and b[1]>=15 and b[2]<=590 and b[3]<=830,(i,b)
 pix=page.get_pixmap(matrix=fitz.Matrix(.33,.33))
 thumbs.append(Image.frombytes('RGB',[pix.width,pix.height],pix.samples))
cols=4;w,h=thumbs[0].size
contact=Image.new('RGB',(cols*w,math.ceil(len(thumbs)/cols)*h),'#b8c7ce')
for i,im in enumerate(thumbs):contact.paste(im,((i%cols)*w,(i//cols)*h))
contact.save(OUT/'pdf-preview.png')
print('PDF validated:',len(doc),'pages',flush=True)

if (OUT/'Chemistry_Revision.mp4').exists() and (OUT/'build-status.json').exists():
 status=json.loads((OUT/'build-status.json').read_text())
 status['pdf_pages']=len(doc)
 (OUT/'build-status.json').write_text(json.dumps(status,indent=2))
 print('Retained validated narrated video; PDF refreshed.',flush=True)
 raise SystemExit(0)

def command(args):subprocess.run(args,check=True)
def duration(f):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(f)]))
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def wrap(draw,text,font,width):
 lines=[];line=''
 for word in text.split():
  trial=(line+' '+word).strip()
  if draw.textlength(trial,font=font)>width and line:lines.append(line);line=word
  else:line=trial
 if line:lines.append(line)
 return lines
async def voice(i,l):
 import edge_tts
 f=TMP/f'voice-{i}.mp3'
 if f.exists() and f.stat().st_size>1000:return f
 for attempt in range(3):
  try:
   await edge_tts.Communicate(l['narration'],'en-US-AriaNeural',rate='-5%').save(str(f))
   if f.stat().st_size>1000:return f
  except Exception as e:print('Voice retry',i,attempt,str(e)[:140],flush=True);await asyncio.sleep(1)
 raise RuntimeError('Natural narration service unavailable; no silent substitution performed.')
async def voices():
 sem=asyncio.Semaphore(3)
 async def one(i,l):
  async with sem:return await voice(i,l)
 return await asyncio.gather(*(one(i,l) for i,l in enumerate(D['lessons'])))
audiofiles=asyncio.run(voices())
segments=[]
for i,(l,audio) in enumerate(zip(D['lessons'],audiofiles)):
 dur=duration(audio)+1
 im=Image.new('RGB',(1280,720),'#092e30');draw=ImageDraw.Draw(im)
 draw.rounded_rectangle((25,20,1255,700),radius=18,outline='#b39766',width=5)
 draw.text((70,45),f'CHEMQUEST 11 / LESSON {i+1:02d} OF 18',font=ImageFont.truetype(BOLD,20),fill='#65e4bd')
 titlefont=ImageFont.truetype(BOLD,34)
 y=88
 for line in wrap(draw,l['title'],titlefont,1130):draw.text((70,y),line,font=titlefont,fill='#ffffff');y+=44
 bodyfont=ImageFont.truetype(FONT,25);y+=20
 for point in l['points']:
  for line in wrap(draw,point,bodyfont,1120):
   draw.text((70,y),line,font=bodyfont,fill='#eef6ee');y+=35
  y+=22
 assert y<640,('Slide overflow',i,y)
 draw.text((70,657),'PAUSE • COVER THE NOTES • EXPLAIN THE RULE',font=ImageFont.truetype(BOLD,18),fill='#ffd16c')
 png=TMP/f'slide-{i}.png';im.save(png)
 seg=TMP/f'segment-{i}.mp4'
 # A moving golden marker follows elapsed narration along the board.
 filt=f"drawtext=fontfile={BOLD}:text='>':fontcolor=0xffd16c:fontsize=30:x='70+1100*min(t/{dur},1)':y=615"
 command(['ffmpeg','-loglevel','error','-y','-loop','1','-framerate','8','-i',str(png),'-i',str(audio),'-vf',filt,'-af','apad','-t',str(dur),'-c:v','libx264','-preset','veryfast','-crf','27','-pix_fmt','yuv420p','-c:a','aac','-b:a','64k',str(seg)])
 segments.append(seg);print('Video lesson',i+1,'of 18',flush=True)
listing=TMP/'concat.txt';listing.write_text('\n'.join("file '"+str(s.resolve())+"'" for s in segments))
video=OUT/'Chemistry_Revision.mp4'
command(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(video)])
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
assert {'audio','video'}.issubset({s['codec_type'] for s in probe['streams']})
assert video.stat().st_size<95*1024*1024
(OUT/'build-status.json').write_text(json.dumps({'pdf_pages':len(doc),'video_seconds':duration(video),'video_bytes':video.stat().st_size,'voice':'en-US-AriaNeural','lessons':18,'questions':64,'exam_marks':60},indent=2))
print('Build complete.',flush=True)
