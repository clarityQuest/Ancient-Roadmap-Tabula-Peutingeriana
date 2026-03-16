// Initialize OpenSeadragon for DZI viewing.
window.addEventListener('DOMContentLoaded', () => {
  const isFileProtocol = window.location.protocol === 'file:';
  const statusEl = document.getElementById('status');

  const svgToDataUrl = (svg) => `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;

  const iconZoomIn = svgToDataUrl(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><path d="M12 6v12M6 12h12" stroke="#f2f7ff" stroke-width="2" stroke-linecap="round"/></svg>'
  );
  const iconZoomOut = svgToDataUrl(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><path d="M6 12h12" stroke="#f2f7ff" stroke-width="2" stroke-linecap="round"/></svg>'
  );
  const iconHome = svgToDataUrl(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><path d="M3.8 11.1L12 4.6l8.2 6.5" stroke="#f2f7ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M6.5 10.3V19h11v-8.7" stroke="#f2f7ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M10.2 19v-4.1h3.6V19" stroke="#f2f7ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  );
  const iconFullpage = svgToDataUrl(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><path d="M8 4H4v4M16 4h4v4M4 16v4h4M20 16v4h-4" stroke="#f2f7ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  );

  // Inline Deep Zoom metadata avoids fetching the .dzi file over XHR,
  // which commonly fails under file:// in browsers.
  const inlineTileSource = {
    Image: {
      xmlns: 'http://schemas.microsoft.com/deepzoom/2008',
      Url: 'Tabula_Peutingeriana_-_Miller_files/',
      Format: 'jpeg',
      Overlap: '1',
      TileSize: '254',
      Size: {
        Width: '46380',
        Height: '2953'
      }
    }
  };

  const viewer = OpenSeadragon({
    id: 'openseadragon1',
    prefixUrl: 'https://cdnjs.cloudflare.com/ajax/libs/openseadragon/4.1.0/images/',
    navImages: {
      zoomIn: {
        REST: iconZoomIn,
        GROUP: iconZoomIn,
        HOVER: iconZoomIn,
        DOWN: iconZoomIn
      },
      zoomOut: {
        REST: iconZoomOut,
        GROUP: iconZoomOut,
        HOVER: iconZoomOut,
        DOWN: iconZoomOut
      },
      home: {
        REST: iconHome,
        GROUP: iconHome,
        HOVER: iconHome,
        DOWN: iconHome
      },
      fullpage: {
        REST: iconFullpage,
        GROUP: iconFullpage,
        HOVER: iconFullpage,
        DOWN: iconFullpage
      }
    },
    tileSources: isFileProtocol ? inlineTileSource : 'Tabula_Peutingeriana_-_Miller.dzi',
    showNavigator: true,
    defaultZoomLevel: 0,
    minZoomLevel: 0,
    maxZoomLevel: 40,
    visibilityRatio: 1.0,
    constrainDuringPan: true,
    blendTime: 0.1,
    animationTime: 0.5,
    backgroundColor: '#181818'
  });

  // If tiled loading still fails for any reason, fall back automatically
  // so users can always see the map without setup steps.
  let usedFallback = false;
  viewer.addHandler('open-failed', () => {
    if (usedFallback) {
      return;
    }
    usedFallback = true;
    viewer.open({
      type: 'image',
      url: 'Tabula_Peutingeriana_-_Miller.jpg'
    });
    if (statusEl) {
      statusEl.textContent = 'Loaded fallback image mode.';
      statusEl.classList.add('visible');
    }
  });
});
