document.getElementById('trackerForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission

    // Get input values
    const startDate = new Date(document.getElementById('startDate').value);
    const cycleLength = parseInt(document.getElementById('cycleLength').value);

    // Calculate the next period date
    const nextPeriodDate = new Date(startDate);
    nextPeriodDate.setDate(startDate.getDate() + cycleLength);

    // Display result
    document.getElementById('result').innerText = `Your next period is expected on: ${nextPeriodDate.toLocaleDateString()}`;
});
