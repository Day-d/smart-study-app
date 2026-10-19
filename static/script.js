let totalSeconds = 25 * 60;
let remaining = totalSeconds;
let interval = null;

function render() {
    const m = String(Math.floor(remaining / 60)).padStart(2, '0');
    const s = String(remaining % 60).padStart(2, '0');
    document.getElementById('timer').textContent = `${m}:${s}`;
}

function startTimer() {
    if (interval) return;
    interval = setInterval(() => {
        if (remaining > 0) {
            remaining--;
            render();
        } else {
            stopTimer();
            alert('အချိန်ပြည့်ပြီ! ခဏနားလိုက်ပါ ☕');
        }
    }, 1000);
}

function stopTimer() {
    clearInterval(interval);
    interval = null;
}

function resetTimer() {
    stopTimer();
    remaining = totalSeconds;
    render();
}