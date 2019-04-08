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

$(document).ready(function(){
    animateScroll();
    setActive();
    expandList();
    floatingBanner();
    downloadAnalytics();
});

$(document).scroll(function() {
    floatingNav();
    floatingBanner();
});

function floatingNav() {
    if ($(this).scrollTop() > 220) {
        $('nav').addClass("sticky");
    }
    else {
        $('nav').removeClass("sticky");
    }
}

function floatingBanner(){

    var distanceFromBottom = $(document).height() - ($(window).height() + $('body').scrollTop());

    if (distanceFromBottom < 70) {
        $('#banner').removeClass("floating-banner").addClass("sticky-banner");
    } else {
        $('#banner').removeClass("sticky-banner").addClass("floating-banner");
    }
}

function expandList() {
    $('ol.collapsible-list').hide();

    $('nav.side-nav').on("click", ".nav-head-collapse", function(){
        var $next = $(this).next();
        $('ol.collapsible-list').not($next).hide();
        $next.toggle();
    });
}

function setActive() {
    $('a[href*=#]').click(function(){
       $('a[href*=#]').removeClass('active');
       $(this).addClass('active');
    });
}

function animateScroll() {
    $('a[href*=#]').click(function() {
        if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
            history.pushState({}, "", this.href);
            var $target = getTarget(this);
            if ($target.length) {
                animate($target.offset().top);
                return false;
            }
        }
    });
}

function getTarget(clickTarget){
    var $target = $(clickTarget.hash);
    $target = $target.length && $target || $('[name=' + clickTarget.hash.slice(1) +']');
    return $target;
}

function animate(targetOffset){
    $('html,body').animate({scrollTop: targetOffset}, 600);
}

function downloadAnalytics() {
    $('a.download').click(function(){
        var filename = getFileName(this.href);
        send_download_event(filename);
    });
}

function getFileName(href) {
    var fileExtension = href.split(".").pop();

    if (fileExtension === "zip" || fileExtension === "mp4") {
        return href.split("/").pop();
    } else{
        return window.location.pathname.split("/").pop();
    }
}

function send_download_event(name_of_file){
    ga('send', {
    hitType: 'event',
    eventCategory: 'PDFs',
    eventAction: 'download',
    eventLabel: name_of_file
    });
}
