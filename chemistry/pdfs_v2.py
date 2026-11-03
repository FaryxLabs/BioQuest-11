import json,re,math
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from PIL import Image
import fitz
P=Path(__file__).parent
E=json.loads((P/'exam.json').read_text())
pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
INK='#18334A';TEAL='#087F83';BLUE='#244BC0';MUTED='#52677A'
forms={'CO3^2-':'CO₃²⁻','CoCl2.6H2O':'CoCl₂·6H₂O','Mg3(PO4)2':'Mg₃(PO₄)₂','(NH4)2SO4':'(NH₄)₂SO₄','Mg(ClO3)2':'Mg(ClO₃)₂','Al2O3':'Al₂O₃','FeCl3':'FeCl₃','CCl4':'CCl₄','PCl5':'PCl₅','N2O5':'N₂O₅','NH4+':'NH₄⁺','NH3':'NH₃','H2O':'H₂O','CO2':'CO₂','CH4':'CH₄','Cu2+':'Cu²⁺','Mg2+':'Mg²⁺','Na+':'Na⁺','K+':'K⁺','Cl-':'Cl⁻'}
def fmt(t):
 for a,b in sorted(forms.items(),key=lambda x:-len(x[0])):t=t.replace(a,b)
 return t
class Book:
 def __init__(self,name,label):
  self.c=canvas.Canvas(str(P/name),pagesize=(595,842));self.label=label;self.n=0
 def para(self,text,y,size=12,width=499,x=48,bold=False,color=INK):
  style=ParagraphStyle('x',fontName='DB' if bold else 'D',fontSize=size,leading=size*1.5,textColor=HexColor(color))
  p=Paragraph(escape(fmt(text)).replace('\n','<br/>'),style);w,h=p.wrap(width,740)
  assert y+h<790,(self.label,self.n,text,y+h)
  p.drawOn(self.c,x,842-y-h);return y+h
 def line(self,y):
  self.c.setStrokeColor(HexColor('#CDDAE3'));self.c.setLineWidth(.7);self.c.line(48,842-y,547,842-y)
 def page(self,title,sub,tag):
  if self.n:self.end()
  self.n+=1;c=self.c
  c.setFillColor(HexColor('#F0F7FA'));c.rect(0,715,595,127,fill=1,stroke=0)
  c.setFillColor(HexColor(TEAL));c.rect(0,715,9,127,fill=1,stroke=0)
  self.para('CHEMQUEST 11  /  '+self.label,24,size=10,bold=True,color=TEAL)
  self.para(title,48,size=25,bold=True,color=INK)
  self.para(sub,91,size=10,color=MUTED)
  self.para(tag,140,size=11,bold=True,color=BLUE)
  return 177
 def end(self):
  self.line(803);c=self.c;c.setFont('D',8);c.setFillColor(HexColor(MUTED))
  c.drawString(48,24,'Units 1 & 2  •  Practice prediction, not the actual exam')
  c.drawRightString(547,24,str(self.n));c.showPage()
 def box(self,title,body,y,fill='#EFF8F4'):
  c=self.c;style=ParagraphStyle('b',fontName='D',fontSize=12,leading=18)
  par=Paragraph(escape(fmt(body)).replace('\n','<br/>'),style);_,h=par.wrap(463,600)
  height=h+49
  assert y+height<790
  c.setFillColor(HexColor(fill));c.roundRect(48,842-y-height,499,height,10,fill=1,stroke=0)
  self.para(title,y+10,size=10,bold=True,x=62,width=463,color=TEAL)
  self.para(body,y+31,size=12,x=62,width=463)
  return y+height+16
 def finish(self):self.end();self.c.save()
