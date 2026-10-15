import fs from 'node:fs/promises';
import {Workbook} from '@oai/artifact-tool';

const root='/home/angsuman/extra_spac/Assam College';
const path=`${root}/general_colleges.csv`;
const reviews=JSON.parse(await fs.readFile(`${root}/academic_evidence/academic_review.json`,'utf8'));
const prior=await fs.readFile(path,'utf8');
const wb=await Workbook.fromCSV(prior,{sheetName:'General colleges'});
const sh=wb.worksheets.getItemAt(0);
const original=sh.getRange('A1:S364').values;
if(original[0][0].replace(/^\uFEFF/,'')!=='No.'||original[0][18]!=='Highlights'||original.length!==364)throw Error('Unexpected source CSV layout');
const fields=Object.keys(reviews[0]).filter(x=>x!=='No.'&&x!=='College / Institute');
const byId=new Map(reviews.map(x=>[String(x['No.']),x]));
if(byId.size!==363)throw Error('Duplicate review identifiers');
const all=[...original[0],...fields];
all[0]=String(all[0]).replace(/^\uFEFF+/, '');
const data=[all];
for(const row of original.slice(1)){
  const review=byId.get(String(row[0]));
  if(!review||review['College / Institute']!==row[1])throw Error(`Review mismatch at row ${row[0]}`);
  // The Behali college's 2026–27 B.A./B.Sc. admission notices and its
  // Science/Arts department menus correct the older Science-only label.
  if(String(row[0])==='4')row[4]='Arts, Science / BA, B.Sc';
  data.push([...row,...fields.map(f=>review[f]??'')]);
}
// Artifact Tool owns the complete spreadsheet edit and validates matrix shape.
const endCol=n=>{let s='';for(let x=n;x;x=Math.floor((x-1)/26))s=String.fromCharCode(65+(x-1)%26)+s;return s};
sh.getRange(`A1:${endCol(all.length)}${data.length}`).values=data;
wb.recalculate();
const verified=sh.getRange(`A1:${endCol(all.length)}${data.length}`).values;
if(verified.length!==364||verified[0].length!==all.length)throw Error('Artifact Tool output shape mismatch');
const field=v=>{const s=String(v??'');return /[",\r\n]/.test(s)?`"${s.replaceAll('"','""')}"`:s};
await fs.writeFile(path,'\uFEFF'+verified.map(r=>r.map(field).join(',')).join('\r\n')+'\r\n','utf8');
console.log(JSON.stringify({rows:verified.length-1,columns:all.length,academicColumns:fields.length}));
