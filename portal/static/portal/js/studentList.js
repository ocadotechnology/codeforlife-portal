function init() {
	$('#moveSelectedStudents').click(function() {
		students = document.getElementsByClassName('student');
		selectedStudents = [];
		for (var i = 0; i < students.length; i++) {
			if (students[i].checked) {
				selectedStudents.push(students[i].name)
			}
		}
		if (selectedStudents.length > 0) {
			// send request to move selectedStudents
			post('/teach/class/' + CLASS_CODE + '/students/move/', {csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(), transfer_students: JSON.stringify(selectedStudents)});
		}

	});
};

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

$( document ).ready(function() {
    init();
});
