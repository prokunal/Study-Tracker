//this time-worker.js script helps to update the timer even user is not interacting with tab
let timerCounter;
let interval;

const updateTimer = () => {
  postMessage({ action: 'tick', timerCounter });
  if (timerCounter === 0) {
    postMessage({ action: 'complete' });
    clearInterval(interval);
  }
  timerCounter = timerCounter - 1;
};

onmessage = (event) => {
  const { action, initialTimerValue } = event.data;

  if (action === 'start') {
    timerCounter = initialTimerValue;
    interval = setInterval(updateTimer, 1000);
  } else if (action === 'pause') {
    clearInterval(interval);
  }
};
