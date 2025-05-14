/**
 * clean-navigation.js - Fixes for mobile navigation issues
 * Cleans up duplicate navigation elements and organizes header on mobile 
 */

document.addEventListener('DOMContentLoaded', function() {
  // Remove duplicate navigation elements that might appear on mobile
  function cleanupNavigation() {
    // Check if we're on the dashboard page
    const isDashboardPage = document.body.classList.contains('dashboard-page');
    
    if (isDashboardPage) {
      // Remove any duplicate New Workout buttons on mobile
      const standaloneNewWorkoutButtons = document.querySelectorAll('.dashboard-container > a[href*="new_workout"], .dashboard-container > .new-workout-btn, .dashboard-top > a[href*="new_workout"]');
      standaloneNewWorkoutButtons.forEach(button => {
        button.classList.add('duplicate-new-workout-btn');
        button.style.display = 'none';
      });
      
      // Check for any bottom-positioned New Workout buttons
      const bottomNewWorkoutButtons = document.querySelectorAll('.dashboard-section .btn-primary, .dashboard-section a.btn-primary');
      bottomNewWorkoutButtons.forEach(button => {
        if (button.href && button.href.includes('new_workout') && window.innerWidth < 768) {
          button.setAttribute('id', 'new-workout-duplicate');
        }
      });
    }
    
    // Mobile optimization
    if (window.innerWidth < 768) {
      // If there's a top-level standalone "New Workout" button that's
      // not part of proper navigation, remove it or hide it
      const standaloneButtons = document.querySelectorAll('main > a.btn, main > button.btn, .dashboard-container > a.btn, .dashboard-top > a.btn');
      standaloneButtons.forEach(button => {
        const text = button.textContent.toLowerCase();
        if (text.includes('new workout') || text.includes('workout') || text.includes('start')) {
          button.classList.add('mobile-hidden');
          button.style.display = 'none';
        }
      });
    }
  }
  
  // Run cleanup on page load
  cleanupNavigation();
  
  // Re-run cleanup if window is resized
  window.addEventListener('resize', cleanupNavigation);
});
