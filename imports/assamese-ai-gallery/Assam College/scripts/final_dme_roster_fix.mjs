import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
const path='/home/angsuman/extra_spac/Assam College/Assam_Colleges_Complete_Directory.xlsx';
const dme='https://dme.assam.gov.in/information-services/courses';
const institute='https://hfw.assam.gov.in/information-services/medical-collegesinstitutes-0';
const course='https://dme.assam.gov.in/sites/default/files/swf_utility_folder/departments/dme_lipl_in_oid_8/menu/information_and_services/8.%20Rural%20Health%20Care%20%28DMRHC%29_0.pdf';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sh=wb.worksheets.getItemAt(0);
const existing=sh.getRange('A2:S559').values;
if(existing.length!==558||existing.filter(r=>r[1]).length!==558)throw Error('Unexpected input');
const items=[
 [559,'Medical Institute, Jorhat','Medical','Diploma in Medicine and Rural Health Care','Jorhat','Jorhat','','','','','principalmij123@gmail.com','Directorate of Medical Education, Assam','','','','State Government','','',`Public institute in DME roster: ${institute}; DMRHC programme source: ${course}; internal departments unverified.`],
 [560,'Institute of Paramedical Sciences, Fakhruddin Ali Ahmed Medical College','Paramedical','Diploma in Paramedical Sciences','Barpeta','Barpeta','','','','','','Directorate of Medical Education, Assam','','','','State Government','','',`Institute in the DME 2026 course list: ${dme}; internal departments unverified.`],
 [561,'Institute of Paramedical Sciences, Tezpur Medical College','Paramedical','Diploma in Paramedical Sciences','Sonitpur','Tezpur','','','','','','Directorate of Medical Education, Assam','','','','State Government','','',`Institute in the DME 2026 course list: ${dme}; internal departments unverified.`]
];
sh.getRange('A560:S562').values=items;
sh.getRange('B560:S562').format.wrapText=true;
await (await SpreadsheetFile.exportXlsx(wb)).save(path);
console.log('Added 3 government medical education institutes; total 561');
