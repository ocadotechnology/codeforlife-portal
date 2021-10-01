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
