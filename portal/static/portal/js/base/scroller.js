$(function() {
    $('input, textarea').placeholder();
});

function animateScroll(bannerHeight) {
    $('a[href*="#"]').click(function() {
        if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
            history.pushState({}, "", this.href);
            let $target = getTarget(this);
            if ($target.length) {
                animate($target.offset().top - bannerHeight);
                return false;
            }
        }
    });
}

function getTarget(clickTarget) {
    let $target = $(clickTarget.hash);
    $target = $target.length && $target || $('[name=' + clickTarget.hash.slice(1) +']');
    return $target;
}

function animate(targetOffset) {
    $('html,body').animate({scrollTop: targetOffset}, 1000);
}

function invokeColorbox() {
    $(".youtube").colorbox({
        iframe:true,
        innerWidth:640,
        innerHeight:390,
        transition: 'fade',
        closeButton: true
    });
}

$(document).ready(function() {
    let bannerHeight = $('.sticky-subnav').height();
    if(bannerHeight) {
        animateScroll(bannerHeight);
    }
    else {
        animateScroll($('.menu').height() * 1.25);
    }
});

$(window).on('scroll', function() {
    let scroll = $(window).scrollTop();
    if (scroll > 0 && $('.dropdown').hasClass('open')) {
        $('.dropdown').removeClass('open');
        $('.button--dropdown').attr("aria-expanded", "false");
    }
});
