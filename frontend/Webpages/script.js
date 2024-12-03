const filterButton = document.getElementById('filter-button');
const filterPopup = document.getElementById('filter-popup');
const closeButton = document.querySelector('.close-button');

// Function to open the filter popup
filterButton.addEventListener('click', () => {
    filterPopup.style.display = 'block'; // Show the popup
});

// Function to close the filter popup
closeButton.addEventListener('click', () => {
    filterPopup.style.display = 'none'; // Hide the popup
});

// Close the popup when clicking outside of it
window.addEventListener('click', (event) => {
    if (event.target == filterPopup) {
        filterPopup.style.display = 'none'; // Hide the popup
    }
});
