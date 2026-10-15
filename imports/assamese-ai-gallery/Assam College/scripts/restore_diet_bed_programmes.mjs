import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const path='/home/angsuman/extra_spac/Assam College/Assam_Colleges_Complete_Directory.xlsx';
const source='https://scert.assam.gov.in/sites/default/files/swf_utility_folder/departments/scert_medhassu_in_oid_6/menu/document/annual_report_2023-24.pdf';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sh=wb.worksheets.getItemAt(0);const rows=sh.getRange('A2:S562').values;
if(rows.length!==561)throw Error('Unexpected workbook');
const districts=new Set(['Biswanath','Goalpara','Kamrup Rural','Jorhat','Dibrugarh','Karimganj','Karbi Anglong','Nalbari','Morigaon','Lakhimpur','Barpeta','Bongaigaon','Hailakandi','Dima Hasao','Dhemaji']);
let changed=0;
for(const r of rows){if(r[1]?.startsWith('District Institute of Education and Training')&&districts.has(r[4])){
 r[3]='B.Ed. / D.El.Ed. / Teacher Education';r[18]=`${r[18]} B.Ed. included in the SCERT 2023–24 report: ${source}.`;changed++;
}}
if(changed!==15)throw Error(`Expected 15 DIETs, got ${changed}`);
sh.getRange('A2:S562').values=rows;
await (await SpreadsheetFile.exportXlsx(wb)).save(path);
console.log('Restored B.Ed. course listing for 15 SCERT-confirmed DIETs');
