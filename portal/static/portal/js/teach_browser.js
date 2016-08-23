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

$(document).ready(function(){
    targetOffset = getTargetOffset();
    setActive();
    expandList();
    backButton();
});

$(document).scroll(function() {
    //console.log($(window).scrollTop())
    if ($(this).scrollTop() > 172) {
        $('nav').addClass("sticky");
    }
    else {
        $('nav').removeClass("sticky");
    }

    if ($(this).scrollTop() > 5222) {
        $('floating-banner').addClass("sticky-banner");
    }
    else {
        $('floating-banner').removeClass("sticky-banner");
    }
});

function backButton() {
    $('#back').click(function(){
        parent.history.back();
        return false;
    });
}

function expandList() {
    $('ol.collapsible-list').hide();

    $('a.nav-head-collapse.ks1').click(function(){
        $('ol.collapsible-list.uks2').hide();
        $('ol.collapsible-list.lks2').hide();
        $('ol.collapsible-list.ks1').toggle();
    });

    $('a.nav-head-collapse.lks2').click(function(){
        $('ol.collapsible-list.ks1').hide();
        $('ol.collapsible-list.uks2').hide();
        $('ol.collapsible-list.lks2').toggle();
    });

    $('a.nav-head-collapse.uks2').click(function(){
        $('ol.collapsible-list.ks1').hide();
        $('ol.collapsible-list.lks2').hide();
        $('ol.collapsible-list.uks2').toggle();
    });
}

function setActive() {
    $('a[href*=#]').click(function(){
       $('a[href*=#]').removeClass('active');
       $(this).addClass('active');
    });
}

function getTargetOffset() {
    $('a[href*=#]').click(function() {
        if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
            $target = getTarget(this);
            if ($target.length) {
                var targetOffset = $target.offset().top;
                animate(targetOffset);
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
    $('html,body').animate({scrollTop: targetOffset}, 500);
}


// $(document).ready(function(){
// $('a[href*=#]').click(function() {
//     if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'')
//     && location.hostname == this.hostname) {
//       var $target = $(this.hash);
//       $target = $target.length && $target || $('[name=' + this.hash.slice(1) +']');
//       if ($target.length) {
//         var targetOffset = $target.offset().top;
//         $('html,body')
//         .animate({scrollTop: targetOffset}, 500);
//        return false;
//       }
//     }
//   });
// });
