// Poll-specific JavaScript functionality

let chart = null;
let pollUpdateInterval = null;

// Initialize the poll view
function initPollView(pollId, hasVoted) {
    // Initial load of poll data
    fetchPollData(pollId);
    
    // Set up voting form submission
    const voteForm = document.getElementById('voteForm');
    if (voteForm) {
        voteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitVote(pollId);
        });
    }
    
    // If user has already voted, show results immediately
    if (hasVoted) {
        showResults();
    }
    
    // Set up polling for updates
    pollUpdateInterval = setInterval(() => {
        fetchPollData(pollId);
    }, 5000); // Update every 5 seconds
}

// Fetch poll data from the server
function fetchPollData(pollId) {
    fetch(`/api/poll/${pollId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch poll data');
            }
            return response.json();
        })
        .then(data => {
            updatePollDisplay(data);
        })
        .catch(error => {
            console.error('Error fetching poll data:', error);
            showError('Unable to load poll data. Please try refreshing the page.');
        });
}

// Submit a vote for the selected option
function submitVote(pollId) {
    const selectedOption = document.querySelector('input[name="option"]:checked');
    
    if (!selectedOption) {
        showError('Please select an option to vote.');
        return;
    }
    
    // Show loading indicator
    document.getElementById('votingSection').classList.add('d-none');
    document.getElementById('loadingIndicator').classList.remove('d-none');
    
    // Submit the vote via API
    fetch('/api/vote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            poll_id: pollId,
            option_id: parseInt(selectedOption.value)
        })
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading indicator
        document.getElementById('loadingIndicator').classList.add('d-none');
        
        if (data.success) {
            // Update UI with new results
            updatePollDisplay(data.poll);
            showResults();
        } else {
            // Show error and return to voting section
            showError(data.message || 'Failed to submit vote.');
            document.getElementById('votingSection').classList.remove('d-none');
        }
    })
    .catch(error => {
        // Hide loading indicator and show error
        document.getElementById('loadingIndicator').classList.add('d-none');
        document.getElementById('votingSection').classList.remove('d-none');
        showError('An error occurred while submitting your vote. Please try again.');
        console.error('Error submitting vote:', error);
    });
}

// Show the results section and hide voting
function showResults() {
    document.getElementById('votingSection').classList.add('d-none');
    document.getElementById('resultsSection').classList.remove('d-none');
}

// Update the poll display with new data
function updatePollDisplay(pollData) {
    // Update total votes count
    const totalVotesElement = document.getElementById('totalVotes');
    if (totalVotesElement) {
        totalVotesElement.textContent = `${formatNumber(pollData.total_votes)} votes`;
    }
    
    // Update results visualization
    updateResultsChart(pollData);
    updateResultsList(pollData);
}

// Update or create the results chart
function updateResultsChart(pollData) {
    const ctx = document.getElementById('resultsChart').getContext('2d');
    
    // Extract labels and data from poll options
    const labels = pollData.options.map(option => option.text);
    const votes = pollData.options.map(option => option.votes);
    const totalVotes = votes.reduce((sum, current) => sum + current, 0);
    
    // Generate monochromatic colors for each option
    const backgroundColors = generateMonochromeColors(labels.length);
    
    // Destroy existing chart if it exists
    if (chart) {
        chart.destroy();
    }
    
    // Create new chart
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Votes',
                data: votes,
                backgroundColor: backgroundColors,
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                borderRadius: 4,
                barPercentage: 0.7,
                hoverBackgroundColor: backgroundColors.map(color => {
                    // Lighten color on hover
                    return color.replace(/rgba\((\d+), (\d+), (\d+), ([\d\.]+)\)/, 
                        (match, r, g, b, a) => `rgba(${parseInt(r)+20}, ${parseInt(g)+20}, ${parseInt(b)+20}, ${a})`);
                })
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        weight: 'bold',
                        size: 14
                    },
                    padding: 10,
                    cornerRadius: 0,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const percentage = totalVotes > 0 ? Math.round((value / totalVotes) * 100) : 0;
                            return `${value} votes (${percentage}%)`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    border: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        lineWidth: 0.5
                    },
                    ticks: {
                        precision: 0,
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    border: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            }
        }
    });
}

// Update the text-based results list
function updateResultsList(pollData) {
    const optionResultsContainer = document.getElementById('optionResults');
    const totalVotes = pollData.total_votes;
    
    let resultsHTML = '';
    
    pollData.options.forEach(option => {
        const percentage = totalVotes > 0 ? Math.round((option.votes / totalVotes) * 100) : 0;
        
        resultsHTML += `
            <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <div>${option.text}</div>
                    <div><strong>${option.votes} votes</strong> (${percentage}%)</div>
                </div>
                <div class="progress" style="height: 25px;">
                    <div class="progress-bar" role="progressbar" style="width: ${percentage}%;" 
                         aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100">
                        ${percentage}%
                    </div>
                </div>
            </div>
        `;
    });
    
    optionResultsContainer.innerHTML = resultsHTML;
}

// Clean up when leaving the page
window.addEventListener('beforeunload', function() {
    if (pollUpdateInterval) {
        clearInterval(pollUpdateInterval);
    }
    
    if (chart) {
        chart.destroy();
    }
});
