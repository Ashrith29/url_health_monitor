// Initialize history data from template
const historyData = window.historyData || [];

// Function to show history details
function showHistoryDetails(index) {
    const historyLength = historyData.length;
    const checkNumber = historyLength - parseInt(index);
    alert('History details for check #' + checkNumber);
}

// Add event delegation for history items
document.addEventListener('DOMContentLoaded', function() {
    const historyContainer = document.querySelector('.list-group-flush');
    if (historyContainer) {
        historyContainer.addEventListener('click', function(event) {
            const historyItem = event.target.closest('.history-item');
            if (historyItem) {
                const index = historyItem.getAttribute('data-index');
                showHistoryDetails(index);
            }
        });
    }
});
