// Ahom: the website. Reads window.AHOM (data/site.js) and renders four views by URL hash:
//   #/            the saga, chapter by chapter (#/saga/<chapter> scrolls to one)
//   #/kings       the forty-one reigns on one time axis
//   #/people      everyone in the chronicles, filterable (#/people?g=<group>&q=<text>)
//   #/person/<id> one person
//   #/scenes      the illustrated scenes (#/scenes/<chapter> for one chapter)
//   #/life        everyday life, villages and objects (#/life/<section> for one section)
(() => {
  "use strict";
  const A = window.AHOM;
  const P = A.people;
  const S = Object.fromEntries(A.scenes.map(s => [s.id, s]));
  const ERA = Object.fromEntries(A.eras.map((e, i) => [e.id, Object.assign(e, { n: i })]));
  const FIRST = 1228, LAST = 1838;
  const ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"];
  const view = document.getElementById("view");
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const dash = s => esc(s).replace(/(\d)-(\d)/g, "$1–$2");
  // LIFE: generated scenes of everyday life, kept apart from the chronicle scenes; ids are prefixed "life:" in the viewer
  const LIFE = (A.life && A.life.sections) || [];
  const LI = {};
  LIFE.forEach(sec => sec.items.forEach(it => { it.sec = sec; LI["life:" + it.id] = it; }));
  const illustrated = ids => ids.map(id => S[id]).filter(s => s && s.images.length);

  // ---------- small shared pieces ----------

  function firstLetter(p) {
    const name = p.as || p.name;
    if (window.Intl && Intl.Segmenter) return [...new Intl.Segmenter("as", { granularity: "grapheme" }).segment(name)][0].segment;
    return name[0];
  }

  // a person's small portrait in the keel-arch frame
  function arch(p, cls = "") {
    if (p.face) return `<span class="arch ${cls}"><img src="${esc(p.face)}" alt="" loading="lazy" decoding="async"></span>`;
    return `<span class="arch arch-empty ${cls}" aria-hidden="true"><span ${p.as ? 'lang="as"' : ""}>${esc(firstLetter(p))}</span></span>`;
  }

  const archLine = `<svg class="arch-line" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><path d="M.5,100 L.5,30 C.5,17 28,13 41,5.5 Q50,.3 59,5.5 C72,13 99.5,17 99.5,30 L99.5,100" vector-effect="non-scaling-stroke"/></svg>`;

  function personLink(id) {
    const p = P[id];
    return `<li><a class="who" href="#/person/${p.id}">${arch(p, "arch-s")}<span class="who-name">${esc(p.name)}${p.as ? `<span lang="as">${esc(p.as)}</span>` : ""}</span><span class="who-role">${esc(p.role || p.group)}</span></a></li>`;
  }

  function sceneFigure(s, list, size = "") {
    const pic = s.images[0];
    const media = pic
      ? `<img src="${esc(size ? pic[0] : pic[1])}" ${size ? `srcset="${esc(pic[1])} 420w, ${esc(pic[0])} 1536w" sizes="(min-width: 900px) 60vw, 100vw"` : ""} alt="${esc(s.alt || s.title)}" loading="lazy" decoding="async">`
      : blankFrame();
    return `<figure class="scene ${size} ${pic ? "" : "scene-blank"}">
      <button type="button" class="scene-open" data-scene="${s.id}" data-list="${list.join(",")}" aria-label="Open scene: ${esc(s.title)}${pic ? "" : " (not yet painted)"}">${media}</button>
      <figcaption><span class="scene-date">${dash(s.date || "Undated")}</span>${esc(s.title)}</figcaption>
    </figure>`;
  }

  // the empty frame shown where a scene has not been painted yet
  function blankFrame() {
    return `<span class="blank" aria-hidden="true">${archLine}<span class="blank-text">Not yet painted</span></span>`;
  }

  function bgWord(word, cls = "") {
    return `<p class="bgword ${cls}" lang="as" aria-hidden="true">${esc(word)}</p>`;
  }

  function setTitle(t) { document.title = t ? `${t} | Ahom` : "Ahom: the kingdom on the Brahmaputra"; }

  // ---------- the saga ----------

  function chapter(e, standalone = false) {
    const scenes = illustrated(e.scenes);
    const moments = illustrated(e.moments);
    const list = scenes.map(s => s.id);
    const reel = e.reel ? A.reels.find(r => r.id === e.reel) : null;
    return `<section class="chapter" id="ch-${e.id}" data-era="${e.id}" data-start="${e.start}" data-end="${e.end}" aria-labelledby="h-${e.id}">
      ${bgWord(e.word, "ch-word")}
      <header class="ch-head">
        <span class="ch-num" aria-hidden="true">${ROMAN[e.n]}</span>
        <div>
          <p class="ch-years"><span class="vh">Chapter ${e.n + 1}, </span>${e.start}–${e.end}</p>
          <${standalone ? 'h1' : 'h2'} id="h-${e.id}">${esc(e.title)}</${standalone ? 'h1' : 'h2'}>
          <p class="ch-gloss"><span lang="as">${esc(e.word)}</span>${esc(e.gloss)}</p>
        </div>
      </header>
      <div class="ch-body ${reel ? "has-film" : ""}">
        <div class="ch-lead">${e.lead.map(t => `<p>${esc(t)}</p>`).join("")}</div>
        ${reel ? film(reel, "ch-film") : ""}
      </div>
      <div class="moments">${moments.map((s, i) => sceneFigure(s, list, i === 0 ? "scene-l" : "")).join("")}</div>
      <div class="ch-foot">
        <ul class="who-list" aria-label="People of this chapter">${e.people.map(personLink).join("")}</ul>
        <a class="more" href="#/scenes/${e.id}">All ${e.scenes.length} scenes, ${e.start}–${e.end}</a>
        ${LIFE.filter(sec => sec.era === e.id).map(sec => `<a class="more more-life" href="#/life/${sec.id}">Daily life: ${esc(sec.title)}</a>`).join("")}
      </div>
    </section>`;
  }

  // the hero's still: the scene chosen for the front of the site, a wide torn print with its caption
  function heroStill(id) {
    const s = S[id], pic = s.images[0];
    return `<figure class="hero-still">
      <div class="hero-still-frame"><img src="${esc(pic[0])}" srcset="${esc(pic[1])} 420w, ${esc(pic[0])} 1536w" sizes="(min-width: 860px) 55vw, 100vw" alt="${esc(s.title)}" width="1536" height="1024"></div>
      <figcaption><span>${esc(s.title)}</span><span class="film-year">${dash(s.date || "")}</span></figcaption>
    </figure>`;
  }

  function film(r, cls) {
    return `<figure class="film ${cls}">
      <div class="film-frame">
        <video src="${esc(r.src)}" poster="${esc(r.poster)}" muted loop playsinline controls preload="none" data-auto aria-label="${esc(r.title)}">${(r.tracks || []).map(t=>`<track kind="subtitles" src="${esc(t.src)}" srclang="${t.lang}" label="${esc(t.label)}">`).join('')}</video>
        ${archLine}
      </div>
      <figcaption>
        <span><a href="#/films/${r.id}">${esc(r.title)}</a><span class="film-year">${esc(r.year)}</span></span>
        <button type="button" class="sound" aria-pressed="false">Sound on</button>
      </figcaption>
    </figure>`;
  }

  // the Ahom crest in relief: stacked gilt copies of the traced crest, each a little deeper, tilted in 3D
  function relief() {
    const layers = Array.from({ length: 10 }, (_, i) => `<div class="crest crest--bare relief-layer" style="--i:${i}"></div>`).join("");
    return `<div class="relief-wrap"><div class="relief" role="img" aria-label="The Ahom crest: a gilt beast in a lobed cartouche">${layers}</div></div>`;
  }

  // the scalloped cartouche of the royal seal: a lobed outline with a dotted rim, the word set inside
  function scallop(cx, cy, rx, ry, n, bulge) {
    const pts = Array.from({ length: n }, (_, i) => {
      const a = 2 * Math.PI * i / n;
      return [cx + rx * Math.cos(a), cy + ry * Math.sin(a)];
    });
    const f = v => v.toFixed(1);
    let d = `M${f(pts[0][0])},${f(pts[0][1])}`;
    for (let i = 1; i <= n; i++) {
      const p = pts[i % n];
      d += ` A${f(bulge)},${f(bulge)} 0 0 1 ${f(p[0])},${f(p[1])}`;
    }
    return d + "Z";
  }
  function cartouche(word) {
    const outer = scallop(110, 60, 98, 52, 12, 22), inner = scallop(110, 60, 84, 42, 12, 16);
    return `<div class="cartouche" aria-hidden="true"><svg viewBox="0 0 220 120" focusable="false"><path class="rim" d="${outer}"/><path class="rim rim-in" d="${inner}"/></svg><span lang="as">${esc(word)}</span></div>`;
  }

  // the forty-one reigns laid on one red line, as the chronicle counts them
  function reignLine() {
    const span = LAST - FIRST;
    const pct = y => ((y - FIRST) / span * 100).toFixed(3);
    const marks = A.reigns.map(r => `<i style="left:${pct(r.start)}%;width:${Math.max(0.4, (r.end - r.start) / span * 100).toFixed(3)}%" title="${esc(P[r.id].name)}, ${r.start === r.end ? r.start : `${r.start}–${r.end}`}"></i>`).join("");
    const ticks = [1300, 1400, 1500, 1600, 1700, 1800].map(y => `<span style="left:${pct(y)}%">${y}</span>`).join("");
    return `<section class="reign-line" aria-label="The forty-one reigns, 1228 to 1838">
      <a class="rl-track" href="#/kings" aria-label="All forty-one reigns">${marks}</a>
      <div class="rl-ticks" aria-hidden="true">${ticks}</div>
    </section>`;
  }

  function home() {
    setTitle("");
    const hero = A.reels.find(r => r.id === "02-sukaphaa-crosses-the-patkai");
    const kings = new Set(A.reigns.map(r => r.id)).size;
    view.innerHTML = `
    <section class="hero" aria-labelledby="hero-title">
      <figure class="hero-back" aria-hidden="true"><img src="media/characters/sukaphaa/portrait-2.webp" alt="" width="1024" height="1536" decoding="async"></figure>
      <div class="hero-text">
        ${relief()}
        <p class="hero-as" lang="as">আহোম</p>
        <p class="hero-dates">1228<span aria-hidden="true"></span>1838</p>
        <h1 id="hero-title">Six hundred years on the Brahmaputra</h1>
        <p class="lede">In 1228 a Tai prince named Sukaphaa crossed the Patkai hills into Assam. His line ruled the valley for six centuries, held off the Mughal Empire and fell only to Burmese armies and a British treaty. This is their story, chapter by chapter.</p>
        <div class="actions">
          <a class="btn btn-gold" href="#/saga/foundation">Begin the saga</a>
          <a class="btn" href="#/kings">See all ${A.reigns.length} reigns</a>
        </div>
      </div>
    </section>
    ${reignLine()}
    <div class="saga">
      <nav class="rail" aria-label="Chapters of the saga">
        <p class="rail-year" aria-hidden="true">1228</p>
        <ol>${A.eras.map(e => `<li><a href="#/saga/${e.id}" data-era="${e.id}"><span class="rail-start">${e.start}</span><span class="rail-title">${esc(e.title)}</span></a></li>`).join("")}</ol>
      </nav>
      <div class="chapters">${A.eras.map(e => chapter(e)).join("")}</div>
    </div>
    <section class="films" aria-labelledby="films-title">
      <div class="films-head">
        <h2 id="films-title">${A.reels.length} short films</h2>
        <p>Scenes from the chronicles, from Sukaphaa’s journey to the campaigns of Suhungmung, in historical order. Tap one to play it with sound. <a href="#/films">Browse the complete film library</a>.</p>
      </div>
      <ul class="film-row">${[...A.reels].sort((a,b)=>(S[a.scene].year || 0)-(S[b.scene].year || 0)).map(r => `<li>
        <button type="button" class="reel" data-reel="${r.id}" aria-label="Play ${esc(r.title)}">
          <span class="film-frame"><img src="${esc(r.poster)}" alt="" loading="lazy">${archLine}<span class="play" aria-hidden="true"></span></span>
        </button>
        <p class="reel-title">${esc(r.title)}<span class="film-year">${esc(r.year)}</span></p>
        ${r.line ? `<p class="reel-line"><span lang="as">${esc(r.line)}</span>${esc(r.translation)}</p>` : ""}
      </li>`).join("")}</ul>
    </section>
    <section class="doors" aria-label="The archive">
      <a href="#/kings" class="door">${bgWord("ৰজা", "door-word")}<span class="door-n">${kings}</span><span class="door-t">Kings in ${A.reigns.length} reigns, on one six-hundred-year line</span></a>
      <a href="#/people" class="door">${bgWord("মানুহ", "door-word")}<span class="door-n">${Object.keys(P).length}</span><span class="door-t">People of the chronicles: queens, ministers, generals, rebels and rivals</span></a>
      <a href="#/scenes" class="door">${bgWord("চিত্ৰ", "door-word")}<span class="door-n">${A.scenes.filter(s => s.images.length).length}</span><span class="door-t">Painted scenes, from Mong Mao to the Treaty of Yandabo</span></a>
    </section>`;
    wireSaga();
  }

  function chapterPage(id) {
    const e = ERA[id];
    if (!e) return notFound("That chapter is not in the saga.", "#/", "See all chapters");
    setTitle(e.title);
    view.innerHTML = `<div class="reference"><nav class="crumbs"><a href="#/">All chapters</a></nav>${chapter(e, true)}
      <p><a href="chapters/${e.id}/">Reference page and all chapter scenes</a></p>
      <nav class="pager" aria-label="Read the saga">${e.n ? `<a href="#/saga/${A.eras[e.n-1].id}">← ${esc(A.eras[e.n-1].title)}</a>` : '<span></span>'}${e.n+1 < A.eras.length ? `<a href="#/saga/${A.eras[e.n+1].id}">${esc(A.eras[e.n+1].title)} →</a>` : '<a href="#/">Return to the beginning</a>'}</nav></div>`;
  }

  function sourceList(values) {
    return values?.length ? `<details class="sources"><summary>Sources (${values.length})</summary><ul>${values.map(u => /^https?:/.test(u) ? `<li><a href="${esc(u)}" target="_blank" rel="noopener">${esc(sourceLabel(u))}</a></li>` : `<li>${esc(u)}</li>`).join("")}</ul></details>` : '<p class="quiet">Sources have not yet been catalogued for this scene.</p>';
  }

  function scenePage(id) {
    const s = S[id];
    if (!s) return notFound("That scene is not in the archive.", "#/scenes", "Browse scenes");
    setTitle(s.title);
    const ordered = [...A.scenes].sort((a,b) => (a.year || 0)-(b.year || 0));
    const i = ordered.indexOf(s);
    const reels = A.reels.filter(r => r.scene === id);
    view.innerHTML = `<article class="reference"><nav class="crumbs"><a href="#/scenes/${s.era}">${esc(ERA[s.era].title)}</a></nav><p>${esc(s.date)}</p><h1>${esc(s.title)}</h1>${sceneFigure(s,[id],"scene-l")}<p>${esc(s.summary)}</p><p class="quiet">${esc(s.notes)}</p>${sourceList(s.sources)}<p>Modern illustrated reconstruction.</p><div class="chips">${s.people.map(pid => `<a class="chip" href="#/person/${pid}">${esc(P[pid].name)}</a>`).join("")}</div><p><a href="scenes/${id.toLowerCase()}/">Reference page for sharing and citation</a></p>${reels.length ? `<h2>Watch this moment</h2><ul>${reels.map(r=>`<li><a href="#/films/${r.id}">${esc(r.title)}</a></li>`).join("")}</ul>` : ""}<nav class="pager" aria-label="Chronological scenes">${i ? `<a href="#/scene/${ordered[i-1].id}">← ${esc(ordered[i-1].title)}</a>` : '<span></span>'}${i+1<ordered.length ? `<a href="#/scene/${ordered[i+1].id}">${esc(ordered[i+1].title)} →</a>` : ""}</nav></article>`;
    $('.chips',view).insertAdjacentHTML('afterend', `<p><a href="#/map?event=${s.id}">Follow this event on MAP →</a></p>`);
  }

  function reelCard(r) {
    return `<li id="film-${r.id}"><button type="button" class="reel" data-reel="${r.id}" aria-label="Play ${esc(r.title)}"><span class="film-frame"><img src="${esc(r.poster)}" alt="Modern reconstructed scene: ${esc(r.title)}" loading="lazy" width="420" height="748"><span class="play" aria-hidden="true"></span></span></button><p class="scene-date">${esc(r.year)} · ${r.duration}s</p><h2>${esc(r.title)}</h2><details><summary>Read scene description</summary><p>${esc(r.description)}</p>${r.line ? `<p lang="as">${esc(r.line)}</p><p>${esc(r.translation)}</p><p class="quiet">Scripted dialogue; not a verified audio transcript.</p>` : ""}</details><p><a href="#/scene/${r.scene}">History and sources</a> · <a href="films/${r.id}/">Share film</a></p></li>`;
  }

  function films(params, id) {
    setTitle("Short films");
    view.innerHTML = `<section class="reference"><h1>${A.reels.length} short films</h1><p>Reconstructed moments from the chronicles, in historical order. Search for a person, place or event, and read each scene description for context without sound.</p><div class="library-filters"><label>Search films <input type="search" id="film-search" placeholder="A person, place or event" value="${esc(params.get('q') || '')}"></label><label>Chapter <select id="film-era"><option value="">All chapters</option>${A.eras.filter(e=>A.reels.some(r=>r.era===e.id)).map(e=>`<option value="${e.id}">${esc(e.title)}</option>`).join("")}</select></label></div><p id="film-count" aria-live="polite"></p><ul class="film-library" id="film-grid"></ul></section>`;
    $('.library-filters').insertAdjacentHTML('beforebegin', '<p class="quiet">The CC menu offers English and Assamese scene context. These subtitles describe the moment; they do not transcribe the dialogue.</p>');
    const q = $('#film-search'), era = $('#film-era'), grid = $('#film-grid');
    era.value = params.get('era') || '';
    function draw() {
      const term=q.value.trim().toLowerCase();
      const found=A.reels.filter(r=>(!era.value || r.era===era.value) && [r.title,r.year,r.description,...S[r.scene].people.map(pid=>[P[pid].name,P[pid].as].join(' '))].join(' ').toLowerCase().includes(term)).sort((a,b)=>(S[a.scene].year || 0)-(S[b.scene].year || 0));
      grid.innerHTML=found.map(reelCard).join('') || '<li>No films match. Try another name or chapter.</li>';
      $('#film-count').textContent=`${found.length} of ${A.reels.length} films`;
    }
    function filter() { draw(); const sp=new URLSearchParams(); if(q.value)sp.set('q',q.value);if(era.value)sp.set('era',era.value);history.replaceState(null,'','#/films'+(sp.size?'?'+sp:'')); }
    q.addEventListener('input',filter);era.addEventListener('change',filter);draw();
    if(id) { const target=$(`#film-${CSS.escape(id)}`);if(target)requestAnimationFrame(()=>{target.scrollIntoView();$('.reel',target).click();}); }
  }

  function explore(params) {
    setTitle("Historical map explorer");
    const atlas=window.AhomAtlas.mount(view,A,params,sourceList);
    cleanup.push(()=>atlas.destroy());
  }

  // the year in the rail follows the reader through each chapter
  function wireSaga() {
    const rail = $(".rail"), yearEl = $(".rail-year"), links = $$(".rail a");
    const chapters = $$(".chapter");
    let ticking = false, lastEra = null;
    // each chapter is read from its start year, through its paintings, to its end year;
    // the year shown is interpolated between the marks above and below the reading line
    const marks = chapters.flatMap(c => {
      const m = illustrated(ERA[c.dataset.era].moments).map(s => s.year).filter(Boolean);
      return [
        [$(".ch-head", c), +c.dataset.start, c],
        [$(".moments", c), m[0] || +c.dataset.start, c],
        [$(".ch-foot", c), m[m.length - 1] || +c.dataset.end, c],
        [c, +c.dataset.end, c, true],
      ];
    });
    function update() {
      ticking = false;
      const line = innerHeight * 0.4;
      let cur = null, year = FIRST;
      for (let i = 0; i < marks.length; i++) {
        const [el, y, c, bottom] = marks[i];
        const r = el.getBoundingClientRect();
        const top = bottom ? r.bottom : r.top;
        if (top > line) break;
        cur = c;
        const next = marks[i + 1];
        if (!next || next[2] !== c) { year = y; continue; }
        const nr = next[0].getBoundingClientRect(), ntop = next[3] ? nr.bottom : nr.top;
        const t = Math.min(1, Math.max(0, (line - top) / Math.max(1, ntop - top)));
        year = Math.round(y + t * (next[1] - y));
      }
      const saga = $(".saga").getBoundingClientRect();
      rail.classList.toggle("is-live", saga.top < innerHeight * 0.6 && saga.bottom > innerHeight * 0.3);
      yearEl.textContent = year;
      const era = cur ? cur.dataset.era : null;
      if (era !== lastEra) {
        lastEra = era;
        links.forEach(a => a.toggleAttribute("aria-current", a.dataset.era === era));
        if (era) yearEl.dataset.title = ERA[era].title;
      }
    }
    const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
    addEventListener("scroll", onScroll, { passive: true });
    cleanup.push(() => removeEventListener("scroll", onScroll));
    update();
  }

  // ---------- the kings ----------

  const GAPS = {
    1364: "No king. The Burhagohain and Borgohain rule",
    1376: "No king. The ministers rule after Sutuphaa’s murder",
    1389: "No king. The ministers rule until the hidden prince is found",
    1822: "Burmese occupation, then the East India Company",
  };

  function kings() {
    setTitle("The forty-one reigns");
    const pct = y => ((y - FIRST) / (LAST - FIRST) * 100).toFixed(3);
    // a faint line at each century behind the bars
    const bands = [1300, 1400, 1500, 1600, 1700, 1800].map(y => {
      const x = pct(y);
      return `transparent calc(${x}% - .5px), var(--band) calc(${x}% - .5px), var(--band) calc(${x}% + .5px), transparent calc(${x}% + .5px)`;
    }).join(", ");
    const rows = [];
    A.reigns.forEach((r, i) => {
      const prev = A.reigns[i - 1];
      if (prev && r.start - prev.end >= 2) {
        rows.push(`<li class="reign reign-gap"><span class="r-no"></span><span class="r-thumb"></span>
          <span class="r-name">${esc(GAPS[prev.end] || "No king on the throne")}</span>
          <span class="r-years">${prev.end}–${r.start}</span>
          <span class="r-bar" aria-hidden="true"><i style="left:${pct(prev.end)}%;width:${pct(FIRST + r.start - prev.end)}%"></i></span></li>`);
      }
      const p = P[r.id];
      const len = Math.max(r.end - r.start, 0);
      rows.push(`<li class="reign"><a href="#/person/${p.id}">
        <span class="r-no">${r.no}</span>
        ${arch(p, "r-thumb")}
        <span class="r-name">${esc(p.name)}${p.as ? `<span lang="as">${esc(p.as)}</span>` : ""}${r.again ? `<span class="r-again">Second reign</span>` : ""}</span>
        <span class="r-years">${r.start === r.end ? r.start : `${r.start}–${r.end}`}<span class="r-len">${len ? `${len} year${len > 1 ? "s" : ""}` : "under a year"}</span></span>
        <span class="r-bar" aria-hidden="true"><i style="left:${pct(r.start)}%;width:max(3px, ${pct(FIRST + len)}%)"></i></span>
      </a></li>`);
    });
    const ticks = [1300, 1400, 1500, 1600, 1700, 1800].map(y => `<span style="left:${pct(y)}%">${y}</span>`).join("");
    view.innerHTML = `
    <section class="page-head">
      ${bgWord("স্বৰ্গদেউ", "page-word")}
      <h1>The forty-one reigns</h1>
      <p class="lede">Thirty-nine kings, the Swargadeos, ruled the Ahom kingdom in forty-one reigns: Chandrakanta Singha and Purandar Singha each took the throne twice. Every bar sits on one line from 1228 to 1838. The red bars are the years with no king.</p>
    </section>
    <div class="reigns-wrap" style="--bands: linear-gradient(90deg, ${bands})">
      <div class="axis" aria-hidden="true"><span class="axis-label">Reign</span><span class="axis-scale">${ticks}</span></div>
      <ol class="reigns">${rows.join("")}</ol>
    </div>`;
  }

  // ---------- people ----------

  function people(params) {
    setTitle("People of the chronicles");
    const total = Object.keys(P).length;
    view.innerHTML = `
    <section class="page-head">
      ${bgWord("বুৰঞ্জী", "page-word")}
      <h1>People of the chronicles</h1>
      <p class="lede">The kings and queens of the Ahom court, their ministers and generals, the rebels who rose against them and the foreign commanders they fought.</p>
    </section>
    <div class="filters">
      <label class="search"><span class="vh">Search people</span>
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/></svg>
        <input type="search" id="q" placeholder="Search by name, in English or Assamese" autocomplete="off" value="${esc(params.get("q") || "")}">
      </label>
      <div class="chips" role="group" aria-label="Show a group">
        <button type="button" class="chip" data-g="">Everyone <span>${total}</span></button>
        ${A.groups.map(g => `<button type="button" class="chip" data-g="${esc(g.name)}">${esc(g.name)} <span>${g.ids.length}</span></button>`).join("")}
      </div>
    </div>
    <p class="count" id="count" aria-live="polite"></p>
    <ul class="people-grid" id="grid"></ul>`;

    const q = $("#q"), grid = $("#grid"), count = $("#count");
    let group = params.get("g") || "";
    const order = A.groups.flatMap(g => g.ids);
    const hay = Object.fromEntries(order.map(id => {
      const p = P[id];
      return [id, [p.name, p.as, p.tai, p.hindu, p.aka, p.role].join(" ").toLowerCase()];
    }));
    function draw() {
      const term = q.value.trim().toLowerCase();
      const ids = order.filter(id => (!group || P[id].group === group) && (!term || hay[id].includes(term)));
      $$(".chip").forEach(c => c.setAttribute("aria-pressed", c.dataset.g === group));
      count.textContent = ids.length === order.length ? `${ids.length} people` : ids.length ? `${ids.length} of ${order.length} people` : "";
      grid.innerHTML = ids.length ? ids.map(id => {
        const p = P[id];
        return `<li><a class="pcard" href="#/person/${p.id}">
          ${arch(p, "arch-m")}
          <span class="pc-name">${esc(p.name)}</span>
          ${p.as ? `<span class="pc-as" lang="as">${esc(p.as)}</span>` : ""}
          <span class="pc-role">${esc(p.role || "")}</span>
          <span class="pc-date">${dash(p.date || "")}</span>
        </a></li>`;
      }).join("") : `<li class="empty">Nobody matches “${esc(q.value)}”${group ? ` in ${esc(group)}` : ""}. Try part of a name, or <button type="button" class="link" id="clear">show everyone</button>.</li>`;
      const sp = new URLSearchParams();
      if (group) sp.set("g", group);
      if (term) sp.set("q", q.value.trim());
      const h = "#/people" + (sp.toString() ? "?" + sp : "");
      if (location.hash !== h) history.replaceState(null, "", h);
      const clear = $("#clear");
      if (clear) clear.onclick = () => { q.value = ""; group = ""; draw(); q.focus(); };
    }
    $(".chips").addEventListener("click", e => {
      const b = e.target.closest(".chip");
      if (b) { group = b.dataset.g; draw(); }
    });
    q.addEventListener("input", draw);
    draw();
  }

  // ---------- one person ----------

  function sourceLabel(u) {
    try {
      const url = new URL(u);
      const tail = decodeURIComponent(url.pathname.split("/").filter(Boolean).pop() || "").replace(/_/g, " ");
      return url.hostname.replace(/^www\.|^en\./, "") + (tail ? `: ${tail}` : "");
    } catch { return u; }
  }

  function person(id) {
    const p = P[id];
    if (!p) return notFound(`There is no one in the chronicles with the id “${id}”.`, "#/people", "Browse everyone");
    setTitle(p.name);
    const group = A.groups.find(g => g.name === p.group).ids;
    const i = group.indexOf(id), prev = P[group[i - 1]], next = P[group[i + 1]];
    const reigns = A.reigns.filter(r => r.id === id);
    const facts = [
      [reigns.length ? (reigns.length > 1 ? "Reigned" : "Reign") : "Dates", dash(p.date)],
      ["Swargadeo", reigns.map(r => `${r.no}${["st", "nd", "rd"][((r.no + 90) % 100 - 10) % 10 - 1] || "th"} of 41`).join(", ")],
      ["Tai name", esc(p.tai)], ["Hindu name", esc(p.hindu)], ["Also called", esc(p.aka)],
      ["Family", esc(p.relation)], ["Consort", esc(p.consort)], ["Fate", esc(p.fate)],
    ].filter(f => f[1]);
    const imgs = p.images || [];
    const scenes = (p.scenes || []).map(s => S[s]);
    scenes.sort((a, b) => (a.year ?? 9999) - (b.year ?? 9999));
    const painted = scenes.filter(s => s.images.length), unpainted = scenes.filter(s => !s.images.length);
    const sure = { high: "Well recorded: the main sources agree.", medium: "Mostly recorded: some details rest on a single source.", low: "Thinly recorded: few sources, and some disagree." }[p.confidence];
    view.innerHTML = `
    <article class="person">
      ${p.as ? bgWord(p.as, "person-word") : ""}
      <nav class="crumbs" aria-label="Breadcrumb"><a href="#/people?g=${encodeURIComponent(p.group)}">${esc(p.group)}</a></nav>
      <div class="person-grid">
        <div class="viewer">
          ${imgs.length ? `<figure class="viewer-main">
            <div class="viewer-frame"><img id="viewer-img" src="${esc(imgs[0].src)}" alt="${esc(imgs[0].caption || p.name)}" width="${imgs[0].w || ""}" height="${imgs[0].h || ""}"></div>
            <figcaption id="viewer-cap">${esc(imgs[0].caption)}</figcaption>
          </figure>
          ${imgs.length > 1 ? `<div class="viewer-thumbs" role="group" aria-label="Images of ${esc(p.name)}">${imgs.map((im, k) => `<button type="button" data-k="${k}" aria-pressed="${k === 0}" aria-label="${esc(im.caption || `Image ${k + 1}`)}"><img src="${esc(im.thumb)}" alt="" loading="lazy"></button>`).join("")}</div>` : ""}`
          : `<div class="viewer-none">${arch(p, "arch-xl")}<p class="quiet">No portrait of ${esc(p.name)} has been painted yet.</p></div>`}
        </div>
        <div class="person-text">
          <h1>${esc(p.name)}</h1>
          ${p.as ? `<p class="person-as" lang="as">${esc(p.as)}</p>` : ""}
          ${p.role ? `<p class="person-role">${esc(p.role)}</p>` : ""}
          <dl class="facts">${facts.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join("")}</dl>
          ${p.summary ? `<p class="person-summary">${esc(p.summary)}</p>` : ""}
          ${p.notes ? `<p>${esc(p.notes)}</p>` : ""}
          ${sure ? `<p class="sure sure-${p.confidence}">${sure}</p>` : ""}
          ${p.sources ? `<details class="sources"><summary>Sources (${p.sources.length})</summary><ul>${p.sources.map(u => /^https?:/.test(u) ? `<li><a href="${esc(u)}" rel="noopener" target="_blank">${esc(sourceLabel(u))}</a></li>` : `<li>${esc(u)}</li>`).join("")}</ul></details>` : ""}
        </div>
      </div>
      ${scenes.length ? `<section class="person-scenes" aria-labelledby="ps-title">
        <h2 id="ps-title">In the scenes</h2>
        <div class="scene-grid">${[...painted, ...unpainted].map(s => sceneFigure(s, [...painted, ...unpainted].map(x => x.id))).join("")}</div>
      </section>` : ""}
      <nav class="pager" aria-label="More from ${esc(p.group)}">
        ${prev ? `<a href="#/person/${prev.id}" rel="prev">${arch(prev, "arch-s")}<span><span class="quiet">Before</span>${esc(prev.name)}</span></a>` : "<span></span>"}
        ${next ? `<a href="#/person/${next.id}" rel="next" class="pager-next"><span><span class="quiet">After</span>${esc(next.name)}</span>${arch(next, "arch-s")}</a>` : "<span></span>"}
      </nav>
    </article>`;
    const thumbs = $(".viewer-thumbs");
    if (thumbs) thumbs.addEventListener("click", e => {
      const b = e.target.closest("button");
      if (!b) return;
      const im = imgs[+b.dataset.k], img = $("#viewer-img");
      img.src = im.src; img.alt = im.caption || p.name;
      if (im.w) { img.width = im.w; img.height = im.h; }
      $("#viewer-cap").textContent = im.caption;
      $$("button", thumbs).forEach(x => x.setAttribute("aria-pressed", x === b));
    });
  }

  // ---------- scenes ----------

  // which reign a scene belongs to: a king named in the scene who reigned that year, else whoever reigned then;
  // years between reigns are their own "no king" section, and undated scenes are kept together at the end
  function reignOf(s) {
    const y = s.year;
    if (y == null) return { key: "undated" };
    const R = A.reigns;
    const during = R.filter(r => r.start <= y && y <= r.end);
    const inter = /interregnum/i.test(s.title);
    const named = !inter && (during.find(r => s.main.includes(r.id)) || during.find(r => s.people.includes(r.id)));
    if (named) return { key: `r${named.no}`, reign: named };
    let k = 0;
    R.forEach((r, i) => { if (r.start <= y) k = i; });
    const r = R[k], next = R[k + 1];
    // an interregnum scene dated to the year its king died belongs to the years with no king
    const between = y > r.end || (y === r.end && inter);
    if (between && next && next.start - r.end >= 2) return { key: `gap${r.end}`, gap: [r.end, next.start] };
    if (y > r.end && !next) return { key: `after${r.end}`, gap: [r.end, LAST] };
    return { key: `r${r.no}`, reign: r };
  }

  function reignHead(g, count, painted) {
    const tally = `${count} scene${count > 1 ? "s" : ""}${painted < count ? `, ${painted} painted` : ""}`;
    if (g.reign) {
      const p = P[g.reign.id], r = g.reign;
      return `<header class="kh">
        <a class="kh-who" href="#/person/${p.id}">${arch(p, "kh-arch")}
          <span class="kh-no" aria-hidden="true">${r.no}</span>
          <span class="kh-text"><span class="kh-name">${esc(p.name)}${r.again ? ` <span class="r-again">second reign</span>` : ""}</span>
          ${p.as ? `<span class="kh-as" lang="as">${esc(p.as)}</span>` : ""}
          <span class="kh-meta">Swargadeo ${r.no} of 41, ${r.start === r.end ? r.start : `${r.start}–${r.end}`}</span></span>
        </a>
        <span class="kh-count">${tally}</span>
      </header>`;
    }
    const title = g.key === "undated" ? "Undated scenes" : (GAPS[g.gap[0]] || "No king on the throne");
    const years = g.gap ? `${g.gap[0]}–${g.gap[1]}` : "Year not recorded";
    return `<header class="kh kh-plain">
      <span class="kh-who"><span class="kh-mark" aria-hidden="true"></span>
        <span class="kh-text"><span class="kh-name">${esc(title)}</span><span class="kh-meta">${years}</span></span></span>
      <span class="kh-count">${tally}</span>
    </header>`;
  }

  function reignSections(list, eraId) {
    const groups = [];
    const byKey = {};
    for (const s of list) {
      const g = reignOf(s);
      if (!byKey[g.key]) { byKey[g.key] = Object.assign(g, { scenes: [] }); groups.push(g); }
      byKey[g.key].scenes.push(s);
    }
    const rank = g => g.reign ? g.reign.start + g.reign.no / 1000 : g.gap ? g.gap[0] + .5 : Infinity;
    groups.sort((a, b) => rank(a) - rank(b));
    const ids = groups.flatMap(g => g.scenes.map(s => s.id));
    return groups.map(g => `<section class="reign-scenes" id="k-${eraId}-${g.key}" aria-label="${esc(g.reign ? P[g.reign.id].name : g.key === "undated" ? "Undated scenes" : "No king on the throne")}">
        ${reignHead(g, g.scenes.length, g.scenes.filter(s => s.images.length).length)}
        <div class="scene-grid">${g.scenes.map(s => sceneFigure(s, ids)).join("")}</div>
      </section>`).join("");
  }

  function scenes(eraId) {
    const era = eraId ? ERA[eraId] : null;
    if (eraId && !era) return notFound(`There is no chapter called “${eraId}”.`, "#/scenes", "See all scenes");
    setTitle(era ? `Scenes: ${era.title}` : "Scenes from the chronicles");
    const shown = era ? [era] : A.eras;
    const painted = A.scenes.filter(s => s.images.length).length;
    // within one chapter, a row of the kings of that chapter to jump between
    let jump = "";
    if (era) {
      const seen = new Set();
      const keys = era.scenes.map(id => reignOf(S[id])).filter(g => g.reign && !seen.has(g.key) && seen.add(g.key));
      keys.sort((a, b) => a.reign.no - b.reign.no);
      jump = `<nav class="king-jump" aria-label="Kings of this chapter">${keys.map(g => `<button type="button" class="chip chip-person" data-jump="k-${era.id}-${g.key}">${arch(P[g.reign.id], "arch-xs")}${esc(P[g.reign.id].name.replace(/ \(.*\)$/, ""))}</button>`).join("")}</nav>`;
    }
    view.innerHTML = `
    <section class="page-head">
      ${bgWord(era ? era.word : "চিত্ৰ", "page-word")}
      <h1>${era ? esc(era.title) : "Scenes from the chronicles"}</h1>
      <p class="lede">${era ? `${era.start}–${era.end}. ${esc(era.lead[0])}` : `${A.scenes.length} moments from the Ahom chronicles, ${painted} of them painted, set out king by king. Pick a chapter, then open a scene to read it.`}</p>
    </section>
    <nav class="tabs" aria-label="Chapters">
      <a href="#/scenes" ${era ? "" : 'aria-current="page"'}>All chapters</a>
      ${A.eras.map(e => `<a href="#/scenes/${e.id}" ${e === era ? 'aria-current="page"' : ""}><span>${e.start}</span>${esc(e.title)}</a>`).join("")}
    </nav>
    ${jump}
    ${shown.map(e => `<section class="era-scenes" aria-labelledby="es-${e.id}">
        ${era ? `<h2 class="vh" id="es-${e.id}">${esc(e.title)}</h2>` : `<h2 id="es-${e.id}"><span class="es-years">${e.start}–${e.end}</span><a href="#/scenes/${e.id}">${esc(e.title)}</a></h2>`}
        ${reignSections(e.scenes.map(id => S[id]), e.id)}
      </section>`).join("")}
    ${era ? `<nav class="pager" aria-label="Other chapters">
      ${era.n > 0 ? `<a href="#/scenes/${A.eras[era.n - 1].id}" rel="prev"><span><span class="quiet">Earlier</span>${esc(A.eras[era.n - 1].title)}</span></a>` : "<span></span>"}
      ${era.n < A.eras.length - 1 ? `<a href="#/scenes/${A.eras[era.n + 1].id}" rel="next" class="pager-next"><span><span class="quiet">Later</span>${esc(A.eras[era.n + 1].title)}</span></a>` : "<span></span>"}
    </nav>` : ""}`;
  }

  function lifeFigure(it, list) {
    return `<figure class="scene life-item ${it.kind === "object" ? "life-object" : ""}">
      <button type="button" class="scene-open" data-scene="life:${it.id}" data-list="${list.join(",")}" aria-label="Open: ${esc(it.title)}"><img src="${esc(it.img[1])}" alt="${esc(it.alt)}" loading="lazy" decoding="async" style="aspect-ratio:${it.w}/${it.h}"></button>
      <figcaption>${it.kind === "photo" ? `<span class="scene-date">Modern photograph</span>` : it.period ? `<span class="scene-date">${esc(it.period)}</span>` : ""}${esc(it.title)}</figcaption>
    </figure>`;
  }

  function lifeSection(sec, full) {
    const ids = sec.items.map(it => "life:" + it.id);
    const groups = [...new Set(sec.items.map(it => it.group || ""))];
    const shown = full ? sec.items : sec.items.slice(0, 4);
    const grid = items => `<div class="scene-grid">${items.map(it => lifeFigure(it, ids)).join("")}</div>`;
    return `<section class="era-scenes life-section" id="life-${sec.id}" aria-labelledby="ls-${sec.id}">
      <h2 id="ls-${sec.id}">${sec.period ? `<span class="es-years">${esc(sec.period)}</span>` : ""}${full ? esc(sec.title) : `<a href="#/life/${sec.id}">${esc(sec.title)}</a>`}</h2>
      <p class="life-intro">${esc(sec.intro)}</p>
      <p class="life-caveat">${esc(sec.caveat)}${sec.era && ERA[sec.era] ? ` <a href="#/saga/${sec.era}">Read the chapter: ${esc(ERA[sec.era].title)}</a>` : ""}</p>
      ${full && groups.length > 1 ? groups.map(g => `<h3 class="life-group">${esc(g)}</h3>${grid(sec.items.filter(it => (it.group || "") === g))}`).join("") : grid(shown)}
      ${full ? "" : `<a class="more" href="#/life/${sec.id}">All ${sec.items.length} images</a>`}
    </section>`;
  }

  function life(secId) {
    const sec = secId ? LIFE.find(x => x.id === secId) : null;
    if (secId && !sec) return notFound(`There is no section called “${secId}”.`, "#/life", "See daily life");
    setTitle(sec ? `Life: ${sec.title}` : "Life in the Ahom kingdom and after");
    const total = LIFE.reduce((n, x) => n + x.items.length, 0);
    const k = sec ? LIFE.indexOf(sec) : -1;
    view.innerHTML = `
    <section class="page-head">
      ${bgWord("জীৱন", "page-word")}
      <h1>${sec ? esc(sec.title) : "Daily life"}</h1>
      <p class="lede">${sec ? esc(sec.intro) : `How people lived, worked and built, beyond the kings and battles: villages, craft, the river, monuments, the things of the house, and Assam since. ${total} images in ${LIFE.length} sections.`}</p>
      <p class="life-label">${esc(A.life.label)} Kachari, Bhuyan and Ahom villages are shown as separate groups.</p>
    </section>
    <nav class="tabs" aria-label="Sections">
      <a href="#/life" ${sec ? "" : 'aria-current="page"'}>All</a>
      ${LIFE.map(x => `<a href="#/life/${x.id}" ${x === sec ? 'aria-current="page"' : ""}>${x.period ? `<span>${esc(x.period)}</span>` : ""}${esc(x.title)}</a>`).join("")}
    </nav>
    ${sec ? lifeSection(sec, true) : LIFE.map(x => lifeSection(x, false)).join("")}
    ${sec ? `<nav class="pager" aria-label="Other sections">
      ${k > 0 ? `<a href="#/life/${LIFE[k - 1].id}" rel="prev"><span><span class="quiet">Previous</span>${esc(LIFE[k - 1].title)}</span></a>` : "<span></span>"}
      ${k < LIFE.length - 1 ? `<a href="#/life/${LIFE[k + 1].id}" rel="next" class="pager-next"><span><span class="quiet">Next</span>${esc(LIFE[k + 1].title)}</span></a>` : "<span></span>"}
    </nav>` : ""}`;
  }

  function notFound(msg, href, label) {
    setTitle("Not found");
    view.innerHTML = `<section class="page-head">${bgWord("নাই", "page-word")}<h1>Not in the chronicles</h1><p class="lede">${esc(msg)}</p><p><a class="btn" href="${href}">${label}</a></p></section>`;
  }

  // ---------- the scene viewer ----------

  const lb = $("#lightbox");
  let lbList = [], lbAt = 0, lbVersion = 0;
  function openScene(id, list) {
    lbList = list.length ? list : [id];
    lbAt = Math.max(0, lbList.indexOf(id));
    lbVersion = 0;
    drawScene();
    if (!lb.open) lb.showModal();
  }
  function drawLife(it) {
    const img = $("#lb-img");
    img.hidden = false; $("#lb-blank").hidden = true;
    img.src = it.img[0]; img.alt = it.alt;
    $("#lb-date").textContent = [it.period, it.group, it.sec.title].filter(Boolean).join(" · ");
    $("#lb-title").textContent = it.title;
    $("#lb-summary").textContent = it.text || it.sec.intro;
    $("#lb-notes").textContent = [it.note, it.kind === "photo" ? "" : A.life.label].filter(Boolean).join(" ");
    $("#lb-sources").innerHTML = it.sources && it.sources.length ? `<details class="sources"><summary>Sources</summary><ul>${it.sources.map(x => `<li><a href="${esc(x.url)}" rel="noopener" target="_blank">${esc(x.title)}</a></li>`).join("")}</ul></details>` : "";
    $("#lb-permalink").href = `#/life/${it.sec.id}`;
    $("#lb-reference").href = `life/${it.sec.id}/`;
    $("#lb-permalink").textContent = "Open this section";
    $("#lb-map-wrap").hidden = true;
    $("#lb-people").innerHTML = "";
    $("#lb-versions").innerHTML = "";
    $("#lb-count").textContent = lbList.length > 1 ? `${lbAt + 1} of ${lbList.length}` : "";
    $("#lb-prev").hidden = $("#lb-next").hidden = lbList.length < 2;
    [lbAt - 1, lbAt + 1].forEach(k => { const n = LI[lbList[(k + lbList.length) % lbList.length]]; if (n) new Image().src = n.img[0]; });
  }
  function drawScene() {
    if (LI[lbList[lbAt]]) return drawLife(LI[lbList[lbAt]]);
    $("#lb-map-wrap").hidden = false;
    $("#lb-permalink").textContent = "Open scene page";
    const s = S[lbList[lbAt]];
    const img = $("#lb-img"), pic = s.images[lbVersion];
    img.hidden = !pic;
    $("#lb-blank").hidden = !!pic;
    if (pic) { img.src = pic[0]; img.alt = s.title; } else img.removeAttribute("src");
    $("#lb-date").textContent = `${(s.date || "Undated").replace(/(\d)-(\d)/g, "$1–$2")}, ${ERA[s.era].title}`;
    $("#lb-title").textContent = s.title;
    $("#lb-summary").textContent = s.summary;
    $("#lb-notes").textContent = s.notes || "";
    $("#lb-sources").innerHTML = sourceList(s.sources);
    $("#lb-permalink").href = `#/scene/${s.id}`;
    $("#lb-reference").href = `scenes/${s.id.toLowerCase()}/`;
    $("#lb-map").href = `#/map?event=${s.id}`;
    $("#lb-people").innerHTML = s.people.map(pid => `<a class="chip chip-person" href="#/person/${pid}">${arch(P[pid], "arch-xs")}${esc(P[pid].name)}</a>`).join("");
    $("#lb-versions").innerHTML = s.images.length > 1 ? s.images.map((im, k) => `<button type="button" data-v="${k}" aria-pressed="${k === lbVersion}">Version ${k + 1}</button>`).join("") : "";
    $("#lb-count").textContent = lbList.length > 1 ? `Scene ${lbAt + 1} of ${lbList.length}` : "";
    $("#lb-prev").hidden = $("#lb-next").hidden = lbList.length < 2;
    // warm the neighbours
    [lbAt - 1, lbAt + 1].forEach(k => { const n = S[lbList[(k + lbList.length) % lbList.length]]; if (n && n.images.length) new Image().src = n.images[0][0]; });
  }
  function step(d) { lbAt = (lbAt + d + lbList.length) % lbList.length; lbVersion = 0; drawScene(); }
  $("#lb-prev").onclick = () => step(-1);
  $("#lb-next").onclick = () => step(1);
  $("#lb-close").onclick = () => lb.close();
  $("#lb-versions").onclick = e => { const b = e.target.closest("button"); if (b) { lbVersion = +b.dataset.v; drawScene(); } };
  lb.addEventListener("click", e => { if (e.target === lb) lb.close(); });
  lb.addEventListener("keydown", e => {
    if (e.key === "ArrowLeft") step(-1);
    if (e.key === "ArrowRight") step(1);
  });

  // ---------- films ----------

  function stopOthers(except) { $$("video").forEach(v => { if (v !== except && !v.paused && !v.hasAttribute("data-auto")) v.pause(); }); }

  document.addEventListener("click", e => {
    const skip = e.target.closest('.skip');
    if(skip) { e.preventDefault(); view.focus(); view.scrollIntoView(); return; }
    const jumpTo = e.target.closest("[data-jump]");
    if (jumpTo) { const t = document.getElementById(jumpTo.dataset.jump); t.scrollIntoView({ behavior: calm ? "auto" : "smooth" }); return; }

    const open = e.target.closest(".scene-open");
    if (open) return openScene(open.dataset.scene, open.dataset.list ? open.dataset.list.split(",") : []);

    const snd = e.target.closest(".sound");
    if (snd) {
      const v = snd.closest(".film").querySelector("video");
      v.muted = !v.muted;
      if (!v.muted) { $$(".sound").forEach(b => { if (b !== snd) { b.closest(".film").querySelector("video").muted = true; b.setAttribute("aria-pressed", "false"); b.textContent = "Sound on"; } }); v.play(); }
      snd.setAttribute("aria-pressed", String(!v.muted));
      snd.textContent = v.muted ? "Sound on" : "Sound off";
      return;
    }

    const reel = e.target.closest(".reel");
    if (reel) {
      const frame = reel.querySelector(".film-frame");
      let v = frame.querySelector("video");
      if (!v) {
        v = document.createElement("video");
        const r = A.reels.find(r => r.id === reel.dataset.reel);
        Object.assign(v, { src: r.src, poster: r.poster, playsInline: true, controls: true });
        v.setAttribute("aria-label", r.title);
        (r.tracks || []).forEach(t => { const track=document.createElement('track');Object.assign(track,{kind:'subtitles',src:t.src,srclang:t.lang,label:t.label});v.append(track); });
        frame.querySelector("img").replaceWith(v);
        frame.querySelector(".play").remove();
        reel.replaceWith(frame);
        frame.classList.add("is-playing");
      }
      $$(".sound[aria-pressed=true]").forEach(b => b.click());
      stopOthers(v);
      v.play().catch(() => {});
      v.addEventListener("play", () => stopOthers(v));
    }
  });

  // muted ambient films play only while on screen, and never for readers who ask for less motion
  let filmWatch;
  function watchFilms() {
    if (filmWatch) filmWatch.disconnect();
    const vids = $$("video[data-auto]");
    if (calm) { vids.forEach(v => { v.preload = "metadata"; v.controls = true; }); return; }
    filmWatch = new IntersectionObserver(entries => entries.forEach(en => {
      const v = en.target;
      if (en.isIntersecting) { v.preload = "auto"; v.play().catch(() => {}); } else v.pause();
    }), { threshold: 0.25 });
    vids.forEach(v => filmWatch.observe(v));
  }

  // ---------- routing ----------

  let cleanup = [];
  let current = "";
  const scrollMemory = new Map();
  let traversing = false;
  if (window.navigation) navigation.addEventListener("navigate", e => { traversing = e.navigationType === "traverse"; });

  function route() {
    const raw = location.hash.replace(/^#\/?/, "");
    const [path, query = ""] = raw.split("?");
    const parts = path.split("/").filter(Boolean);
    const params = new URLSearchParams(query);
    const requested = parts[0] || "saga";
    const page = requested === 'explore' ? 'map' : requested;
    const key = page === 'saga' ? 'saga' : `${page}/${parts[1] || ""}${page === 'explore' ? '?' + query : ''}`;

    if (lb.open) lb.close();
    if (current && current !== key) scrollMemory.set(current, scrollY);
    const same = key === current && !['films','people','map'].includes(page);
    if (!same) {
      $$("video").forEach(v => v.pause());
      cleanup.forEach(f => f()); cleanup = [];
      if (page === "saga") home();
      else if (page === "kings") kings();
      else if (page === "people") people(params);
      else if (page === "person") person(parts[1]);
      else if (page === "scenes") scenes(parts[1]);
      else if (page === "scene") scenePage(parts[1]);
      else if (page === "life") life(parts[1]);
      else if (page === "films") films(params, parts[1]);
      else if (page === "map") explore(params);
      else notFound("That page is not part of this site.", "#/", "Go to the saga");
      current = key;
      watchFilms();
    }
    $$("[data-nav]").forEach(a => { if(a.dataset.nav === (page === "person" ? "people" : page === 'scene' ? 'scenes' : page))a.setAttribute('aria-current','page');else a.removeAttribute('aria-current'); });
    document.body.dataset.route = page === "saga" ? "home" : page;

    if (page === "saga" && parts[1] && ERA[parts[1]]) {
      const target = $(`#ch-${parts[1]}`);
      requestAnimationFrame(() => target.scrollIntoView({ behavior: same && !calm ? "smooth" : "auto" }));
    } else if (!same) {
      const back = traversing && scrollMemory.has(key);
      scrollTo(0, back ? scrollMemory.get(key) : 0);
      if (!back && raw) view.focus({ preventScroll: true });
    }
    traversing = false;
  }


  // the welcome: the throne film's own sound, played once when the site opens. Browsers only let sound start
  // after a press or key, so if the first attempt is refused it starts on the reader's first touch.
  // The header button turns it on and off.
  function welcome() {
    const btn = $(".sound-toggle");
    if (!btn) return;
    const a = new Audio();
    a.preload = "none";
    a.src = "assets/welcome.mp3";
    a.volume = 0.7;
    let on = false;
    const show = v => { on = v; btn.setAttribute("aria-pressed", String(v)); btn.textContent = v ? "Sound off" : "Sound on"; };
    const begin = () => { $$("video").forEach(v => { v.muted = true; }); return a.play().then(() => show(true)).catch(() => {}); };
    btn.addEventListener("click", () => { if (on) { a.pause(); show(false); } else { begin(); } });
    a.addEventListener("ended", () => show(false));
    document.addEventListener('play', e => { if(e.target.tagName==='VIDEO' && !e.target.muted) { a.pause(); show(false); } }, true);
  }
  welcome();


  addEventListener("hashchange", route);
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  route();
})();
