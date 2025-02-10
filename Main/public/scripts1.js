document.addEventListener('DOMContentLoaded', () => {
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          const tempImage = new Image();
          tempImage.onload = () => {
            img.src = img.dataset.src;
            img.classList.remove('opacity-0');
            img.classList.add('opacity-100');
          };
          tempImage.src = img.dataset.src;
          img.removeAttribute('data-src');
          observer.unobserve(img);
        }
      }
    });
  }, {
    rootMargin: '50px 0px',
    threshold: 0.01
  });

  const loadImage = (img) => {
    if ('loading' in HTMLImageElement.prototype) {
      img.loading = 'lazy';
    }

    img.classList.add('transition-opacity', 'duration-300', 'opacity-0');

    img.onerror = () => {
      const width = img.getAttribute('width') || img.clientWidth || 300;
      const height = img.getAttribute('height') || img.clientHeight || 200;
      img.src = `https://placehold.co/${width}x${height}/DEDEDE/555555?text=Image+Unavailable`;
      img.alt = 'Image unavailable';
      img.classList.remove('opacity-0');
      img.classList.add('opacity-100', 'error-image');
    };

    if (img.dataset.src) {
      imageObserver.observe(img);
    } else {
      img.classList.remove('opacity-0');
      img.classList.add('opacity-100');
    }
  };

  document.querySelectorAll('img[data-src], img:not([data-src])').forEach(loadImage);

  // Watch for dynamically added images
  new MutationObserver((mutations) => {
    mutations.forEach(mutation => {
      mutation.addedNodes.forEach(node => {
        if (node.nodeType === 1) {
          if (node.tagName === 'IMG') {
            loadImage(node);
          }
          node.querySelectorAll('img').forEach(loadImage);
        }
      });
    });
  }).observe(document.body, {
    childList: true,
    subtree: true
  });
});

// Performance monitoring
if ('performance' in window && 'PerformanceObserver' in window) {
  // Create performance observer
  const observer = new PerformanceObserver((list) => {
    const entries = list.getEntries();
    entries.forEach((entry) => {
      if (entry.entryType === 'largest-contentful-paint') {
        // console.log(`LCP: ${entry.startTime}ms`);
      }
      if (entry.entryType === 'first-input') {
        // console.log(`FID: ${entry.processingStart - entry.startTime}ms`);
      }
      if (entry.entryType === 'layout-shift') {
        // console.log(`CLS: ${entry.value}`);
      }
    });
  });

  // Observe performance metrics
  observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });

  // Log basic performance metrics
  window.addEventListener('load', () => {
    const timing = performance.getEntriesByType('navigation')[0];
    console.log({
      'DNS Lookup': timing.domainLookupEnd - timing.domainLookupStart,
      'TCP Connection': timing.connectEnd - timing.connectStart,
      'DOM Content Loaded': timing.domContentLoadedEventEnd - timing.navigationStart,
      'Page Load': timing.loadEventEnd - timing.navigationStart
    });
  });
}

// Handle offline/online status
window.addEventListener('online', () => {
  document.body.classList.remove('offline');
  console.log('Connection restored');
});

window.addEventListener('offline', () => {
  document.body.classList.add('offline');
  console.log('Connection lost');
});


//Layout
document.getElementById('menuToggle').addEventListener('click', function () {
  const nav = document.querySelector('nav');
  nav.classList.toggle('hidden');

  const svg = this.querySelector('svg');
  if (nav.classList.contains('hidden')) {
    svg.innerHTML = '<path d="M4 6h16M4 12h16M4 18h16"></path>';
  } else {
    svg.innerHTML = '<path d="M6 18L18 6M6 6l12 12"></path>';
  }
});

document.addEventListener('DOMContentLoaded', function () {
  const links = document.querySelectorAll('nav a');

  links.forEach(link => {
    link.addEventListener('click', function (e) {
      links.forEach(l => l.classList.remove('active'));
      this.classList.add('active');
    });
  });
});

