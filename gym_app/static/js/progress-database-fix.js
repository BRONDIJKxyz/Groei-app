/**
 * Progress Database & Workout Popup Fix
 * This script fixes issues with the progress database and improves the workout popup
 */

document.addEventListener('DOMContentLoaded', function() {
    // Fix for Progress Database
    function initProgressDatabase() {
        const exerciseList = document.getElementById('exercise-progress-list');
        if (!exerciseList) return;

        const exerciseItems = document.querySelector('.exercise-list-items');
        if (!exerciseItems) return;
        
        const loadingState = exerciseItems.querySelector('.loading-state');
        if (!loadingState) return;

        // Get spinner while loading
        loadingState.style.display = 'flex';
        
        // Try-catch to handle any unexpected errors
        try {
            // First fetch all exercises
            fetch('/workout/api/exercises')
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    // Clear loading state
                    loadingState.style.display = 'none';
                    
                    // Fetch completed workouts to get exercise data 
                    fetch('/workout/api/completed-workouts')
                        .then(response => {
                            if (!response.ok) {
                                // Fallback to active-workouts if completed-workouts fails
                                return fetch('/workout/api/active-workouts');
                            }
                            return response;
                        })
                        .then(response => {
                            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                            return response.json();
                        })
                        .then(workoutData => {
                            // Get unique exercise IDs that have been used
                            const exerciseIds = new Set();
                            
                            // Process workout data to extract exercise IDs
                            if (Array.isArray(workoutData)) {
                                workoutData.forEach(workout => {
                                    // Handle different API response formats
                                    const exercises = workout.exercises || workout.workout_exercises || [];
                                    exercises.forEach(exercise => {
                                        const id = exercise.exercise_id || exercise.id;
                                        if (id) exerciseIds.add(id);
                                    });
                                });
                            }
                            
                            // Create a list of all exercises in the system
                            const allExercises = Array.isArray(data) ? data : (data.exercises || []);
                            
                            // Filter to exercises the user has actually done
                            let usedExercises = [];
                            if (exerciseIds.size > 0) {
                                usedExercises = allExercises.filter(exercise => 
                                    exerciseIds.has(exercise.id));
                            } else {
                                // If no exercises found in workouts, show all exercises
                                usedExercises = allExercises;
                            }
                            
                            // Sort exercises by name
                            usedExercises.sort((a, b) => 
                                (a.name || '').localeCompare(b.name || ''));
                                
                            // Populate exercise list
                            if (usedExercises.length > 0) {
                                displayExercises(usedExercises, exerciseItems);
                            } else {
                                // No exercises found
                                const noExercisesMsg = document.createElement('p');
                                noExercisesMsg.className = 'empty-state-message';
                                noExercisesMsg.textContent = 'No exercises found in your workouts.';
                                exerciseItems.appendChild(noExercisesMsg);
                            }
                        })
                        .catch(error => {
                            console.error('Error fetching workout data:', error);
                            displayError(exerciseItems);
                        });
                })
                .catch(error => {
                    console.error('Error fetching exercises:', error);
                    displayError(exerciseItems);
                });
        } catch (error) {
            console.error('Progress database error:', error);
            displayError(exerciseItems);
        }
    }
    
    // Helper to display exercises in the list
    function displayExercises(exercises, container) {
        container.innerHTML = ''; // Clear container
        
        exercises.forEach(exercise => {
            const exerciseEl = document.createElement('div');
            exerciseEl.className = 'exercise-list-item';
            exerciseEl.dataset.exerciseId = exercise.id;
            
            const name = document.createElement('h4');
            name.textContent = exercise.name;
            
            const viewBtn = document.createElement('button');
            viewBtn.className = 'btn btn-sm btn-secondary';
            viewBtn.textContent = 'View Progress';
            viewBtn.addEventListener('click', () => {
                window.location.href = `/workout/exercise/${exercise.id}/progress`;
            });
            
            exerciseEl.appendChild(name);
            exerciseEl.appendChild(viewBtn);
            container.appendChild(exerciseEl);
        });
    }
    
    // Helper to display error message
    function displayError(container) {
        container.innerHTML = '';
        const errorMsg = document.createElement('div');
        errorMsg.className = 'error-message';
        errorMsg.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <p>There was an error loading the progress database. Please try refreshing the page.</p>
        `;
        container.appendChild(errorMsg);
    }
    
    // Initialize the progress database
    setTimeout(initProgressDatabase, 100);
});
