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
            $("#deleteSelectedStudents-confirm").dialog("open");
        });
        event.preventDefault();
    });

    $("#deleteSelectedStudents-confirm").dialog({
        autoOpen: false,
        resizable: false,
        height:200,
        modal: true,
        buttons: {
            Cancel: function() {
                $( this ).dialog( "close" );
            },
            "Delete Students": function() {
                $( this ).dialog( "close" );
                postSelectedStudents(DELETE_STUDENTS_URL);
            }
        }
    });

    $('#selectedStudentsListToggle').click(function() {
        var students = document.getElementsByClassName('student');
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
        var students = document.getElementsByClassName('student');

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

    })
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
    var students = document.getElementsByClassName('student');
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

function post(path, params) {

    var form = document.createElement("form");
    form.setAttribute("method", 'POST');
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
}
