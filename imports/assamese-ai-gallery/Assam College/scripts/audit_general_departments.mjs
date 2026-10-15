import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const root = '/home/angsuman/extra_spac/Assam College';
const input = root + '/outputs/medical_departments_20261001/Assam_Colleges_Departments_Trades_and_Medical.xlsx';
const output = root + '/Assam_Colleges_Complete_Directory.xlsx';
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(input));
const sh = wb.worksheets.getItemAt(0);
const patches = [
  [49, 'Assamese; Botany; Chemistry; Education; English; Physics; Political Science; Zoology', 'https://www.arba.ac.in/ug.php', 'UG degree subjects on institution site; Academy-wide teaching staff not used'],
  [43, 'Bengali; Botany; Chemistry; Economics; Education; English; History; Mathematics; Physics; Political Science; Sociology; Statistics; Zoology', 'https://webbackend.pduameraligool.ac.in/src/uploads/COLLEGE_DOWNLOADS/Prospectus_2024_25_PW82qnSL3R.pdf', '13 department profiles in official 2024–25 prospectus'],
  [68, 'Mass Communication', 'https://chaiduarcollege.ac.in/teachingstaff.php'],
  [72, 'Computer Science and Information Technology', 'https://www.birjhoramahavidyalaya.in/', 'Official department navigation; existing entries retained'],
  [73, 'Assamese; Bengali; Bodo; Economics; Education; English; Hindi; History; Philosophy; Political Science', 'https://bongaigaoncollege.ac.in/doc/notice/OhF9rHkxRe0Mq9swnNXa.pdf', 'Ten named major subjects in official 2025 admission notice; department structure may include more'],
  [79, 'Bengali; Economics; Education; English; Environmental Studies; Hindi; History; Manipuri; Philosophy; Political Science; Sociology', 'https://nehrucollege.org.in/uploaded-files/3dbe8e73df1f5251041ca4d7295d3f9b.pdf', 'Named faculties in official staff directory; vacant Hmar faculty excluded'],
  [80, 'Bengali; Commerce; Economics; Education; English; History; Manipuri; Philosophy; Political Science', 'https://www.rmcollege.org/bengdept.htm\nhttps://www.rmcollege.org/manipudept.htm\nhttps://www.rmcollege.org/IQAC-Archive/FINAL%20SUPPLEMENTARY%20SSR.pdf', 'Official department pages and college SSR; verify whether other departments exist'],
  [93, 'Assamese; Arabic; Bengali; Bodo; Botany; Chemistry; Computer Science and Information Technology; Economics; Education; English; Geography; History; Mathematics; Philosophy; Physics; Political Science; Sanskrit; Statistics; Zoology; Vocational Studies', 'https://www.mangaldaicollege.org/upload/FINAL_IDP_MC-22-31.pdf', '20 departments in official institutional development plan, faculty strength table'],
  [102, 'Assamese; Botany; Chemistry; Economics; Education; English; History; Mathematics; Philosophy; Physics; Political Science; Sociology; Zoology', 'https://silapatharcollege.edu.in/arts.php\nhttps://silapatharcollege.edu.in/science.php', 'Arts and Science departments on official site; Logic & Philosophy normalized to Philosophy'],
  [105, 'Arabic; Assamese; Bengali; Biotechnology; Botany; Chemistry; Commerce; Computer Science and BCA; Economics; Education; English; Hindi; History; Mathematics; Philosophy; Physics; Political Science; Sanskrit; Statistics; Zoology', 'https://www.bncollege.co.in/pdf/IQAC/prospectus/Prospectus-2016-17.pdf', '20 departments in official prospectus campus directory; historical source'],
  [107, 'Assamese; Travel and Tourism Management', 'https://chilaraicollege.com/department.php?d_id=1'],
  [115, 'Computer Science', 'https://dhskcommercecollege.edu.in/teachingstaff.php'],
  [126, 'Assamese; Bengali; Economics; Education; English; History; Political Science; Sociology', 'https://maibangdegreecollege.edu.in/upload/prospectus/1746446352.pdf', 'Eight department headings in official 2025–26 prospectus; Assamese teaching post shown vacant'],
  [118, 'Assamese; Bengali; Botany; Chemistry; Computer Science; Economics; Education; English; Geography; Hindi; History; Home Science/Community Science; Mathematics; Philosophy; Physics; Political Science; Sanskrit; Sociology; Statistics; Zoology', 'https://mdkgcollege.edu.in/departments/', '20 departments on current official index'],
  [127, 'Assamese; Bodo; Economics; Education; English; Geography; History; Political Science', 'https://bikalicollege.org/departments/arts/'],
  [141, 'Bengali; Commerce; Economics; Education; English; History; Persian; Philosophy; Political Science', 'https://alccollege.ac.in/', 'Official current site lists eight Arts departments and Commerce'],
  [158, 'Botany; Chemistry; Geography; Mathematics; Physics; Statistics; Zoology; Information Technology; Business Administration', 'https://www.bborooahcollege.ac.in/science.php\nhttps://www.bborooahcollege.ac.in/upload/notice/1747377791.pdf'],
  [165, 'Assamese; Bengali; Community Science (Home Science); Economics; Education; English; Hindi; History; Philosophy; Political Science', 'https://krbgirlscollege.ac.in/PDFs/KRB%20Giirls%20College%20Prospectus%202025-26.pdf', 'Ten academic departments named in official 2025–26 prospectus'],
  [166, 'Accountancy; Assamese; Commerce; Economics; Education; English; Environmental Studies; Finance; Geography; Hindi; History; Information Technology; Management; Philosophy; Political Science; Psychology', 'https://www.khscollege.com/faculty.htm', 'Current official faculty page lists 15 numbered departments plus self-financed Commerce faculty'],
  [172, 'Accountancy; Assamese; Bengali; Computer Science; Economics; Education; English; Finance; Hindi; History; Management; Mathematics; Performing Arts; Political Science', 'https://www.rgbaruahcollege.ac.in/departments.php', '14 departments on current official index'],
  [160, 'Anthropology; Assamese; Biotechnology; Botany; Chemistry; Computer Science; Eco-Restoration; Economics; Education; English; Environmental Management; Folklore; Geography; Geology; Hindi; History; Linguistics; Mathematics; Physics; Political Science; Statistics; Zoology', 'https://dimoriacollege.ac.in/Academic-All-Departments.php', 'Official department index; Library excluded'],
  [179, 'Psychology', 'https://dkcollegemirza.com/teachingstaff.php'],
  [178, 'Accountancy; Assamese; Banking; BMST; Economics; Education; English; Hindi; History; IT & Computer Application; Management; Philosophy; Political Science', 'https://chhaygaoncollege.in/department.php', '13 named departments on current official index; directory website uses a different spelling/domain'],
  [182, 'Arabic; Assamese; Bengali; Bodo; Botany; Business Administration; Chemistry; Commerce; Computer Applications; Economics; Education; English; Geography; History; Information Technology; Mathematics; Philosophy; Physical Education; Physics; Political Science; Sanskrit; Vocational Studies; Zoology', 'https://rangiacollege.ac.in/images/AQAR%202020-21/2021.pdf', '23 departments listed in official AISHE return; historical source'],
  [185, 'Assamese; Botany; Chemistry; Computer Science & Application; Economics; Education; English; Folklore; Geography; History; Linguistics; Mathematics; Medical Laboratory Technology (B.Voc); Philosophy; Physics; Political Science; Zoology', 'https://surendascollege.co.in/', 'Current official Arts, Science and Vocational department navigation'],
  [190, 'Arabic; Bengali; Botany and Biotechnology; Chemistry; Commerce; Computer Science and Application; Ecology and Environmental Science; Economics; English; Geology; History; Mathematics; Philosophy; Physics; Political Science; Sanskrit; Statistics; Zoology', 'https://iqac.karimganjcollege.ac.in/prospectus/Prospectus_2024-25.pdf', '18 named departments in official 2024–25 prospectus'],
  [192, 'Arabic; Bengali; Botany; Chemistry; Economics; English; History; Manipuri; Mathematics; Philosophy; Physics; Political Science; Zoology', 'https://pkdc.ac.in/portal/webadmin/secured/upload/AQAR/1738830737_1.1.1%20Final%20C.pdf', '13 departments named in official supporting document'],
  [202, 'Home Science', 'https://bihpuriacollege.edu.in/teaching-staff/'],
  [203, 'Anthropology; Assamese; Botany; Chemistry; Computer Science; Economics; Education; English; History; Mathematics; Philosophy; Physics; Political Science; Sociology; Zoology', 'https://dhakuakhanacollege.ac.in/arts.php\nhttps://dhakuakhanacollege.ac.in/science.php\nhttps://dhakuakhanacollege.ac.in/new1111/programmes.php', 'Named on official department pages and programme outcomes; official overview mentions 16 departments, so one may remain unidentified'],
  [206, 'Accountancy; Assamese; Banking; Commerce; Commercial Arithmetic; Commercial Law; Economics; Education; English; Hindi; Management; Mathematics; Political Science; Sociology; Statistics', 'https://cdn.lccollege.edu.in/prospectus/1776953651605_Final_Prospectus-_2026.pdf', '15 teaching departments explicitly listed in official 2026 prospectus; directory website URL points to another college'],
  [219, 'Acting (B.Voc); Assamese; Bengali; Biotechnology; Bodo; Botany; Chemistry; Commerce; Computer; Economics; Education; English; Geography; Hindi; History; Mathematics; Physics; Political Science; Retail Management (B.Voc); Tourism; Zoology', 'https://jagiroadcollegelive.co.in/upload/assests/prospectus.pdf', '21 academic department headings in official prospectus; Sports excluded'],
  [228, 'Assamese; Botany; Chemistry; Economics; Education; English; Geography; History; Mathematics; Physics; Political Science; Sociology; Statistics; Zoology', 'https://kaliaborcollege.ac.in/teachingstaff.php'],
  [231, 'Psychology', 'https://www.nonoicollege.in/departments.php'],
  [239, 'Travel and Tourism Management', 'https://mncbm.ac.in/travel.php'],
  [240, 'Physical Education', 'https://nalbaricollege.ac.in/teachingstaff.php'],
  [241, 'Accountancy; Assamese; B.Voc. IT Software Development; B.Voc. Retail Management & IT; Commerce (Finance); Economics; Education; English; Information Technology; Management; Maths & Statistics; Political Science; Sociology', 'https://www.nccnalbari.in/pdf/2024/DCF_II_2022-2023.pdf', '13 departments/centres in college AISHE return; 2022–23 source'],
  [250, 'Electronics', 'https://www.sibsagaruniversity.ac.in/teachingstaff.php'],
  [253, 'Psychology', 'https://darrangcollege.ac.in/teachingstaff.php'],
  [254, 'Political Science', 'https://lokdcollege.ac.in/arts-stream/'],
  [256, 'Travel and Tourism Management', 'https://tezpurcollege.com/department.php?r=10'],
  [196, 'Accountancy; Banking; Business Administration; Commerce; Economics; English; Mathematics; MIL; Management', 'https://commercecollege.ac.in/doc/71e02eCQayqu6L86FtoA.pdf\nhttps://www.commercecollege.ac.in/doc/Q7tXTSU1dymvQxhrcaYb.pdf', 'Academic departments named in official prospectus faculty section; historical source'],
  [262, 'Assamese; Bengali; Botany; Chemistry; Commerce; Computer Science; Economics; Education; English; Hindi; History; Mathematics; Physics; Political Science; Sociology; Statistics; Zoology', 'https://www.doomdoomacollege.in/page/arts\nhttps://www.doomdoomacollege.in/page/science\nhttps://doomdoomacollege.in/api/staff/fetch_staff', 'Arts and Science department pages plus official faculty list (Sociology, Statistics, Commerce)'],
  [267, 'Assamese; Bengali; Commerce; Computer; Economics; Education; English; Hindi; Political Science; Sociology', 'https://tinsukiacommercecollege.edu.in/staff/', 'Academic fields named in current official teaching staff list'],
  [273, 'Accountancy; Finance; Management', 'https://www.tanglacollege.ac.in/commerce-stream/'],
];
let changed = 0;
for (const [row, names, url, note] of patches) {
  const old = String(sh.getRange(`Q${row}`).values[0][0] ?? '');
  const combined = [...new Set([...old.split(';').map(x => x.trim()), ...names.split(';').map(x => x.trim())].filter(Boolean))].sort((a,b) => a.localeCompare(b)).join('; ');
  const oldUrl = String(sh.getRange(`R${row}`).values[0][0] ?? '').trim();
  const sourceUrls = [...new Set([...oldUrl.split(/\s+/), ...url.split(/\s+/)].filter(Boolean))].join('\n');
  sh.getRange(`Q${row}`).values = [[combined]];
  sh.getRange(`R${row}`).values = [[sourceUrls]];
  sh.getRange(`S${row}`).values = [[note ?? 'Additional departments confirmed on official institution page; previous names retained']];
  sh.getRange(`Q${row}:S${row}`).format.wrapText = true;
  sh.getRange(`Q${row}`).format.rowHeight = Math.max(42, Math.ceil(combined.length / 85) * 21);
  changed++;
}
const audit = JSON.parse(await fs.readFile('/tmp/assam_general_audit.json', 'utf8'));
let unverified = 0;
for (const { row, status } of audit) {
  if (String(sh.getRange(`Q${row}`).values[0][0] ?? '').trim()) continue;
  sh.getRange(`S${row}`).values = [[status === 'no-site' ? 'No institution website in directory; department list unverified' : 'Department list not verified in this audit; follow-up needed']];
  unverified++;
}
sh.getRange('S191').values = [['Directory website currently displays unrelated gambling content; original college department list unavailable']];
sh.getRange('R:R').format.columnWidth = 46;
sh.getRange('S:S').format.columnWidth = 47;
const affiliationOrder = 'https://www.bhattadevuniversity.ac.in/docs/2025/Affiliation%20Govt.%20Order%20-840-2.pdf';
const affiliationUpdates = [
  [11, 'Assam Veterinary and Fishery University', 'https://avfu.ac.in/colleges/', 'Constituent college of AVFU'],
  [12, 'Assam Veterinary and Fishery University', 'https://avfu.ac.in/colleges/', 'Constituent college of AVFU'],
  [13, 'Assam Veterinary and Fishery University', 'https://avfu.ac.in/colleges/', 'Constituent college of AVFU'],
  [30, 'Madhabdev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [49, 'Bodoland University', 'https://www.arba.ac.in/upload/notice/1747551891.pdf', 'College 2025–26 prospectus confirms Bodoland University'],
  [57, 'Bhattadev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [58, 'Bhattadev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [59, 'Bhattadev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [60, 'Bhattadev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [63, 'Bhattadev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [64, 'Bhattadev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [65, 'Bhattadev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [66, 'Madhabdev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [68, 'Madhabdev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [69, 'Madhabdev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [72, 'Bongaigaon University', 'https://bongaigaonuniversity.ac.in/about.php', 'Constituent college and Science Campus of Bongaigaon University from March 2026'],
  [73, 'Bongaigaon University', 'https://www.bongaigaonuniversity.ac.in/about.php', 'Former Bongaigaon College upgraded to a state university'],
  [145, 'Rabindranath Tagore University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [146, 'Rabindranath Tagore University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [147, 'Rabindranath Tagore University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [202, 'Madhabdev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [208, 'Madhabdev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [210, 'Madhabdev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [211, 'Madhabdev University', affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [232, 'Nagaon University', 'https://www.nagaonuniversity.ac.in/', 'Former Nowgong College (Autonomous) upgraded to a state university'],
  [250, 'Sibsagar University', 'https://sibsagaruniversity.ac.in/Prospectus_Sibsagar_University%202025-26_Latest.pdf', 'Former Sibsagar College (Autonomous) upgraded to a state university'],
];
sh.getRange('V1:W1').values = [['Affiliation source URL', 'Affiliation verification']];
for (const [row, university, source, note] of affiliationUpdates) {
  sh.getRange(`M${row}`).values = [[university]];
  sh.getRange(`V${row}:W${row}`).values = [[source, note]];
  sh.getRange(`M${row}:W${row}`).format.wrapText = true;
  sh.getRange(`M${row}`).format.rowHeight = 70;
  const accred = String(sh.getRange(`N${row}`).values[0][0] ?? '');
  if (accred.endsWith('University Affiliated')) sh.getRange(`N${row}`).values = [['NAAC grade not verified']];
}
sh.getRange('V50:W50').values = [[affiliationOrder, 'Bhattadev University confirmed in government order']];
sh.getRange('V67:W67').values = [['https://biswanathcollege.in/', 'Gauhati University confirmed on current college site']];
sh.getRange('V204:W204').values = [['https://www.harhicollege.org/rti.php', 'Dibrugarh University retained; Harhi is absent from the Madhabdev government order']];
const addedColleges = [
  [376, 'Chatia College', 'General Degree (Provincialised)', 'Arts / BA', 'Biswanath', 'Sootea', 784175, 1982, 'Dr. Swapan Kumar Kalita', 'https://chatiacollege.com/', 'chatiacollege@gmail.com', 'Directorate of Higher Education, Assam', 'Madhabdev University', 'NAAC B', 'Arts college in Sootea', 'Provincialised State College', 'Assamese; Bodo; Economics; Education; English; History; Nepali; Political Science; Sanskrit', 'https://chatiacollege.com/', 'Nine departments on official department navigation', null, null, affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [377, 'Kherajkhat College', 'General Degree (Provincialised)', 'Arts, Science / BA, B.Sc', 'Lakhimpur', 'Deotola', 787033, 1982, 'Dr. Mridul Buragohain', 'https://kherajkhatcollege.co.in/', 'kherajkhatcollege7@gmail.com', 'Directorate of Higher Education, Assam', 'Madhabdev University', 'NAAC accredited; grade not verified', 'Arts and Science college; Model Degree College', 'Provincialised State College', 'Assamese; Botany; Chemistry; Economics; Education; English; Geography; Hindi; History; Mathematics; Philosophy; Physics; Political Science; Sociology; Zoology', 'https://kherajkhatcollege.co.in/uploads/gallery/media/KKC%20Prospectus%202025%20%281%29.pdf', 'Names from official prospectus department/faculty and UG subject sections', null, null, affiliationOrder, 'Government affiliation order, effective 2024–25'],
  [378, 'Pub Dikrong College', 'General Degree (Provincialised)', 'Arts / BA', 'Lakhimpur', 'Lahalial', 784161, 1991, 'Dr. Prasanta Neog', 'https://pubdikrongcollege.in/', 'prasantaprincipalpdc@gmail.com', 'Directorate of Higher Education, Assam', 'Madhabdev University', 'NAAC B+', 'Arts college in Lahalial', 'Provincialised State College', null, null, 'Department list unverified; website lists subjects but does not confirm department structure', null, null, affiliationOrder, 'Government affiliation order, effective 2024–25; 2025 college notice confirms Madhabdev classes'],
];
sh.getRange('A377:W379').values = addedColleges;
sh.getRange('Q377:W379').format.wrapText = true;
sh.getRange('A377:W379').format.rowHeight = 63;
sh.getRange('M:M').format.columnWidth = 38;
sh.getRange('N:N').format.columnWidth = 29;
sh.getRange('V:V').format.columnWidth = 54;
sh.getRange('W:W').format.columnWidth = 55;
wb.recalculate();
await (await SpreadsheetFile.exportXlsx(wb)).save(output);
console.log(JSON.stringify({ output, departmentRowsChanged: changed, affiliationsCorrected: affiliationUpdates.length, collegesAdded: addedColleges.length, unverifiedDepartmentRows: unverified + 1 }));
