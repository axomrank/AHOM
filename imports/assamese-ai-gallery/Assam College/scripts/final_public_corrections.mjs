import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const path='/home/angsuman/extra_spac/Assam College/Assam_Colleges_Complete_Directory.xlsx';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sh=wb.worksheets.getItemAt(0);
const set=(col,row,value)=>sh.getRange(`${col}${row}`).values=[[value]];

// Two unsupported legacy rows are replaced by active provincialised colleges.
const replacements=[
  [49,'Damdama College','Kamrup Rural','Gauhati University','https://damdamacollege.edu.in/',
   'Assamese; Economics; Education; English; History; Information Technology; Political Science',
   'https://damdamacollege.edu.in/storage/notifications/69f31d074e46b.pdf',
   'Seven departments in 2026 prospectus; institution in DHE 337 roster; replaced private Anundoram Borooah Academy Degree College'],
  [62,'B.L.B. College','Sivasagar','Dibrugarh University','',
   '','',
   'Provincialised college in DHE 337 roster; departments not yet verified; replaced unsupported Chenga OGC Girls College'],
];
for(const [row,name,district,university,website,depts,deptSource,note] of replacements){
  sh.getRange(`A${row}:S${row}`).values=[[row-1,name,'General Degree (Provincialised)','Arts / BA',district,'','','','',website,'','Directorate of Higher Education, Assam',university,'','','Provincialised State College',depts,deptSource,note]];
  sh.getRange(`B${row}:S${row}`).format.wrapText=true;
}

// 2025-26 university brochure and individual college profiles supersede the older DHE roster.
const bhattadev=[50,57,58,59,60,61,63,64,65,345,380,381,382,383,467,473,493,494];
for(const row of new Set(bhattadev)){
  set('M',row,'Bhattadev University');
  const cell=sh.getRange(`S${row}`);
  const prior=String(cell.values[0][0]??'');
  if(!prior.includes('BU-Brochure'))cell.values=[[prior+'; current affiliation: https://bhattadevuniversity.ac.in/docs/BU-Brochure%202025.pdf']];
}
set('E',345,'Barpeta'); set('M',345,'Bhattadev University'); set('J',345,'https://mkcollege.ac.in/');
set('E',381,'Bajali');
set('E',467,'Barpeta'); set('M',467,'Bhattadev University');
set('E',473,'Barpeta'); set('M',473,'Bhattadev University');

// Swahid Peoli Phukan College has a current department index.
set('M',403,'Dibrugarh University');set('J',403,'https://sppcollege.in/');
set('Q',403,'Assamese; Chemistry; Economics; Education; English; Geography; Geology; History; Mathematics; Political Science; Sociology; Statistics; Zoology');
set('R',403,'https://sppcollege.in/firstpage.php');
set('S',403,'Thirteen named departments on official Arts and Science navigation');

set('Q',345,'Anthropology; Arabic; Assamese; Economics; Education; English; Hindi; History; Philosophy; Political Science; Sanskrit');
set('R',345,'https://www.mkcollege.ac.in/clgdepartments.php');
set('S',345,'Eleven departments on official college department index; current affiliation: https://bhattadevuniversity.ac.in/docs/BU-Brochure%202025.pdf');
set('E',408,'Bongaigaon');set('M',408,'Gauhati University');set('J',408,'https://mgcc.ac.in/');
set('Q',408,'Assamese; Education; English; Political Science');
set('R',408,'https://mgcc.ac.in/doc/rXtkgPRTOwNNPKH0Kz90.pdf');
set('S',408,'Four named departments in official 2024–25 prospectus');
set('E',435,'Barpeta');set('M',435,'Gauhati University');set('J',435,'https://janapriyacollege.in/');
set('M',388,'Gauhati University');
set('M',402,'Assam University');

await (await SpreadsheetFile.exportXlsx(wb)).save(path);
console.log('Corrected private/unsupported rows and current affiliations');
