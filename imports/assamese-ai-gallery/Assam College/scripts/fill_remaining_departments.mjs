import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const root = '/home/angsuman/extra_spac/Assam College';
const path = `${root}/Assam_Colleges_Complete_Directory.xlsx`;
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sh = wb.worksheets.getItemAt(0);
const patches = [];
const add = (row, names, url, note = 'Named departments on official institution website') => patches.push([row, names, url, note]);
const aau = 'https://www.aau.ac.in/assets/files/prospectus/AAU-Information-Bulletin-2026-2027.pdf';
add(6, 'Agricultural Economics; Extension Education; Horticulture; Agronomy; Plant Physiology; Animal Husbandry & Dairying; Plant Breeding & Genetics; Plant Pathology; Biochemistry; Entomology; Nematology; Soil Science; Agricultural Statistics; Agricultural Engineering; Agricultural Meteorology; Tea Husbandry & Technology', 'https://aau.ac.in/faculty/profile/Dr-Bikram-Borkotoki/142', 'Department navigation on AAU faculty profile');
add(7, 'Agricultural Economics; Agricultural Engineering; Agricultural Meteorology; Agricultural Statistics; Agronomy; Animal Husbandry & Dairying; Biochemistry; Entomology; Extension Education; Horticulture; Molecular Biology and Biotechnology; Nematology; Plant Breeding & Genetics; Plant Pathology; Plant Physiology; Soil Science', 'https://www.aau.ac.in/department/department_details/55', 'AAU institution department index');
add(8, 'Molecular Biology and Biotechnology; Agricultural Economics; Agricultural Meteorology; Agricultural Statistics; Agronomy; Biochemistry; Plant Physiology; Entomology; Extension Education; Horticulture; Nematology; Plant Breeding & Genetics; Plant Pathology; Sericulture; Soil Science; Tea Husbandry & Technology; Animal Husbandry & Dairying; Agricultural Engineering', 'https://www.aau.ac.in/faculty/profile/Dr-Kishore-Kumar-Sharma/60', 'Department navigation on AAU faculty profile; programmes excluded');
add(9, 'Food Science and Nutrition; Human Development and Family Studies; Family Resource Management and Consumer Science; Textiles and Apparel Designing; Extension Education and Communication Management', 'https://www.aau.ac.in/ccs_alumni', 'Five named departments on AAU college page');
add(10, 'Agriculture & Allied Subjects; Basic Sciences & Humanities; Cocoon Crop Production; Host Plant Production; Sericulture Crop Improvement; Silk Product Science', aau, 'Named departments in AAU information bulletin; six verified');
add(11, 'Animal Biotechnology; Anatomy & Histology; Animal Genetics & Breeding; Animal Nutrition; Animal Reproduction, Gynaecology & Obstetrics; Extension Education; Livestock Production & Management; Livestock Products Technology; Poultry Science; Veterinary Biochemistry; Veterinary Clinical Medicine, Ethics & Jurisprudence; Veterinary Epidemiology & Preventive Medicine; Veterinary Microbiology; Veterinary Parasitology; Veterinary Pathology; Veterinary Pharmacology & Toxicology; Veterinary Physiology; Veterinary Public Health; Veterinary Surgery & Radiology', 'https://www.avfu.ac.in/cvsc/', 'AVFU department index; farm complexes excluded');
add(12, 'Anatomy & Histology; Animal Genetics & Breeding; Animal Nutrition; Animal Reproduction, Gynaecology & Obstetrics; Extension Education; Livestock Production & Management; Livestock Products Technology; Veterinary Physiology and Biochemistry; Veterinary Clinical Medicine, Ethics & Jurisprudence; Veterinary Epidemiology & Preventive Medicine; Veterinary Microbiology; Veterinary Parasitology; Veterinary Pathology; Veterinary Pharmacology & Toxicology; Veterinary Public Health; Veterinary Surgery & Radiology', 'https://www.avfu.ac.in/lcvsc/', 'AVFU department index; farm/clinical complexes excluded');
add(13, 'Aquaculture; Aquatic Animal Health Management; Aquatic Environment Management; Fish Processing Technology; Fisheries Engineering; Fishery Extension, Economics & Statistics; Fishery Resource Management', 'https://www.avfu.ac.in/cfsc/', 'Seven departments on AVFU college page');
add(14, 'Basic Science; Floriculture & Landscape Architecture; Fruit Science; Natural Resource Management; Plant Protection; Post-Harvest Technology; Social Science; Vegetable Science', aau, 'Eight departments in AAU information bulletin');
add(78, 'Arabic; Bengali; Botany; Chemistry; Commerce; Economics; English; Geology; Hindi; History; Manipuri; Mathematics; Persian; Philosophy; Physics; Political Science; Zoology', 'https://www.mcdcollege.org.in/facultyarts.htm\nhttps://www.mcdcollege.org.in/facultysc.htm\nhttps://www.mcdcollege.org.in/facultycomm.htm', 'Department-wise faculty pages across Arts, Science and Commerce; previous directory stream description is incomplete');
add(96, 'Assamese; Economics; Education; English; Hindi; History; Mathematics; Philosophy; Political Science; Sociology', 'https://dhemajicitycollege.in/tstaff', 'Official teaching staff page of Dhemaji City College, formerly Dhemaji Girls College');
add(204, 'Anthropology; Assamese; Economics; Education; English; Hindi; History; Mathematics; Philosophy; Political Science; Sociology', 'https://harhicollege.org/rti.php', 'Official list of teaching departments; MIL entry is an offered language grouping and omitted');
add(208, 'Assamese; English; Economics; Education; Political Science; Sociology; History; Philosophy; Hindi', 'https://lalukcollege.in/courses-and-subjects/', 'Official college page explicitly identifies nine teaching departments');
add(101, 'Assamese; Anthropology; Economics; Education; English; Geography; Hindi; History; Mathematics; Philosophy; Political Science; Sociology', 'https://paschimdhemajicollege.org/', 'Twelve disciplines on official college navigation; Assamese has a dedicated department page');
add(193, 'Bengali; English; History; Economics; Philosophy; Political Science; Computer Science; Sanskrit; Commerce; Mathematics; Education; Mass Communication', 'https://rabindrasadangirlscollege.in/Dept.aspx', 'Twelve departments on official college department index');
add(194, 'English; Bengali; Sanskrit; Hindi; Economics; Political Science; History; Sociology; Philosophy; Physics; Chemistry; Mathematics', 'https://www.rknagarcollege.org/IQAC/SSR%206.5.2.pdf', 'Academic audit names nine Arts and three Science departments');
add(268, 'Assamese; Bengali; Economics; Education; English; Hindi; History; Mathematics; Philosophy; Political Science; Sanskrit; Commerce; Sociology; Community Science; Computer Science', 'https://wcttsk.ac.in/uploads/files/WCT%20Prospectus%202025-2026%20Final%20-%20converted.pdf', 'Current college prospectus, teaching and self-finance department sections');
add(23, 'Civil Engineering; Chemical Engineering; Mechanical Engineering', 'https://gecassam.ac.in/', 'Official college department navigation and 2026 undergraduate branches');
add(47, 'Assamese; Economics; Education; English; History; Mathematics; Political Science; Sociology', 'https://brmgmc.ac.in/', 'Eight named departments on official college home page');
add(197, 'Hindi; Folklore; Bodo; English; Education; Bengali; Economics; Tourism and Travel Management; Assamese; History; Political Science', 'https://fakiragramcollege.ac.in/category/department/\nhttps://www.fakiragramcollege.ac.in/Academics/CourseOutcomes/OutCome', 'Official department index and course outcomes; political science added from latter page');
add(277, 'Assamese; Hindi; Bodo; English; Education; Logic & Philosophy; Economics; History; Political Science; Geography; Physical Education', 'https://webbackend.tnc.ac.in/src/uploads/COLLEGE_ACADEMIC_NOTICE/Prospectus_2025-26%20Thong%20Nokbe%20College_w3YeOmw65x.pdf', 'Eleven explicit department headings in official 2025–26 prospectus; science faculty subjects excluded');
add(16, 'Sculpture; Painting; Graphic Art (Printmaking); Applied Art; History of Art; Crafts; English; MIL (Assamese, Hindi, Sanskrit)', 'https://govtcollegeofart.ac.in/departments.php', 'Eight named departments on official college department index');
add(81, 'English; Economics; Political Science; Bengali; Manipuri; Hindi; History; Commerce', 'https://www.smdevcollege.ac.in/portal/webadmin/secured/upload/notice/Prospectus-2025-26.pdf', 'Eight department headings in official 2025–26 prospectus');
add(82, 'Bengali; English; Economics; Education; Hindi; History; Journalism & Mass Communication; Manipuri; Philosophy; Political Science; Sanskrit; Computer Science; Environmental Education; Library Science; Commerce', 'https://wcsilchar.ac.in/welcome', 'Fifteen academic entries in current official department menu; home page 13-department count appears outdated; NCC and NSS excluded');
add(110, 'Arabic; Assamese; Bengali; Economics; Education; English; History; Philosophy; Political Science; Sanskrit', 'https://halakuracollege.ac.in/wp-content/uploads/2024/03/COURSE-OUTCOME-OF-ALL-DEPARTMENT.pdf', 'College course outcomes document has department headings; ten departments corroborated by 2025-26 admission notice');
add(151, 'Assamese; Bengali; Economics; Education; English; Geography; History; Philosophy; Political Science; Sanskrit; Physics; Chemistry; Zoology; Botany; Mathematics', 'https://oldweb.dibru.ac.in/wp-content/uploads/2022/09/Final-Electoral-Roll-2022-Website.pdf', 'Dibrugarh University 2022 teacher roll, pages 46-47, names these departments');
add(98, 'Assamese; Economics; Education; English; History; Philosophy; Political Science; Sociology', 'https://oldweb.dibru.ac.in/wp-content/uploads/2022/09/Final-Electoral-Roll-2022-Website.pdf', 'Dibrugarh University 2022 teacher roll, page 88, has staff in these eight departments');
add(263, 'Assamese; Economics; Education; English; Hindi; History; Philosophy; Political Science; Sociology', 'https://oldweb.dibru.ac.in/wp-content/uploads/2022/09/Final-Electoral-Roll-2022-Website.pdf', 'Dibrugarh University 2022 teacher roll, page 7, has staff in these nine departments');
add(379, 'Assamese; Education; English; Political Science; Sociology', 'https://directorateofhighereducation.assam.gov.in/sites/default/files/swf_utility_folder/departments/dhe_medhassu_in_oid_4/menu/document/5_0.pdf\nhttps://www.unom.ac.in/asc/uploads/2014-15/orientation-programmes-14-15.pdf', 'Verified departments from Assam higher education staff list and university training roster; partial historical list, current full department index unavailable');
const scte = 'https://scteassam.com/poly_seats.php';
const poly = {
340:'Civil Engineering; Mechanical Engineering; Chemical Engineering',
341:'Civil Engineering; Mechanical Engineering; Biomedical Engineering',
342:'Civil Engineering; Electrical Engineering; Mechanical (Automobile) Engineering',
343:'Civil Engineering; Electrical Engineering; Mechanical Engineering; Electronics & Telecommunication Engineering',
344:'Civil Engineering; Agricultural Engineering; Electrical Engineering',
346:'Civil Engineering; Electrical Engineering; Mechanical Engineering',
348:'Civil Engineering; Mechanical Engineering; Electrical Engineering',
349:'Civil Engineering; Mechanical Engineering; Biomedical Engineering',
350:'Textile Design; Electronics & Telecommunication Engineering',
351:'Civil Engineering; Computer Science & Engineering; Electrical Engineering',
352:'Civil Engineering; Electrical Engineering; Mechanical Engineering; Electronics & Telecommunication Engineering; Mechanical (Automobile) Engineering; Instrumentation Technology; Agricultural Engineering',
353:'Civil Engineering; Electrical Engineering; Mechanical Engineering; Electronics & Telecommunication Engineering; Computer Engineering; Chemical Engineering',
354:'Textile Technology; Fashion Technology; Garment Technology',
355:'Civil Engineering; Computer Engineering; Architectural Assistantship; Modern Office Management',
356:'Electrical Engineering; Electronics & Telecommunication Engineering; Mechanical (Automobile) Engineering',
357:'Civil Engineering',
358:'Civil Engineering; Electrical Engineering; Industrial & Production Engineering',
360:'Civil Engineering; Electrical Engineering; Medical Electronics',
361:'Civil Engineering; Electrical Engineering; Mechanical Engineering; Computer Engineering',
362:'Electrical Engineering; Computer Science & Engineering; Printing Technology',
363:'Civil Engineering; Mechanical Engineering; Electrical Engineering',
364:'Civil Engineering; Mechanical Engineering; Electrical Engineering',
365:'Civil Engineering; Mechanical Engineering; Mining Engineering',
366:'Civil Engineering; Mechanical Engineering; Food Processing Engineering'
};
for (const [row, names] of Object.entries(poly)) add(+row, names, +row === 344 ? 'https://chirangpolytechnic.ac.in/about-the-departments/' : scte, +row === 344 ? 'Three teaching departments on official college page' : 'Official SCTE Assam branch list; engineering branches used as teaching disciplines (department names not independently confirmed)');

for (const [row, names, url, note] of patches) {
  const cell = sh.getRange(`Q${row}`);
  const normalized = names.split(';').map(x => x.trim()).sort((a,b)=>a.localeCompare(b)).join('; ');
  if (String(cell.values[0][0] ?? '').trim() === normalized) continue;
  if (String(cell.values[0][0] ?? '').trim() && row !== 151) throw new Error(`Refusing to overwrite nonblank Q${row}`);
  cell.values = [[normalized]];
  sh.getRange(`R${row}`).values = [[url]];
  sh.getRange(`S${row}`).values = [[note]];
  sh.getRange(`Q${row}:S${row}`).format.wrapText = true;
  sh.getRange(`Q${row}`).format.rowHeight = Math.max(42, Math.ceil(names.length / 85) * 21);
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path);
console.log(`Updated ${patches.length} previously blank rows in one workbook`);
