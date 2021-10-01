function toggleStickySubnav (scrollToTop) {
  $(window).on('scroll', function () {
    var currentScroll = $(window).scrollTop()
    if (currentScroll >= scrollToTop) {
      if (!$('.sticky-subnav').hasClass('sub-nav--fixed')) {
        $('.sticky-subnav').addClass('sub-nav--fixed')
      }
      if (!$('#sticky-warning').hasClass('sub-nav--warning--fixed')) {
        $('#sticky-warning').addClass('sub-nav--warning--fixed')
      }
      $('#top').addClass('sub-nav--filler')
    } else {
      $('#sticky-warning').removeClass('sub-nav--warning--fixed')
      $('.sticky-subnav').removeClass('sub-nav--fixed')
      $('#top').removeClass('sub-nav--filler')
      $('.menu').removeClass('hide')
    }
  })
}

$(function () {
  $('a.x-icon').on('click', function () {
    $(this)
      .parent()
      .remove()
    return false
  })
})
