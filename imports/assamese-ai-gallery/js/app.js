/**
 * Assamese Heritage & Legends — AI Art Gallery
 * Interactive Application Logic
 */

(function () {
  'use strict';

  // Application State
  let galleryData = { categories: {}, items: [] };
  let filteredItems = [];
  let currentCategory = 'all';
  let activeTag = null;
  let searchQuery = '';
  let currentSort = 'featured';
  let currentLightboxIndex = -1;
  let zoomLevel = 1;

  // DOM Elements
  const themeToggle = document.getElementById('themeToggle');
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const categoryFilters = document.getElementById('categoryFilters');
  const categorySummary = document.getElementById('categorySummary');
  const sortSelect = document.getElementById('sortSelect');
  const viewBtns = document.querySelectorAll('.view-btn');
  const galleryGrid = document.getElementById('galleryGrid');
  const resultsCount = document.getElementById('resultsCount');
  const activeTagsContainer = document.getElementById('activeTagsContainer');
  const activeTagChip = document.getElementById('activeTagChip');
  const clearTagFilter = document.getElementById('clearTagFilter');
  const emptyState = document.getElementById('emptyState');
  const resetFiltersBtn = document.getElementById('resetFiltersBtn');

  // Lightbox Elements
  const lightboxModal = document.getElementById('lightboxModal');
  const lightboxOverlay = document.getElementById('lightboxOverlay');
  const lightboxClose = document.getElementById('lightboxClose');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  const lightboxImg = document.getElementById('lightboxImg');
  const slideIndicator = document.getElementById('slideIndicator');
  const modalCategoryBadge = document.getElementById('modalCategoryBadge');
  const modalTitle = document.getElementById('modalTitle');
  const modalDescription = document.getElementById('modalDescription');
  const modalTags = document.getElementById('modalTags');
  const downloadBtn = document.getElementById('downloadBtn');
  const copyLinkBtn = document.getElementById('copyLinkBtn');
  const copyLinkText = document.getElementById('copyLinkText');
  const zoomInBtn = document.getElementById('zoomInBtn');
  const zoomOutBtn = document.getElementById('zoomOutBtn');
  const zoomResetBtn = document.getElementById('zoomResetBtn');

  // About Modal Elements
  const aboutBtn = document.getElementById('aboutBtn');
  const aboutModal = document.getElementById('aboutModal');
  const aboutOverlay = document.getElementById('aboutOverlay');
  const aboutClose = document.getElementById('aboutClose');
  const toast = document.getElementById('toast');

  // Initialize App
  async function init() {
    initTheme();
    setupEventListeners();
    await loadGalleryData();
    checkUrlHash();
  }

  // Theme Management
  function initTheme() {
    const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    document.documentElement.setAttribute('data-theme', savedTheme);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  }

  // Load Data
  async function loadGalleryData() {
    try {
      const response = await fetch('data/gallery.json');
      if (!response.ok) throw new Error('Failed to load gallery data');
      galleryData = await response.json();
      renderCategorySummary();
      renderCategoryFilters();
      applyFiltersAndSort();
    } catch (err) {
      console.error('Error fetching gallery.json:', err);
      resultsCount.textContent = 'Error loading gallery data. Please refresh.';
    }
  }

  // Render Category Quick Stat Summary in Hero
  function renderCategorySummary() {
    if (!categorySummary || !galleryData.categories) return;
    
    let html = '';
    const counts = getCategoryCounts();

    Object.entries(galleryData.categories).forEach(([key, cat]) => {
      const count = counts[key] || 0;
      html += `
        <div class="cat-stat-card" data-category="${key}" title="${cat.description}">
          <span class="cat-stat-icon">${cat.icon}</span>
          <span class="cat-stat-name">${cat.name}</span>
          <span class="cat-stat-count">${count}</span>
        </div>
      `;
    });

    categorySummary.innerHTML = html;

    // Attach click listeners to hero stat cards
    categorySummary.querySelectorAll('.cat-stat-card').forEach(card => {
      card.addEventListener('click', () => {
        const cat = card.dataset.category;
        setCategory(cat);
        scrollToControls();
      });
    });
  }

  // Render Filter Pills in Control Panel
  function renderCategoryFilters() {
    if (!categoryFilters || !galleryData.categories) return;

    const counts = getCategoryCounts();
    let html = `
      <button class="cat-pill active" data-category="all" role="tab" aria-selected="true">
        <span>🌟 All Artworks</span>
        <span class="pill-count">(${galleryData.items.length})</span>
      </button>
    `;

    Object.entries(galleryData.categories).forEach(([key, cat]) => {
      const count = counts[key] || 0;
      html += `
        <button class="cat-pill" data-category="${key}" role="tab" aria-selected="false">
          <span>${cat.icon} ${cat.name}</span>
          <span class="pill-count">(${count})</span>
        </button>
      `;
    });

    categoryFilters.innerHTML = html;

    // Attach click listeners to filter pills
    categoryFilters.querySelectorAll('.cat-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        setCategory(pill.dataset.category);
      });
    });
  }

  function getCategoryCounts() {
    const counts = {};
    if (!galleryData.items) return counts;
    galleryData.items.forEach(item => {
      counts[item.category] = (counts[item.category] || 0) + 1;
    });
    return counts;
  }

  function setCategory(catKey) {
    currentCategory = catKey;

    // Update pill UI
    if (categoryFilters) {
      categoryFilters.querySelectorAll('.cat-pill').forEach(pill => {
        const isActive = pill.dataset.category === catKey;
        pill.classList.toggle('active', isActive);
        pill.setAttribute('aria-selected', isActive ? 'true' : 'false');
      });
    }

    applyFiltersAndSort();
  }

  function setTag(tag) {
    activeTag = tag;
    if (activeTag) {
      activeTagsContainer.style.display = 'flex';
      activeTagChip.textContent = `# ${tag}`;
    } else {
      activeTagsContainer.style.display = 'none';
    }
    applyFiltersAndSort();
    scrollToControls();
  }

  function clearTag() {
    setTag(null);
  }

  function scrollToControls() {
    const el = document.querySelector('.control-panel');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  // Filter and Sort Engine
  function applyFiltersAndSort() {
    if (!galleryData.items) return;

    let items = [...galleryData.items];

    // 1. Category Filter
    if (currentCategory !== 'all') {
      items = items.filter(item => item.category === currentCategory);
    }

    // 2. Tag Filter
    if (activeTag) {
      items = items.filter(item => 
        item.tags && item.tags.some(t => t.toLowerCase() === activeTag.toLowerCase())
      );
    }

    // 3. Search Query Filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      items = items.filter(item => {
        const matchTitle = item.title.toLowerCase().includes(q);
        const matchDesc = item.description.toLowerCase().includes(q);
        const matchCat = item.categoryName.toLowerCase().includes(q);
        const matchTags = item.tags && item.tags.some(t => t.toLowerCase().includes(q));
        return matchTitle || matchDesc || matchCat || matchTags;
      });
    }

    // 4. Sorting
    if (currentSort === 'title-asc') {
      items.sort((a, b) => a.title.localeCompare(b.title));
    } else if (currentSort === 'title-desc') {
      items.sort((a, b) => b.title.localeCompare(a.title));
    } else if (currentSort === 'category') {
      items.sort((a, b) => a.categoryName.localeCompare(b.categoryName) || a.title.localeCompare(b.title));
    } else if (currentSort === 'random') {
      items.sort(() => Math.random() - 0.5);
    }

    filteredItems = items;
    renderGallery();
  }

  // Render Gallery Grid
  function renderGallery() {
    if (!galleryGrid) return;

    // Update Result count
    const total = galleryData.items.length;
    const current = filteredItems.length;
    resultsCount.textContent = `Showing ${current} of ${total} artworks`;

    if (current === 0) {
      galleryGrid.innerHTML = '';
      emptyState.style.display = 'block';
      return;
    }

    emptyState.style.display = 'none';

    let html = '';
    filteredItems.forEach((item, index) => {
      const tagsHtml = item.tags ? item.tags.slice(0, 3).map(tag => 
        `<span class="card-tag" data-tag="${escapeHtml(tag)}">#${escapeHtml(tag)}</span>`
      ).join('') : '';

      html += `
        <article class="gallery-card" data-index="${index}" data-id="${item.id}" tabindex="0">
          <div class="card-media">
            <span class="card-category-badge">
              <span>${item.categoryIcon}</span>
              <span>${item.categoryName}</span>
            </span>
            <img class="card-img" src="${item.imagePath}" alt="${escapeHtml(item.title)}" loading="lazy" />
            <div class="card-hover-actions">
              <button class="action-pill view-art-btn" data-index="${index}" title="View Fullscreen">
                <span>🔍 Expand View</span>
              </button>
            </div>
          </div>
          <div class="card-body">
            <h3 class="card-title">${escapeHtml(item.title)}</h3>
            <p class="card-description">${escapeHtml(item.description)}</p>
            <div class="card-tags">
              ${tagsHtml}
            </div>
          </div>
        </article>
      `;
    });

    galleryGrid.innerHTML = html;

    // Attach Card Click & Tag Click Listeners
    galleryGrid.querySelectorAll('.gallery-card').forEach(card => {
      const idx = parseInt(card.dataset.index, 10);
      
      card.addEventListener('click', (e) => {
        // If clicking a tag inside card
        if (e.target.classList.contains('card-tag')) {
          e.stopPropagation();
          setTag(e.target.dataset.tag);
          return;
        }
        openLightbox(idx);
      });

      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openLightbox(idx);
        }
      });
    });
  }

  // Lightbox Modal
  function openLightbox(index) {
    if (index < 0 || index >= filteredItems.length) return;
    currentLightboxIndex = index;
    zoomLevel = 1;
    updateZoom();

    const item = filteredItems[currentLightboxIndex];
    if (!item) return;

    lightboxImg.src = item.imagePath;
    lightboxImg.alt = item.title;
    slideIndicator.textContent = `${currentLightboxIndex + 1} / ${filteredItems.length}`;
    
    modalCategoryBadge.innerHTML = `<span>${item.categoryIcon}</span><span>${item.categoryName}</span>`;
    modalTitle.textContent = item.title;
    modalDescription.textContent = item.description;

    // Tags
    if (item.tags && item.tags.length) {
      modalTags.innerHTML = item.tags.map(t => 
        `<span class="tag-chip modal-tag-item" data-tag="${escapeHtml(t)}">#${escapeHtml(t)}</span>`
      ).join('');
      
      modalTags.querySelectorAll('.modal-tag-item').forEach(tagEl => {
        tagEl.addEventListener('click', () => {
          closeLightbox();
          setTag(tagEl.dataset.tag);
        });
      });
    } else {
      modalTags.innerHTML = '<span class="text-muted">None</span>';
    }

    // Download button
    downloadBtn.href = item.imagePath;
    downloadBtn.setAttribute('download', item.imagePath.split('/').pop());

    // URL Hash update
    history.replaceState(null, '', `#${item.id}`);

    lightboxModal.classList.add('active');
    lightboxModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    lightboxModal.classList.remove('active');
    lightboxModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    currentLightboxIndex = -1;
    zoomLevel = 1;
    updateZoom();
    history.replaceState(null, '', window.location.pathname + window.location.search);
  }

  function nextImage() {
    if (currentLightboxIndex < filteredItems.length - 1) {
      openLightbox(currentLightboxIndex + 1);
    } else {
      openLightbox(0); // loop
    }
  }

  function prevImage() {
    if (currentLightboxIndex > 0) {
      openLightbox(currentLightboxIndex - 1);
    } else {
      openLightbox(filteredItems.length - 1); // loop
    }
  }

  // Lightbox Zoom
  function updateZoom() {
    lightboxImg.style.transform = `scale(${zoomLevel})`;
    zoomResetBtn.textContent = `${Math.round(zoomLevel * 100)}%`;
  }

  function zoomIn() {
    if (zoomLevel < 3) {
      zoomLevel = Math.min(3, zoomLevel + 0.25);
      updateZoom();
    }
  }

  function zoomOut() {
    if (zoomLevel > 0.5) {
      zoomLevel = Math.max(0.5, zoomLevel - 0.25);
      updateZoom();
    }
  }

  function zoomReset() {
    zoomLevel = 1;
    updateZoom();
  }

  // Toast & Copy Link
  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2800);
  }

  function copyCurrentArtworkLink() {
    const item = filteredItems[currentLightboxIndex];
    if (!item) return;

    const url = `${window.location.origin}${window.location.pathname}#${item.id}`;
    navigator.clipboard.writeText(url).then(() => {
      copyLinkText.textContent = 'Copied!';
      showToast('Artwork URL copied to clipboard!');
      setTimeout(() => {
        copyLinkText.textContent = 'Copy Link';
      }, 2000);
    }).catch(() => {
      showToast('Could not copy link.');
    });
  }

  // Check URL hash for direct links
  function checkUrlHash() {
    const hash = window.location.hash.replace('#', '').trim();
    if (!hash) return;

    const targetIdx = filteredItems.findIndex(item => item.id === hash);
    if (targetIdx !== -1) {
      openLightbox(targetIdx);
    }
  }

  // Event Listeners
  function setupEventListeners() {
    // Theme toggle
    if (themeToggle) themeToggle.addEventListener('click', toggleTheme);

    // Search input
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        clearSearchBtn.style.display = searchQuery ? 'block' : 'none';
        applyFiltersAndSort();
      });
    }

    if (clearSearchBtn) {
      clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchQuery = '';
        clearSearchBtn.style.display = 'none';
        applyFiltersAndSort();
        searchInput.focus();
      });
    }

    // Sort select
    if (sortSelect) {
      sortSelect.addEventListener('change', (e) => {
        currentSort = e.target.value;
        applyFiltersAndSort();
      });
    }

    // View toggle buttons
    viewBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        viewBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const view = btn.dataset.view;
        galleryGrid.classList.toggle('masonry', view === 'masonry');
      });
    });

    // Tag clear
    if (clearTagFilter) clearTagFilter.addEventListener('click', clearTag);

    // Reset filters button in empty state
    if (resetFiltersBtn) {
      resetFiltersBtn.addEventListener('click', () => {
        searchQuery = '';
        if (searchInput) searchInput.value = '';
        if (clearSearchBtn) clearSearchBtn.style.display = 'none';
        activeTag = null;
        activeTagsContainer.style.display = 'none';
        setCategory('all');
      });
    }

    // Lightbox Modal events
    if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
    if (lightboxOverlay) lightboxOverlay.addEventListener('click', closeLightbox);
    if (nextBtn) nextBtn.addEventListener('click', nextImage);
    if (prevBtn) prevBtn.addEventListener('click', prevImage);
    if (copyLinkBtn) copyLinkBtn.addEventListener('click', copyCurrentArtworkLink);
    if (zoomInBtn) zoomInBtn.addEventListener('click', zoomIn);
    if (zoomOutBtn) zoomOutBtn.addEventListener('click', zoomOut);
    if (zoomResetBtn) zoomResetBtn.addEventListener('click', zoomReset);

    // About Modal events
    if (aboutBtn) {
      aboutBtn.addEventListener('click', () => {
        aboutModal.classList.add('active');
        aboutModal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
      });
    }
    if (aboutClose) {
      aboutClose.addEventListener('click', () => {
        aboutModal.classList.remove('active');
        aboutModal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
      });
    }
    if (aboutOverlay) {
      aboutOverlay.addEventListener('click', () => {
        aboutModal.classList.remove('active');
        aboutModal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
      });
    }

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (lightboxModal.classList.contains('active')) {
        if (e.key === 'Escape') closeLightbox();
        else if (e.key === 'ArrowRight') nextImage();
        else if (e.key === 'ArrowLeft') prevImage();
        else if (e.key === '+' || e.key === '=') zoomIn();
        else if (e.key === '-' || e.key === '_') zoomOut();
        else if (e.key === '0') zoomReset();
      } else if (aboutModal.classList.contains('active')) {
        if (e.key === 'Escape') {
          aboutModal.classList.remove('active');
          aboutModal.setAttribute('aria-hidden', 'true');
          document.body.style.overflow = '';
        }
      }
    });

    // Touch swipe for mobile lightbox
    let touchStartX = 0;
    let touchEndX = 0;
    if (lightboxModal) {
      lightboxModal.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
      }, { passive: true });

      lightboxModal.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
      }, { passive: true });
    }

    function handleSwipe() {
      const diff = touchEndX - touchStartX;
      if (Math.abs(diff) > 50) {
        if (diff > 0) prevImage();
        else nextImage();
      }
    }
  }

  // Utility escape
  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Start app
  document.addEventListener('DOMContentLoaded', init);
})();
