define ['jquery'], ($)->
  $(document).ajaxSend (event, xhr, settings)->
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
    '公募基金': 'funds'

    '货币基金': ['funds', {type:'货币型'}]

    'cashs': 'cashes'
    'cashes': 'cashes'
    '现金类理财产品': 'cashes'
    '现金': 'cashes'

    'p2p': 'p2ps'
    'P2P': 'p2ps'
    'p2ps': 'p2ps'

    'favorite/trusts': 'favorite/trusts'
    'favorite/funds': 'favorite/funds'
    'favorite/cashes': 'favorite/cashes'
    'favorite/financings': 'favorite/financings'

  normalizeType = (type)->
    typeRecord = typeMapping[type]
    if typeof typeRecord == 'string'
      return typeRecord
    else
      return typeRecord[0]

  loadData = (type, params)->
    if _.has(typeMapping, type)
      typeRecord = typeMapping[type]

      normalizedType = typeRecord
      if typeof typeRecord != 'string'
        normalizedType = typeRecord[0]
        params = _.extend(params, typeRecord[1])

      url = apiurl + normalizedType + '/.jsonp?' + $.param(params)

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

  # change password
  changePassword = (params)->
    url = '/accounts/password/change/'
    $.post url,
      params

  addToFavorite = (target, type)->
    id = $(target).data('id')
    is_favorited = $(target).attr('data-is-favorited')
    url = apiurl + 'favorite/' + type + '/'
    if is_favorited != '1'
      $.post url, {
        item: id
      }
      .done ()->
        $(target).html('取消收藏')
        $(target).addClass('button-no-border')
        $(target).attr('data-is-favorited', '1')
      .fail (xhr)->
        if xhr.status == 403
          window.location.href = '/accounts/register/?next=' + window.location.href
        else if xhr.status == 409
          $(target).html('取消')
          $(target).addClass('button-no-border')
          $(target).attr('data-is-favorited', '1')
        else
          alert('收藏失败')
    else
      $.ajax {
        url: url + id + '/'
        type: 'DELETE'
      }
      .done ()->
        $(target).html('收藏')
        $(target).attr('data-is-favorited', '0')
        $(target).removeClass('button-no-border')
      .fail ()->
          alert '取消收藏失败'

  joinFavorites = (products, type, table, transformer)->
    loadData 'favorite/' + type, {}
    .done (favorites)->
      ids = _.map(favorites.results, (f)->
        return f.item.id)
      for i, product of products.results
        if _.contains ids, product.id
          product.is_favorited = 1
    .always ()->
      if transformer
        data = transformer products
        table.data data
      else
        table.data(products.results)
      table.isEmpty table.data().length == 0

  loadFavorites = (type)->
    url = apiurl + 'favorite/' + type + '/'
    $.get url

  userExists = (identifier)->
    url = apiurl + 'user_exists/' + identifier + '/'
    $.get url

  fundInfo = ()->
    url = apiurl + 'fund_info/'
    $.get url

  userProfile = (data)->
    url = apiurl + 'profile/'
    if not data?
      $.get url
    else
      $.ajax
        url: url
        type: 'PUT'
        data: data

  window.addToFavorite = (e, type)->
    e = e || window.event;
    target = e.target || e.srcElement;
    if(e.preventDefault)
      e.preventDefault();
    addToFavorite target, type

  isInRange = (param, range)->
    if param == range
      return true
    if !range
      return false
    params = param.split('-')
    ranges = range.split('-')
    # >300
    if ranges.length == 1
      ranges[0] = ranges[0].substr(1)
    if params.length == 1
      if params[0][0] == '>'
        params[0] = params[0].substr(1)
      params[0] = parseInt(params[0])

      if ranges.length == 2
        if params[0] >= ranges[0] && params[0] <= ranges[1]
          return true
        else
          return false
      if ranges.length == 1
        if params[0] >= ranges[0]
          return true
        else
          return false
    if params.length == 2
      params[0] = parseInt(params[0])
      params[1] = parseInt(params[1])
      if ranges.length == 2
        if params[0] >= ranges[0] && params[1] <= ranges[1]
          return true
        else
          return false
      if ranges.length == 1
        if params[0] >= ranges[0]
          return true
        else
          return false

  checkEmail = (identifier) ->
    re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    re.test identifier

  checkMobile = (identifier) ->
    re = /^1\d{10}$/
    re.test identifier

  checkBalance = (amount, element)->
    balance = $(element).attr('data-balance')
    return (amount - balance).toFixed(2) <= 0

  checkMoney = (amount, element)->
    re = /^\d+(\.\d{0,2})?$/
    re.test amount

  checkCardNo = (card_no)->
    re = /^\d{10,20}$/
    return re.test card_no

  purchaseP2P = (data)->
    $.post '/api/p2p/purchase/', data

  return {
    loadData: loadData
    isValidType: isValidType

    loadPortfolio: loadPortfolio

    createPreOrder: createPreOrder
    changePassword: changePassword

    addToFavorite: addToFavorite
    loadFavorites: loadFavorites
    joinFavorites: joinFavorites
    normalizeType: normalizeType

    userExists: userExists
    fundInfo: fundInfo
    userProfile: userProfile
    isInRange: isInRange
    checkEmail: checkEmail
    checkMobile: checkMobile

    purchaseP2P: purchaseP2P
    checkBalance: checkBalance
    checkMoney: checkMoney
    checkCardNo: checkCardNo
  }
