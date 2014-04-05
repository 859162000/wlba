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

    'cashs': 'cashes'
    'cashes': 'cashes'
    '现金类理财产品': 'cashes'
    '现金': 'cashes'
    'favorite/trusts': 'favorite/trusts'
    'favorite/funds': 'favorite/funds'
    'favorite/cashes': 'favorite/cashes'
    'favorite/financings': 'favorite/financings'

  normalizeType = (type)->
    typeMapping[type]

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

  # change password
  changePassword = (params)->
    url = '/accounts/password/change/'
    $.post url,
      params

  addToFavorite = (e, type)->
    e.preventDefault()
    id = $(e.target).attr('data-id')
    is_favorited = $(e.target).attr('data-is-favorited')
    url = apiurl + 'favorite/' + type + '/'
    if is_favorited != '1'
      $.post url, {
        item: id
      }
      .done ()->
        $(e.target).html('取消')
        $(e.target).attr('data-is-favorited', '1')
      .fail (xhr)->
        if xhr.status == 403
          window.location.href = '/accounts/login/?next=' + window.location.href
        else if xhr.status == 409
          $(e.target).html('取消')
          $(e.target).attr('data-is-favorited', '1')
        else
          alert('收藏失败')
    else
      $.ajax {
        url: url + id + '/'
        type: 'DELETE'
      }
      .done ()->
        e.target.textContent = '收藏'
        $(e.target).attr('data-is-favorited', '0')
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

  loadFavorites = (type)->
    url = apiurl + 'favorite/' + type + '/'
    $.get url

  userExists = (identifier)->
    url = apiurl + 'user_exists/' + identifier + '/'
    $.get url

  window.addToFavorite = (e, type)->
    e.preventDefault()

    id = $(e.target).attr('data-id')
    is_favorited = $(e.target).attr('data-is-favorited')
    addToFavorite e, type, id, is_favorited

  parseQuery = (search)->
    queries = {};
    $.each(search.substr(1).split('&'), (index,value)->
      pair = value.split('=');
      if pair.length == 2
        queries[pair[0].toString()] = pair[1].toString())
    return queries

  deepCompare = (x, y)->
    compare2Objects = (x, y) ->
      p = undefined

      # remember that NaN === NaN returns false
      # and isNaN(undefined) returns true
      return true  if isNaN(x) and isNaN(y) and typeof x is "number" and typeof y is "number"

      # Compare primitives and functions.
      # Check if both arguments link to the same object.
      # Especially useful on step when comparing prototypes
      return true  if x is y

      # Works in case when functions are created in constructor.
      # Comparing dates is a common scenario. Another built-ins?
      # We can even handle functions passed across iframes
      return x.toString() is y.toString()  if (typeof x is "function" and typeof y is "function") or (x instanceof Date and y instanceof Date) or (x instanceof RegExp and y instanceof RegExp) or (x instanceof String and y instanceof String) or (x instanceof Number and y instanceof Number)

      # At last checking prototypes as good a we can
      return false  unless x instanceof Object and y instanceof Object
      return false  if x.isPrototypeOf(y) or y.isPrototypeOf(x)

      # check for infinitive linking loops
      return false  if leftChain.indexOf(x) > -1 or rightChain.indexOf(y) > -1

      # Quick checking of one object beeing a subset of another.
      # todo: cache the structure of arguments[0] for performance
      for p of y
        if y.hasOwnProperty(p) isnt x.hasOwnProperty(p)
          return false
        else return false  if typeof y[p] isnt typeof x[p]
      for p of x
        if y.hasOwnProperty(p) isnt x.hasOwnProperty(p)
          return false
        else return false  if typeof y[p] isnt typeof x[p]
        switch typeof (x[p])
          when "object", "function"
            leftChain.push x
            rightChain.push y
            return false  unless compare2Objects(x[p], y[p])
            leftChain.pop()
            rightChain.pop()
          else
            return false  if x[p] isnt y[p]
      true

    leftChain = []
    rightChain = []
    compare2Objects(x, y)

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
    parseQuery: parseQuery
    deepCompare: deepCompare
  }
