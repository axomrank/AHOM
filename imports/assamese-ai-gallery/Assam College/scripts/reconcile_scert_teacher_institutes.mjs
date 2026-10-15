import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const file='/home/angsuman/extra_spac/Assam College/Assam_Colleges_Complete_Directory.xlsx';
const roster='https://elementary.assam.gov.in/information-services/list-of-teacher-education-institutesteis';
const admission='https://scert.assam.gov.in/sites/default/files/swf_utility_folder/departments/scert_medhassu_in_oid_6/portlet/level_2/information-brochure-pet-2026.pdf';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(file));
const sh=wb.worksheets.getItemAt(0);
const rows=sh.getRange('A2:S519').values;
if(rows.length!==518 || rows.filter(r=>r[1]).length!==518)throw Error('Unexpected input');
const map=new Map(rows.map((r,i)=>[r[1],i]));
const diets={
 'Sonitpur':['Biswanath','Biswanath Chariali'],
 'Goalpara':['Goalpara','Dudhnoi'],
 'Kamrup':['Kamrup Rural','Mirza'],
 'Jorhat':['Jorhat','Titabor'],
 'Dibrugarh':['Dibrugarh','Chabua'],
 'Karimganj':['Karimganj','Kaliganj'],
 'Karbi Anglong':['Karbi Anglong',''],
 'Nalbari':['Nalbari','Karia'],
 'Morigaon':['Morigaon',''],
 'Lakhimpur':['Lakhimpur','Azad'],
 'Barpeta':['Barpeta','Howly'],
 'Bongaigaon':['Bongaigaon',''],
 'Hailakandi':['Hailakandi',''],
 'Dima Hasao':['Dima Hasao','Haflong'],
 'Dhemaji':['Dhemaji','']
};
for(const [old,[district,place]] of Object.entries(diets)){
 const i=map.get(`District Institute of Education and Training (DIET), ${old}`);
 if(i===undefined)throw Error(`Missing DIET ${old}`);
 const r=rows[i];
 r[1]=`District Institute of Education and Training (DIET), ${old==='Sonitpur'?'Biswanath':old}${place?', '+place:''}`;
 r[3]='D.El.Ed. / Teacher Education';r[4]=district;r[5]=place;
 r[18]=`Institution and location in SCERT public TEI roster: ${roster}. D.El.Ed. intake is documented in 2026 SCERT brochure where listed: ${admission}. Internal departments unverified.`;
}
const add=[];
function push(name,district,location,course,source=roster){
 if(rows.some(r=>r[1]===name)||add.some(r=>r[1]===name))throw Error(`Duplicate ${name}`);
 add.push([519+add.length,name,'Teacher Education',course,district,location,'','','','',
  '','State Council of Educational Research and Training, Assam','SCERT, Assam','','',
  'State Government','','',`Public teacher education institute listed by SCERT: ${source}. Internal departments unverified.`]);
}
// The eight DIETs in SCERT's 2025 roster that were absent from the workbook.
for(const [district,place] of [
 ['Nagaon','Samaguri'],['Kokrajhar','Gourang Nwgwr'],['Cachar','Udharbond'],
 ['Darrang','Dalgaon'],['Dhubri','Golakganj'],['Golaghat','Dergaon'],
 ['Tinsukia','Tingrai Habi, Sripuria'],['Charaideo','Sonari']
])push(`District Institute of Education and Training (DIET), ${district}${place?', '+place:''}`,district,place,'D.El.Ed. / Teacher Education',admission);
// Basic Training Centres and the institute now called BITE Rangia.
for(const [name,district,location] of [
 ['Basic Training Centre, Ravanapara','Majuli','Ravanapara'],
 ['Basic Training Centre, Chenga','Barpeta','Chenga'],
 ['Basic Training Centre, Golakganj','Dhubri','Golakganj'],
 ['Basic Training Centre, Azad','Lakhimpur','Azad'],
 ['Basic Training Centre, Dalgaon','Darrang','Dalgaon'],
 ['Basic Training Centre, Khowang','Dibrugarh','Khowang'],
 ['Basic Training Centre, Nalbari','Nalbari','Nalbari'],
 ['Basic Training Centre, Sonari','Charaideo','Sonari'],
 ['Basic Training Centre, Dudhnoi','Goalpara','Dudhnoi'],
 ['Basic Training Centre, Kaliganj','Karimganj','Kaliganj'],
 ['Basic Training Centre, Hailakandi','Hailakandi','Hailakandi'],
 ['Basic Training Centre, Howly','Barpeta','Howly'],
 ['Basic Training Centre, Chabua','Dibrugarh','Chabua'],
 ['Basic Training Centre, Raha','Nagaon','Raha'],
 ['Block Institute of Teacher Education (BITE), Rangia','Kamrup Rural','Rangia'],
 ['Basic Training Centre, Diphu','Karbi Anglong','Diphu'],
 ['Basic Training Centre, Dergaon','Golaghat','Dergaon'],
 ['Basic Training Centre, Kokrajhar','Kokrajhar','Kokrajhar'],
 ['Basic Training Centre, Joysagar','Sivasagar','Joysagar']
])push(name,district,location,'Teacher Education / D.El.Ed. where offered');
for(const [place,district] of [
 ['Jorhat','Jorhat'],['Bongaigaon','Bongaigaon'],['Dhakuakhana','Lakhimpur'],
 ['Nagaon','Nagaon'],['Silchar','Cachar'],['Sootea','Biswanath'],['Howly','Barpeta']
])push(`Normal School, ${place}`,district,place,'Teacher Education / D.El.Ed. where offered');
for(const [name,district,place] of [
 ['Pre-Primary Teachers Training Centre, Dibrugarh','Dibrugarh','Dibrugarh'],
 ['Hindi Teachers Training College, North Guwahati','Kamrup Rural','North Guwahati'],
 ['Hindi Training Centre, Diphu','Karbi Anglong','Diphu']
])push(name,district,place,'Teacher Education');
sh.getRange('A2:S519').values=rows;
sh.getRange(`A520:S${519+add.length}`).values=add;
sh.getRange(`B2:S${519+add.length}`).format.wrapText=true;
await (await SpreadsheetFile.exportXlsx(wb)).save(file);
console.log(JSON.stringify({added:add.length,total:518+add.length}));
