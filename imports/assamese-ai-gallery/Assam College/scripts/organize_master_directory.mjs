import {FileBlob, SpreadsheetFile, Workbook} from '@oai/artifact-tool';

const path='/home/angsuman/extra_spac/Assam College/Assam_Colleges_Complete_Directory.xlsx';
const input=await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const source=input.worksheets.getItemAt(0);
const old=source.getRange('A1:S562').values;
if(old[0][1]==='College / Institute'){
 source.getRange('H2:H562').format.wrapText=false;
 let restored=0;
 for(let i=1;i<old.length;i++)for(const col of [6,14]){
  const cell=source.getCell(i,col);
  const formula=cell.formulas?.[0]?.[0];
  if(typeof formula==='string' && formula.startsWith('=HYPERLINK("')){
   const match=formula.match(/^=HYPERLINK\("((?:[^"]|"")*)",/);
   if(!match)throw Error(`Cannot restore URL in row ${i+1}`);
   cell.values=[[match[1].replaceAll('""','"')]];
   restored++;
  }
 }
 input.recalculate();
 await (await SpreadsheetFile.exportXlsx(input)).save(path);
 console.log(`Tidied notes and restored ${restored} readable URLs`);
 process.exit(0);
}
if(old.length!==562 || old[0][1]!=='College_Name')throw Error('Unexpected input layout');
const entries=old.slice(1).filter(r=>r[1]);
if(entries.length!==561)throw Error(`Expected 561 records; found ${entries.length}`);

const categories=[
 'General Degree (Government)','General Degree (Provincialised)','Engineering',
 'Polytechnic','ITI','Medical','Dental','Nursing','Paramedical','Pharmacy',
 'AYUSH','Agriculture & Allied','Teacher Education','Law','Art & Culture'
];
const rank=new Map(categories.map((s,i)=>[s,i]));
const districtNames={
 'Kamrup (M)':'Kamrup Metropolitan','Kamrup (R )':'Kamrup Rural',
 'BTR (Kokrajhar)':'Kokrajhar','BTR (KOKRAJHAR)':'Kokrajhar',
 'BTR (Baksa)':'Baksa','South Salmara':'South Salmara-Mankachar'
};
const normalized=entries.map(r=>{
 const x=[...r];
 x[4]=districtNames[x[4]]??x[4];
 if(typeof x[7]==='string' && /^\d{4}$/.test(x[7]))x[7]=Number(x[7]);
 return x;
});
normalized.sort((a,b)=>(rank.get(a[2])??99)-(rank.get(b[2])??99)
 ||String(a[4]).localeCompare(String(b[4]),'en',{sensitivity:'base'})
 ||String(a[1]).localeCompare(String(b[1]),'en',{sensitivity:'base'}));

const headers=[
 'No.','College / Institute','District','Category','Courses / Streams',
 'Departments / ITI Trades','Department Source URL','Department Verification',
 'University / Board','Governing Body / Directorate','Location','PIN Code',
 'Established','Principal / Head','Website URL','Official Email',
 'Accreditation','Institution Type','Highlights'
];
const data=normalized.map((r,i)=>[
 i+1,r[1],r[4],r[2],r[3],r[16],r[17],r[18],r[12],r[11],
 r[5],r[6],r[7],r[8],r[9],r[10],r[13],r[15],r[14]
]);
const wb=Workbook.create();
const sh=wb.worksheets.add('Assam Public Institutions');
sh.showGridLines=false;
sh.tabColor='#174A76';
sh.getRange('A1:S562').values=[headers,...data];
sh.getRange('A1:S562').format.font={name:'Aptos',size:10,color:'#243447'};
sh.getRange('A1:S1').format={
 fill:'#174A76',font:{name:'Aptos Display',size:11,bold:true,color:'#FFFFFF'},
 verticalAlignment:'center',wrapText:true
};
sh.getRange('A1:S1').format.rowHeight=38;
sh.getRange('A2:S562').format.rowHeight=48;
sh.getRange('A2:S562').format.verticalAlignment='center';
sh.getRange('F2:F562').format.wrapText=true;
sh.getRange('H2:H562').format.wrapText=true;
sh.getRange('A2:A562').format.numberFormat='0';
sh.getRange('L2:L562').format.numberFormat='000000';
sh.getRange('M2:M562').format.numberFormat='0';

const widths={A:7,B:43,C:23,D:30,E:31,F:68,G:49,H:65,I:37,J:39,
 K:23,L:13,M:15,N:26,O:44,P:37,Q:26,R:32,S:62};
for(const [col,width] of Object.entries(widths))sh.getRange(`${col}1:${col}562`).format.columnWidth=width;
sh.getRange('G2:G562').format.font={name:'Aptos',size:10,color:'#1767A6'};
sh.getRange('O2:O562').format.font={name:'Aptos',size:10,color:'#1767A6'};
sh.getRange('H2:H562').format.font={name:'Aptos',size:10,color:'#5A6674'};

const table=sh.tables.add('A1:S562',true,'AssamInstitutions');
table.style='TableStyleMedium2';
table.showFilterButton=true;
for(let i=0;i<data.length;i++)if(!data[i][5]){
 sh.getRange(`F${i+2}`).format.fill='#FFF1DA';
}
sh.freezePanes.freezeRows(1);
wb.recalculate();
const check=await wb.inspect({kind:'table',range:'Assam Public Institutions!A1:H8',include:'values',tableMaxRows:8,tableMaxCols:8,tableMaxCellChars:72});
console.log(check.ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(path);
console.log(JSON.stringify({records:data.length,missingDepartments:data.filter(r=>!r[5]).length,sheet:sh.name}));
