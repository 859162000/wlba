define ['jquery'], ($)->

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
      url: params.url
      product_type: params.product_type
      product_name: params.product_name
      user_name: params.user_name
      phone: params.phone
    }

  loadData: loadData
  isValidType: isValidType

  loadPortfolio: loadPortfolio

  createPreOrder: createPreOrder