document.addEventListener('DOMContentLoaded', function () {
  const themeToggle = document.querySelector('.theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      document.body.classList.toggle('dark');
    });
  }

  const filterButtons = document.querySelectorAll('.filter-btn');
  if (filterButtons) {
    filterButtons.forEach(button => {
      button.addEventListener('click', function () {
        filterButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
  
        const severity = this.getAttribute('data-severity');
        const vulnCards = document.querySelectorAll('.vuln-card');
        vulnCards.forEach(card => {
          const severity_tag = card.querySelector('.severity-b')?.textContent.trim();
          if (severity === 'all' || severity_tag.includes(severity)) {  // Change contains() to includes()
            card.style.display = 'block'; // Show matching cards
          } else {
            card.style.display = 'none'; // Hide non-matching cards
          }
        });
      });
    });
  }  

  const searchInput = document.querySelector('#vulnsearch');
  if (searchInput) {
    const performSearch = () => {
      const searchTerm = searchInput.value.toLowerCase().trim();
      const vulnCards = document.querySelectorAll('.vuln-card');

      vulnCards.forEach(card => {
        const title = card.querySelector('.vuln-title')?.textContent.toLowerCase() || '';
        const description = card.querySelector('.vuln-description')?.textContent.toLowerCase() || '';

        if (title.includes(searchTerm) || description.includes(searchTerm)) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    };

    searchInput.addEventListener('input', performSearch);
    searchInput.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') performSearch();
    });
  }

  const exportPDFBtn = document.querySelector('.export-btn.primary');
  if (exportPDFBtn) {
    exportPDFBtn.addEventListener('click', async function () {
      const vulnerabilities = document.querySelectorAll('.vuln-card');

      if (vulnerabilities.length === 0) {
        console.error("No vulnerabilities found for PDF export.");
        return;
      }

      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();

      doc.setFontSize(18);
      doc.text('Vulnerability Report', 14, 15);

      const rows = [];
      vulnerabilities.forEach(card => {
        const severity = card.querySelector('.severity-badge')?.textContent.trim() || "N/A";
        const type = card.querySelector('.vuln-title')?.textContent.trim() || "N/A";
        const description = card.querySelector('.vuln-description')?.textContent.trim() || "N/A";
        const component = card.querySelector('.detail-item .value')?.textContent.trim() || "N/A";
        const cve = card.querySelector('.vuln-details .value:nth-child(2)')?.textContent.trim() || "N/A";
        const recommendation = card.querySelector('.recommendation .value')?.textContent.trim() || "N/A";
        const timestamp = card.querySelector('.timestamp')?.textContent.trim() || "N/A";

        rows.push([severity, type, description, component, cve, recommendation, timestamp]);
      });

      doc.autoTable({
        head: [['Severity', 'Type', 'Description', 'Component', 'CVE', 'Recommendation', 'Timestamp']],
        body: rows,
        startY: 20,
        styles: { fontSize: 10, cellPadding: 3 },
      });

      doc.save('vulnerability_report.pdf');
    });
  }

  const exportCSVBtn = document.querySelector('.export-btn.secondary');
  if (exportCSVBtn) {
    exportCSVBtn.addEventListener('click', function () {
      const vulnerabilities = document.querySelectorAll('.vuln-card');
      if (vulnerabilities.length === 0) {
        console.error("No vulnerabilities found for CSV export.");
        return;
      }

      let csvContent = "data:text/csv;charset=utf-8,";
      csvContent += "Severity,Type,Description,Component,CVE,Recommendation,Timestamp\n";

      vulnerabilities.forEach(vuln => {
        const severity = vuln.querySelector('.severity-badge')?.textContent.trim() || "N/A";
        const type = vuln.querySelector('.vuln-title')?.textContent.trim() || "N/A";
        const description = vuln.querySelector('.vuln-description')?.textContent.trim() || "N/A";
        const component = vuln.querySelector('.detail-item .value')?.textContent.trim() || "N/A";
        const cve = vuln.querySelector('.vuln-details .value:nth-child(2)')?.textContent.trim() || "N/A";
        const recommendation = vuln.querySelector('.recommendation .value')?.textContent.trim() || "N/A";
        const timestamp = vuln.querySelector('.timestamp')?.textContent.trim() || "N/A";

        const row = [
          severity,
          type,
          `"${description}"`,
          `"${component}"`,
          `"${cve}"`,
          `"${recommendation}"`,
          timestamp
        ].join(',');

        csvContent += row + "\n";
      });

      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", "vulnerability_report.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }

  loadReport();
});