exam=Book('Chemistry_Exam.pdf','EXAM ONLY')
for part in range(2):
 y=exam.page('A • Choose the answer','60 marks total  |  Suggested time: 60 minutes','Questions '+('1–4' if part==0 else '5–8')+'  /  1 mark each')
 if part==0:
  y=exam.para('Name: ____________________    Date: __________',y,size=11)+15
 for q,m,a in E[0]['items'][part*4:part*4+4]:
  stem,opts=q.split(': ',1) if ': ' in q else (q,'')
  y=exam.para(stem,y,bold=True)+7
  y=exam.para(opts.replace('; ','\n'),y,size=11)+15
for si in [1,2,3]:
 s=E[si];y=exam.page(s['section'].replace(' | ',' • '),'Write your answers below. Keep the answer guide closed.',s['intro'])
 for q,m,a in s['items']:
  y=exam.para(q+'  ['+str(m)+']',y,bold=True)+22
  for z in range(3 if si!=2 else 5):exam.line(y);y+=23
  y+=18
for idx in [0,1]:
 q,m,a=E[4]['items'][idx]
 y=exam.page('E • '+('Write the formulas' if idx==0 else 'Name the compounds'),'One mark for each correct answer.','Question '+str(18+idx)+'  /  5 marks')
 intro,rest=q.split(': ',1)
 for chunk in rest.rstrip('.').split('; '):
  y=exam.para(chunk,y,size=14,bold=True)+36;exam.line(y);y+=43
y=exam.page('F • Draw Lewis structures','Include every lone pair and any overall ion charge.','Question 20  /  3 marks per structure')
for label in ['(a) NH3','(b) H2O','(c) CO3^2- — one resonance contributor']:
 y=exam.para(label,y,size=14,bold=True)+10
 exam.c.setStrokeColor(HexColor('#B5CAD8'));exam.c.roundRect(48,842-y-130,499,130,9,fill=0,stroke=1);y+=151
y=exam.page('G • Explain and apply','Show the calculation for Q23.','Questions 21–24  /  12 marks')
for q,m,a in E[6]['items']:
 y=exam.para(q+'  ['+str(m)+']',y,bold=True)+13
 for z in range(2):exam.line(y);y+=20
 y+=14
exam.finish()
b=Book('Chemistry_Answers_Easy.pdf','ANSWERS + EASY EXPLANATIONS')
y=b.page('A • Answers that make sense','Try the exam first. Then check the answer AND its reason.','Questions 1–8  /  8 marks')
for q,m,a in E[0]['items']:
 n=q.split('.')[0];y=b.para(n+'. '+a,y,bold=False,size=12)+15
y=b.box('REMEMBER','Protons identify the element. Electrons determine ion charge.\nIdentical bonded atoms share equally.',y)
y=b.page('B • Four definitions to learn','The highlighted keywords are the ideas that earn marks.','Questions 9–12  /  2 marks each')
for title,body in [
('9  ISOTOPE','Atoms of the same element with the same number of protons but different numbers of neutrons.'),
('10  FIRST IONIZATION ENERGY','Energy needed to remove one electron from an isolated gaseous atom.'),
('11  ELECTRONEGATIVITY','The ability of a bonded atom to attract shared electrons.'),
('12  IONIC BOND','Electrostatic attraction between oppositely charged ions.')]:
 y=b.box(title,body,y)
