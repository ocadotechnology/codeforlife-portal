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