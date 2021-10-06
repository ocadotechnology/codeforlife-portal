// Here we want to send off an ajax request whenever the user types something
// but we want it limited to some rate. This method of setting timeouts will
// unfortunately introduce a delay but it was easy to implement and it ensures
// that every character the user types is considered and the last one cannot
// be missed off.

var timeout_scheduled = false;
function updateChosenOrgSelect() {
    if (!timeout_scheduled) {
        timeout_scheduled = true;
        update_timeout = setTimeout(function() {
            fuzzy_name = $('#' + FUZZY_NAME_FIELD_ID).val();
            $.getJSON(FUZZY_ORG_LOOKUP_URL, { fuzzy_name: fuzzy_name }, function(data) {
                select = document.getElementById(CHOSEN_ORG_FIELD_ID);
                select.options.length = 0;

                if (data.length > 0) {
                    for (var i = 0; i < data.length; i++) {
                        var d = data[i];
                        select.options.add(new Option(d.name + ', ' + d.postcode + ', ' + d.admin_domain, d.id));
                    }
                }
                else {
                    select.options.add(new Option('Select school/club', ''));
                    select.options[0].disabled = true;
                    select.options[0].style.display = 'none';
                }
            });
            timeout_scheduled = false;
        }, 200);
    }
}

$(function() {
    fuzzy_name = $('#' + FUZZY_NAME_FIELD_ID);
    if (fuzzy_name.length > 0) { // Only do things if the elements exist!!
        fuzzy_name.on('keydown', updateChosenOrgSelect);
        fuzzy_name.on('paste', updateChosenOrgSelect);
        fuzzy_name.on('cut', updateChosenOrgSelect);

        select = document.getElementById(CHOSEN_ORG_FIELD_ID);
        select.options.add(new Option('Select school/club', ''));
        select.options[0].disabled = true;
        select.options[0].style.display = 'none';
    }
});