b.para('Memory cue: isotope = neutrons differ; ionization = remove; electronegativity = attract; ionic = opposite charges.',y,size=11,color=BLUE)
y=b.page('C • Calculate one step at a time','Write the rule first. Substitute the numbers. Check the answer.','Questions 13–14  /  7 marks')
y=b.box('13  GIVEN: 17 PROTONS, 18 NEUTRONS, 18 ELECTRONS','Atomic number = protons = 17.\nMass number = protons + neutrons = 17 + 18 = 35.\nCharge = protons − electrons = 17 − 18 = −1.',y)
y=b.para('Why negative? There is one more negative electron than positive proton. Award 1 mark for each answer.',y,size=11)+20
y=b.box('14  WEIGHTED AVERAGE','Step 1: Divide percentages by 100: 0.20, 0.30, 0.50.\nStep 2: Multiply each mass by its fraction:\n10 × 0.20 = 2.0\n11 × 0.30 = 3.3\n12 × 0.50 = 6.0\nStep 3: Add: 2.0 + 3.3 + 6.0 = 11.3 u.',y)
b.para('The answer is not a whole number because it is an average of a mixture of isotopes, not the mass number of one atom. Marking: fractions [1], weighted method [1], result [1], explanation [1].',y,size=11)
y=b.page('D • Understand the trends','Learn the cause, not just the direction of an arrow.','Questions 15–17  /  6 marks')
for title,body in [
('15  SMALLEST → LARGEST','F < Cl < Br < I.\nMoving down the group adds occupied electron shells, so the atoms get larger.'),
('16  Na IS LARGER THAN Na+','Sodium loses its outer electron to form Na+. Its occupied outer shell is removed, so the ion is smaller.'),
('17  ACROSS A PERIOD: RADIUS DECREASES','There are more protons, but the extra electrons enter the same main shell. Stronger attraction pulls the electrons closer to the nucleus.')]:
 y=b.box(title,body,y)
b.para('Marking: Q15 order + reason; Q16 comparison + reason; Q17 increased nuclear charge + same-shell attraction. One mark per point.',y,size=11)
y=b.page('E • Build the formula','For ionic compounds, the total charge must equal zero.','Question 18  /  1 mark per formula')
for title,body in [
('(a) Aluminium oxide → Al2O3','2 aluminium ions at +3 give +6; 3 oxide ions at −2 give −6.'),
('(b) Magnesium phosphate → Mg3(PO4)2','3 magnesium ions at +2 give +6; 2 phosphate ions at −3 give −6. Parentheses keep each phosphate together.'),
('(c) Iron(III) chloride → FeCl3','Iron is +3. Three chloride ions at −1 balance it.'),
('(d) Ammonium sulfate → (NH4)2SO4','Two ammonium ions at +1 balance one sulfate ion at −2.'),
('(e) Carbon tetrachloride → CCl4','This is molecular: tetra means four chlorine atoms. Use the prefix, not ion charges.')]:
 y=b.box(title,body,y)
y=b.page('E • Read the name correctly','Do not mix up sulfide/sulfate or chloride/chlorate.','Question 19  /  1 mark per name')
for title,body in [
('(a) FeS → iron(II) sulfide','Sulfide has charge −2, so iron must be +2. Sulfate would contain oxygen.'),
('(b) Mg(ClO3)2 → magnesium chlorate','ClO3− is chlorate. Cl− alone is chloride.'),
('(c) PCl5 → phosphorus pentachloride','Penta means five. PCl3 would be phosphorus trichloride.'),
('(d) N2O5 → dinitrogen pentoxide','Di means two nitrogen atoms; pentoxide means five oxygen atoms.'),
('(e) CoCl2.6H2O → cobalt(II) chloride hexahydrate','Two Cl− ions require Co²⁺. Hexahydrate means six waters of crystallization.')]:
 y=b.box(title,body,y)
