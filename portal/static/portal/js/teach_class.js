/*
Code for Life

Copyright (C) 2016, Ocado Innovation Limited

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

ADDITIONAL TERMS – Section 7 GNU General Public Licence

This licence does not grant any right, title or interest in any “Ocado” logos,
trade names or the trademark “Ocado” or any other trademarks or domain names
owned by Ocado Innovation Limited or the Ocado group of companies or any other
distinctive brand features of “Ocado” as may be secured from time to time. You
must not distribute any modification of this program using the trademark
“Ocado” or claim any affiliation or association with Ocado or its employees.

You are not authorised to use the name Ocado (or any of its trade names) or
the names of any author or contributor in advertising or for publicity purposes
pertaining to the distribution of this program, without the prior written
authorisation of Ocado.

Any propagation, distribution or conveyance of this program must include this
copyright notice and these terms. You must not misrepresent the origins of this
program; modified versions of the program must be marked as such and not
identified as the original program.
*/
$(function() {
	$('#moveSelectedStudents').click(function() {
		postSelectedStudents(MOVE_STUDENTS_URL);
        return false;
	});

    $('#dismissSelectedStudents').click(function() {
        postSelectedStudents(DISMISS_STUDENTS_URL);
        return false;
    });

    // Link to open the dialog
    $("#deleteSelectedStudents").click(function() {
        runIfStudentsSelected(function() {
            openConfirmationBox('deleteStudents');
        });
        return false;
    });

    $("#resetSelectedStudents").click(function() {
        runIfStudentsSelected(function() {
            openConfirmationBox('resetStudents');
        });
        return false;
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

    $("#deleteClass").click(function() {
        openConfirmationBox('deleteClass');
        return false;
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
