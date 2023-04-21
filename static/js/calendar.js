let calendar = document.querySelector('.calendar');

const month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                     'November', 'December'];

isLeapYear = (year) => {
    return (year % 4 === 0 && year % 100 !== 0 && year % 400 !== 0) || (year % 100 === 0 && year % 400 ===0);
};

getFebDays = (year) => {
    return isLeapYear(year) ? 29 : 28;
};

async function changeDay(day) {
    document.querySelector('.curr-date').classList.remove("curr-date");
    day.target.classList.add("curr-date");
    let response = await fetch('/calendar/get?date=' + get_date());//.then((response) => {
        /* if (response.ok) { // если HTTP-статус в диапазоне 200-299
            // получаем тело ответа (см. про этот метод ниже)

            console.log(response.text());
            document.querySelector('#schedule').innerHTML = json;
        } else {
            alert("Ошибка HTTP: " + response.status);
        } */
    let form = await response.text();
    document.querySelector('#schedule').innerHTML = form;
    // });
}

generateCalendar = (month, year) => {

    let calendar_days = calendar.querySelector('.calendar-days');
    let calendar_header_year = calendar.querySelector('#year');

    let days_of_month = [31, getFebDays(year), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

    calendar_days.innerHTML = '';

    let currDate = new Date();
    if (month > 11 || month < 0) month = currDate.getMonth();
    if (!year) year = currDate.getFullYear();

    let curr_month = `${month_names[month]}`;
    month_picker.innerHTML = curr_month;
    calendar_header_year.innerHTML = year;

    // get first day of month

    let first_day = new Date(year, month, 1);

    for (let i = 0; i <= days_of_month[month] + first_day.getDay() - 1; i++) {
        let day = document.createElement('div');
        if (i >= first_day.getDay()) {
            day.classList.add('calendar-day-hover');
            day.onclick = changeDay.bind();
            day.innerHTML = i - first_day.getDay() + 1;
            if (i - first_day.getDay() + 1 === currDate.getDate() && year === currDate.getFullYear() && month === currDate.getMonth()) {
                day.classList.add('curr-date');
            }
        }
        calendar_days.appendChild(day);
    }
    document.querySelector('.curr-date').click()
}

let month_list = calendar.querySelector('.month-list');

month_names.forEach((e, index) => {
    let month = document.createElement('div');
    month.innerHTML = `<div data-month="${index}">${e}</div>`;
    month.querySelector('div').onclick = () => {
        month_list.classList.remove('show');
        curr_month.value = index;
        generateCalendar(index, curr_year.value);
    };
    month_list.appendChild(month);
});

let month_picker = calendar.querySelector('#month-picker');

month_picker.onclick = () => {
    month_list.classList.add('show');
};

let currDate = new Date();

var curr_month = {value: currDate.getMonth()};
var curr_year = {value: currDate.getFullYear()};

generateCalendar(curr_month.value, curr_year.value);

document.querySelector('#prev-year').onclick = () => {
    --curr_year.value;
    generateCalendar(curr_month.value, curr_year.value);
};

document.querySelector('#next-year').onclick = () => {
    ++curr_year.value;
    generateCalendar(curr_month.value, curr_year.value);
};

var curr_date = document.querySelector('.curr-date');
function get_date() {
    let c_date = document.querySelector('.curr-date').textContent;
    let c_month = month_names.indexOf(document.querySelector('.month-picker').textContent) + 1;
    let c_year = document.querySelector('#year').textContent;
    if (c_month < 10) {c_month = '0' + c_month;}
    if (c_date < 10) {c_date = '0' + c_date;}
    return c_year + '-' + c_month + '-' + c_date;
}

document.querySelector('.add').onclick = () => {
    console.log('/calendar/new?date=' + get_date());
    window.location.href = '/calendar/new?date=' + get_date();
}