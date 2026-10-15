import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const path='/home/angsuman/extra_spac/Assam College/Assam_Colleges_Complete_Directory.xlsx';
const source='https://cdnbbsr.s3waas.gov.in/s3f3d9de86462c28781cbe5c47ef22c3e5/uploads/2024/05/2024052045.pdf';
const entries=[
 ['Govt. ITI Dhansiri','Golaghat'],
 ['Govt. ITI Dudhnoi','Goalpara'],
 ['Govt. ITI Pathsala','Bajali'],
 ['Govt. ITI Sootea','Biswanath'],
 ['Govt. ITI for Dibyang, Dibrugarh','Dibrugarh'],
 ['Govt. ITI Boko','Kamrup Rural'],
 ['Govt. ITI Kajalgaon','Chirang'],
 ['Govt. ITI Lahowal','Dibrugarh'],
 ['Govt. ITI Bokajan','Karbi Anglong'],
 ['Govt. ITI for Women, Nalbari','Nalbari'],
 ['Govt. ITI Kazigaon','Kokrajhar'],
 ['Govt. ITI Ballamguri','Kokrajhar'],
];
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sh=wb.worksheets.getItemAt(0);
for(let i=0;i<entries.length;i++){
 const row=502+i,[name,district]=entries[i];
 sh.getRange(`A${row}:S${row}`).values=[[row-1,name,'ITI','',district,'','','','','','','Directorate of Employment and Craftsmen Training, Assam','NCVT / SCVT','','','State Government','','',
  `Listed in official government ITI directory; trades not yet verified; institution source: ${source}`]];
 sh.getRange(`B${row}:S${row}`).format.wrapText=true;
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path);
console.log('Added 12 government ITIs');
