import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const path='/home/angsuman/extra_spac/Assam College/Assam_Colleges_Complete_Directory.xlsx';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sh=wb.worksheets.getItemAt(0);
const dme='https://dme.assam.gov.in/information-services/medical-collegesinstitutes';
const nursing='https://dme.assam.gov.in/sites/default/files/swf_utility_folder/departments/dme_lipl_in_oid_8/menu/information_and_services/5.nursing_courses.pdf';
const items=[
 [15,'Government Nursing College, Jorhat','Nursing','Jorhat','Srimanta Sankaradeva University of Health Sciences',nursing,'Replaced unsupported College of Sericulture, Debapar; AAU lists only its Titabar sericulture college'],
 [497,'Government Nursing College, Kokrajhar','Nursing','Kokrajhar','Srimanta Sankaradeva University of Health Sciences',nursing,'In current DME government nursing seat list'],
 [498,'Institute of Paramedical Sciences, Gauhati Medical College','Paramedical','Kamrup Metropolitan','',dme,'Government institute in DME directory'],
 [499,'Institute of Paramedical Sciences, Assam Medical College','Paramedical','Dibrugarh','',dme,'Government institute in DME directory'],
 [500,'Institute of Paramedical Sciences, Silchar Medical College','Paramedical','Cachar','',dme,'Government institute in DME directory'],
 [501,'Institute of Paramedical Sciences, Jorhat Medical College','Paramedical','Jorhat','',dme,'Government institute in DME directory'],
];
for(const [row,name,category,district,univ,source,note] of items){
  sh.getRange(`A${row}:S${row}`).values=[[row-1,name,category,'',district,'','','','','','','Directorate of Medical Education, Assam',univ,'','',
    'State Government', '', '', `${note}; institution source: ${source}; departments not yet verified`]];
  sh.getRange(`B${row}:S${row}`).format.wrapText=true;
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path);
console.log('Added five DME institutes and corrected one unsupported sericulture entry');