async function loadReport() {
  try {
    const response = await fetch('http://localhost:8000/20250203_104013_report.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const report = await response.json();

    console.log('Fetched report:', report);

    // Update the vulnerability list
    const vulnGrid = document.getElementById('vuln-list'); // Adjusted to match the grid container
    if (vulnGrid) {
      vulnGrid.innerHTML = ''; // Clear existing content
      report.detailed_findings.vulnerabilities.forEach(vuln => {
        const vulnCard = `
            <div class="border border-neutral-200/20 rounded-lg p-4 hover:bg-neutral-50 vuln-card">
              <div class="flex justify-between items-start mb-3">
                  <span
                      class="px-2 py-1 text-xs font-semibold text-red-700 bg-red-100 rounded-full severity-b"> ${vuln.severity.toLowerCase()}</span>
                  <span class="text-sm text-neutral-500">${new Date(vuln.timestamp)}</span>
              </div>
              <h3 class="text-lg font-medium text-neutral-700 mb-2 vuln-title">${vuln.type}</h3>
              <p class="text-neutral-600 mb-4 vuln-description">${vuln.description}</p>
              <div class="grid grid-cols-2 gap-4 mb-4 vuln-details">
                  <div>
                      <span class="text-sm text-neutral-500">Component</span>
                      <p class="font-medium text-neutral-700">${vuln.component}</p>
                  </div>
                  <div>
                      <span class="text-sm text-neutral-500">CVE ID</span>
                      <p class="font-medium text-neutral-700">${vuln.cve_id || 'N/A'}</p>
                  </div>
              </div>
              <div class="flex justify-end space-x-3">
                  <button
                      class="flex items-center px-3 py-1 text-sm font-medium text-neutral-700 hover:text-neutral-900">
                      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                          <path
                              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z">
                          </path>
                      </svg>
                      Details
                  </button>
                  <button
                      class="flex items-center px-3 py-1 text-sm font-medium text-red-600 hover:text-red-700">
                      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z">
                          </path>
                      </svg>
                      Mark ${vuln.severity}
                  </button>
              </div>
          </div>
        `;
        vulnGrid.innerHTML += vulnCard;
      });
    }

    const riskScore = document.getElementById('riskScore');
    if (riskScore) riskScore.textContent = Math.round(report.scan_summary.risk_score);

    const lastScanTime = document.getElementById('lastScanTime');
    if (lastScanTime) lastScanTime.textContent = new Date(report.scan_summary.generated_at).toLocaleString();

    const criticalCount = document.getElementById('criticalCount');
    if (criticalCount) criticalCount.textContent = report.vulnerability_summary.by_severity.CRITICAL;

    const highCount = document.getElementById('highCount');
    if (highCount) highCount.textContent = report.vulnerability_summary.by_severity.HIGH;

    const mediumCount = document.getElementById('mediumCount');
    if (mediumCount) mediumCount.textContent = report.vulnerability_summary.by_severity.MEDIUM;

    const lowCount = document.getElementById('lowCount');
    if (lowCount) lowCount.textContent = report.vulnerability_summary.by_severity.LOW;

    const platformInfo = document.getElementById('platformInfo');
    if (platformInfo) platformInfo.textContent = `${report.scan_summary.system_info.platform}`;

    const Version = document.getElementById('Version');
    if (Version) Version.textContent = `${report.scan_summary.system_info.version}`;

    const processor = document.getElementById('processor');
    if (processor) processor.textContent = `${report.scan_summary.system_info.machine}`;
    const architecture = document.getElementById('architecture');
    if (architecture) architecture.textContent = `${report.scan_summary.system_info.architecture}`;

    const timelinePhases = document.getElementById('timelinePhases');
    if (timelinePhases) {
      const timeline = report.remediation_timeline;
      timelinePhases.innerHTML = `
                    <div class="phase immediate">
                        <div class="phase-header">
                            <span class="phase-title">Immediate Action Required</span>
                            <span class="phase-count">${timeline.immediate} Issues</span>
                        </div>
                        <div class="phase-details">
                            <p class="timeline-info">${timeline.suggested_timeline.immediate}</p>
                        </div>
                    </div>
                    <div class="phase short-term">
                        <div class="phase-header">
                            <span class="phase-title">Short Term Action</span>
                            <span class="phase-count">${timeline.short_term} Issues</span>
                        </div>
                        <div class="phase-details">
                            <p class="timeline-info">${timeline.suggested_timeline.short_term}</p>
                        </div>
                    </div>
                    <div class="phase long-term">
                        <div class="phase-header">
                            <span class="phase-title">Long Term Action</span>
                            <span class="phase-count">${timeline.long_term} Issues</span>
                        </div>
                        <div class="phase-details">
                            <p class="timeline-info">${timeline.suggested_timeline.long_term}</p>
                        </div>
                    </div>
                `;
    }

    const severityChart = document.getElementById('severityChart');
    const categoryChart = document.getElementById('categoryChart');
    const remediationChart = document.getElementById('remediationChart');

    if (severityChart || categoryChart || remediationChart) {
      initializeCharts(report);
    }

  } catch (error) {
    console.error('Error loading report:', error);
    const errorMessage = document.createElement('div');
    errorMessage.className = 'error-message';
    errorMessage.textContent = 'Failed to load report data. Please try refreshing the page.';
    console.log(errorMessage);
  }
}

const buttons = document.querySelectorAll('button[data-severity]');

buttons.forEach(button => {
  const severity = button.getAttribute('data-severity').toUpperCase(); // Get severity (convert to uppercase)
  let count = 0;
  switch(severity) {
    case 'ALL':
      count = report.scan_summary.total_vulnerabilities
      break;
    case 'CRITICAL':
      count = report.vulnerability_summary.by_severity.CRITICAL;
      break;
    case 'HIGH':
      count = report.vulnerability_summary.by_severity.HIGH;
      break;
    case 'MEDIUM':
      count = report.vulnerability_summary.by_severity.MEDIUM;
      break;
    case 'LOW':
      count = report.vulnerability_summary.by_severity.LOW;
      break;
    default:
      count = 0;
      break;
  }
  button.textContent = `${severity.charAt(0).toUpperCase() + severity.slice(1)} (${count})`;
});

function initializeCharts(report) {
  const severityData = report.vulnerability_summary.by_severity;
  const severityCtx = document.getElementById('severityChart').getContext('2d');

  new Chart(severityCtx, {
    type: 'doughnut',
    data: {
      labels: ['Critical', 'High', 'Medium', 'Low'],
      datasets: [{
        data: [
          severityData.CRITICAL,
          severityData.HIGH,
          severityData.MEDIUM,
          severityData.LOW
        ],
        backgroundColor: ['#B60000', '#BF5400', '#E1DB12', '#00D306'],
        borderColor: '#fff',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'left',
          align: 'start',
          labels: {
            color: '#aaa',
            boxWidth: 20,
            font: {
              size: 18
            }
          }
        },
      },
      layout: {
        padding: {
          left: 0,
          right: 0,
          top: 10,
          bottom: 20
        }
      },
      cutout: '50%',
      backgroundColor: '#000'
    }
  });

  // Category Distribution Chart
  const categoryData = report.vulnerability_summary.by_category;
  const categoryCtx = document.getElementById('categoryChart').getContext('2d');
  new Chart(categoryCtx, {
    type: 'bar',
    data: {
      labels: Object.keys(categoryData),
      datasets: [{
        label: 'Vulnerabilities by Category',
        data: Object.values(categoryData),
        backgroundColor: '#00ff00'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });

  // Remediation Timeline Chart
  const timelineCtx = document.getElementById('timelineChart').getContext('2d');
  new Chart(timelineCtx, {
    type: 'bar',
    data: {
      labels: ['Immediate (24h)', 'Short Term (1w)', 'Long Term (1m)'],
      datasets: [{
        label: 'Issues by Timeline',
        data: [
          report.remediation_timeline.immediate,
          report.remediation_timeline.short_term,
          report.remediation_timeline.long_term
        ],
        backgroundColor: [
          '#dc3545',  // Red for immediate
          '#ffc107',  // Yellow for short-term
          '#28a745'   // Green for long-term
        ],
        borderRadius: 6,
        barThickness: 30
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
            font: {
              family: "'Inter', sans-serif",
              size: 12
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        x: {
          ticks: {
            font: {
              family: "'Inter', sans-serif",
              size: 12
            }
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleFont: {
            family: "'Inter', sans-serif",
            size: 14
          },
          bodyFont: {
            family: "'Inter', sans-serif",
            size: 13
          },
          padding: 12,
          callbacks: {
            label: function (context) {
              const value = context.raw;
              return `${value} Issue${value !== 1 ? 's' : ''} to address`;
            }
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  loadReport();

  const pdfExportBtn = document.querySelector('.export-btn.primary');
  if (pdfExportBtn) {
    pdfExportBtn.addEventListener('click', exportToPDF);
  }

  const csvExportBtn = document.querySelector('.export-btn.secondary');
  if (csvExportBtn) {
    csvExportBtn.addEventListener('click', exportToCSV);
  }
});
