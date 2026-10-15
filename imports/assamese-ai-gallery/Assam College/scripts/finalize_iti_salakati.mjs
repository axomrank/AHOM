import fs from 'node:fs';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const path='/home/angsuman/extra_spac/Assam College/Assam_Colleges_Complete_Directory.xlsx';
const source='https://cdnbbsr.s3waas.gov.in/s3f3d9de86462c28781cbe5c47ef22c3e5/uploads/2025/07/2025072143.pdf';
const trades=JSON.parse(fs.readFileSync('/tmp/assam_iti_2025_trades.json','utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sh=wb.worksheets.getItemAt(0);
sh.getRange('A514:S514').values=[[513,'Govt. ITI Salakati','ITI','','Kokrajhar','','','','','','','Directorate of Employment and Craftsmen Training, Assam','NCVT / SCVT','','','State Government','','','Listed in the 2025 Assam ITI eCounselling vacancy roster']];
for(let row=502;row<=514;row++){
  sh.getRange(`Q${row}`).values=[[trades[row]]];
  sh.getRange(`R${row}`).values=[[source]];
  sh.getRange(`S${row}`).values=[[`Trades shown in the 2025 eCounselling vacant-seat roster; this may not be the complete trade list. Source: ${source}`]];
  sh.getRange(`B${row}:S${row}`).format.wrapText=true;
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path);
console.log('Added Salakati and 2025 trade evidence for 13 ITIs');
