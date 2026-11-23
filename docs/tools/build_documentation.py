"""Build offline HTML documentation and editable SVG diagrams using Python stdlib."""
from pathlib import Path
import html, re

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'diagrams'
OUT = ROOT / 'output'
D.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
esc = html.escape

class Diagram:
    def __init__(self, title, w=1120, h=760):
        self.w,self.h = w,h
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">', '<defs><marker id="arrow" markerWidth="9" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#486577"/></marker></defs>', f'<rect width="{w}" height="{h}" fill="#fff"/>']
    def text(self,x,y,s,size=15,color='#173b42',anchor='middle'):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" text-anchor="{anchor}">{esc(s)}</text>')
    def box(self,x,y,w,h,title,fields=(),fill='#eef7f3'):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="#31756a" stroke-width="1.5"/>')
        self.text(x+w/2,y+25,title,16)
        if fields:
            self.parts.append(f'<path d="M{x},{y+36} H{x+w}" stroke="#aac8bd"/>')
            for i,t in enumerate(fields): self.text(x+12,y+57+i*21,t,13,anchor='start')
    def line(self,points,label='',lx=None,ly=None,dashed=False,arrow=True):
        pts=' '.join(f'{x},{y}' for x,y in points)
        self.parts.append(f'<polyline points="{pts}" fill="none" stroke="#486577" stroke-width="1.5"'+(' stroke-dasharray="6 4"' if dashed else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
        if label:
            x,y=points[len(points)//2]
            self.text(lx if lx is not None else x,ly if ly is not None else y-7,label,12)
    def diamond(self,x,y,w,h,label):
        self.parts.append(f'<polygon points="{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}" fill="#fff4d9" stroke="#b58d36"/>')
        self.text(x+w/2,y+h/2+5,label,14)
    def actor(self,x,y,label):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="13" fill="none" stroke="#173b42" stroke-width="2"/><path d="M{x},{y+13} v35 M{x-24},{y+29} h48 M{x},{y+48} l-23,28 M{x},{y+48} l23,28" fill="none" stroke="#173b42" stroke-width="2"/>')
        self.text(x,y+97,label,15)
    def ellipse(self,x,y,w,h,label):
        self.parts.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="#eef7f3" stroke="#31756a"/>')
        self.text(x+w/2,y+h/2+5,label,14)
    def save(self,name):
        p=D/(name+'.svg');p.write_text('\n'.join(self.parts+['</svg>']),encoding='utf-8'); return name

diagrams=[]
def register(name,title,caption,g):
    g.save(name);diagrams.append((name,title,caption))

g=Diagram('System architecture',1120,650)
g.box(30,230,210,130,'Responsive browser',['Three role dashboards','Next.js / TypeScript','Read-only chat interface'])
g.box(350,60,350,85,'API and security',['Authentication, ownership, validation'])
g.box(350,195,350,195,'Spring Boot modular backend',['Identity / produce / trade','Visits / inspection / administration','Assistant: allowlisted read tools','Transactions and audit events','Expiry / notification / retention jobs'])
g.box(350,455,350,110,'PostgreSQL',['Domain records, constraints, history','Migrations and transaction locks'])
g.box(820,220,255,105,'External model provider',['Minimum authorized context','No direct database access'])
g.box(820,455,255,110,'Encrypted off-host backups',['Daily schedule','Demonstrated restore'])
g.line([(240,270),(290,270),(290,100),(350,100)],'HTTPS',285,215)
g.line([(525,145),(525,195)])
g.line([(525,390),(525,455)],'SQL transactions',610,425)
g.line([(700,270),(820,270)],'HTTPS',760,257)
g.line([(700,510),(820,510)],'Backup',760,495)
g.text(560,615,'One market • one backend deployment • no payment gateway • AI optional at runtime',16)
register('01-architecture','System architecture','Logical deployment and trust boundaries. Provider access occurs only through the backend adapter.',g)

g=Diagram('Three-role use cases',1120,820)
g.parts.append('<rect x="220" y="30" width="680" height="750" rx="12" fill="none" stroke="#91aca4"/>')
g.text(560,60,'Dambulla AgriFlow — three roles',18)
g.actor(90,150,'Farmer');g.actor(90,490,'Buyer');g.actor(1010,330,'Administrator')
for x,y,label in [(250,100,'Publish lots / asking prices'),(250,195,'Accept or reject buyer offers'),(250,290,'Visits / deductions / own sales'),(250,450,'Search lots / make price offer'),(250,545,'Consent / confirm purchase'),(250,640,'Own offers / purchases'),(590,110,'Slots / check-in / unloading'),(590,220,'Record inspections / shortages'),(590,330,'Collections / payouts'),(590,440,'Audited corrections'),(590,550,'Accounts / prices / reports')]:
    g.ellipse(x,y,280,60,label)
for y in [130,225,320]:g.line([(115,190),(250,y)],arrow=False)
for y in [480,575,670]:g.line([(115,530),(250,y)],arrow=False)
for y in [140,250,360,470,580]:g.line([(985,370),(870,y)],arrow=False)
g.ellipse(590,675,280,60,'Read-only assistant')
g.text(730,760,'Available within each signed-in role’s scope',12)
register('02-use-cases','Use-case diagram — three roles','Administrator includes market operations and inspection recording. Farmer and buyer decisions remain their own; negotiation is by private offers, not an auction.',g)

def entity(g,x,y,title,fields):g.box(x,y,260,145,title,fields)
g=Diagram('Trade ERD',1120,880)
entity(g,35,35,'USERS',['PK id','name, status','roles through USER_ROLES'])
entity(g,425,35,'HARVESTS',['PK id; FK farmer_id → USERS','FK produce_type_id','expected_kg, arrival'])
entity(g,815,35,'LOTS',['PK id; FK harvest_id','status, asking_price_per_kg','stock_basis, price_version'])
entity(g,815,295,'OFFERS',['PK id; FK lot_id, buyer_id','quantity_kg, offered_price_per_kg','status, accepted_at'])
entity(g,425,295,'RESERVATIONS',['PK id; FK offer_id UNIQUE','agreed_kg, expires_at','status; amendment history'])
entity(g,35,295,'SALES',['PK id; FK reservation_id UNIQUE','sold_kg, price, confirmed_at','immutable financial snapshot'])
entity(g,35,575,'SETTLEMENTS',['PK id; FK sale_id UNIQUE','gross, deductions, net','collection / payout balances'])
entity(g,425,575,'PAYMENT_ENTRIES',['PK id; FK settlement_id','direction, amount, evidence','FK reversal_of → self (optional)'])
entity(g,815,575,'STOCK_ADJUSTMENTS',['PK id; FK lot_id, actor_id','signed_kg, reason, time','inspection / loss / withdrawal'])
g.line([(295,100),(425,100)],'1 : 0..*',360,87)
g.line([(685,100),(815,100)],'1 : 0..*',750,87)
g.line([(945,180),(945,295)],'1 : 0..*',1000,240)
g.line([(815,365),(685,365)],'1 : 0..1',750,350)
g.line([(425,365),(295,365)],'1 : 0..1',360,350)
g.line([(165,440),(165,575)],'1 : 1',210,515)
g.line([(295,645),(425,645)],'1 : 0..*',360,630)
g.line([(1075,160),(1095,160),(1095,650),(1075,650)],'1 : 0..*',1040,520)
g.text(560,780,'Cardinality reads from source to target. FK = foreign key; PK = primary key.',15)
g.text(560,808,'Buyer/actor FKs reference USERS. Offer acceptance creates at most one reservation.',14)
g.text(560,835,'Support entities and remaining foreign keys are specified in the data dictionary.',14)
register('03-erd-trade','ERD — produce and trade','Core logical relationships. One lot supports multiple offers and sales; there is no single buyer_id on a lot. A confirmed sale creates one settlement atomically.',g)

g=Diagram('Operations ERD',1120,850)
for x,y,t,f in [
 (30,30,'ZONES',['PK id','name, enabled','unloading bays per zone']),
 (425,30,'SLOTS',['PK id; FK zone_id','starts_at, ends_at','booking_limit']),
 (820,30,'VISITS',['PK id; FK slot_id, vehicle_id','FK farmer_id; status','arrival / unloading / departure']),
 (30,320,'UNLOADING_BAYS',['PK id; FK zone_id','label, enabled','one active allocation per bay']),
 (425,320,'BAY_ALLOCATIONS',['PK id; FK bay_id, visit_id','allocated_at, released_at','unique active visit and bay']),
 (820,320,'VISIT_LOTS',['PK/FK visit_id','PK/FK lot_id','owned lot association']),
 (820,610,'LOTS',['PK id; FK harvest_id','status, stock basis','trade ERD contains details']),
 (425,610,'INSPECTIONS',['PK id; FK lot_id, recorded_by_admin_id','total / saleable kg, grade','FK supersedes_id; reason']),
 (30,610,'RECONCILIATION_CASES',['PK id; FK lot_id, inspection_id','state, deficit, coordinator_id','many buyer proposals'])]:entity(g,x,y,t,f)
for pts,l,x,y in [([(290,100),(425,100)],'1 : 0..*',355,85), ([(685,100),(820,100)],'1 : 0..*',750,85), ([(160,175),(160,320)],'1 : 0..*',215,250), ([(290,390),(425,390)],'1 : 0..*',355,375), ([(950,175),(950,320)],'1 : 1..*',1005,250), ([(950,465),(950,610)],'0..* : 1',1015,550), ([(820,680),(685,680)],'1 : 0..*',750,665), ([(425,680),(290,680)],'1 : 0..1',355,665)]:g.line(pts,l,x,y)
g.line([(820,150),(750,150),(750,260),(555,260),(555,320)],'1 : 0..* allocations',600,245)
g.text(560,810,'VEHICLES 1 → many VISITS; USERS 1 → many visits / inspections / coordinated cases.',14)
register('04-erd-operations','ERD — visits and inspection','Bookings and simultaneous bay capacity are different constraints. VISIT_LOTS resolves the many-to-many lot/visit relationship. At most one active inspection-shortage case per lot.',g)

def sequence(name,title,actors,messages,notes):
    h=180+len(messages)*60
    g=Diagram(title,1120,h)
    xs=[80+i*(960/(len(actors)-1)) for i in range(len(actors))]
    for x,a in zip(xs,actors):
        g.box(x-70,15,140,44,a)
        g.line([(x,60),(x,h-70)],dashed=True,arrow=False)
    for i,(a,b,label) in enumerate(messages):
        y=105+i*60
        if a==b:
            g.line([(xs[a],y),(xs[a]+45,y),(xs[a]+45,y+20),(xs[a],y+20)],label,xs[a]+155,y+4)
        else:g.line([(xs[a],y),(xs[b],y)],label,(xs[a]+xs[b])/2,y-9,dashed=b<a)
    g.text(560,h-20,notes,13)
    register(name,title,'Time progresses downward; return messages are dashed. Failure branches are stated alongside the flow.',g)

sequence('05a-sequence-negotiation','Sequence — asking price and buyer negotiation',['Farmer','Application','Buyer'],[(0,1,'Publish potatoes: 100 kg at LKR 200/kg'),(1,2,'Show asking price and available quantity'),(2,1,'Offer 50 kg at LKR 195/kg; total LKR 9,750'),(1,0,'Notify: pending offer; no stock held'),(0,1,'Accept offered price and quantity'),(1,0,'Atomic hold: 50 kg at 195/kg; expires +24h'),(1,2,'Notify accepted offer and reservation expiry')],'Alternative: farmer rejects; no hold is created. Buyer may submit a new offer.')
sequence('05-sequence-reservation','Sequence — reservation acceptance',['Farmer','API / Auth','Trade service','PostgreSQL'],[(0,1,'Accept buyer price offer on own lot'),(1,2,'Validated identity + offer ID'),(2,3,'BEGIN; lock offer and lot'),(3,2,'Current state and unexpired allocations'),(2,3,'If available: create reservation, expires +24h'),(2,3,'Store acceptance + audit + notification event'),(3,2,'COMMIT: one accepted reservation'),(2,1,'Reservation ID and server expiry'),(1,0,'Show held kg and expiry')],'Conflict: rollback and return 409. Repeat acceptance returns the existing reservation.')
sequence('06-sequence-sale','Sequence — inspection-qualified purchase',['Buyer','API / Auth','Trade service','PostgreSQL'],[(0,1,'Confirm reservation + idempotency key'),(1,2,'Verify buyer ownership'),(2,3,'BEGIN; lock lot/reservation; check key'),(3,2,'Fresh time, inspection, holds, consent, deductions'),(2,3,'Validate active + no reconciliation deficit'),(2,3,'Create sale + settlement; consume reservation'),(2,3,'Store idempotent response + audit + event'),(3,2,'COMMIT atomically'),(2,1,'Sale / receipt; payment remains unpaid'),(1,0,'Show agreed kg and totals')],'Expired, rejected or unreconciled: rollback. Same key/input returns same result; changed input conflicts.')
sequence('07-sequence-ai','Sequence — authorized AI answer',['Signed-in user','Assistant API','Model adapter','Read tools','Database'],[(0,1,'Question + owned session ID'),(1,2,'Bounded prompt + approved tool schemas'),(2,1,'Request allowlisted read tool'),(1,3,'Validate schema; derive actor from session'),(3,4,'Authorized parameterized read'),(4,3,'Current facts + timestamps'),(3,1,'Minimal permitted result'),(1,2,'Authorized facts for explanation'),(2,1,'Draft explanation'),(1,0,'Validated answer + backend source cards')],'No writes. Invalid facts use templates. Provider failure or 20-second deadline returns a clear fallback.')

g=Diagram('Trade activity',1120,930)
g.box(380,20,350,45,'Farmer publishes lot + asking price')
g.box(380,100,350,45,'Buyer proposes price; farmer accepts')
g.box(380,180,350,45,'24-hour stock reservation')
g.box(380,260,350,45,'Visit → check-in → unloading')
g.box(380,340,350,45,'Administrator records inspected kg')
g.diamond(425,420,260,85,'Quality accepted?')
g.box(790,435,290,65,'Reject lot / cancel holds')
g.diamond(425,550,260,85,'Allocations fit?')
g.box(35,555,300,80,'Shortage reconciliation',['Propose reductions; buyer consent'])
g.box(380,685,350,50,'Buyer confirms valid reservation')
g.box(380,780,350,50,'Sale → settlement → admin payments')
for a,b in [(65,100),(145,180),(225,260),(305,340),(385,420),(505,550),(635,685),(735,780)]:g.line([(555,a),(555,b)])
g.line([(685,462),(790,462)],'No',740,450)
g.line([(425,592),(335,592)],'No',375,578)
g.line([(185,635),(185,710),(380,710)],'Resolved; still valid',245,694)
g.text(625,535,'Yes',13);g.text(625,666,'Yes',13)
g.text(560,885,'Expiry/cancellation may end a hold at any stage before confirmation; no automatic extension.',14)
register('08-activity','Activity — produce to settlement','Main path with inspection exceptions. Visit booking can also occur before or without a reservation. Payments require actual external payment evidence.',g)

g=Diagram('State transitions',1120,800)
g.text(560,30,'Reservation state machine',19)
g.box(40,85,200,55,'ACTIVE')
for y,t in [(60,'CONFIRMED'),(170,'CANCELLED'),(280,'EXPIRED')]:g.box(790,y,230,55,t)
g.line([(240,110),(500,110),(500,87),(790,87)],'Inspected + consent + valid time',520,65)
g.line([(240,120),(450,120),(450,197),(790,197)],'Explicit cancellation / rejection',600,180)
g.line([(240,130),(390,130),(390,307),(790,307)],'Server time ≥ expires_at',600,290)
g.text(560,390,'Visit state machine',19)
for x,t in [(25,'BOOKED'),(250,'ARRIVED'),(475,'CALLED'),(700,'UNLOADING'),(925,'COMPLETED')]:g.box(x,460,170,55,t)
for x in [195,420,645,870]:g.line([(x,487),(x+55,487)])
g.line([(560,515),(560,570),(335,570),(335,515)],'Recall: release bay; mark unready',455,595)
g.box(25,670,200,55,'CANCELLED / NO_SHOW')
g.line([(110,515),(110,670)],'Before arrival',190,640)
g.text(770,650,'Bay reserved from CALLED through UNLOADING.',14)
g.text(770,680,'COMPLETED releases bay; departure timestamp follows.',14)
g.text(560,770,'Reconciliation is a lot-level hold, not a new reservation terminal state.',14)
register('09-states','State diagrams — reservations and visits','Terminal reservations are never reused. All transitions validate actor, current state and concurrency constraints.',g)

def md(text):
    """Small deterministic renderer for these local Markdown sources."""
    def inline(s):
        s=esc(s)
        s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
        s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
        s=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1',s)
        return s
    out=[]; table=False; listing=False
    for line in text.splitlines()+['']:
        if line.startswith('|'):
            if re.match(r'^\|[ :|\-]+$',line):continue
            cells=line.strip('|').split('|')
            if not table:out.append('<table>');table=True;tag='th'
            else:tag='td'
            out.append('<tr>'+''.join(f'<{tag}>{inline(c.strip())}</{tag}>' for c in cells)+'</tr>');continue
        if table:out.append('</table>');table=False
        li=re.match(r'^(?:- |\d+\. )(.*)',line)
        if li:
            if not listing:out.append('<ul>');listing=True
            out.append('<li>'+inline(li[1])+'</li>');continue
        if listing:out.append('</ul>');listing=False
        if not line.strip():continue
        heading=re.match(r'^(#{1,6}) (.*)',line)
        if heading:
            level=min(len(heading[1])+1,5)
            out.append(f'<h{level}>{inline(heading[2])}</h{level}>')
        else:out.append('<p>'+inline(line)+'</p>')
    return '\n'.join(out)

source=(ROOT/'project-documentation-v1.5.md').read_text(encoding='utf-8')
chunks=re.split(r'<!-- SECTION: ([a-z]+) \| (.*?) -->',source)
sections=[(chunks[i],chunks[i+1],md(chunks[i+2])) for i in range(1,len(chunks),3)]

css='''@page { size:A4; margin:17mm 16mm 19mm; } *{box-sizing:border-box} body{font-family:Arial,sans-serif;color:#203c43;font-size:10pt;line-height:1.48;margin:0} h1,h2,h3,h4,h5{color:#155b4a;break-after:avoid} h1{font-size:27pt;line-height:1.2} h2{font-size:20pt;border-bottom:2px solid #77ad90;padding-bottom:8px} h3{font-size:15pt;margin-top:22px} h4{font-size:12pt} h5{font-size:10.5pt} p{orphans:3;widows:3} table{border-collapse:collapse;width:100%;margin:12px 0;font-size:8.3pt;table-layout:fixed} th,td{border:1px solid #bfd2ca;padding:7px;vertical-align:top;overflow-wrap:anywhere} th{background:#e4f1eb;color:#164e40} tr{break-inside:avoid} li{margin:5px 0} code{font-size:8.5pt;background:#f0f5f3;overflow-wrap:anywhere} .cover{page-break-after:always;padding:95px 15px 20px;border-top:12px solid #26755b;min-height:900px}.eyebrow{letter-spacing:3px;color:#528577;font-size:11pt}.subtitle{font-size:17pt;color:#628374}.meta{margin-top:65px;border-left:4px solid #7db998;padding:15px;background:#f0f7f3}.section{page-break-before:always}.figure{page-break-before:always;break-inside:avoid}.figure h2{font-size:18pt}.figure img{display:block;width:100%;max-height:218mm;object-fit:contain}.caption{font-size:9pt;color:#536d73}.note{background:#fff6df;padding:12px;border-left:4px solid #c59c39}a{color:#155b4a} .toc li{margin:12px 0} @media screen{body{max-width:960px;margin:auto;padding:35px;background:white}.figure{margin-top:60px}}'''
toc='<ol class="toc">'+''.join(f'<li><a href="#{sid}">{title}</a></li>' for sid,title,_ in sections)+'<li><a href="#diagrams">Design diagrams (10 figures)</a></li><li><a href="#references">Sources, status and revision record</a></li></ol>'
body='''<div class="cover"><p class="eyebrow">PROJECT DOCUMENTATION • VERSION 1.5</p><h1>Dambulla<br>AgriFlow</h1><p class="subtitle">Software requirements &amp; system design</p><p>A single-market agricultural wholesale coordination platform</p><div class="meta"><p><strong>Prepared:</strong> 3 November 2026</p><p><strong>Delivery model:</strong> one student developer with AI assistance</p><p><strong>Planning horizon:</strong> 22 weeks, subject to effort and deadline confirmation</p><p><strong>Status:</strong> pre-implementation design baseline for review</p></div><p>Includes functional requirements, business policies, data design, role permissions, APIs, verification, delivery plan and ten editable diagrams.</p><p>Author/student details, institution and supervisor sign-off remain to be supplied. This document does not claim implementation, testing or approval has occurred.</p></div><h2>Document guide</h2><p>This consolidated document incorporates the supplied v1.3 requirements and the subsequent project decisions. The MVP uses three roles: Farmer, Buyer and Administrator. Farmers publish asking prices and buyers negotiate through price offers. Twenty-four-hour reservations supersede the original two-hour rule. Administrator-managed collections and payouts are separate records; no payment gateway is included.</p>'''+toc
body+=''.join(f'<section class="section" id="{sid}"><h2>{title}</h2>{content}</section>' for sid,title,content in sections)
for i,(name,title,caption) in enumerate(diagrams,1):
    body+=f'<section class="figure" id="{"diagrams" if i==1 else name}"><h2>Figure {i}. {title}</h2><img src="../diagrams/{name}.svg" alt="{esc(title)}"><p class="caption">{esc(caption)}</p></section>'
body+='''<section class="section" id="references"><h2>Sources and revision record</h2><p>Primary source: Dambulla_AgriFlow_Complete_Requirements_v1.3 (1).docx, draft dated 31 October 2026, supplied in the project folder.</p><p>Current editable source: docs/project-documentation-v1.5.md. This source consolidates the requirements and subsequent role, reservation and negotiation decisions. User decisions: at least a day for reservations; administration handles payment records; remaining principal policies delegated for selection.</p><p>Version 1.5 consolidates those requirements, selects the 24-hour rule, defines inspection shortages, separates collection/payout, specifies correction holds and atomic bay allocation, and adds diagrams and implementation coverage. Additional MVP defaults are explicitly identified as design choices requiring walkthrough validation.</p><p>External references listed in the original SRS are not treated as verified integration contracts. Current library versions, model pricing and price-data access are intentionally not asserted here.</p><h3>Deliverable status</h3><p>Completed: requirements/design document and editable SVG diagrams. Pending implementation: source code, migrations, machine-readable OpenAPI, detailed wireframe assets, observed test results, operational commands, deployment and measured backup restoration. Pending stakeholder review: grading thresholds, operational defaults, real payment process, retention, deadline and assessment constraints.</p><h3>How to maintain this document</h3><p>Edit the Markdown inputs and docs/tools/build_documentation.py, run the generator, then export the generated HTML to PDF. SVG diagrams are editable vector files. Keep requirement IDs stable and update diagrams, acceptance conditions and timeline when business rules change.</p></section>'''
document='<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Dambulla AgriFlow — Project Documentation v1.5</title><style>'+css+'</style></head><body>'+body+'</body></html>'
(OUT/'Dambulla_AgriFlow_Project_Documentation_v1.5.html').write_text(document,encoding='utf-8')
(D/'README.md').write_text('# Editable design diagrams\n\nGenerated as standalone SVG files by `../tools/build_documentation.py`. Open in a browser or edit with a vector editor. Relations use explicitly labelled cardinalities; the data dictionary completes supporting relationships.\n\n'+'\n'.join(f'- [{title}]({name}.svg)' for name,title,_ in diagrams)+'\n',encoding='utf-8')
print(f'Generated HTML documentation and {len(diagrams)} SVG diagrams.')
