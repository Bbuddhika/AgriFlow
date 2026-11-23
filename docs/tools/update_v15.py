from pathlib import Path
p=Path(__file__).with_name('build_documentation.py')
s=p.read_text(encoding='utf-8')
s=s.replace('Five role dashboards','Three role dashboards').replace('Five demo roles','Three demo roles')
start=s.index("g=Diagram('Role use cases'")
end=s.index('\ndef entity',start)
s=s[:start]+'''g=Diagram('Three-role use cases',1120,820)
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
''' +s[end:]
s=s.replace("'quantity_kg, unit_price'","'quantity_kg, offered_price_per_kg'")
s=s.replace("'status, lookup_token','stock_basis, version'","'status, asking_price_per_kg','stock_basis, price_version'")
s=s.replace('inspector_id','recorded_by_admin_id').replace('Inspector measures saleable stock','Administrator records inspected kg')
s=s.replace("(0,1,'Accept own lot offer')","(0,1,'Accept buyer price offer on own lot')")
s=s.replace("'Farmer registers lot'","'Farmer publishes lot + asking price'").replace("'Buyer offers; farmer accepts'","'Buyer proposes price; farmer accepts'")
start=s.index('| Action | Farmer | Buyer | Operator | Inspector | Administrator |')
end=s.index('\n### Additional MVP policies',start)
s=s[:start]+'''| Action | Farmer | Buyer | Administrator |
|---|---|---|---|
| Publish lot / edit asking price | Own | No | No impersonation |
| Submit price offer | No | Own | No impersonation |
| Accept/reject offer | Own lot | No | No impersonation |
| Shortage consent / purchase confirmation | No | Own | Coordinate only |
| Approve deductions | Own | View agreement | Propose / record |
| Book visit | Own | No | Rebook with reason |
| Slots / check-in / call / unload | No | No | Yes, audited |
| Inspection / reinspection / verify stock | No | No | Yes, audited |
| Payments / corrections | No | No | Yes, audited |
| Accounts / catalog / source prices | No | No | Yes |
| Reports / audit | Own history | Own history | Market-wide |
| Assistant / chat | Own scope | Own scope | Authorized scope |
''' +s[end:]
s=s.replace('Users may hold multiple roles, but each action still checks role and record ownership.','The role catalog contains FARMER, BUYER and ADMINISTRATOR only; each action checks role and ownership. An actor cannot accept their own buyer offer through another role.')
s=s.replace('Only with operator role','Administrator').replace('Only with inspector role','Administrator')
s=s.replace('Operator: slot capacity, arrivals, check-in/manual lookup, bay board and departure. Inspector: lot lookup, measurement form, history and correction-stock verification. Administrator:', 'Administrator: slot capacity, arrivals, check-in/manual lookup, bay board, departure, lot lookup, measurement form, inspection history, correction-stock verification,')
s=s.replace('Inspector','Administrator').replace('inspectors','administrators').replace('inspector','administrator').replace('Operator','Administrator').replace('operators','administrators').replace('operator','administrator')
s=s.replace('| status', '| status')
s=s.replace('Lot/buyer FKs; quantity and price >0; status and acceptance time','Lot/buyer FKs; quantity and offered price >0; asking-price snapshot/version; status and acceptance time')
s=s.replace('Harvest FK; unique opaque lookup token; state/version; provisional quantity and effective stock basis','Harvest FK; asking_price_per_kg >0 on publish; price_version/published_at; opaque lookup token; state; stock basis')
s=s.replace('weeks', 'weeks')
# Apply current roles to historical text imported into the consolidated document.
needle="requirements=requirements.replace('two-hour expiry"
pos=s.index(needle)
s=s[:pos]+'''def current_roles(text):
    text=text.replace('Five active roles: farmer, buyer, operator, inspector and administrator.', 'Three active roles: farmer, buyer and administrator.')
    text=text.replace('Five demo roles','Three demo roles').replace('Five roles','Three roles').replace('five roles','three roles').replace('five active roles','three active roles').replace('the five roles','the three roles')
    text=text.replace('inspectors','administrators').replace('Inspectors','Administrators').replace('inspector','administrator').replace('Inspector','Administrator')
    text=text.replace('operators','administrators').replace('Operators','Administrators').replace('operator','administrator').replace('Operator','Administrator')
    return text
requirements=current_roles(requirements)
a=requirements.index('### Actors')
b=requirements.index('## 3. Functional requirement inventory')
requirements=requirements[:a]+"""### Actors

| Actor | Responsibilities | Boundary |
|---|---|---|
| Farmer | Publish asking-priced lots, accept/reject offers, book visits, approve deductions, view own sales | Own records; cannot inspect or record payments |
| Buyer | Search lots, propose price/kg and quantity, consent to shortages, confirm purchase | Own offers/transactions; no other buyer's private offers |
| Administrator | Operations, inspections, shortages, payments, corrections, accounts, prices, reports | Audited actions; cannot impersonate farmer or buyer consent |

The assistant is a read-only feature, not an additional role. Separate operations and inspection staff accounts are future extensions.

"""+requirements[b:]
requirements=requirements.replace('Buyer search and offers','Buyer search and negotiated price offers').replace('Traceable lots and QR lookup','Published asking-priced lots and QR lookup')
amend=current_roles(amend)
amend=amend.replace('Farmers, buyers and administrators cannot record administrator-only financial corrections or payments.', 'Farmers and buyers cannot record administrator-only financial corrections or payments.')
amend=amend.replace('An administrator verifies whether', 'An administrator physically verifies whether')
scope=(ROOT/'srs-v1.5-roles-and-negotiation.md').read_text(encoding='utf-8')
''' +s[pos:]
s=s.replace("plan=plan.replace('P0 decisions resolved;'", "plan=current_roles(plan)\nplan=plan.replace('P0 decisions resolved;'")
s=s.replace("sections=[('overview'", "sections=[('scope','Current scope: three roles and price negotiation',md(scope)),('overview'")
# New artifact version; preserve original amendment filename as historical source.
s=s.replace('VERSION 1.4','VERSION 1.5').replace('Version 1.4 consolidates','Version 1.5 consolidates').replace('Documentation v1.4','Documentation v1.5').replace('Documentation_v1.4','Documentation_v1.5')
s=s.replace('four role','three role')
s=s.replace('Twenty-four-hour reservations supersede the original two-hour rule.', 'The MVP uses three roles: Farmer, Buyer and Administrator. Farmers publish asking prices and buyers negotiate through price offers. Twenty-four-hour reservations supersede the original two-hour rule.')
s=s.replace('Business amendment: docs/srs-v1.4-business-rules.md.', 'Business amendments: docs/srs-v1.4-business-rules.md and docs/srs-v1.5-roles-and-negotiation.md; v1.5 takes precedence.')
p.write_text(s,encoding='utf-8')
print('Updated documentation generator for v1.5.')
