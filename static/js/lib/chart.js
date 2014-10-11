(function() {
  define(['jquery', 'underscore', 'raphael'], function($, _, raphael) {
    var PieChart, pie;
    pie = function(cx, cy, r, percent, startPercent) {
      var annotation, arcTo, flag, largeFlag, lineTo, middlePercent, moveTo, result, tx, tx2middle, txend, txmiddle, ty, ty2middle, tyend, tymiddle, x, x2middle, xend, xmiddle, y, y2middle, yend, ymiddle;
      if (percent > 1) {
        percent = percent / 100;
      }
      if (percent > 0.99) {
        percent = 0.99;
      }
      if (startPercent > 1) {
        startPercent = startPercent / 100;
      }
      moveTo = 'M' + cx + ' ' + cy;
      tx = r * Math.sin(startPercent * Math.PI * 2);
      ty = r * Math.cos(startPercent * Math.PI * 2);
      x = cx + tx;
      y = cy - ty;
      lineTo = 'L' + x + ' ' + y;
      txend = r * Math.sin((startPercent + percent) * Math.PI * 2);
      tyend = r * Math.cos((startPercent + percent) * Math.PI * 2);
      xend = cx + txend;
      yend = cy - tyend;
      largeFlag = 1;
      if (percent <= 0.5) {
        largeFlag = 0;
      }
      arcTo = 'A ' + r + ' ' + r + ' 0 ' + largeFlag + ' 1 ' + xend + ' ' + yend;
      result = moveTo + lineTo + arcTo + 'z';
      middlePercent = startPercent + (percent / 2);
      txmiddle = r * Math.sin(middlePercent * Math.PI * 2);
      tymiddle = r * Math.cos(middlePercent * Math.PI * 2);
      xmiddle = cx + txmiddle;
      ymiddle = cy - tymiddle;
      tx2middle = r * 1.1 * Math.sin(middlePercent * Math.PI * 2);
      ty2middle = r * 1.1 * Math.cos(middlePercent * Math.PI * 2);
      x2middle = cx + tx2middle;
      y2middle = cy - ty2middle;
      flag = 1;
      if (middlePercent > 0.5) {
        flag = -1;
      }
      annotation = 'M' + xmiddle + ' ' + ymiddle + 'L' + x2middle + ' ' + y2middle + 'H' + (cx + flag * r * 1.1);
      return {
        pie: result,
        annotation: annotation,
        'right-side': flag >= 1,
        'text-position': [cx + flag * r * 1.1, y2middle],
        direction: [(xmiddle - cx) / r, (ymiddle - cy) / r]
      };
    };
    PieChart = (function() {
      function PieChart(element, context) {
        var anchor, current_percent_sum, el, path, paths, piece, self, _i, _len, _ref;
        self = this;
        this.context = context;
        this.strokeWidth = "3px";
        $(element).html('');
        this.paper = new Raphael(element);
        this.events = {};
        if (_.has(context, 'events')) {
          this.events = _(this.events).extend(context.events);
        }
        self = this;
        paths = [];
        current_percent_sum = 0;
        _ref = this.context.pieces;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          piece = _ref[_i];
          path = pie(this.context.x, this.context.y, this.context.r, piece.percent, current_percent_sum);
          el = this.paper.path(path.pie.attr({
            fill: piece.color,
            stroke: 'white',
            'stroke-width': this.strokeWidth
          })).data({
            'piece': piece,
            'path': path
          }).click(function(e) {
            var delta, direction, p, translate, _j, _len2;
            piece = this.data('piece');
            path = this.data('path');
            direction = path.direction;
            delta = 10;
            translate = 't ' + delta * direction[0] + ',' + delta * direction[1];
            for (_j = 0, _len2 = paths.length; _j < _len2; _j++) {
              p = paths[_j];
              p.animate({
                transform: ''
              });
            }
            this.attr({
              fill: piece.color,
              'stroke-width': this.strokeWidth,
              stroke: 'white'
            });
            this.animate({
              transform: translate + "s1.1"
            }, 200, "elastic");
            if (_.has(self.events, 'click')) {
              return self.events.click(piece);
            }
          });
          paths.push(el);
          this.paper.path(path.annotation.attr({
            stroke: piece.color,
            'stroke-width': '1px'
          }));
          anchor = 'end';
          if (path['right-side']) {
            anchor = 'start';
          }
          this.paper.text(path['text-position'][0], path['text-position'][1], piece.percent + '%'.attr({
            'font-size': 15,
            'text-anchor': anchor,
            fill: piece.color,
            'font-family': 'Trebuchet MS'
          }));
          current_percent_sum += piece.percent;
        }
      }
      return PieChart;
    })();
    return {
      PieChart: PieChart
    };
  });
}).call(this);
