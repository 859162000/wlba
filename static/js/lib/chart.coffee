define ['jquery', 'underscore', 'raphael'], ($, _, raphael)->
  pie = (cx, cy, r, percent, startPercent)->
    if percent > 1
      percent = percent / 100

    if startPercent > 1
      startPercent = startPercent / 100
    moveTo = 'M' + cx + ' ' + cy
    tx = r * Math.sin(startPercent * Math.PI * 2)
    ty = r * Math.cos(startPercent * Math.PI * 2)
    x = cx + tx
    y = cy - ty
    lineTo = 'L' + x + ' ' + y

    txend = r * Math.sin((startPercent+percent) * Math.PI * 2)
    tyend = r * Math.cos((startPercent+percent) * Math.PI * 2)
    xend = cx + txend
    yend = cy - tyend

    largeFlag = 1
    if percent <= 0.5
      largeFlag = 0
    arcTo = 'A ' + r + ' ' + r + ' 0 ' + largeFlag + ' 1 ' + xend + ' ' + yend

    result = moveTo + lineTo + arcTo + 'z'

    middlePercent = startPercent + (percent / 2)
    txmiddle = r * Math.sin(middlePercent * Math.PI * 2)
    tymiddle = r * Math.cos(middlePercent * Math.PI * 2)
    xmiddle = cx + txmiddle
    ymiddle = cy - tymiddle

    tx2middle = r * 1.2 * Math.sin(middlePercent * Math.PI * 2)
    ty2middle = r * 1.2 * Math.cos(middlePercent * Math.PI * 2)
    x2middle = cx + tx2middle
    y2middle = cy - ty2middle

    flag = 1
    if middlePercent > 0.5
      flag = -1

    annotation = 'M' + xmiddle + ' ' + ymiddle + 'L' + x2middle + ' ' + y2middle + 'H' + (cx + flag * r * 1.2)

    return {
      pie: result
      annotation: annotation
      'right-side': flag >= 1
      'text-position': [cx + flag * r * 1.2, y2middle]
      direction: [(xmiddle - cx)/r, (ymiddle - cy)/r]
    }

  class PieChart
    constructor: (element, context)->
      self = this
      @context = context
      @strokeWidth = "3px"
      @paper = new Raphael(element)

      @events = {}

      if _.has context, 'events'
        @events = _(@events).extend context.events

      self = this
      paths = []
      current_percent_sum = 0
      for piece in @context.pieces
        path = pie @context.x, @context.y, @context.r, piece.percent, current_percent_sum
        el = @paper.path path.pie
        .attr
          fill: piece.color
          stroke: 'white'
          'stroke-width': @strokeWidth
        .data
          'piece': piece
          'path': path
        .click (e)->
          piece = this.data 'piece'
          path = this.data 'path'
          direction = path.direction

          delta = 10
          translate = 't ' + delta * direction[0] + ',' + delta * direction[1]
          for p in paths
            p.animate
              transform: ''
          this.attr
            fill: piece.color
            'stroke-width': @strokeWidth
            stroke: 'white'

          this.animate
            transform: translate + "s1.1"
          , 200, "elastic"

          if _.has self.events, 'click'
            self.events.click piece

        paths.push el # Push the element, in future we can modify them

        @paper.path path.annotation
        .attr
          stroke: piece.color
          'stroke-width': '1px'

        anchor = 'end'
        if path['right-side']
          anchor = 'start'

        @paper.text path['text-position'][0], path['text-position'][1], piece.percent + '%'
        .attr
          'font-size':15
          'text-anchor': anchor
          fill: piece.color
          'font-family':'Trebuchet MS'

        current_percent_sum += piece.percent


  return PieChart: PieChart