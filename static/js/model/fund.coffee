define ['jquery', 'underscore', 'knockout'], ($, _, ko)->

  class viewModel
    constructor: (context)->
      self = this
      if _.has(context, 'data')
        _(self).extend(context['data'])

    frontEndRate: ()=>
      if @issue_front_end_charge_rates.length > 0
        return @issue_front_end_charge_rates[0].value.toFixed(2) + '%'
      return '--'

    backEndRate:  ()=>
      if @issue_back_end_charge_rates.length > 0
        return @issue_back_end_charge_rates[0].value.toFixed(2) + '%'
      return '--'

  viewModel: viewModel
