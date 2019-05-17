/*
Code for Life

Copyright (C) 2019, Ocado Innovation Limited

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

/* global postWithCsrf */

function deleteGameConfirmation(path, game_name) {
    var $content =
        "<div class='dialog-overlay'>" +
        "<div class='dialog'>" +
        "<header><h3> Delete Game </h3></header>" +
        "<div class='dialog-msg'><p> Are you sure you want to delete the game: <strong>" + game_name +
        "</strong>?</p><p> Deleting will permanently delete players&rsquo; progress for this particular game.</p></div>" +
        "<footer><button id='cancel' class='button--medium button--cancel'> Cancel </button>" +
        "<button id='delete_game' class='button--medium button--delete'> Delete game </button></footer></div></div>";
    $('body').prepend($content);
    $('#delete_game').click(function () {
        postWithCsrf(path);
        $(this).parents('.dialog-overlay').remove();
    });
    $('#cancel').click(function () {
        $(this).parents('.dialog-overlay').remove();
    });
}
