const display = document.getElementById("display");

const expressionLine =
    document.getElementById("expression");

const angleButton =
    document.getElementById("angleMode");

let expression = "";
let answer = 0;
let isDegree = true;


// DISPLAY UPDATE

function render() {

    display.value = expression || "0";

    angleButton.textContent =
        isDegree ? "DEG" : "RAD";

}


// ADD VALUE

function append(value) {

    if (expression === "Error") {
        expression = "";
    }

    if (expression === "0" && /^[0-9.]$/.test(value)) {
        expression = "";
    }

    expression += value;

    render();

}


// CLEAR ALL

function clearAll() {

    expression = "";

    expressionLine.textContent = "Ready";

    render();

}


// DELETE LAST CHARACTER

function deleteLast() {

    expression = expression.slice(0, -1);

    render();

}


// FACTORIAL

function factorial(n) {

    if (
        !Number.isInteger(n) ||
        n < 0 ||
        n > 170
    ) {
        throw new Error("Invalid factorial");
    }

    let result = 1;

    for (let i = 2; i <= n; i++) {
        result *= i;
    }

    return result;

}


// CALCULATOR ENGINE

function calculate() {

    if (!expression) return;

    try {

        let exp = expression;

        // BASIC OPERATORS

        exp = exp
            .replaceAll("×", "*")
            .replaceAll("÷", "/")
            .replaceAll("π", "PI")
            .replace(/\bAns\b/g, `(${answer})`)
            .replace(/\be\b/g, "E")
            .replaceAll("^", "**");

        // SCIENTIFIC FUNCTIONS

        exp = exp
            .replace(/√\(/g, "sqrt(")
            .replace(/log\(/g, "log10(")
            .replace(/ln\(/g, "log(");

        // FACTORIAL

        exp = exp.replace(
            /(\d+(?:\.\d+)?)!/g,
            "factorial($1)"
        );

        // PERCENTAGE

        exp = exp.replace(
            /(\d+(?:\.\d+)?)%/g,
            "($1/100)"
        );

        // DEGREE AND RADIAN

        const toRad = function(x) {

            return isDegree
                ? x * Math.PI / 180
                : x;

        };

        const sin = x => Math.sin(toRad(x));
        const cos = x => Math.cos(toRad(x));
        const tan = x => Math.tan(toRad(x));

        const sqrt = Math.sqrt;
        const log10 = Math.log10;
        const log = Math.log;

        const PI = Math.PI;
        const E = Math.E;

        // VALIDATE EXPRESSION

        if (!/^[0-9+\-*/().,\sA-Za-z_]*$/.test(exp)) {

            throw new Error("Invalid expression");

        }

        // CALCULATE RESULT

        const result = Function(

            "sin",
            "cos",
            "tan",
            "sqrt",
            "log10",
            "log",
            "factorial",
            "PI",
            "E",

            `"use strict"; return (${exp})`

        )(

            sin,
            cos,
            tan,
            sqrt,
            log10,
            log,
            factorial,
            PI,
            E

        );

        if (
            typeof result !== "number" ||
            !Number.isFinite(result)
        ) {

            throw new Error("Math Error");

        }

        answer = Number(
            parseFloat(result.toPrecision(12))
        );

        expressionLine.textContent =
            expression + " =";

        expression = String(answer);

    }

    catch (error) {

        expressionLine.textContent =
            "Invalid Expression";

        expression = "Error";

    }

    render();

}


// BUTTON CLICK EVENTS

document
    .querySelector(".buttons")
    .addEventListener("click", function(event) {

        const button = event.target.closest("button");

        if (!button) return;

        const action = button.dataset.action;

        if (action === "clear") {

            clearAll();

        }

        else if (action === "delete") {

            deleteLast();

        }

        else if (action === "equals") {

            calculate();

        }

        else {

            append(button.dataset.value);

        }

    });


// DEG / RAD SWITCH

angleButton.addEventListener("click", function() {

    isDegree = !isDegree;

    render();

});


// KEYBOARD SUPPORT

document.addEventListener("keydown", function(event) {

    if (/^[0-9.]$/.test(event.key)) {

        append(event.key);

    }

    else if (
        ["+", "-", "(", ")"].includes(event.key)
    ) {

        append(event.key);

    }

    else if (event.key === "*") {

        append("×");

    }

    else if (event.key === "/") {

        event.preventDefault();

        append("÷");

    }

    else if (
        event.key === "Enter" ||
        event.key === "="
    ) {

        event.preventDefault();

        calculate();

    }

    else if (event.key === "Backspace") {

        deleteLast();

    }

    else if (event.key === "Escape") {

        clearAll();

    }

});


// INITIALIZE

render();
