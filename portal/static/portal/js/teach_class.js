$(function() {
	$('#moveSelectedStudents').click(function() {
		postSelectedStudents(MOVE_STUDENTS_URL);
	});

    $('#dismissSelectedStudents').click(function() {
        postSelectedStudents(DISMISS_STUDENTS_URL);
    });

    // Link to open the dialog
    $("#deleteSelectedStudents").click(function(event) {
        runIfStudentsSelected(function() {
            openConfirmationBox('deleteStudents');
        });
        event.preventDefault();
    });

    $('#selectedStudentsListToggle').click(function() {
        var students = $('.student');
        var selectedStudents = [];
        for (var i = 0; i < students.length; i++) {
            if (students[i].checked) {
                selectedStudents.push(students[i].name)
            }
        }
        if (selectedStudents.length < students.length) {
            // select all students
            for (var i = 0; i < students.length; i++) {
                students[i].checked = true
            }
            $('#selectedStudentsListToggle')[0].checked = true
            $('#num_students_selected').text(students.length)

        }
        else {
            // unselect all students
            for (var i = 0; i < students.length; i++) {
                students[i].checked = false
            }
            $('#selectedStudentsListToggle')[0].checked = false
            $('#num_students_selected').text("0")
        }
    });
    $('.student').click(function() {
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

    $("#deleteClass").click(function(event) {
        openConfirmationBox('deleteClass');
        event.preventDefault();
    });
});

function postSelectedStudents(path) {
    runIfStudentsSelected(function(selectedStudents) {
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
