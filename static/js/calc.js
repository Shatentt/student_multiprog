let a = '';
let b = '';
let sign = '';
let finished = false;
let count = 0;

const digit = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'];
const action = ['+', '-', 'X', '/'];

// Ввод пользователя
const out = document.querySelector('.screen p');

function clearAll() {
    a = '';
    b = '';
    sign = '';
    finished = false;
    out.textContent = 0;
}

document.querySelector('.ac').onclick = clearAll;
document.querySelector('.buttons').onclick = (event) => {
    // Не кнопка
    if(!event.target.classList.contains('calc-btn')) return;
    // Уже обработали ac
    if(event.target.classList.contains('ac')) return;
    console.log(count++);
    out.textContent = '';
    const key = event.target.textContent;

    if (digit.includes(key)) {
        if (b === '' && sign == '') {
            a += key;
            out.textContent = a;
        }
        else if (a !== '' && b !== '' && finished) {
            clearAll();
            a += key;
        }
        else {
            b += key;
            out.textContent = b;
        }
        return;

    }

    if (action.includes(key)) {
        sign = key;
        if (a !== '' && b !== '' && finished) {
            b = '';
            finished = false;
        }
        out.textContent = sign;
        console.log(sign);
        return;
    }

    if (key === '=') {
        if (b === '') b = a;
        switch (sign) {
            case "+":
                a = (+a) + (+b);
                break;
            case "-":
                a = a - b;
                break;
            case "X":
                a = a * b;
                break;
            case "/":
                if (b === '0') {
                    clearAll();
                    out.textContent = 'Ошибка';
                }
                a = a / b;
                break;
        }
        finished = true;
        out.textContent = a;
    }

    if (key === '+/-') {
        if (b !== '') {
            b *= -1
            out.textContent = b;
        }
        else {
            a *= -1
            out.textContent = a;
        }
    }

    if (key === '%') {
        if (b !== '') {
            b /= 100
            out.textContent = b;
        }
        else {
            a /= 100
            out.textContent = a;
        }
    }
}