import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
const path='/home/angsuman/extra_spac/Assam College/Assam_Colleges_Complete_Directory.xlsx';
const scert='https://scert.assam.gov.in/portlet-innerpage/list-of-teis-under-scert';
const goalpara='https://www.ctegoalpara.co.in/index.php';
const pgtc='https://www.iasejorhat.in/';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sh=wb.worksheets.getItemAt(0);
let rows=sh.getRange('A2:S556').values;
if(rows.length!==555||rows.filter(r=>r[1]).length!==555)throw Error('Unexpected input');
rows=rows.filter(r=>!['Government College of Teacher Education (GCTE), Dhubri','Government College of Teacher Education (GCTE), Jorhat'].includes(r[1]));
const p=rows.find(r=>r[1]==='Post Graduate Training College (PGTC), Jorhat');
if(!p)throw Error('Missing PGTC');
p[1]='Post Graduate Training College (IASE), Jorhat';p[8]='';p[9]=pgtc;p[10]='iasepgtcjorhat@gmail.com';p[3]='Teacher Education / B.Ed';
p[14]='Institute of Advanced Studies in Education (IASE), Jorhat';
p[18]=`Same institution as IASE Jorhat in the SCERT roster; verified NCTE institution record and college site: ${pgtc}. Internal departments unverified.`;
function add(name,district,location,course,site=''){
 rows.push([0,name,'Teacher Education',course,district,location,'','','',site,'',
  'State Council of Educational Research and Training, Assam','SCERT, Assam','','',
  'State Government','','',`Government teacher education institution in SCERT roster: ${scert}. Internal departments unverified.`]);
}
add('District Institute of Education and Training (DIET), Baksa','Baksa','','D.El.Ed. / Teacher Education');
add('District Institute of Education and Training (DIET), Chirang','Chirang','','D.El.Ed. / Teacher Education');
add('District Institute of Education and Training (DIET), Kamrup Metropolitan','Kamrup Metropolitan','','D.El.Ed. / Teacher Education');
add('District Institute of Education and Training (DIET), Udalguri','Udalguri','','D.El.Ed. / Teacher Education');
add('Government B.T. College (CTE), Goalpara','Goalpara','Goalpara','B.Ed. / Teacher Education',goalpara);
const g=rows.at(-1);g[12]='Gauhati University';g[18]=`Government B.T. College (CTE), Goalpara and Gauhati University affiliation: ${goalpara}; also in SCERT roster: ${scert}. Internal departments unverified.`;
rows.forEach((r,i)=>r[0]=i+1);
sh.getRange('A2:S559').values=rows;
sh.getRange('B2:S559').format.wrapText=true;
await (await SpreadsheetFile.exportXlsx(wb)).save(path);
console.log(JSON.stringify({total:rows.length,teacherEducation:rows.filter(r=>r[2]==='Teacher Education').length}));
