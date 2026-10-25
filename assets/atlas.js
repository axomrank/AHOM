// Story/map coordinator. Selection, filters, playback and URL state share one event.
window.AhomAtlas = (() => {
  'use strict';
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const rx=v=>v.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');

  function mount(root,A,params,sources) {
    const scenes=Object.fromEntries(A.scenes.map(s=>[s.id,s]));
    const eras=Object.fromEntries(A.eras.map(e=>[e.id,e]));
    const sites=Object.fromEntries(A.atlas.sites.map(p=>[p.id,p]));
    const ordered=[...A.scenes].sort((a,b)=>(a.year||0)-(b.year||0));
    let queue=[],selected=params.get('event')||'AHOM-017',playing=false,timer=0,storyFrame=0;
    root.innerHTML=`<section class="historical-atlas"><header class="atlas-heading"><div><p class="atlas-eyebrow">The chronicles in motion · 1215–1838</p><h1>History, along the river.</h1></div><p>Read an event. Follow its places. Watch the story move through the Brahmaputra valley.</p></header>
      <div class="atlas-workspace"><aside class="atlas-story-panel" aria-label="Historical story">
      <div class="atlas-filters"><label class="atlas-search">Find an event<input type="search" id="atlas-search" placeholder="A king, battle, river or place" value="${esc(params.get('q')||'')}"></label>
      <label>Chapter<select id="atlas-era"><option value="">All eight chapters</option>${A.eras.map(e=>`<option value="${e.id}">${esc(e.title)}</option>`).join('')}</select></label>
      <label>Reading path<select id="atlas-trail"><option value="">Full chronicle</option>${A.trails.map(t=>`<option value="${t.id}">${esc(t.title)}</option>`).join('')}</select></label>
      <details class="atlas-extra-filters"><summary>Filter by place or person</summary><label>Place<select id="atlas-place"><option value="">Every place</option>${A.atlas.sites.filter(p=>p.scenes.length).map(p=>`<option value="${p.id}">${esc(p.name)}</option>`).join('')}</select></label><label>Person<select id="atlas-person"><option value="">Everyone</option>${Object.values(A.people).map(p=>`<option value="${p.id}">${esc(p.name)}</option>`).join('')}</select></label><button class="link" id="atlas-clear" type="button">Reset filters</button></details></div>
      <div class="atlas-transport"><button type="button" id="atlas-prev" aria-label="Previous event">←</button><button type="button" id="atlas-play" aria-pressed="false">▶ Play sequence</button><button type="button" id="atlas-next" aria-label="Next event">→</button><span id="atlas-position" aria-live="polite"></span></div>
      <div class="atlas-story-scroll"><article id="atlas-story"></article><details class="atlas-queue"><summary id="atlas-queue-title">Events in this sequence</summary><ol id="atlas-event-list"></ol></details></div></aside>
      <section class="atlas-map-panel" aria-label="Animated historical map"><div class="atlas-map-heading"><div><span class="atlas-map-kicker" id="atlas-map-era"></span><p id="atlas-map-year"></p></div><div id="atlas-map-focus" aria-live="polite">Places in this event</div></div><div id="chronicles-map"></div>
      <div class="atlas-route-caption" id="atlas-route-caption" aria-live="polite"></div><label class="atlas-scrubber">Move through this sequence<input id="atlas-scrub" type="range" min="0" max="0" step="1" value="0" aria-label="Event in sequence"><span id="atlas-scrub-date"></span></label>
      <details class="atlas-geography-note"><summary>About this map</summary><p>All 39 river paths come from the local APP geographic catalogue. Site pins use its reference coordinates. Animated connections link the places in an account; they do not claim exact historical tracks or unrecorded borders. Some stories do not specify a mappable location. Boundary pills show optional modern reference geography, not Ahom borders; district lines retain the local source’s 33-unit vintage.</p><p>India outline: <a href="https://github.com/datameet/maps/blob/master/Country/README.md" target="_blank" rel="noopener">DataMeet Community Maps / Survey of India derived</a> · CC BY-SA 2.5 / ODbL. <a href="assets/maps/boundaries.json" target="_blank" rel="noopener">Boundary data and provenance</a></p><a href="assets/maps/assam.json" target="_blank" rel="noopener">River geography</a></details></section></div></section>`;
    const $=sel=>root.querySelector(sel);
    const journeyLink=document.createElement('a');journeyLink.className='atlas-journey-link';journeyLink.href='#/map?trail=sukaphaa&event=AHOM-001';journeyLink.textContent='Follow Sukaphaa’s journey →';$('.atlas-heading').after(journeyLink);
    const worldNote=document.createElement('p');worldNote.innerHTML='International outlines: <a href="https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/" target="_blank" rel="noopener">Natural Earth</a>, public domain. Modern country and territory outlines, including coastlines; de facto borders may differ from the separately sourced India outline. This layer downloads when first enabled.';$('.atlas-geography-note').append(worldNote);
    const eventGeography=document.createElement('p');$('.atlas-geography-note').append(eventGeography);
    const q=$('#atlas-search'),era=$('#atlas-era'),trail=$('#atlas-trail'),place=$('#atlas-place'),person=$('#atlas-person');
    era.value=params.get('era')||'';trail.value=params.get('trail')||'';place.value=params.get('place')||'';person.value=params.get('person')||'';
    if(trail.value&&!params.has('event'))selected=A.trails.find(t=>t.id===trail.value)?.scenes[0]||selected;
    const map=window.AhomMap.mount($('#chronicles-map'),A.basemap,A.atlas.sites,id=>{
      $('#atlas-map-focus').textContent=sites[id].name;
      root.querySelectorAll('[data-focus-site]').forEach(b=>b.classList.toggle('is-focused',b.dataset.focusSite===id));
    },A.boundaries);

    function annotate(text,event) {
      const matches=[];
      for(const id of event.sites)for(const alias of sites[id].aliases) {
        for(const match of text.matchAll(new RegExp('(?<!\\w)'+rx(alias)+'(?!\\w)','gi')))matches.push({start:match.index,end:match.index+match[0].length,id,type:'site'});
      }
      for(const id of event.rivers) {
        const river=A.basemap.rivers[id];
        const aliases=[river.name.split('/')[0],id.replaceAll('-',' '),...(id==='dihing'?['Dehing','Dihing']:[])];
        for(const alias of aliases)for(const match of text.matchAll(new RegExp('(?<!\\w)'+rx(alias)+'(?!\\w)','gi')))matches.push({start:match.index,end:match.index+match[0].length,id,type:'river'});
      }
      matches.sort((a,b)=>a.start-b.start||b.end-a.end);let at=0,out='';
      for(const m of matches){if(m.start<at)continue;out+=esc(text.slice(at,m.start))+`<button type="button" class="story-location" data-focus-${m.type}="${m.id}">${esc(text.slice(m.start,m.end))}</button>`;at=m.end;}
      return out+esc(text.slice(at));
    }
    function persist() {
      const sp=new URLSearchParams();if(selected)sp.set('event',selected);
      for(const [key,el] of [['q',q],['era',era],['trail',trail],['place',place],['person',person]])if(el.value)sp.set(key,el.value);
      history.replaceState(null,'','#/map'+(sp.size?'?'+sp:''));
    }
    function stop(){playing=false;clearInterval(timer);$('#atlas-play').textContent='▶ Play sequence';$('#atlas-play').setAttribute('aria-pressed','false');}
    function bringStoryIntoView() {
      if(innerWidth>760)return;
      cancelAnimationFrame(storyFrame);storyFrame=requestAnimationFrame(()=>{const offset=document.querySelector('.bar').getBoundingClientRect().height+$('.atlas-map-panel').getBoundingClientRect().height+12;scrollTo({top:Math.max(0,$('#atlas-story').getBoundingClientRect().top+scrollY-offset),behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});});
    }
    function clock(){clearInterval(timer);timer=setInterval(()=>{const i=queue.findIndex(s=>s.id===selected);if(i>=queue.length-1){stop();return;}choose(queue[i+1].id,true,true);},10000);}
    function choose(id,animate=true,scrollStory=false) {
      if(!scenes[id]||!queue.some(s=>s.id===id))return;
      selected=id;const s=scenes[id],event=A.atlas.events[id],i=queue.findIndex(s=>s.id===id);
      const pic=s.images[0];
      $('#atlas-story').innerHTML=`<p class="atlas-story-date">${esc(s.date)} <span>${esc(eras[s.era].title)}</span></p><h2 tabindex="-1">${esc(s.title)}</h2>${pic?`<figure class="atlas-story-image"><img src="${esc(pic[1])}" alt="${esc(s.alt)}" width="420" height="280"><figcaption>Modern illustrated reconstruction</figcaption></figure>`:''}<p class="atlas-story-summary">${annotate(s.summary,event)}</p>${s.notes?`<p class="quiet">${esc(s.notes)}</p>`:''}<div class="atlas-place-chips">${event.sites.map(id=>`<button type="button" data-focus-site="${id}">${esc(sites[id].name)}</button>`).join('')}${event.rivers.map(id=>`<button type="button" class="river-chip" data-focus-river="${id}">${esc(A.basemap.rivers[id].name)}</button>`).join('')}</div>${!event.sites.length&&!event.rivers.length?'<p class="atlas-unlocated">This record does not specify a mapped place. The valley remains in view for context.</p>':''}${sources(s.sources)}<div class="atlas-story-links"><a href="#/scene/${s.id}">Open the full scene →</a><a href="scenes/${s.id.toLowerCase()}/">Reference page</a></div>`;
      const figure=$('.atlas-story-image');if(figure)$('.atlas-story-summary').after(figure);
      const inlineNav=document.createElement('nav');inlineNav.className='atlas-inline-nav';inlineNav.setAttribute('aria-label','Continue the story');inlineNav.innerHTML=`<button type="button" data-atlas-step="-1" ${i===0?'disabled':''}>← Previous story</button><button type="button" data-atlas-step="1" ${i===queue.length-1?'disabled':''}>Next story →</button>`;$('#atlas-story').append(inlineNav);
      $('#atlas-map-era').textContent=eras[s.era].title;$('#atlas-map-year').textContent=event.mapDate||s.date;
      $('#atlas-map-focus').textContent=event.sites.length?`${event.sites.length} ${event.sites.length===1?'place':'places'} in this event`:event.rivers.length?'Follow the river':'Valley context';
      $('#atlas-route-caption').innerHTML=event.route.length?`<p class="atlas-route-points">${event.route.map(id=>esc(sites[id].name)).join('<span aria-hidden="true"> → </span>')}</p><p>${esc(event.caption||'A connection between the places named in this account.')}</p>`:`<p>${esc(event.caption||'Select an underlined place in the story to look closer on the map.')}</p>`;
      if(event.sources?.length){const refs=document.createElement('details');refs.className='atlas-route-sources';refs.innerHTML='<summary>Journey references</summary>'+event.sources.map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a>`).join('');$('#atlas-route-caption').append(refs);}
      $('#atlas-position').textContent=`${i+1} / ${queue.length}`;$('#atlas-prev').disabled=i===0;$('#atlas-next').disabled=i===queue.length-1;
      eventGeography.textContent=event.caption||'';
      $('#atlas-scrub').value=i;$('#atlas-scrub-date').textContent=s.date;
      root.querySelectorAll('[data-event]').forEach(b=>{b.setAttribute('aria-current',b.dataset.event===id?'true':'false');});
      map.showEvent(event,animate);persist();if(playing)clock();
      $('#atlas-story').parentElement.scrollTop=0;
      if(scrollStory)bringStoryIntoView();
    }
    function filter() {
      stop();const chosen=A.trails.find(t=>t.id===trail.value),pool=chosen?chosen.scenes.map(id=>scenes[id]):ordered,term=q.value.trim().toLowerCase();
      queue=pool.filter(s=>(!era.value||s.era===era.value)&&(!place.value||A.atlas.events[s.id].sites.includes(place.value))&&(!person.value||s.people.includes(person.value))&&[s.title,s.summary,s.date,...s.people.map(id=>[A.people[id].name,A.people[id].as].join(' '))].join(' ').toLowerCase().includes(term));
      $('#atlas-event-list').innerHTML=queue.map(s=>`<li><button type="button" data-event="${s.id}"><span>${esc(s.date)}</span>${esc(s.title)}</button></li>`).join('');
      $('#atlas-queue-title').textContent=`Browse ${queue.length} events in this sequence`;
      $('#atlas-scrub').max=Math.max(0,queue.length-1);$('#atlas-scrub').disabled=!queue.length;$('#atlas-play').disabled=queue.length<2;
      if(queue.length)choose(queue.some(s=>s.id===selected)?selected:queue[0].id);
      else {
        selected='';eventGeography.textContent='';$('#atlas-story').innerHTML='<h2>No matching events</h2><p>Try another name, chapter or place, or reset the filters.</p>';
        $('#atlas-position').textContent='0 / 0';$('#atlas-prev').disabled=true;$('#atlas-next').disabled=true;
        $('#atlas-map-year').textContent='';$('#atlas-map-era').textContent='';$('#atlas-route-caption').textContent='';$('#atlas-scrub-date').textContent='';$('#atlas-map-focus').textContent='Valley context';
        map.showEvent({sites:[],rivers:[],route:[]},false);persist();
      }
    }
    [q,era,trail,place,person].forEach(el=>el.addEventListener('input',filter));
    $('#atlas-clear').onclick=()=>{q.value='';era.value='';trail.value='';place.value='';person.value='';filter();};
    $('#atlas-prev').onclick=()=>{const i=queue.findIndex(s=>s.id===selected);if(i>0)choose(queue[i-1].id,true,true);};
    $('#atlas-next').onclick=()=>{const i=queue.findIndex(s=>s.id===selected);if(i+1<queue.length)choose(queue[i+1].id,true,true);};
    $('#atlas-play').onclick=()=>{if(playing){stop();return;}if(queue.findIndex(s=>s.id===selected)===queue.length-1)choose(queue[0].id);playing=true;$('#atlas-play').textContent='Ⅱ Pause sequence';$('#atlas-play').setAttribute('aria-pressed','true');map.replay();clock();};
    $('#atlas-scrub').addEventListener('input',()=>{stop();if(queue[+$('#atlas-scrub').value])choose(queue[+$('#atlas-scrub').value].id);});
    $('#atlas-scrub').addEventListener('change',bringStoryIntoView);
    const handleClick=e=>{
      const step=e.target.closest('[data-atlas-step]');if(step){const i=queue.findIndex(s=>s.id===selected),next=queue[i+Number(step.dataset.atlasStep)];if(next)choose(next.id,true,true);return;}
      const pick=e.target.closest('[data-event]');if(pick){choose(pick.dataset.event,true,true);return;}
      const spot=e.target.closest('[data-focus-site]');if(spot){map.focusPlace(spot.dataset.focusSite);$('#atlas-map-focus').textContent=sites[spot.dataset.focusSite].name;root.querySelectorAll('[data-focus-site]').forEach(b=>b.classList.toggle('is-focused',b.dataset.focusSite===spot.dataset.focusSite));return;}
      const river=e.target.closest('[data-focus-river]');if(river){map.focusRiver(river.dataset.focusRiver);$('#atlas-map-focus').textContent=A.basemap.rivers[river.dataset.focusRiver].name;}
    };
    root.addEventListener('click',handleClick);
    const visibility=()=>{if(document.hidden)stop();};document.addEventListener('visibilitychange',visibility);
    filter();
    return {destroy(){stop();cancelAnimationFrame(storyFrame);map.destroy();root.removeEventListener('click',handleClick);document.removeEventListener('visibilitychange',visibility);}};
  }
  return {mount};
})();
