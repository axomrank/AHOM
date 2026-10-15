import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';

const root='/home/angsuman/extra_spac/Assam College';
const input=await SpreadsheetFile.importXlsx(await FileBlob.load(`${root}/Assam_Colleges_Complete_Directory.xlsx`));
const rows=input.worksheets.getItemAt(0).getRange('A1:S562').values;
if(rows[0][1]!=='College / Institute'||rows[0][3]!=='Category')throw Error('Unexpected workbook layout');
const general=rows.slice(1).filter(r=>r[3]==='General Degree (Government)'||r[3]==='General Degree (Provincialised)');
if(general.length!==370)throw Error(`Expected 370 general colleges; got ${general.length}`);
const records=[rows[0],...general];
const field=value=>{
 const text=value==null?'':String(value);
 return /[",\r\n]/.test(text)?`"${text.replaceAll('"','""')}"`:text;
};
const csv='\uFEFF'+records.map(row=>row.map(field).join(',')).join('\r\n')+'\r\n';
await fs.writeFile(`${root}/general_colleges.csv`,csv,'utf8');
console.log(JSON.stringify({records:general.length,columns:rows[0].length,bytes:Buffer.byteLength(csv)}));
