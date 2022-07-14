$(function() {
    const formSet = $("#register-forms");
    const form = $("#form-fields");

    const dobDaySelect = $("#id_independent_student_signup-date_of_birth_day");
    const dobMonthSelect = $("#id_independent_student_signup-date_of_birth_month");
    const dobYearSelect = $("#id_independent_student_signup-date_of_birth_year");

    let dobDay;
    let dobMonth;
    let dobYear;

    showFormIfDobInputted();

    dobDaySelect.add(dobMonthSelect).add(dobYearSelect).on("change", showFormIfDobInputted)

    function showFormIfDobInputted() {
        if (isDobInputted()) {
            const age = calculateAge();
            showFormAccordingToAge(age);
        }
        else {
            hideForm();
        }
    }

    function isDobInputted() {
        dobDay = dobDaySelect.val();
        dobMonth = dobMonthSelect.val();
        dobYear = dobYearSelect.val();

        return dobDay !== "" && dobMonth !== "" && dobYear !== "";
    }

    function calculateAge() {
        const birthdate = new Date(`${dobYear}-${dobMonth}-${dobDay}`);
        const ageInMs = new Date() - birthdate;
        return Math.floor(ageInMs/1000/60/60/24/365.25);
    }

    function showFormAccordingToAge(age) {
        showForm();

        if (age < 18) {
            $("#independent-newsletter").hide();

            $("#independent-adult-legal").hide();
            $("#independent-child-legal").show();
        }
        else {
            $("#independent-newsletter").show();

            $("#independent-adult-legal").show();
            $("#independent-child-legal").hide();
        }

        if (age < 13) {
            $("#id_independent_student_signup-consent_ticked").prop("checked", true);
            $("#independent-consent").hide();

            $("#independent-parent-notification").show();

            $("#independent-email-help-text").text("Please enter your parent's email address");
            $("#id_independent_student_signup-email").attr("placeholder", "Parent's email address");
        }
        else {
            $("#independent-consent").show();
            $("#id_independent_student_signup-consent_ticked").prop("checked", false);

            $("#independent-parent-notification").hide();

            $("#independent-email-help-text").text("Enter your email address");
            $("#id_independent_student_signup-email").attr("placeholder", "Email address");
        }
    }

    function hideForm() {
        formSet.addClass("align-items-start");
        form.hide();
    }

    function showForm() {
        formSet.removeClass("align-items-start");
        form.show();
    }
});
