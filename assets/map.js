// Historical map renderer: local river geography, animated camera, event places and routes.
window.AhomMap = (() => {
  'use strict';
  const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const PRESETS={assam:[89.2,24,96.25,28.2],upper:[93.5,26.35,96.2,28.15],india:[67,6,98,38]};
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');

  function mount(root,base,sites,onPlace,boundaries) {
    const byId=Object.fromEntries(sites.map(p=>[p.id,p]));
    const layers={assam:false,india:false,district:false};
    let box=[...PRESETS.assam], event={sites:[],rivers:[],route:[]}, focused='', focusedRiver='', drag=null;
    let width=900,height=550,centre=[92.7,26],cosine=1,scale=1;
    let cameraFrame=0,routeFrame=0,routeAnimation=null,dead=false,cameraMoving=false;
    root.innerHTML=`<div class="atlas-toolbar"><div class="map-presets" role="group" aria-label="Map region"><button type="button" data-region="event">Follow event</button><button type="button" data-region="assam">Whole valley</button><button type="button" data-region="upper">Upper Assam</button></div><div class="map-zoom" role="group" aria-label="Map zoom"><button type="button" data-zoom="in" aria-label="Zoom in">+</button><button type="button" data-zoom="out" aria-label="Zoom out">−</button><button type="button" data-replay aria-label="Replay map animation">↻</button></div></div><div class="geographic-map"><svg class="geographic-canvas" role="group" aria-label="Historical places and rivers. Drag or use arrow keys to pan." tabindex="0"></svg><p class="map-hint">Drag to explore · + / − to zoom</p><span class="atlas-compass" aria-hidden="true">N<br>↑</span></div><div class="atlas-map-key"><span><i class="key-river"></i>Rivers</span><span><i class="key-place"></i>Event places</span><span><i class="key-route"></i>Story connection</span></div>`;
    const svg=root.querySelector('svg'),frame=root.querySelector('.geographic-map');
    const controls=document.createElement('div');
    controls.className='atlas-boundary-pills';
    controls.setAttribute('role','group');controls.setAttribute('aria-label','Modern reference boundaries');
    controls.innerHTML='<span class="boundary-label">Boundaries</span>'+Object.keys(layers).map(id=>`<button type="button" data-boundary="${id}" aria-pressed="false"><i aria-hidden="true"></i>${id==='district'?'District':id==='india'?'India':'Assam'}</button>`).join('')+'<button type="button" class="boundary-overview" data-region="india" hidden>View India ↗</button>';
    frame.before(controls);
    const project=([lat,lon])=>[width/2+(lon-centre[0])*cosine*scale,height/2-(lat-centre[1])*scale];
    const inside=([x,y],pad=30)=>x>pad&&x<width-pad&&y>pad&&y<height-pad;
    const line=points=>'M'+points.map(p=>project(p).map(v=>v.toFixed(2)).join(',')).join('L');
    function boundaryMarkup() {
      let content='';
      if(layers.district)for(const [id,d] of Object.entries(base.districts))content+=`<path class="atlas-boundary boundary-district" data-district="${id}" d="${d.rings.map(r=>line(r)+'Z').join('')}"><title>${esc(d.name)} district · source reference geography</title></path>`;
      for(const id of ['india','assam'])if(layers[id])content+=`<path class="atlas-boundary boundary-${id}" data-outline="${id}" d="${boundaries[id].rings.map(r=>line(r)+'Z').join('')}"><title>${esc(boundaries[id].name)} · modern reference</title></path>`;
      return content;
    }

    function stopAnimations(){cancelAnimationFrame(cameraFrame);cancelAnimationFrame(routeFrame);routeAnimation?.cancel();routeAnimation=null;cameraMoving=false;}
    function routePoints() {
      const points=(event.route||[]).map(id=>byId[id].geo);
      if(event.mode!=='river'||points.length<2)return points;
      const river=base.rivers.brahmaputra.pts;
      const nearest=p=>river.reduce((best,q,i)=>{
        const d=(p[0]-q[0])**2+((p[1]-q[1])*Math.cos(p[0]*Math.PI/180))**2;
        return d<best.d?{d,i}:best;
      },{d:Infinity,i:0}).i;
      const out=[points[0]];
      for(let n=1;n<points.length;n++) {
        const a=nearest(points[n-1]),b=nearest(points[n]);
        const segment=river.slice(Math.min(a,b),Math.max(a,b)+1);
        out.push(...(a>b?segment.reverse():segment),points[n]);
      }
      return out;
    }
    function eventBox() {
      let points=[...(event.sites||[]).map(id=>byId[id].geo),...routePoints()];
      if(!points.length)for(const id of event.rivers||[])points.push(...base.rivers[id].pts);
      if(!points.length)return [...PRESETS.assam];
      const lat=points.map(p=>p[0]),lon=points.map(p=>p[1]);
      const cx=(Math.min(...lon)+Math.max(...lon))/2,cy=(Math.min(...lat)+Math.max(...lat))/2;
      const dx=Math.max(Math.max(...lon)-Math.min(...lon),points.length===1?1.2:.12)*.7;
      const dy=Math.max(Math.max(...lat)-Math.min(...lat),points.length===1?.7:.09)*.75;
      return [cx-dx,cy-dy,cx+dx,cy+dy];
    }
    function draw(animate=false) {
      if(dead)return;
      width=Math.max(280,frame.clientWidth);height=Math.max(220,frame.clientHeight);
      centre=[(box[0]+box[2])/2,(box[1]+box[3])/2];cosine=Math.cos(centre[1]*Math.PI/180);
      scale=Math.min((width-90)/((box[2]-box[0])*cosine),(height-100)/(box[3]-box[1]));
      svg.setAttribute('viewBox',`0 0 ${width} ${height}`);svg.dataset.bounds=box.join(',');
      const activeRivers=new Set(event.rivers||[]);
      if(focusedRiver)activeRivers.add(focusedRiver);
      if(event.mode==='river'&&event.route?.length)activeRivers.add('brahmaputra');
      let content='<defs><radialGradient id="atlas-paper" cx="40%" cy="35%" r="85%"><stop offset="0" stop-color="#fbf7eb"/><stop offset="1" stop-color="#eae0c6"/></radialGradient><marker id="atlas-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,1L9,5L0,9" fill="none" stroke="currentColor" stroke-width="1.6"/></marker></defs>';
      content+=`<rect class="map-ground" width="${width}" height="${height}"/>`;
      content+=`<g class="atlas-boundaries">${boundaryMarkup()}</g>`;
      for(const [id,r] of Object.entries(base.rivers)) {
        const d=line(r.pts),main=id==='brahmaputra',active=activeRivers.has(id);
        content+=`<g class="atlas-river ${main?'is-main':''} ${active?'is-highlighted':''}" data-river="${id}"><title>${esc(r.name)}</title><path class="river-bed" d="${d}"/><path class="river-ink" d="${d}"/></g>`;
      }
      const points=routePoints();
      if(points.length>1)content+=`<path class="atlas-route-halo" d="${line(points)}" opacity="${cameraMoving?0:1}"/><path class="atlas-route" d="${line(points)}" opacity="${cameraMoving?0:1}" marker-end="url(#atlas-arrow)"/><circle class="route-traveller" r="5" visibility="hidden"/>`;
      const occupied=[];
      const avoid=(rect,pad=8)=>occupied.some(r=>rect[0]<r[2]+pad&&rect[2]>r[0]-pad&&rect[1]<r[3]+pad&&rect[3]>r[1]-pad);
      for(const id of [...new Set(['brahmaputra',...activeRivers,'dikhou','dihing','manas','dhansiri-south'])]) {
        const river=base.rivers[id];if(!river)continue;
        const points=river.pts.map(project).filter(p=>inside(p,50));
        if(!points.length || (!activeRivers.has(id)&&id!=='brahmaputra'&&box[2]-box[0]>4))continue;
        for(const t of [.5,.25,.75]) {
          const [x,y]=points[Math.floor((points.length-1)*t)],name=river.name.replace(/\/.*/,'');
          const rect=[x-name.length*3.5,y-22,x+name.length*3.5,y];
          if(avoid(rect))continue;occupied.push(rect);
          content+=`<text class="geo-river-label" x="${x}" y="${y-8}">${esc(name)}</text>`;break;
        }
      }
      const active=(event.sites||[]).map(id=>byId[id]);
      for(const id of ['guwahati','charaideo','sadiya','jorhat','dimapur']) {
        if(active.some(p=>p.id===id))continue;
        const [x,y]=project(byId[id].geo);if(inside([x,y],10))content+=`<circle class="atlas-reference-dot" cx="${x}" cy="${y}" r="2.5"/>`;
      }
      const pinPoints=active.map(p=>project(p.geo));
      for(const [i,p] of active.entries()) {
        const [x,y]=pinPoints[i];if(!inside([x,y],10))continue;
        const name=p.name.replace(' Stone Bridge',' Bridge'),tw=Math.max(50,name.length*7.2+18);
        let label=null;
        for(const [dx,dy] of [[15,-23],[15,30],[-15,-23],[-15,30],[15,-52],[-15,54],[40,-80],[-40,80]]) {
          const lx=x+dx,ly=y+dy,left=dx<0?lx-tw:lx,rect=[left,ly-17,left+tw,ly+7];
          if(rect[0]<4||rect[2]>width-4||rect[1]<10||rect[3]>height-24||avoid(rect))continue;
          if(pinPoints.some((point,j)=>j!==i&&point[0]>rect[0]-12&&point[0]<rect[2]+12&&point[1]>rect[1]-12&&point[1]<rect[3]+12))continue;
          label={lx,ly,left,anchor:dx<0?'end':'start'};occupied.push(rect);break;
        }
        if(label)content+=`<g class="geo-place-label" aria-hidden="true"><path d="M${x},${y}L${label.lx},${label.ly-5}"/><rect x="${label.left-3}" y="${label.ly-18}" width="${tw+6}" height="26" rx="4"/><text x="${label.lx}" y="${label.ly}" text-anchor="${label.anchor}">${esc(name)}</text></g>`;
        content+=`<g class="geo-pin atlas-event-pin ${focused===p.id?'is-selected':''} ${animate?'animate-pin':''}" role="button" tabindex="0" data-map-place="${p.id}" aria-label="${esc(p.name)}" aria-pressed="${focused===p.id}"><circle class="geo-hit" cx="${x}" cy="${y}" r="20"/><circle class="event-pulse" cx="${x}" cy="${y}" r="15" style="transform-origin:${x}px ${y}px;animation-delay:${i*.18}s"/><circle class="geo-dot" cx="${x}" cy="${y}" r="9"/><circle class="event-pin-centre" cx="${x}" cy="${y}" r="2.5"/></g>`;
      }
      svg.innerHTML=content;
      if(animate)animateRoute();
    }
    function animateRoute() {
      const route=svg.querySelector('.atlas-route');if(!route||reduced.matches)return;
      routeAnimation?.cancel();cancelAnimationFrame(routeFrame);
      const length=route.getTotalLength(),duration=3600;
      routeAnimation=route.animate([{strokeDasharray:`${length} ${length}`,strokeDashoffset:length},{strokeDasharray:`${length} ${length}`,strokeDashoffset:0}],{duration,easing:'linear'});
      const traveller=svg.querySelector('.route-traveller'),start=performance.now();
      const tick=now=>{
        if(dead||!route.isConnected)return;
        const t=Math.min(1,(now-start)/duration),p=route.getPointAtLength(length*t);
        traveller.setAttribute('cx',p.x);traveller.setAttribute('cy',p.y);traveller.setAttribute('visibility','visible');
        if(t<1)routeFrame=requestAnimationFrame(tick);else traveller.setAttribute('visibility','hidden');
      };
      routeFrame=requestAnimationFrame(tick);
    }
    function flyTo(target,animate=true) {
      stopAnimations();
      if(!animate||reduced.matches){box=[...target];draw(animate);return;}
      cameraMoving=true;
      const from=[...box],start=performance.now();
      const tick=now=>{
        const t=Math.min(1,(now-start)/850),ease=1-(1-t)**3;
        box=from.map((v,i)=>v+(target[i]-v)*ease);draw(false);
        if(t<1)cameraFrame=requestAnimationFrame(tick);else {cameraMoving=false;draw(true);}
      };
      cameraFrame=requestAnimationFrame(tick);
    }
    function showEvent(value,animate=true){event=value;focused='';focusedRiver='';flyTo(eventBox(),animate);}
    function focusPlace(id){if(!byId[id])return;focused=id;const [lat,lon]=byId[id].geo;flyTo([lon-.06,lat-.04,lon+.06,lat+.04]);}
    function focusRiver(id){if(!base.rivers[id])return;focusedRiver=id;const pts=base.rivers[id].pts,lat=pts.map(p=>p[0]),lon=pts.map(p=>p[1]);flyTo([Math.min(...lon)-.2,Math.min(...lat)-.2,Math.max(...lon)+.2,Math.max(...lat)+.2]);}
    function replay(){focused='';focusedRiver='';flyTo(eventBox());}
    function click(e) {
      const layer=e.target.closest('[data-boundary]');if(layer){const id=layer.dataset.boundary;layers[id]=!layers[id];layer.setAttribute('aria-pressed',String(layers[id]));root.querySelector('.boundary-overview').hidden=!layers.india;svg.querySelector('.atlas-boundaries').innerHTML=boundaryMarkup();return;}
      const pin=e.target.closest('[data-map-place]');if(pin){focusPlace(pin.dataset.mapPlace);onPlace?.(pin.dataset.mapPlace);return;}
      const preset=e.target.closest('[data-region]');if(preset){if(preset.dataset.region==='event')replay();else flyTo(PRESETS[preset.dataset.region]);return;}
      if(e.target.closest('[data-replay]')){replay();return;}
      const zoom=e.target.closest('[data-zoom]');if(zoom){const f=zoom.dataset.zoom==='in'?.65:1/.65,dx=Math.max(.06,Math.min(40,(box[2]-box[0])*f))/2,dy=dx*(box[3]-box[1])/(box[2]-box[0]);flyTo([centre[0]-dx,centre[1]-dy,centre[0]+dx,centre[1]+dy]);}
    }
    root.addEventListener('click',click);
    root.addEventListener('keydown',e=>{
      if(e.target.closest('[data-map-place]')&&['Enter',' '].includes(e.key)){e.preventDefault();click(e);}
      if(e.target===svg&&['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){
        e.preventDefault();stopAnimations();const dx=(box[2]-box[0])*.1*(e.key==='ArrowLeft'?-1:e.key==='ArrowRight'?1:0),dy=(box[3]-box[1])*.1*(e.key==='ArrowDown'?-1:e.key==='ArrowUp'?1:0);box=[box[0]+dx,box[1]+dy,box[2]+dx,box[3]+dy];draw();
      }
    });
    svg.addEventListener('pointerdown',e=>{if(e.target.closest('[data-map-place]')||e.button!==0)return;stopAnimations();drag={x:e.clientX,y:e.clientY,box:[...box],scale,cosine};svg.setPointerCapture(e.pointerId);svg.classList.add('is-panning');});
    svg.addEventListener('pointermove',e=>{if(!drag)return;const dx=(e.clientX-drag.x)/(drag.scale*drag.cosine),dy=(e.clientY-drag.y)/drag.scale;box=[drag.box[0]-dx,drag.box[1]+dy,drag.box[2]-dx,drag.box[3]+dy];draw();});
    const release=()=>{drag=null;svg.classList.remove('is-panning');};svg.addEventListener('pointerup',release);svg.addEventListener('pointercancel',release);
    const observer=new ResizeObserver(()=>{if(frame.clientWidth===width&&Math.max(220,frame.clientHeight)===height)return;stopAnimations();draw();});observer.observe(frame);draw();
    return {showEvent,focusPlace,focusRiver,replay,destroy(){dead=true;stopAnimations();observer.disconnect();}};
  }
  return {mount};
})();
