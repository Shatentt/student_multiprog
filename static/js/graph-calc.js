let func = document.querySelector('#func');
let size = document.querySelector('#size');
let accuracy = document.querySelector('#accuracy');
let canvas = document.querySelector('canvas');
let context = canvas.getContext('2d');

// задаем центр
context.translate(context.width / 2, context.height / 2);

function draw() {
    // сетка
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.beginPath();
    for (let x = 0; x <= +size.value * 2; x++) {
        context.strokeStyle = "#bdbdbd";
        var cellSize = canvas.width / (+size.value * 2);
        context.moveTo(x * cellSize, -canvas.height);
        context.lineTo(x * cellSize, canvas.height);
        context.stroke();
        context.moveTo(-canvas.width, x * cellSize);
        context.lineTo(canvas.width, x * cellSize);
        context.stroke();
    }

    context.beginPath();
    context.strokeStyle = "black";
    context.lineWidth = 2;
    context.moveTo(canvas.width / 2, 0);
    context.lineTo(canvas.width / 2, canvas.height);
    context.moveTo(0, canvas.height / 2);
    context.lineTo(canvas.width, canvas.height /2);
    context.stroke();

    // график функции
    context.strokeStyle = "#9247f5";
    context.lineWidth = 3;
    context.beginPath();
    let y = x => eval(func.value);
    for (var i = -size.value; i <= +size.value * 2; i += +accuracy.value) {
        if (y(i) === Infinity) {
            i += +accuracy.value;
            context.moveTo((i + +size.value) * cellSize, (-y(i) + +size.value) * cellSize);
        }

        context[i ? 'lineTo' : 'moveTo']((i + +size.value) * cellSize, (-y(i) + +size.value) * cellSize);
    }
    context.stroke();
}

document.querySelector('#submit').onclick = draw;
