require.config(
  paths:
    jquery: 'lib/jquery.min'
)

require ['jquery'], ($)->
    $('#huifu-pay').submit()

