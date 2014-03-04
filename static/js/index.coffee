require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'

require ['jquery', 'underscore', 'knockout', 'lib/backend'], ($, _, ko, backend)->
  $(document).ready ->
    class DataViewModel
      constructor: ()->
        self = this

        self.trusts = ko.observable (_.pluck data.hot_trusts, 'trust')
        self.funds = ko.observable (_.pluck data.hot_funds, 'fund')
        self.financings = ko.observable (_.pluck data.hot_financings, 'bank_financing')

    model = new DataViewModel()
    ko.applyBindings(model)

    # setup the background switcher
    switchBackground = (max)->
      imageUrl = $('.big-background').css('background-image')
      matches = imageUrl.match(/\/bg(\d).jpg/)
      if matches.length == 2
        current = parseInt(matches[1]) + 1
        if current > max
          current = 1

        $('.big-background').css 'background-image',
          imageUrl.replace /\/bg\d.jpg/, '/bg' + current + '.jpg'

    switchBackgroundWrapper = ->
      switchBackground(4)
      setTimeout(switchBackgroundWrapper, 10 * 1000)

    setTimeout switchBackgroundWrapper, 10 * 1000
