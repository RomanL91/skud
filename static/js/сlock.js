/**
 * Отображает текущее время в элементе с id === 'clock'
 */
function showTime() {
  const time = formatDateTimeForClock();
  document.getElementById("clock").textContent = time;
}
showTime();
setInterval(showTime, 1000);