def molecule(kind,cy):
 c=b.c;cx=292;cy=842-cy
 c.setFillColor(HexColor(INK));c.setStrokeColor(HexColor(INK));c.setLineWidth(1.5)
 def atom(x,y,t):c.setFont('DB',17);c.drawCentredString(x,y-5,t)
 def pair(x,y,vertical=False):
  for k in [-3,3]:c.circle(x if vertical else x+k,y+k if vertical else y,1.6,fill=1,stroke=0)
 def bond(x1,y1,x2,y2,double=False):
  if double:c.line(x1,y1-3,x2,y2-3);c.line(x1,y1+3,x2,y2+3)
  else:c.line(x1,y1,x2,y2)
 if kind in ['water','ammonia']:
  atom(cx,cy,'O' if kind=='water' else 'N');atom(cx-65,cy,'H');atom(cx+65,cy,'H')
  bond(cx-52,cy,cx-14,cy);bond(cx+14,cy,cx+52,cy);pair(cx,cy+25)
  if kind=='water':pair(cx,cy-25)
  else:atom(cx,cy-52,'H');bond(cx,cy-14,cx,cy-38)
 else:
  atom(cx,cy,'C');atom(cx-85,cy,'O');atom(cx+85,cy,'O');atom(cx,cy-55,'O')
  bond(cx-70,cy,cx-14,cy,True);bond(cx+14,cy,cx+70,cy);bond(cx,cy-14,cx,cy-41)
  for x in [cx-85,cx+85]:pair(x,cy+24);pair(x,cy-24)
  pair(cx+108,cy,True);pair(cx-24,cy-55,True);pair(cx+24,cy-55,True);pair(cx,cy-79)
  c.setFont('D',12);c.drawString(cx+98,cy+13,'−');c.drawString(cx+15,cy-40,'−')
  for x,k in [(cx-130,1),(cx+130,-1)]:
   c.line(x,cy-94,x,cy+42);c.line(x,cy+42,x+k*9,cy+42);c.line(x,cy-94,x+k*9,cy-94)
  c.drawString(cx+139,cy+38,'2−')
y=b.page('F • See the electrons','A line = one shared pair. Two dots = one lone pair.','Question 20  /  9 marks')
b.para('NH3: 3 N–H bonds + 1 lone pair on nitrogen.',y,bold=True);molecule('ammonia',y+62)
y+=153;b.para('H2O: 2 O–H bonds + 2 lone pairs on oxygen.',y,bold=True);molecule('water',y+62)
y+=139;b.para('CO3^2-: one valid resonance contributor.',y,bold=True);molecule('carbonate',y+87)
y+=204;b.para('NH3 and H2O each have 8 valence electrons. Carbonate has 24. The double bond can be drawn at any of its three oxygen positions. Mark each structure for bonds [1], lone pairs [1], and correct electron total/charge [1].',y,size=11)
y=b.page('G • Explain it simply','Use these short scientific sentences in your answers.','Questions 21–24  /  12 marks')
for title,body in [
('21  SOLID KBr vs MOLTEN KBr  [4]','Solid: ions are present but fixed in a lattice, so they cannot move and carry charge.\nMolten: ions are free to move, so they carry charge and conduct electricity.'),
('22  IONIC vs COVALENT  [4]','Ionic: electrons transfer to form positive and negative ions; opposite charges attract.\nCovalent: atoms share pairs of electrons.'),
('23  C–O BOND  [2]','Difference = 3.4 − 2.6 = 0.8.\nThis is polar covalent under your course rule. Oxygen attracts the shared electrons more strongly.'),
('24  RADIATION  [2]','(a) Alpha: two protons and two neutrons.\n(b) Gamma: high-energy electromagnetic waves.')]:
 y=b.box(title,body,y)
b.para('After marking: circle your mistakes. Cover the answer and explain it aloud. Retry the same question later without looking.',y,size=11,color=BLUE)
b.finish()
summary={}
for name in ['Chemistry_Exam.pdf','Chemistry_Answers_Easy.pdf']:
 doc=fitz.open(P/name);summary[name]=len(doc);ims=[]
 for i,page in enumerate(doc):
  for block in page.get_text('blocks'):
   assert block[0]>=20 and block[2]<=575 and block[1]>=15 and block[3]<=830,(name,i,block)
  pix=page.get_pixmap(matrix=fitz.Matrix(.45,.45));ims.append(Image.frombytes('RGB',[pix.width,pix.height],pix.samples))
 w,h=ims[0].size;sheet=Image.new('RGB',(3*w,math.ceil(len(ims)/3)*h),'#cedae2')
 for i,im in enumerate(ims):sheet.paste(im,((i%3)*w,(i//3)*h))
 sheet.save(P/(name.replace('.pdf','_preview.png')))
(P/'pdfs-v2-status.json').write_text(json.dumps(summary))
print(summary)
