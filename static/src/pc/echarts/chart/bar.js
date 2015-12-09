define("echarts/chart/bar", ["require", "./base", "zrender/shape/Rectangle", "../component/axis", "../component/grid", "../component/dataZoom", "../config", "../util/ecData", "zrender/tool/util", "zrender/tool/color", "../chart"], function(e) {
	function t(e, t, n, a, o) {
		i.call(this, e, t, n, a, o), this.refresh(a)
	}
	var i = e("./base"),
		n = e("zrender/shape/Rectangle");
	e("../component/axis"), e("../component/grid"), e("../component/dataZoom");
	var a = e("../config");
	a.bar = {
		zlevel: 0,
		z: 2,
		clickable: !0,
		legendHoverLink: !0,
		xAxisIndex: 0,
		yAxisIndex: 0,
		barMinHeight: 0,
		barGap: "30%",
		barCategoryGap: "20%",
		itemStyle: {
			normal: {
				barBorderColor: "#fff",
				barBorderRadius: 0,
				barBorderWidth: 0,
				label: {
					show: !1
				}
			},
			emphasis: {
				barBorderColor: "#fff",
				barBorderRadius: 0,
				barBorderWidth: 0,
				label: {
					show: !1
				}
			}
		}
	};
	var o = e("../util/ecData"),
		r = e("zrender/tool/util"),
		s = e("zrender/tool/color");
	return t.prototype = {
		type: a.CHART_TYPE_BAR,
		_buildShape: function() {
			this._buildPosition()
		},
		_buildNormal: function(e, t, i, o, r) {
			for (var s, l, h, d, c, m, p, u, V, U, g, f, y = this.series, b = i[0][0], _ = y[b], x = "horizontal" == r, k = this.component.xAxis, v = this.component.yAxis, L = x ? k.getAxis(_.xAxisIndex) : v.getAxis(_.yAxisIndex), w = this._mapSize(L, i), W = w.gap, X = w.barGap, I = w.barWidthMap, S = w.barMaxWidthMap, K = w.barWidth, C = w.barMinHeightMap, T = w.interval, E = this.deepQuery([this.ecTheme, a], "island.r"), z = 0, A = t; A > z && null != L.getNameByIndex(z); z++) {
				x ? d = L.getCoordByIndex(z) - W / 2 : c = L.getCoordByIndex(z) + W / 2;
				for (var M = 0, F = i.length; F > M; M++) {
					var J = y[i[M][0]].yAxisIndex || 0,
						P = y[i[M][0]].xAxisIndex || 0;
					s = x ? v.getAxis(J) : k.getAxis(P), p = m = V = u = s.getCoord(0);
					for (var O = 0, D = i[M].length; D > O; O++) b = i[M][O], _ = y[b], g = _.data[z], f = this.getDataFromOption(g, "-"), o[b] = o[b] || {
						min: Number.POSITIVE_INFINITY,
						max: Number.NEGATIVE_INFINITY,
						sum: 0,
						counter: 0,
						average: 0
					}, h = Math.min(S[b] || Number.MAX_VALUE, I[b] || K), "-" !== f && (f > 0 ? (l = O > 0 ? s.getCoordSize(f) : x ? p - s.getCoord(f) : s.getCoord(f) - p, 1 === D && C[b] > l && (l = C[b]), x ? (m -= l, c = m) : (d = m, m += l)) : 0 > f ? (l = O > 0 ? s.getCoordSize(f) : x ? s.getCoord(f) - V : V - s.getCoord(f), 1 === D && C[b] > l && (l = C[b]), x ? (c = u, u += l) : (u -= l, d = u)) : (l = 0, x ? (m -= l, c = m) : (d = m, m += l)), o[b][z] = x ? d + h / 2 : c - h / 2, o[b].min > f && (o[b].min = f, x ? (o[b].minY = c, o[b].minX = o[b][z]) : (o[b].minX = d + l, o[b].minY = o[b][z])), o[b].max < f && (o[b].max = f, x ? (o[b].maxY = c, o[b].maxX = o[b][z]) : (o[b].maxX = d + l, o[b].maxY = o[b][z])), o[b].sum += f, o[b].counter++, z % T === 0 && (U = this._getBarItem(b, z, L.getNameByIndex(z), d, c - (x ? 0 : h), x ? h : l, x ? l : h, x ? "vertical" : "horizontal"), this.shapeList.push(new n(U))));
					for (var O = 0, D = i[M].length; D > O; O++) b = i[M][O], _ = y[b], g = _.data[z], f = this.getDataFromOption(g, "-"), h = Math.min(S[b] || Number.MAX_VALUE, I[b] || K), "-" == f && this.deepQuery([g, _, this.option], "calculable") && (x ? (m -= E, c = m) : (d = m, m += E), U = this._getBarItem(b, z, L.getNameByIndex(z), d, c - (x ? 0 : h), x ? h : E, x ? E : h, x ? "vertical" : "horizontal"), U.hoverable = !1, U.draggable = !1, U.style.lineWidth = 1, U.style.brushType = "stroke", U.style.strokeColor = _.calculableHolderColor || this.ecTheme.calculableHolderColor || a.calculableHolderColor, this.shapeList.push(new n(U)));
					x ? d += h + X : c -= h + X
				}
			}
			this._calculMarkMapXY(o, i, x ? "y" : "x")
		},
		_buildHorizontal: function(e, t, i, n) {
			return this._buildNormal(e, t, i, n, "horizontal")
		},
		_buildVertical: function(e, t, i, n) {
			return this._buildNormal(e, t, i, n, "vertical")
		},
		_buildOther: function(e, t, i, a) {
			for (var o = this.series, r = 0, s = i.length; s > r; r++) for (var l = 0, h = i[r].length; h > l; l++) {
				var d = i[r][l],
					c = o[d],
					m = c.xAxisIndex || 0,
					p = this.component.xAxis.getAxis(m),
					u = p.getCoord(0),
					V = c.yAxisIndex || 0,
					U = this.component.yAxis.getAxis(V),
					g = U.getCoord(0);
				a[d] = a[d] || {
					min0: Number.POSITIVE_INFINITY,
					min1: Number.POSITIVE_INFINITY,
					max0: Number.NEGATIVE_INFINITY,
					max1: Number.NEGATIVE_INFINITY,
					sum0: 0,
					sum1: 0,
					counter0: 0,
					counter1: 0,
					average0: 0,
					average1: 0
				};
				for (var f = 0, y = c.data.length; y > f; f++) {
					var b = c.data[f],
						_ = this.getDataFromOption(b, "-");
					if (_ instanceof Array) {
						var x, k, v = p.getCoord(_[0]),
							L = U.getCoord(_[1]),
							w = [b, c],
							W = this.deepQuery(w, "barWidth") || 10,
							X = this.deepQuery(w, "barHeight");
						null != X ? (x = "horizontal", _[0] > 0 ? (W = v - u, v -= W) : W = _[0] < 0 ? u - v : 0, k = this._getBarItem(d, f, _[0], v, L - X / 2, W, X, x)) : (x = "vertical", _[1] > 0 ? X = g - L : _[1] < 0 ? (X = L - g, L -= X) : X = 0, k = this._getBarItem(d, f, _[0], v - W / 2, L, W, X, x)), this.shapeList.push(new n(k)), v = p.getCoord(_[0]), L = U.getCoord(_[1]), a[d].min0 > _[0] && (a[d].min0 = _[0], a[d].minY0 = L, a[d].minX0 = v), a[d].max0 < _[0] && (a[d].max0 = _[0], a[d].maxY0 = L, a[d].maxX0 = v), a[d].sum0 += _[0], a[d].counter0++, a[d].min1 > _[1] && (a[d].min1 = _[1], a[d].minY1 = L, a[d].minX1 = v), a[d].max1 < _[1] && (a[d].max1 = _[1], a[d].maxY1 = L, a[d].maxX1 = v), a[d].sum1 += _[1], a[d].counter1++
					}
				}
			}
			this._calculMarkMapXY(a, i, "xy")
		},
		_mapSize: function(e, t, i) {
			var n, a, o = this._findSpecialBarSzie(t, i),
				r = o.barWidthMap,
				s = o.barMaxWidthMap,
				l = o.barMinHeightMap,
				h = o.sBarWidthCounter,
				d = o.sBarWidthTotal,
				c = o.barGap,
				m = o.barCategoryGap,
				p = 1;
			if (t.length != h) {
				if (i) n = e.getGap(), c = 0, a = +(n / t.length).toFixed(2), 0 >= a && (p = Math.floor(t.length / n), a = 1);
				else if (n = "string" == typeof m && m.match(/%$/) ? (e.getGap() * (100 - parseFloat(m)) / 100).toFixed(2) - 0 : e.getGap() - m, "string" == typeof c && c.match(/%$/) ? (c = parseFloat(c) / 100, a = +((n - d) / ((t.length - 1) * c + t.length - h)).toFixed(2), c = a * c) : (c = parseFloat(c), a = +((n - d - c * (t.length - 1)) / (t.length - h)).toFixed(2)), 0 >= a) return this._mapSize(e, t, !0)
			} else if (n = h > 1 ? "string" == typeof m && m.match(/%$/) ? +(e.getGap() * (100 - parseFloat(m)) / 100).toFixed(2) : e.getGap() - m : d, a = 0, c = h > 1 ? +((n - d) / (h - 1)).toFixed(2) : 0, 0 > c) return this._mapSize(e, t, !0);
			return this._recheckBarMaxWidth(t, r, s, l, n, a, c, p)
		},
		_findSpecialBarSzie: function(e, t) {
			for (var i, n, a, o, r = this.series, s = {}, l = {}, h = {}, d = 0, c = 0, m = 0, p = e.length; p > m; m++) for (var u = {
				barWidth: !1,
				barMaxWidth: !1
			}, V = 0, U = e[m].length; U > V; V++) {
				var g = e[m][V],
					f = r[g];
				if (!t) {
					if (u.barWidth) s[g] = i;
					else if (i = this.query(f, "barWidth"), null != i) {
						s[g] = i, c += i, d++, u.barWidth = !0;
						for (var y = 0, b = V; b > y; y++) {
							var _ = e[m][y];
							s[_] = i
						}
					}
					if (u.barMaxWidth) l[g] = n;
					else if (n = this.query(f, "barMaxWidth"), null != n) {
						l[g] = n, u.barMaxWidth = !0;
						for (var y = 0, b = V; b > y; y++) {
							var _ = e[m][y];
							l[_] = n
						}
					}
				}
				h[g] = this.query(f, "barMinHeight"), a = null != a ? a : this.query(f, "barGap"), o = null != o ? o : this.query(f, "barCategoryGap")
			}
			return {
				barWidthMap: s,
				barMaxWidthMap: l,
				barMinHeightMap: h,
				sBarWidth: i,
				sBarMaxWidth: n,
				sBarWidthCounter: d,
				sBarWidthTotal: c,
				barGap: a,
				barCategoryGap: o
			}
		},
		_recheckBarMaxWidth: function(e, t, i, n, a, o, r, s) {
			for (var l = 0, h = e.length; h > l; l++) {
				var d = e[l][0];
				i[d] && i[d] < o && (a -= o - i[d])
			}
			return {
				barWidthMap: t,
				barMaxWidthMap: i,
				barMinHeightMap: n,
				gap: a,
				barWidth: o,
				barGap: r,
				interval: s
			}
		},
		_getBarItem: function(e, t, i, n, a, r, l, h) {
			var d, c = this.series,
				m = c[e],
				p = m.data[t],
				u = this._sIndex2ColorMap[e],
				V = [p, m],
				U = this.deepMerge(V, "itemStyle.normal"),
				g = this.deepMerge(V, "itemStyle.emphasis"),
				f = U.barBorderWidth;
			d = {
				zlevel: m.zlevel,
				z: m.z,
				clickable: this.deepQuery(V, "clickable"),
				style: {
					x: n,
					y: a,
					width: r,
					height: l,
					brushType: "both",
					color: this.getItemStyleColor(this.deepQuery(V, "itemStyle.normal.color") || u, e, t, p),
					radius: U.barBorderRadius,
					lineWidth: f,
					strokeColor: U.barBorderColor
				},
				highlightStyle: {
					color: this.getItemStyleColor(this.deepQuery(V, "itemStyle.emphasis.color"), e, t, p),
					radius: g.barBorderRadius,
					lineWidth: g.barBorderWidth,
					strokeColor: g.barBorderColor
				},
				_orient: h
			};
			var y = d.style;
			d.highlightStyle.color = d.highlightStyle.color || ("string" == typeof y.color ? s.lift(y.color, -.3) : y.color), y.x = Math.floor(y.x), y.y = Math.floor(y.y), y.height = Math.ceil(y.height), y.width = Math.ceil(y.width), f > 0 && y.height > f && y.width > f ? (y.y += f / 2, y.height -= f, y.x += f / 2, y.width -= f) : y.brushType = "fill", d.highlightStyle.textColor = d.highlightStyle.color, d = this.addLabel(d, m, p, i, h);
			for (var b = [y, d.highlightStyle], _ = 0, x = b.length; x > _; _++) {
				var k = b[_].textPosition;
				if ("insideLeft" === k || "insideRight" === k || "insideTop" === k || "insideBottom" === k) {
					var v = 5;
					switch (k) {
					case "insideLeft":
						b[_].textX = y.x + v, b[_].textY = y.y + y.height / 2, b[_].textAlign = "left", b[_].textBaseline = "middle";
						break;
					case "insideRight":
						b[_].textX = y.x + y.width - v, b[_].textY = y.y + y.height / 2, b[_].textAlign = "right", b[_].textBaseline = "middle";
						break;
					case "insideTop":
						b[_].textX = y.x + y.width / 2, b[_].textY = y.y + v / 2, b[_].textAlign = "center", b[_].textBaseline = "top";
						break;
					case "insideBottom":
						b[_].textX = y.x + y.width / 2, b[_].textY = y.y + y.height - v / 2, b[_].textAlign = "center", b[_].textBaseline = "bottom"
					}
					b[_].textPosition = "specific", b[_].textColor = b[_].textColor || "#fff"
				}
			}
			return this.deepQuery([p, m, this.option], "calculable") && (this.setCalculable(d), d.draggable = !0), o.pack(d, c[e], e, c[e].data[t], t, i), d
		},
		getMarkCoord: function(e, t) {
			var i, n, a = this.series[e],
				o = this.xMarkMap[e],
				r = this.component.xAxis.getAxis(a.xAxisIndex),
				s = this.component.yAxis.getAxis(a.yAxisIndex);
			if (!t.type || "max" !== t.type && "min" !== t.type && "average" !== t.type) if (o.isHorizontal) {
				i = "string" == typeof t.xAxis && r.getIndexByName ? r.getIndexByName(t.xAxis) : t.xAxis || 0;
				var l = o[i];
				l = null != l ? l : "string" != typeof t.xAxis && r.getCoordByIndex ? r.getCoordByIndex(t.xAxis || 0) : r.getCoord(t.xAxis || 0), n = [l, s.getCoord(t.yAxis || 0)]
			} else {
				i = "string" == typeof t.yAxis && s.getIndexByName ? s.getIndexByName(t.yAxis) : t.yAxis || 0;
				var h = o[i];
				h = null != h ? h : "string" != typeof t.yAxis && s.getCoordByIndex ? s.getCoordByIndex(t.yAxis || 0) : s.getCoord(t.yAxis || 0), n = [r.getCoord(t.xAxis || 0), h]
			} else {
				var d = null != t.valueIndex ? t.valueIndex : null != o.maxX0 ? "1" : "";
				n = [o[t.type + "X" + d], o[t.type + "Y" + d], o[t.type + "Line" + d], o[t.type + d]]
			}
			return n
		},
		refresh: function(e) {
			e && (this.option = e, this.series = e.series), this.backupShapeList(), this._buildShape()
		},
		addDataAnimation: function(e, t) {
			function i() {
				V--, 0 === V && t && t()
			}
			for (var n = this.series, a = {}, r = 0, s = e.length; s > r; r++) a[e[r][0]] = e[r];
			for (var l, h, d, c, m, p, u, V = 0, r = this.shapeList.length - 1; r >= 0; r--) if (p = o.get(this.shapeList[r], "seriesIndex"), a[p] && !a[p][3] && "rectangle" === this.shapeList[r].type) {
				if (u = o.get(this.shapeList[r], "dataIndex"), m = n[p], a[p][2] && u === m.data.length - 1) {
					this.zr.delShape(this.shapeList[r].id);
					continue
				}
				if (!a[p][2] && 0 === u) {
					this.zr.delShape(this.shapeList[r].id);
					continue
				}
				"horizontal" === this.shapeList[r]._orient ? (c = this.component.yAxis.getAxis(m.yAxisIndex || 0).getGap(), d = a[p][2] ? -c : c, l = 0) : (h = this.component.xAxis.getAxis(m.xAxisIndex || 0).getGap(), l = a[p][2] ? h : -h, d = 0), this.shapeList[r].position = [0, 0], V++, this.zr.animate(this.shapeList[r].id, "").when(this.query(this.option, "animationDurationUpdate"), {
					position: [l, d]
				}).done(i).start()
			}
			V || t && t()
		}
	}, r.inherits(t, i), e("../chart").define("bar", t), t
});