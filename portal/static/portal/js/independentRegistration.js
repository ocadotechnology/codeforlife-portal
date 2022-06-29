$(function() {
    const form = $("#form-fields");

    const dobDaySelect = $("#id_independent_student_signup-date_of_birth_day");
    const dobMonthSelect = $("#id_independent_student_signup-date_of_birth_month");
    const dobYearSelect = $("#id_independent_student_signup-date_of_birth_year");

    let dobDay;
    let dobMonth;
    let dobYear;

    if (isDobInputted()) {
        form.show();
    }
    else {
        form.hide();
    }

    dobDaySelect.add(dobMonthSelect).add(dobYearSelect).on("change", dobChangeHandler)

    function dobChangeHandler() {
        if (isDobInputted()) {
            const age = calculateAge();
            form.show();
            showFormAccordingToAge(age);
        }
        else {
            form.hide();
        }
    }

    function isDobInputted() {
        dobDay = dobDaySelect.find("option:selected").text();
        dobMonth = dobMonthSelect.find("option:selected").text();
        dobYear = dobYearSelect.find("option:selected").text();

        return dobDay !== "Day" && dobMonth !== "Month" && dobYear !== "Year";
    }

    function calculateAge() {
        const birthdate = new Date(`${dobYear}-${dobMonth}-${dobDay}`);
        const ageInMs = new Date() - birthdate;
        return Math.floor(ageInMs/1000/60/60/24/365);
    }

    function showFormAccordingToAge(age) {
        if (age < 18) {
            $("#independent-newsletter").hide();
        }
        else {
            $("#independent-newsletter").show();
        }

        if (age < 13) {
            $("#id_independent_student_signup-consent_ticked").prop("checked", true);
            $("#independent-consent").hide();

            $("#independent-parent-notification").show();

            $("#independent-email-help-text").text("Please enter your parent's email address");
            $("#id_independent_student_signup-email").attr("placeholder", "Parent's email address");
        }
        else
        {
            $("#independent-consent").show();
            $("#id_independent_student_signup-consent_ticked").prop("checked", false);

            $("#independent-parent-notification").hide();

            $("#independent-email-help-text").text("Enter your email address");
            $("#id_independent_student_signup-email").attr("placeholder", "Email address");
        }
    }
});
