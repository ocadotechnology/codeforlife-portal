/* global post */
/* global postWithCsrf */
/* global showPopupConfirmation */

var CONFIRMATION_DATA = {};

$(function () {
    $('#selectedStudentsListToggle').click(function () {
        var students = $('.student');
        var selectedStudents = [];
        for (var i = 0; i < students.length; i++) {
            if (students[i].checked) {
                selectedStudents.push(students[i].name)
            }
        }
        if (selectedStudents.length < students.length) {
            // select all students
            for (var j = 0; j < students.length; j++) {
                students[j].checked = true
            }
            $('#selectedStudentsListToggle')[0].checked = true;
            $('#num_students_selected').text(students.length)

        }
        else {
            // unselect all students
            for (var k = 0; k < students.length; k++) {
                students[k].checked = false
            }
            $('#selectedStudentsListToggle')[0].checked = false;
            $('#num_students_selected').text("0")
        }
    });
    $('.student').click(function () {
        var students = $('.student');

        var count = 0;
        for (var i = 0; i < students.length; i++) {
            if (students[i].checked) {
                count++;
            }
        }
        if (count < students.length) {
            // set list select toggler unchecked
            $('#selectedStudentsListToggle')[0].checked = false
        }
        if (count == students.length) {
            // set list select toggler unchecked
            $('#selectedStudentsListToggle')[0].checked = true
        }
        $('#num_students_selected').text(count)
    });
});

function deleteClassConfirmation(path) {
    var title = "Delete class";
    var text = "<div class='popup-text'><p class='body-text'>This class will be permanently deleted. Are you sure?</p></div>";
    var confirm_handler = "postWithCsrf('" + path + "')";

    showPopupConfirmation(title, text, confirm_handler);
}

function deleteStudentsConfirmation(path) {
    runIfStudentsSelected(function () {
        var title = "Delete students";
        var text = "<div class='popup-text'><p class='body-text'>These students will be permanently deleted. Are you sure?</p></div>";
        var confirm_handler = "postSelectedStudents('" + path + "')";

        showPopupConfirmation(title, text, confirm_handler);
    })
}

function resetStudentPasswords(path) {
    runIfStudentsSelected(function () {
        var title = "Reset student passwords";
        var text = "<div class='popup-text'><p class='body-text'>These students will have their passwords permanently changed. You will be given the option to print out the new passwords. Are you sure that you want to continue?</p></div>";
        var confirm_handler = "postSelectedStudents('" + path + "')";

        showPopupConfirmation(title, text, confirm_handler);
    })
}

function postSelectedStudents(path) {
    runIfStudentsSelected(function (selectedStudents) {
        post(path, {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            transfer_students: JSON.stringify(selectedStudents)
        });
    });
}

function runIfStudentsSelected(func) {
    var students = $('.student');
    var selectedStudents = [];
    for (var i = 0; i < students.length; i++) {
        if (students[i].checked) {
            selectedStudents.push(students[i].name)
        }
    }

    if (selectedStudents.length > 0) {
        func(selectedStudents);
    }
}
