/**
 * Groei App - Main JavaScript
 * 
 * This file contains the core functionality for the Groei workout tracking app.
 */

// Utility functions
const GroeiApp = {
    // Initialize the application
    init: function() {
        // Set up event listeners
        this.setupEventListeners();
        
        // Handle page-specific initialization
        this.initCurrentPage();
        
        // Set the current year for the footer
        this.setCurrentYear();
    },
    
    // Set up general event listeners
    setupEventListeners: function() {
        // Flash message dismissal
        const flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(message => {
            const closeButton = message.querySelector('.close-btn');
            if (closeButton) {
                closeButton.addEventListener('click', () => {
                    message.style.display = 'none';
                });
            }
        });
    },
    
    // Initialize functionality based on the current page
    initCurrentPage: function() {
        // Dashboard page
        if (document.getElementById('workout-heatmap')) {
            this.initDashboard();
        }
        
        // Workout session page
        if (document.querySelector('.workout-session-container')) {
            this.initWorkoutSession();
        }
        
        // Exercises page
        if (document.querySelector('.exercises-container')) {
            this.initExercisesPage();
        }
    },
    
    // Dashboard-specific initialization
    initDashboard: function() {
        // Already handled by dashboard-specific JavaScript in the template
        console.log('Dashboard page initialized');
    },
    
    // Workout session-specific initialization
    initWorkoutSession: function() {
        // Enable smooth scrolling to exercises
        const exerciseLinks = document.querySelectorAll('.exercise-sidebar-link');
        exerciseLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 100, // Account for fixed header
                        behavior: 'smooth'
                    });
                }
            });
        });
        
        // Smart suggestions for weight
        this.initSmartSuggestions();
    },
    
    // Exercise page-specific initialization
    initExercisesPage: function() {
        // Handled by the page-specific JavaScript in the template
        console.log('Exercises page initialized');
    },
    
    // Initialize smart suggestions for weight and reps
    initSmartSuggestions: function() {
        const addSetForms = document.querySelectorAll('.add-set-form');
        
        addSetForms.forEach(form => {
            const exerciseId = form.closest('.exercise-tracking-card').id.replace('exercise-', '');
            const weightInput = form.querySelector('input[name="weight"]');
            const repsInput = form.querySelector('input[name="reps"]');
            
            // Look for previous weight and reps for this exercise in localStorage
            const storageKey = `exercise-${exerciseId}`;
            const previousData = localStorage.getItem(storageKey);
            
            if (previousData) {
                const data = JSON.parse(previousData);
                
                // If there's previous data and this is a new session without any sets yet
                const setCards = form.closest('.sets-container').querySelectorAll('.set-card');
                
                if (setCards.length === 0 && data.lastWeight && data.lastReps) {
                    // Suggest weight increase if the last workout hit target reps
                    if (data.lastReps >= 12) {
                        // Increase weight by 2.5kg or 5% (whichever is greater)
                        const increasedWeight = Math.max(
                            parseFloat(data.lastWeight) + 2.5,
                            parseFloat(data.lastWeight) * 1.05
                        ).toFixed(1);
                        
                        weightInput.value = increasedWeight;
                        repsInput.value = 8; // Reset reps to target range
                    } else {
                        // Keep the same weight if target reps weren't reached
                        weightInput.value = data.lastWeight;
                        repsInput.value = data.lastReps;
                    }
                }
            }
            
            // Store the data when a set is logged
            form.addEventListener('submit', () => {
                localStorage.setItem(storageKey, JSON.stringify({
                    lastWeight: weightInput.value,
                    lastReps: repsInput.value
                }));
            });
        });
    },
    
    // Set current year for the footer copyright
    setCurrentYear: function() {
        const currentYear = new Date().getFullYear();
        const yearElements = document.querySelectorAll('.current-year');
        yearElements.forEach(element => {
            element.textContent = currentYear;
        });
    }
};

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    GroeiApp.init();
});
