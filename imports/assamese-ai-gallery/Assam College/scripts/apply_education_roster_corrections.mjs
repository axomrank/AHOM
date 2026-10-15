import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const book='/home/angsuman/extra_spac/Assam College/Assam_Colleges_Complete_Directory.xlsx';
const model='https://directorateofhighereducation.assam.gov.in/sites/default/files/swf_utility_folder/departments/dhe_medhassu_in_oid_4/menu/document/public_notice_english_and_assamese.pdf';
const scert='https://scert.assam.gov.in/sites/default/files/swf_utility_folder/departments/scert_medhassu_in_oid_6/menu/document/annual_report_2023-24.pdf';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(book));
const sh=wb.worksheets.getItemAt(0);
const rows=sh.getRange('A2:S504').values;
if(rows.length!==503)throw Error('Unexpected workbook size');
const byName=new Map(rows.map((r,i)=>[r[1],i]));

function update(name,patch){
 const i=byName.get(name);
 if(i===undefined)throw Error(`Missing ${name}`);
 const r=rows[i];
 for(const [col,val] of Object.entries(patch))r[Number(col)]=val;
}
update('Government Model College, Deithor',{
  3:'Arts / BA',
  12:'Dibrugarh University',
  14:'Six Arts teaching departments; affiliation confirmed on college site',
  18:'Six departments listed by college; Dibrugarh University affiliation confirmed at https://gmcdeithor.ac.in/'
});
update('Government College of Teacher Education (GCTE), Guwahati',{
  1:'Government Banikanta College of Teacher Education (IASE), Guwahati',
  9:'https://iaseguwahati.in/',
  18:'Official college name and government management confirmed at https://iaseguwahati.in/; education departments not yet verified'
});
update('Government College of Teacher Education (GCTE), Nagaon',{
  1:'Government Shikshan Mahavidyalaya (CTE), Nagaon',
  18:`Name confirmed in SCERT 2023–24 B.Ed. provider list: ${scert}; education departments not yet verified`
});
update('Government College of Teacher Education (GCTE), Kokrajhar',{
  12:'Bodoland University',
  18:'Government college and Bodoland University affiliation in NCTE institution list; education departments not yet verified: https://web.ncte.gov.in/page-regional-committee-institution-lists/4/www.dietbarpeta.co.in?page=6'
});

const subjects=[
 ['Government Model Women’s College, Hailakandi','Bengali; English; Geography; Hindi; Sociology'],
 ['Hari Singha Government Model Women’s College, Udalguri','Assamese; Bodo; English; Geography; Mass Communication'],
 ['Government Model College, Chirang','Assamese; Bodo; English; Geography; Mass Communication'],
 ['Government Model College, Majuli','Assamese; English; Geography; Mass Communication; Psychology'],
 ['Government Model College, Borsola','Assamese; English; Geography; Mass Communication; Psychology'],
 ['Government Model Women’s College, Mangaldai','Assamese; English; Geography; Mass Communication; Psychology'],
 ['Government Model Women’s College, Golakganj','Assamese; English; Geography; Mass Communication; Political Science'],
 ['Government Model College, Majar Alga','Assamese; Education; English; Geography; Mass Communication'],
 ['Government Model College, Lahorighat','Assamese; Education; English; History; Political Science'],
 ['Government Model College, Samaguri','Accountancy; Assamese; Economics; English; Finance; Mathematics']
];
for(const [name,list] of subjects){
 update(name,{16:list,17:model,18:`Teaching subjects listed in the DHE 2025–26 admission notice; separate departmental status has not been confirmed. Source: ${model}`});
}

const diets=['Sonitpur','Goalpara','Kamrup Rural','Jorhat','Dibrugarh','Karimganj','Karbi Anglong','Nalbari','Morigaon','Lakhimpur','Barpeta','Bongaigaon','Hailakandi','Dima Hasao','Dhemaji'];
const added=diets.map((district,i)=>[
  504+i,`District Institute of Education and Training (DIET), ${district==='Kamrup Rural'?'Kamrup':district}`,
  'Teacher Education','B.Ed. / Teacher Education',district,'','','','','','',
  'State Council of Educational Research and Training, Assam','','','',
  'State Government','','',
  `Government DIET offering the 2-year B.Ed. course in the SCERT 2023–24 report; institution source: ${scert}; internal departments not yet verified`
]);
sh.getRange('A2:S504').values=rows;
sh.getRange('A505:S519').values=added;
sh.getRange('B2:S519').format.wrapText=true;
await (await SpreadsheetFile.exportXlsx(wb)).save(book);
console.log('Corrected government colleges and added 15 official DIETs');
