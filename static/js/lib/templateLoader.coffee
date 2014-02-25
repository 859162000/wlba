define ['underscore', 'jquery'], (_, $)->
  mapping =
    '信托': 'trust-table'
    '银行理财': 'financing-table'
    '基金': 'fund-table'

  template = (type)->
    if _.has mapping, type
      mapping[type]
    else
      null

  template: template