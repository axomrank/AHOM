import fs from 'node:fs';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const book='/home/angsuman/extra_spac/Assam College/Assam_Colleges_Complete_Directory.xlsx';
const roster='https://cdnbbsr.s3waas.gov.in/s3f3d9de86462c28781cbe5c47ef22c3e5/uploads/2024/05/2024052045.pdf';
const trades='https://cdnbbsr.s3waas.gov.in/s3f3d9de86462c28781cbe5c47ef22c3e5/uploads/2025/07/2025072143.pdf';
const prepared=JSON.parse(fs.readFileSync('/tmp/assam_iti_roster_reconciled.json','utf8'));
const byRow=new Map(Object.values(prepared.matched).map(x=>[x.row,x]));
const excluded=new Set(prepared.excluded.map(x=>x.row));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(book));
const sh=wb.worksheets.getItemAt(0);
const values=sh.getRange('A2:S514').values;
if(values.length!==513)throw Error(`Expected 513 data rows; found ${values.length}`);
const kept=[];
for(let i=0;i<values.length;i++){
  const oldRow=i+2;
  if(excluded.has(oldRow))continue;
  const row=[...values[i]];
  const official=byRow.get(oldRow);
  if(official){
    if(oldRow===283)row[1]='Govt. ITI Srikona (Silchar)';
    if(oldRow===312)row[1]='Govt. ITI Gargaon (Sivasagar)';
    if(oldRow===314)row[1]='Govt. ITI South Salmara';
    row[16]=official.trades;
    row[17]=trades;
    row[18]=`Government ITI confirmed in ${oldRow===514?'2025 counselling roster':'official government ITI list'}; trades shown in 2025 counselling vacant-seat roster and may be incomplete. Institution: ${oldRow===514?trades:roster}; trades: ${trades}`;
  }
  row[0]=kept.length+1;
  kept.push(row);
}
if(kept.length!==503)throw Error(`Expected 503 retained rows; found ${kept.length}`);
sh.getRange('A2:S504').values=kept;
sh.getRange('A505:S514').clear({applyTo:'all'});
sh.getRange('B2:S504').format.wrapText=true;
await (await SpreadsheetFile.exportXlsx(wb)).save(book);
console.log(`Retained ${kept.length} entries including 45 government ITIs`);
