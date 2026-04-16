// Poll-specific JavaScript functionality

let chart = null;
let pollUpdateInterval = null;

function initPollView(pollId, hasVoted) {
    fetchPollData(pollId);

    const voteForm = document.getElementById('voteForm');
    if (voteForm) {
        voteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitVote(pollId);
        });
    }

    if (hasVoted) {
        showResults();
    }

    pollUpdateInterval = setInterval(() => {
        fetchPollData(pollId);
    }, 5000);
}

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

function submitVote(pollId) {
    const selectedOption = document.querySelector('input[name="option"]:checked');

    if (!selectedOption) {
        showError('Please select an option to vote.');
        return;
    }

    document.getElementById('votingSection').classList.add('d-none');
    document.getElementById('loadingIndicator').classList.remove('d-none');

    fetch('/api/vote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            poll_id: pollId,
            option_id: parseInt(selectedOption.value, 10)
        })
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('loadingIndicator').classList.add('d-none');

            if (data.success) {
                updatePollDisplay(data.poll);
                showResults();
            } else {
                showError(data.message || 'Failed to submit vote.');
                document.getElementById('votingSection').classList.remove('d-none');
            }
        })
        .catch(error => {
            document.getElementById('loadingIndicator').classList.add('d-none');
            document.getElementById('votingSection').classList.remove('d-none');
            showError('An error occurred while submitting your vote. Please try again.');
            console.error('Error submitting vote:', error);
        });
}

function showResults() {
    document.getElementById('votingSection').classList.add('d-none');
    document.getElementById('resultsSection').classList.remove('d-none');
}

function updatePollDisplay(pollData) {
    const totalVotesElement = document.getElementById('totalVotes');
    if (totalVotesElement) {
        totalVotesElement.textContent = `${formatNumber(pollData.total_votes)} votes`;
    }

    updateResultsChart(pollData);
    updateResultsList(pollData);
}

function updateResultsChart(pollData) {
    const chartElement = document.getElementById('resultsChart');
    if (!chartElement) {
        return;
    }

    const ctx = chartElement.getContext('2d');
    const labels = pollData.options.map(option => option.text);
    const votes = pollData.options.map(option => option.votes);
    const totalVotes = votes.reduce((sum, current) => sum + current, 0);
    const backgroundColors = generateMonochromeColors(labels.length);

    if (chart) {
        chart.destroy();
    }

    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Votes',
                data: votes,
                backgroundColor: backgroundColors,
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                borderRadius: 4,
                barPercentage: 0.7
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
                    ticks: {
                        precision: 0,
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            }
        }
    });
}

function updateResultsList(pollData) {
    const optionResultsContainer = document.getElementById('optionResults');
    if (!optionResultsContainer) {
        return;
    }

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
                    <div class="progress-bar" role="progressbar" style="width: ${percentage}%;" aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100">
                        ${percentage}%
                    </div>
                </div>
            </div>
        `;
    });

    optionResultsContainer.innerHTML = resultsHTML;
}

window.addEventListener('beforeunload', function() {
    if (pollUpdateInterval) {
        clearInterval(pollUpdateInterval);
    }

    if (chart) {
        chart.destroy();
    }
});
