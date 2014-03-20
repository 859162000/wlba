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

    'cashs': 'cashes'
    'cashes': 'cashes'
    '现金类理财产品': 'cashes'

    'favorite/trusts': 'favorite/trusts'

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

  addToFavorite = (e, type, id, is_favorited)->
    url = apiurl + 'favorite/' + type + '/'
    if is_favorited != '1'
      $.post url, {
        item: id
      }
      .done ()->
        $(e.target).html('取消收藏')
        $(e.target).attr('data-is-favorited', '1')
      .fail (xhr)->
        if xhr.status == 403
          window.location.href = '/accounts/login/?next=' + window.location.href
        else if xhr.status == 409
          $(e.target).html('取消收藏')
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

  joinFavorites = (products, type, table)->
    loadData 'favorite/' + type, {}
    .done (favorites)->
      ids = _.map(favorites.results, (f)->
        return f.item.id)
      for i, product of products.results
        if _.contains ids, product.id
          product.is_favorited = 1
      table.data(products.results)

  loadFavorites = (type)->
    url = apiurl + 'favorite/' + type + '/'
    $.get url

  window.addToFavorite = (e)->
    e.preventDefault()

    id = $(e.target).attr('data-id')
    is_favorited = $(e.target).attr('data-is-favorited')
    addToFavorite e, 'trusts', id, is_favorited

  return {
    loadData: loadData
    isValidType: isValidType

    loadPortfolio: loadPortfolio

    createPreOrder: createPreOrder
    changePassword: changePassword

    addToFavorite: addToFavorite
    loadFavorites: loadFavorites
    joinFavorites: joinFavorites
  }



