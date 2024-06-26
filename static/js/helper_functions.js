/**
 * Форматирует время в формате DD.MM.YYYY HH:MM:SS. Если время не передано - берем текущее
 * @param {*} timeIn
 * @returns
 */
function formatDateTime(timeIn) {
  let formattedString = timeIn.replace('T', ' ').replace('Z', '');
  return formattedString;
}

function formatDateTimeForClock() {
  const dTimezone = new Date();
  const offset = dTimezone.getTimezoneOffset() / 60;
  const now = new Date() ;
  const year = now.getFullYear();
  const month = ("0" + (now.getMonth() + 1)).slice(-2);
  const day = ("0" + now.getDate()).slice(-2);
  const hour = ("0" + now.getHours()).slice(-2);
  // console.log("const hour = (`0` + now.getHours()).slice(-2) ",typeof hour)
  const minute = ("0" + now.getMinutes()).slice(-2);
  const second = ("0" + now.getSeconds()).slice(-2);
  const time = `${day}.${month}.${year} ${hour}:${minute}:${second}`;
  return time;
}
