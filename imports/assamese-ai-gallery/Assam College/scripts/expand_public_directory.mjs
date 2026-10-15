import fs from 'node:fs/promises';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const root='/home/angsuman/extra_spac/Assam College';
const path=`${root}/Assam_Colleges_Complete_Directory.xlsx`;
const additions=JSON.parse(await fs.readFile('/tmp/assam_public_additions.json','utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sh=wb.worksheets.getItemAt(0);
const replace=[21,33,61,345];
const rows=[...replace,...Array.from({length:additions.length-replace.length},(_,i)=>380+i)];

for(let i=0;i<additions.length;i++){
  const a=additions[i], row=rows[i];
  const model=a.type==='State Government Model College';
  const medical=a.type==='State Government Medical College';
  const streams=a.streams.length?a.streams.join(', '):'';
  const record=[row-1,a.name,medical?'Medical':model?'General Degree (Government)':'General Degree (Provincialised)',
    streams?a.streams.join(', ')+' / '+a.streams.map(x=>x==='Arts'?'BA':x==='Science'?'B.Sc':x==='Commerce'?'B.Com':x).join(', '):'',
    a.district||'', '', '', '', '', a.website||'', '',
    medical?'Directorate of Medical Education, Assam':'Directorate of Higher Education, Assam',
    a.university||'', '', '', a.type, '', '',
    a.note+'; institution source: '+a.source+(i<replace.length?'; replaced unsupported previous directory entry':'')];
  sh.getRange(`A${row}:S${row}`).values=[record];
  sh.getRange(`B${row}:S${row}`).format.wrapText=true;
  sh.getRange(`S${row}`).format.rowHeight=42;
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path);
console.log(`Wrote ${additions.length} verified public institutions, replacing ${replace.length} unsupported rows`);
