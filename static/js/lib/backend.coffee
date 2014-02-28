define ['jquery'], ($)->
  $ document
  .ajaxSend (event, xhr, settings)->
    getCookie = (name)->
      cookieValue = null
      if document.cookie and document.cookie != ''
        cookies = document.cookie.split(';')
        for i in [0..document.cookie.length-1]
          cookie = jQuery.trim(cookies[i])
          if (cookie.substring(0, name.length + 1) == (name + '='))
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            break
      cookieValue

    sameOrigin = (url)->
      host = document.location.host
      protocol = document.location.protocol
      sr_origin = '//' + host
      origin = protocol + sr_origin
      (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        !(/^(\/\/|http:|https:).*/.test(url))

    safeMethod = (method)->
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))

    if not safeMethod(settings.type) and sameOrigin(settings.url)
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'))

  apiurl = '/api/'
  if document.location.protocol == 'file:'
    apiurl = 'http://127.0.0.1:8000/api/'

  # The type mapping which map several types to the correct products type
  typeMapping =
    '信托': 'trusts'
    'trust': 'trusts'
    'trusts': 'trusts'

    '银行理财': 'bank_financings'
    'bank': 'bank_financings'
    'financing': 'bank_financings'
    'financings': 'bank_financings'
    'bank_financings': 'bank_financings'

    'fund': 'funds'
    'funds': 'funds'
    '基金': 'funds'

  loadData = (type, params)->
    if _.has(typeMapping, type)
      url = apiurl + typeMapping[type] + '/.jsonp?' + $.param(params)

      $.ajax(url, {
        dataType: 'jsonp'
      })
    else
      # TODO use the similar as Defered syntax to return error
      if console?
        console.log "The type not supported"

  loadPortfolio = (params)->
    url = apiurl + 'portfolios/.jsonp?' + $.param(params)

    $.ajax(url, {
      dataType: 'jsonp'
    })

  isValidType = (type)->
    _.has(typeMapping, type)

  # create a preorder
  createPreOrder = (params)->
    url = apiurl + 'pre_orders/'

    $.post url, {
      product_url: params.product_url
      product_type: params.product_type
      product_name: params.product_name
      user_name: params.user_name
      phone: params.phone
    }

  loadData: loadData
  isValidType: isValidType

  loadPortfolio: loadPortfolio

  createPreOrder: createPreOrder
