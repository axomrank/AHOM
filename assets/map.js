// Geographic map drawn from the local APP district/river dataset. No tile service required.
window.AhomMap = (() => {
  'use strict';
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const PRESETS = {
    assam: [89.4, 23.95, 96.15, 28.15],
    upper: [93.55, 26.35, 96.15, 28.15],
    capitals: [94.35, 26.7, 95.1, 27.2],
  };

  function mount(root, base, places, select) {
    let box = [...PRESETS.assam], selected = '', preset = 'assam', drag = null;
    let width = 1000, height = 570, scale, cosine, centre;
    root.innerHTML = `<div class="map-toolbar" aria-label="Map controls"><div class="map-presets" role="group" aria-label="Map region"><button type="button" data-region="assam">All Assam</button><button type="button" data-region="upper">Upper Assam</button><button type="button" data-region="capitals">Royal capitals</button></div><div class="map-zoom" role="group" aria-label="Map zoom"><button type="button" data-zoom="in" aria-label="Zoom in">+</button><button type="button" data-zoom="out" aria-label="Zoom out">−</button><button type="button" data-region="assam" aria-label="Reset map view">Reset</button></div></div>
      <div class="geographic-map"><svg class="geographic-canvas" role="group" aria-label="Geographic map of Assam with historical places" tabindex="0"></svg><p class="map-hint">Drag to pan · Use + / − to zoom</p></div>
      <div class="map-key"><span><i class="key-district"></i>Districts</span><span><i class="key-river"></i>Rivers</span><span><i class="key-place"></i>Historical places</span></div>
      <div class="map-place-list" role="group" aria-label="Find scenes by place">${places.map((p,i)=>`<button type="button" data-map-place="${p.id}" aria-pressed="false"><span class="place-number">${i+1}</span><span>${esc(p.name)}<small>${p.scenes.length} scenes</small></span></button>`).join('')}</div>
      <p class="map-attribution">District and river geometry from the local APP map catalogue, imported from <cite>Dist + Rivers (simplified).kmz</cite>. District outlines are a modern reference; site locations follow the local catalogue. <a href="assets/maps/assam.json" target="_blank" rel="noopener">View map data</a>.</p>`;
    const svg = root.querySelector('svg');

    function project([lat,lon]) {
      return [width/2+(lon-centre[0])*cosine*scale, height/2-(lat-centre[1])*scale];
    }
    const path = (points, close=false) => 'M'+points.map(p=>project(p).map(n=>n.toFixed(2)).join(',')).join('L')+(close?'Z':'');
    const inView = ([x,y], pad=20) => x>pad && y>pad && x<width-pad && y<height-pad;

    function draw() {
      width = Math.max(280,root.querySelector('.geographic-map').clientWidth);
      height = width<600 ? 420 : Math.round(width*.57);
      centre=[(box[0]+box[2])/2,(box[1]+box[3])/2];
      cosine=Math.cos(centre[1]*Math.PI/180);
      scale=Math.min((width-36)/((box[2]-box[0])*cosine),(height-36)/(box[3]-box[1]));
      svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
      svg.setAttribute('width',width);svg.setAttribute('height',height);
      svg.dataset.bounds=box.join(',');
      let out=`<rect class="map-ground" width="${width}" height="${height}"/>`;
      out+=Object.entries(base.districts).map(([id,d])=>`<path class="geo-district" data-district="${id}" d="${d.rings.map(r=>path(r,true)).join(' ')}"><title>${esc(d.name)} · modern district</title></path>`).join('');
      out+=Object.entries(base.rivers).map(([id,r])=>`<path class="geo-river ${id==='brahmaputra'?'geo-main-river':''}" data-river="${id}" d="${path(r.pts)}"><title>${esc(r.name)}</title></path>`).join('');
      const main=base.rivers.brahmaputra;
      const visible=main.pts.map(project).filter(p=>inView(p,45));
      if(visible.length) {
        const p=visible[Math.floor(visible.length*.5)];
        out+=`<text class="geo-river-label" x="${p[0]}" y="${p[1]-12}">Brahmaputra</text>`;
      }
      // Numbered pins stay at their geographic positions. Labels use leader lines to avoid overlaps.
      const labels=[];
      const offsets=[[12,-20],[12,24],[-12,-20],[-12,24],[12,-48],[-12,48],[12,50],[-12,-50],[35,-75],[-35,75]];
      for(const [i,p] of places.entries()) {
        const [x,y]=project(p.geo);
        if(!inView([x,y],8))continue;
        const name=p.mapLabel || p.name.split(' / ')[0];
        const tw=name.length*7+14;
        let label=null;
        for(const [dx,dy] of offsets) {
          const lx=x+dx, ly=y+dy, left=dx<0?lx-tw:lx;
          const rect=[left,ly-15,left+tw,ly+6];
          if(rect[0]<4||rect[2]>width-4||rect[1]<35||rect[3]>height-35)continue;
          if(labels.some(r=>rect[0]<r[2]+6&&rect[2]>r[0]-6&&rect[1]<r[3]+6&&rect[3]>r[1]-6))continue;
          // Keep labels away from every other place marker.
          if(places.some(other=>{if(other===p)return false;const [px,py]=project(other.geo);return px>rect[0]-10&&px<rect[2]+10&&py>rect[1]-10&&py<rect[3]+10;}))continue;
          label={lx,ly,left,rect,anchor:dx<0?'end':'start'};labels.push(rect);break;
        }
        const active=selected===p.id;
        if(label)out+=`<g class="geo-place-label" aria-hidden="true"><path d="M${x},${y}L${label.lx},${label.ly-5}"/><rect x="${label.left-3}" y="${label.ly-16}" width="${tw+6}" height="23" rx="3"/><text x="${label.lx}" y="${label.ly}" text-anchor="${label.anchor}">${esc(name)}</text></g>`;
        out+=`<g class="geo-pin ${active?'is-selected':''}" role="button" tabindex="0" data-map-place="${p.id}" aria-label="${esc(p.name)}, ${p.scenes.length} scenes" aria-pressed="${active}"><circle class="geo-hit" cx="${x}" cy="${y}" r="18"/><circle class="geo-dot" cx="${x}" cy="${y}" r="11"/><text x="${x}" y="${y+4}" aria-hidden="true">${i+1}</text></g>`;
      }
      out+=`<g class="map-north" transform="translate(${width-25},25)" aria-hidden="true"><path d="M0,12V-4M-4,1L0,-5L4,1"/><text y="-10">N</text></g>`;
      svg.innerHTML=out;
      root.querySelectorAll('.map-presets [data-region]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.region===preset)));
      root.querySelectorAll('.map-place-list [data-map-place]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mapPlace===selected)));
    }

    function setSelected(id) {
      if(selected===id)return;
      const focusedPin=svg.contains(document.activeElement) ? document.activeElement.dataset.mapPlace : null;
      selected=id;
      const p=places.find(p=>p.id===id);
      if(p && !inView(project(p.geo),25)) {
        const dx=(box[2]-box[0])/2,dy=(box[3]-box[1])/2;
        box=[p.geo[1]-dx,p.geo[0]-dy,p.geo[1]+dx,p.geo[0]+dy];preset='';
      }
      draw();
      if(focusedPin)svg.querySelector(`[data-map-place="${focusedPin}"]`)?.focus();
    }
    function activate(event) {
      const pin=event.target.closest('[data-map-place]');
      if(pin) {select(pin.dataset.mapPlace);return;}
      const region=event.target.closest('[data-region]');
      if(region) {preset=region.dataset.region;box=[...PRESETS[preset]];draw();return;}
      const zoom=event.target.closest('[data-zoom]');
      if(zoom) {
        const factor=zoom.dataset.zoom==='in'?.65:1/.65;
        const dx=Math.min(12,Math.max(.06,(box[2]-box[0])*factor))/2;
        const dy=dx*(box[3]-box[1])/(box[2]-box[0]);
        box=[centre[0]-dx,centre[1]-dy,centre[0]+dx,centre[1]+dy];preset='';draw();
      }
    }
    root.addEventListener('click',activate);
    function keyboard(event) {
      if(event.target===svg && ['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key)) {
        event.preventDefault();
        const dx=(box[2]-box[0])*.1*(event.key==='ArrowLeft'?-1:event.key==='ArrowRight'?1:0);
        const dy=(box[3]-box[1])*.1*(event.key==='ArrowDown'?-1:event.key==='ArrowUp'?1:0);
        box=[box[0]+dx,box[1]+dy,box[2]+dx,box[3]+dy];preset='';draw();return;
      }
      if(event.target.closest('[data-map-place]') && ['Enter',' '].includes(event.key)) {
        if(event.target.tagName==='BUTTON')return; // Native HTML buttons already activate on keypress.
        event.preventDefault();activate(event);
      }
    }
    root.addEventListener('keydown',keyboard);
    svg.addEventListener('pointerdown',event=>{
      if(event.target.closest('[data-map-place]') || event.button!==0)return;
      drag={x:event.clientX,y:event.clientY,box:[...box],scale,cosine};
      svg.setPointerCapture(event.pointerId);svg.classList.add('is-panning');
    });
    svg.addEventListener('pointermove',event=>{
      if(!drag)return;
      const dx=(event.clientX-drag.x)/(drag.scale*drag.cosine),dy=(event.clientY-drag.y)/drag.scale;
      box=[drag.box[0]-dx,drag.box[1]+dy,drag.box[2]-dx,drag.box[3]+dy];preset='';draw();
    });
    const stop=()=>{drag=null;svg.classList.remove('is-panning');};
    svg.addEventListener('pointerup',stop);svg.addEventListener('pointercancel',stop);
    const observer=new ResizeObserver(()=>draw());observer.observe(root.querySelector('.geographic-map'));
    draw();
    return {setSelected,destroy(){observer.disconnect();}};
  }
  return {mount};
})();
