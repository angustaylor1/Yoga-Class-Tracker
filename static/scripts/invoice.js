let classSelect = document.querySelector("#classes");
let inputsContainer = document.querySelector(".dates-input-container");

classSelect.addEventListener("change", function (e) {
    // get the number of classes
    let container = document.querySelector('.dates-input-container');
    container.innerHTML = "";

    let count = this.value
    for (let i = 1; i <= count; i++) {
        // create label for input

        let label = document.createElement("label");
        label.textContent = `Class ${i} Date:`;
        label.setAttribute("for", `class-date-${i}`)

        let input = document.createElement("input");
        input.type = "date";
        input.name = `class-date-${i}`;
        input.id = `class-date-${i}`;
        input.required = true;


        let div = document.createElement("div");

        div.appendChild(label);
        div.appendChild(input);

        inputsContainer.appendChild(div)


    };
});

let studioSelector = document.querySelector("#recipient");
let classTypeContainer = document.querySelector("#class-types-container");



studioSelector.addEventListener("change", function (e) {
    classTypeContainer.innerHTML = "";
    let select = document.createElement("select");
    let name = this.value;
    let disabled = document.createElement("option");
    disabled.setAttribute("disabled", "")
    disabled.setAttribute("selected", "")
    disabled.innerHTML = "Class Type"

    if (name == "Hotpod Yoga Dulwich") {

        let option1 = document.createElement("option");
        option1.name = "60mins"
        option1.innerHTML = "60mins"

        let option2 = document.createElement("option");
        option2.name = "45mins";
        option2.innerHTML = "45mins";

        select.appendChild(disabled);
        select.appendChild(option1);
        select.appendChild(option2);

        classTypeContainer.appendChild(select)
    }
    else if (name == "David Rhodes") {

        let option = document.createElement("option");
        option.name = "private-session";
        option.innerHTML = "1 hour private session";

        select.appendChild(disabled);
        select.appendChild(option);

        classTypeContainer.appendChild(select)


    }
    else if (name === "ONCORE") {
        let option = document.createElement("option");
        option.name = "flow-to-restore";
        option.innerHTML = "60min Flow to Restore";

        select.appendChild(disabled);
        select.appendChild(option);

        classTypeContainer.appendChild(select);
    }
    else if (name === "St Martin's School") {
        let option = document.createElement("option");
        option.name = "musical-theatre-lessons";
        option.innerHTML = "Musical Theatre Lessons";

        let classes = document.querySelector(".classes-amount");
        classes.innerHTML = "";

        select.appendChild(disabled);
        select.appendChild(option);

        let select2 = document.createElement("select");
        select2.setAttribute("style", "margin-top: 15px;")

        let disabled2 = document.createElement("option");
        disabled2.name = "num-of-weeks";
        disabled2.innerHTML = "How many weeks?";
        disabled2.setAttribute("disabled", "");
        disabled2.setAttribute("selected", "");
        select2.appendChild(disabled2);

        let count = 20;

        for (i = 1; i <= count; i++) {
            optionWeeks = document.createElement("option");
            optionWeeks.name = `week ${i}`;
            optionWeeks.innerHTML = `${i}`;

            select2.appendChild(optionWeeks)
        }


        classTypeContainer.appendChild(select);
        classTypeContainer.appendChild(select2);

        select2.addEventListener("change", function (e) {
            let weeks = e.target.value;

            for (let i = 1; i <= weeks; i++) {
                let label = document.createElement("label");
                label.textContent = `Week ${i} Classes:`;
                label.setAttribute("for", `week ${i}`)


                let input = document.createElement("input");
                input.name = `week ${i}`;
                input.id = `week ${i}`
                input.type = `number`

                classes.appendChild(label);
                classes.appendChild(input);
            }

            let count = this.value
            for (let i = 1; i <= count; i++) {
                // create label for input
                let label = document.createElement("label");
                label.textContent = `Class ${i} Date:`;
                label.setAttribute("for", `class-date-${i}`)

                let input = document.createElement("input");
                input.type = "date";
                input.name = `class-date-${i}`;
                input.id = `class-date-${i}`;
                input.required = true;


                let div = document.createElement("div");

                div.appendChild(label);
                div.appendChild(input);

                inputsContainer.appendChild(div)


            };


        })
    }
})
