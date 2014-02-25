define ['jquery', 'underscore', 'knockout'], ($, _, ko)->

  class viewModel
    constructor: (context)->
      self = this
      if _.has(context, 'data')
        _(self).extend(context['data'])

  viewModel: viewModel