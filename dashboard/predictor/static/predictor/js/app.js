/**
 * Dysglycemia Screening Clinical Decision Support (CDSS)
 * Application Shell & Accessible Interaction Engine (Phase D2.1)
 */

(function () {
  'use strict';

  // 1. Theme Management (Light / Dark)
  function initTheme() {
    const savedTheme = localStorage.getItem('dashboard-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeToggleUI(savedTheme);
  }

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('dashboard-theme', newTheme);
    updateThemeToggleUI(newTheme);
  }

  function updateThemeToggleUI(theme) {
    const labelEl = document.getElementById('theme-label');
    const iconSun = document.getElementById('theme-icon-sun');
    const iconMoon = document.getElementById('theme-icon-moon');

    if (labelEl) {
      labelEl.textContent = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
    }
    if (iconSun && iconMoon) {
      if (theme === 'dark') {
        iconSun.style.display = 'inline-block';
        iconMoon.style.display = 'none';
      } else {
        iconSun.style.display = 'none';
        iconMoon.style.display = 'inline-block';
      }
    }
  }

  // 2. Mobile Drawer / Sheet Navigation (Accessible Focus Trap & Esc)
  let previousActiveElement = null;

  function openMobileSheet() {
    const sheet = document.getElementById('mobile-sheet');
    const backdrop = document.getElementById('sheet-backdrop');
    if (!sheet || !backdrop) return;

    previousActiveElement = document.activeElement;
    sheet.classList.add('active');
    backdrop.classList.add('active');
    sheet.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    // Focus close button inside drawer
    const closeBtn = sheet.querySelector('.ui-sheet-close');
    if (closeBtn) closeBtn.focus();
  }

  function closeMobileSheet() {
    const sheet = document.getElementById('mobile-sheet');
    const backdrop = document.getElementById('sheet-backdrop');
    if (!sheet || !backdrop) return;

    sheet.classList.remove('active');
    backdrop.classList.remove('active');
    sheet.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';

    if (previousActiveElement && typeof previousActiveElement.focus === 'function') {
      previousActiveElement.focus();
    }
  }

  // Keyboard navigation listener (Escape key closes drawer)
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      const sheet = document.getElementById('mobile-sheet');
      if (sheet && sheet.classList.contains('active')) {
        closeMobileSheet();
      }
    }
  });

  // 3. Dialog Modal Helper for HTML5 <dialog>
  window.openDialog = function (dialogId) {
    const dialog = document.getElementById(dialogId);
    if (dialog && typeof dialog.showModal === 'function') {
      dialog.showModal();
    }
  };

  window.closeDialog = function (dialogId) {
    const dialog = document.getElementById(dialogId);
    if (dialog && typeof dialog.close === 'function') {
      dialog.close();
    }
  };

  // Expose global methods
  window.toggleTheme = toggleTheme;
  window.openMobileSheet = openMobileSheet;
  window.closeMobileSheet = closeMobileSheet;

  // Run on DOM ready
  document.addEventListener('DOMContentLoaded', function () {
    initTheme();

    // Attach drawer trigger listeners
    const toggleBtn = document.getElementById('sidebar-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', openMobileSheet);
    }
    const closeBtn = document.getElementById('sheet-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', closeMobileSheet);
    }
    const backdrop = document.getElementById('sheet-backdrop');
    if (backdrop) {
      backdrop.addEventListener('click', closeMobileSheet);
    }
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
      themeBtn.addEventListener('click', toggleTheme);
    }

    // 4. Stage-1 Screening Form UX (Phase D2.2)
    const errorSummary = document.getElementById('error-summary');
    if (errorSummary) {
      errorSummary.focus();
    }

    const clearBtn = document.getElementById('clear-form-btn');
    const screeningForm = document.getElementById('stage1-screening-form');
    if (clearBtn && screeningForm) {
      clearBtn.addEventListener('click', function (e) {
        const inputs = screeningForm.querySelectorAll('input[type="number"]');
        let hasContent = false;
        inputs.forEach(function (inp) {
          if (inp.value.trim() !== '') hasContent = true;
        });

        if (hasContent) {
          const confirmClear = window.confirm('Are you sure you want to clear all entered parameters?');
          if (!confirmClear) {
            e.preventDefault();
            return false;
          }
        }
      });
    }
  });
})();
