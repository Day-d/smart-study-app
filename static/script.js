let timeLeft = 1500;
let timerId = null;

function updateDisplay() {
    let mins = Math.floor(timeLeft / 60);
    let secs = timeLeft % 60;
    document.getElementById('timer').innerText = 
        `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function startTimer() {
    if (timerId !== null) return;
    timerId = setInterval(() => {
        if (timeLeft > 0) {
            timeLeft--;
            updateDisplay();
        } else {
            clearInterval(timerId);
            timerId = null;
            alert("Time's up! နားဖို့အချိန်တန်ပြီ!");
        }
    }, 1000);
}

function stopTimer() {
    clearInterval(timerId);
    timerId = null;
}

function resetTimer() {
    stopTimer();
    timeLeft = 1500;
    updateDisplay();
}