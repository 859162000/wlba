require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    'jquery.modal': 'lib/jquery.modal.min'

  shim:
    'jquery.modal': ['jquery']

require ['jquery', 'underscore', 'lib/backend', 'lib/modal'], ($, _, backend, modal)->
  $('.portfolio-submit').click ()->
    asset = $('#portfolio-asset')[0].value
    period = $('#portfolio-period')[0].value
    window.location.href = '/portfolio/?period=' + period + '&asset=' + asset

  $('.portfolio-input').keyup (e)->
    if e.keyCode == 13
      $('.portfolio-submit').click()

  currentBanner = 0
  banners = $('*[class^="home-banner"]')
  bannerCount = banners.length
  anchors = $('.background-anchor')
  setInterval(()->
      $(banners[currentBanner]).hide()
      $(anchors[currentBanner]).toggleClass('active')
      currentBanner = (currentBanner + 1) % bannerCount
      $(banners[currentBanner]).fadeIn()
      $(anchors[currentBanner]).toggleClass('active')
    , 6000)

  $('.background-anchor').click (e)->
    e.preventDefault()
    index = $(e.target).parent().index()
    if(index != currentBanner)
      $(banners[currentBanner]).hide()
      $(anchors[currentBanner]).toggleClass('active')
      $(banners[index]).fadeIn()
      $(anchors[index]).toggleClass('active')
      currentBanner = index

  $('.home-banner-2').click ()->
    window.location.href='/trust/detail/8526'

  trustId = 0
  trustName = ''
  $('.order-button').click (e)->
    e.preventDefault()
    trustId = $(e.target).attr('data-trust-id')
    trustName = $(e.target).attr('data-trust-name')
    $(this).modal()

  $('#preorder_submit').click (event)->
    event.preventDefault()

    name = $('#name_input').val()
    phone = $('#phone_input').val()

    if name and phone
      backend.createPreOrder
        product_url: trustId
        product_type: 'trust'
        product_name: trustName
        user_name: name
        phone: phone
      .done ->
          alert '预约成功，稍后我们的客户经理会联系您'
          $('#name_input').val ''
          $('#phone_input').val ''
          $.modal.close()

      .fail ()->
          alert '预约失败，请稍后再试或者拨打400-9999999'
