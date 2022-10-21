class AdditionalFunctions{
    static async getJsonData(destination, message) {
        let url =  `${window.origin}` + destination;
        let response = await fetch(url,{
            method: "POST",
            credentials: "include",
            body: JSON.stringify(message),
            cache: "no-cache",
            headers: new Headers({
                "content-type":"application/json"
            })
        })
        return await response.json();
    }
}

class InputHandler{
    constructor(input_name) {
    this.input_name = input_name;
    }

    setInputValue(input_value){
        let inputs = document.getElementsByName(this.input_name)
        for (let input of inputs) {
           input.value = input_value
        }
    }
}

class CalendarHandler{
    constructor() {
        this.displayedDate = new Date();
    }

    async displayCalendar() {
        const monthCz = ["Leden","Únor","Březen","Duben","Květen","Červen","Červenec","Srpen","Září","Ríjen","Listopad","Prosinec"];
        const monthEn = ['January','February','March','April','May','June','July','August','September','October','November','December'];
        let date = this.displayedDate;
        let displayedMonthNumber = date.getMonth();
        let displayedYear = date.getFullYear() ;
        let daysInMonth = new Date(displayedYear, displayedMonthNumber + 1, 0).getDate();
        let displayedMonthEn = monthEn[ displayedMonthNumber ];
        let displayedMonthCz = monthCz[displayedMonthNumber];
        const firstDayOfTheMonth = new Date(displayedMonthEn  + " 1, " + displayedYear + " 00:00:00");
        let monthFirstWeekDay = firstDayOfTheMonth.getDay();
        let month_occupancy;
        let tbody;

        let message = {
            month: displayedMonthNumber,
            year: displayedYear
        }

        month_occupancy = await AdditionalFunctions.getJsonData('/consultation_days',message);
        tbody = this.fillTbody(monthFirstWeekDay, daysInMonth, month_occupancy,displayedMonthNumber, displayedYear);
        document.getElementById("calendarHeader").innerHTML = displayedMonthCz + ', ' + displayedYear + ' ' ; // budut owibki pomenay na monthCz[date.getMonth()]
        document.getElementById("calendarBody").innerHTML = tbody;
    }


    displayNextMonth() {
        this.displayedDate.setMonth( this.displayedDate.getMonth() + 1 );
        this.displayCalendar();
    }

    displayPrevMonth() {
        this.displayedDate.setMonth( this.displayedDate.getMonth() - 1 );
        this.displayCalendar();
    }

    displayCurrMonth() {
        this.displayedDate = new Date();
        this.displayCalendar();
    }

    fillTbody(monthFirstWeekDay, daysInMonth, month_occupancy,displayedMonthNumber, displayedYear){
        let tbody = "<tr>";
        let fullDaysArray = month_occupancy["full_consultation_days"];
        let freeDaysArray = month_occupancy["free_consultation_days"];

        if (monthFirstWeekDay === 0) {
            monthFirstWeekDay = 7;
        }

        for (let i = 1; i < monthFirstWeekDay; i++) {
            tbody += "<td> </td>\n";
        }

        for (let i = 1, j = monthFirstWeekDay; i <= daysInMonth;){
            for (; j < 8 && i <= daysInMonth; j++){
                if ( fullDaysArray.includes(i) && !freeDaysArray.includes(i)){
                    tbody += "<td><a href=\"/reservations/" + i + "/" + displayedMonthNumber + "/"+ displayedYear +"\" class=\"link-danger\">" + i + "</a></td>\n";
                }
                else if(freeDaysArray.includes(i)){
                    tbody += "<td><a href=\"/reservations/" + i + "/" + displayedMonthNumber + "/"+ displayedYear +"\" class=\"link-success\">" + i + "</a></td>\n";
                }
                else{
                    tbody += "<td>" + i + "</td>\n";
                }
                i++
            }
            tbody += "</tr>";
            j = 1;
        }
        tbody += "</tr>";
        return tbody;
    }

}

 function handleCheckBox(){
            let checkBox = document.getElementById("repeatCheckbox");
            let div_var = document.getElementById("repeatForm");

            if (checkBox.checked === true){
                div_var.style.display = "block";
            } else {
                div_var.style.display = "none";
            }
        }


function toggle(source) {
            let checkboxes = document.querySelectorAll('input[type="checkbox"]');
            for (let i = 0; i < checkboxes.length; i++) {
                if (checkboxes[i] !== source)
                    checkboxes[i].checked = source.checked;
            }
        }


