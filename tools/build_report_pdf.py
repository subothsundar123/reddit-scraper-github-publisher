from pathlib import Path
import sys
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT=Path(__file__).resolve().parents[1]; SRC=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'reports'/'tradingview-community-analysis-2026-08-27.md'; OUT=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'reports'/'TradingView_Community_Analysis_2026-08-27.pdf'
styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name='ReportTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=colors.HexColor('#0B2545'), alignment=TA_CENTER, spaceAfter=5)); styles.add(ParagraphStyle(name='ReportSub', parent=styles['Normal'], fontSize=11, leading=14, textColor=colors.HexColor('#555555'), alignment=TA_CENTER, spaceAfter=16)); styles.add(ParagraphStyle(name='H1x', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=colors.HexColor('#2E74B5'), spaceBefore=14, spaceAfter=7)); styles.add(ParagraphStyle(name='Bodyx', parent=styles['BodyText'], fontSize=9.3, leading=12, spaceAfter=5)); styles.add(ParagraphStyle(name='Cell', parent=styles['BodyText'], fontSize=7.5, leading=9)); styles.add(ParagraphStyle(name='CellHead', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.HexColor('#0B2545'))); styles.add(ParagraphStyle(name='Linkx', parent=styles['BodyText'], fontSize=8, leading=10, textColor=colors.HexColor('#0563C1')))
def clean(s):
    s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s); return s.replace('&','&amp;').replace('<b>','@@B@@').replace('</b>','@@/B@@').replace('<','&lt;').replace('>','&gt;').replace('@@B@@','<b>').replace('@@/B@@','</b>')
def footer(canvas, doc):
    canvas.saveState(); canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#666666')); canvas.drawRightString(7.5*inch,0.55*inch,f'Page {doc.page}'); canvas.restoreState()
def main():
    doc=SimpleDocTemplate(str(OUT),pagesize=LETTER,rightMargin=inch,leftMargin=inch,topMargin=inch,bottomMargin=inch)
    lines=SRC.read_text(encoding='utf-8').splitlines(); title=lines[0].lstrip('# ').strip() if lines and lines[0].startswith('# ') else 'Community Analysis'; story=[Paragraph(clean(title),styles['ReportTitle']),Paragraph('Research window: 29 May to 27 August 2026',styles['ReportSub'])]; i=0
    while i<len(lines):
        line=lines[i]
        if line.startswith('Research window:'):
            i+=1; continue
        if not line.strip() or line.startswith('# '): i+=1; continue
        if line.startswith('## '): story.append(Paragraph(clean(line[3:]),styles['H1x'])); i+=1; continue
        if line.startswith('|') and i+1<len(lines) and lines[i+1].startswith('|---'):
            headers=[x.strip() for x in line.strip('|').split('|')]; i+=2; data=[]
            while i<len(lines) and lines[i].startswith('|'): data.append([x.strip() for x in lines[i].strip('|').split('|')]); i+=1
            rows=[[Paragraph(clean(x),styles['CellHead']) for x in headers]]+[[Paragraph(clean(x),styles['Cell']) for x in row] for row in data]
            t=Table(rows,repeatRows=1,hAlign='LEFT',colWidths=[6.5*inch/len(headers)]*len(headers)); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8EEF5')),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#B8C2CC')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)])); story += [t,Spacer(1,6)]; continue
        if line.startswith('- '): story.append(Paragraph('• '+clean(line[2:]),styles['Bodyx'])); i+=1; continue
        if line.startswith('http'):
            url=line.strip(); story.append(Paragraph(f'<link href="{url}">{url}</link>',styles['Linkx'])); i+=1; continue
        story.append(Paragraph(clean(line),styles['Bodyx'])); i+=1
    OUT.parent.mkdir(exist_ok=True); doc.build(story,onFirstPage=footer,onLaterPages=footer); print(OUT)
if __name__=='__main__': main()
