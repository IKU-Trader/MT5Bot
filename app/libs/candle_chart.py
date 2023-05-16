# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 22:02:43 2022

@author: IKU-Trader
"""

import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec

from .utils import Utils
from .time_utils import TimeUtils
from .const import const

class colors():    
    @property
    def light_green(self):
        return '#22bbbb'
    @property
    def light_red(self):
        return '#ee9999'
    @property
    def red(self):
        return '#ff4444'
    @property
    def green(self):
        return '#44ffcc'
    
Colors = colors()

def candleData2arrays(ohlc):
    if len(ohlc) == 0:
        return []
    n = len(ohlc[0])
    arrays = []
    for i in range(n):
        array = []
        for data in ohlc:
            array.append(data[i])
        arrays.append(array)
    return arrays

def array2Candle(ohlc_arrays):
    out = []
    n = len(ohlc_arrays)
    size = len(ohlc_arrays[0])
    for i in range(size):
        v = []
        for j in range(n):
            v.append(ohlc_arrays[j][i])
        out.append(v)
    return out        

def awarePyTime2Float(time):
    naive = TimeUtils.awarePytime2naive(time)
    t = mdates.date2num([naive])
    return t[0]


def awarePyTimeList2Float(aware_pytime_list):
    naives = []
    for time in aware_pytime_list:
        naive = TimeUtils.awarePytime2naive(time)
        naives.append(naive)
    return mdates.date2num(naives)

def makeFig(rows, cols, size):
    fig, ax = plt.subplots(rows, cols, figsize=(size[0], size[1]))
    return (fig, ax)

def gridFig(row_rate, size):
    rows = sum(row_rate)
    fig = plt.figure(figsize=size)
    gs = gridspec.GridSpec(rows, 1, hspace=0.6)
    axes = []
    begin = 0
    for rate in row_rate:
        end = begin + rate
        ax = plt.subplot(gs[begin: end, 0])
        axes.append(ax)
        begin = end
    return (fig, axes)

def getMarker(i):
    markers = ['\\alpha', '\\beta', '\gamma', '\sigma','\infty', \
                '\spadesuit', '\heartsuit', '\diamondsuit', '\clubsuit', \
                '\\bigodot', '\\bigotimes', '\\bigoplus', '\imath', '\\bowtie', \
                '\\bigtriangleup', '\\bigtriangledown', '\oslash' \
               '\ast', '\\times', '\circ', '\\bullet', '\star', '+', \
                '\Theta', '\Xi', '\Phi', \
                '\$', '\#', '\%', '\S']
    return "$"+markers[i % len(markers)]+"$"

# -----
    
class CandleGraphic:
    def __init__(self, py_time, ohlc, box_width):
        if len(ohlc) < 4:
            raise Exception('Bad ohlc data')
        self.box_width = box_width
        self.line_width = 1.0
        self.alpha = 0.7
        self.box_body_color_positive = Colors.light_green
        self.box_line_color_positive = Colors.green
        self.box_body_color_negative = Colors.light_red
        self.box_line_color_negative = Colors.red
        t = awarePyTime2Float(py_time)
        op = ohlc[0]
        hi = ohlc[1]
        lo = ohlc[2]
        cl = ohlc[3]
        if cl >= op:
            body_color = self.box_body_color_positive
            line_color = self.box_line_color_positive
            box_low = op
            box_high = cl
            height = cl - op
        else:
            body_color = self.box_body_color_negative
            line_color = self.box_line_color_negative
            box_low = cl
            box_high = op
            height = op - cl
        line_upper = Line2D(xdata=(t, t),
                            ydata=(box_high, hi),
                            color=line_color,
                            linewidth=self.line_width,
                            antialiased=True)
        line_lower = Line2D(xdata=(t, t),
                            ydata=(box_low, lo),
                            color=line_color,
                            linewidth=self.line_width,
                            antialiased=True)
        rect = Rectangle(xy=(t - self.box_width / 2, box_low),
                         width=self.box_width,
                         height=height,
                         facecolor=body_color,
                         edgecolor=body_color)
        rect.set_alpha(self.alpha)
        self.line_upper = line_upper
        self.line_lower = line_lower
        self.rect = rect
    
    def setObject(self, ax):
        ax.add_line(self.line_upper)
        ax.add_line(self.line_lower)
        ax.add_patch(self.rect)

# -----
    
class BoxGraphic:
    def __init__(self, py_time, box_width, value, color):
        self.alpha = 0.7
        t = awarePyTime2Float(py_time)
        if value >= 0:
            box_low = 0.0
            box_height = value
        else:
            box_low = value
            box_height = -value
        rect = Rectangle(xy=(t - box_width / 2, box_low),
                         width=box_width,
                         height=box_height,
                         facecolor=color,
                         edgecolor=color)
        rect.set_alpha(self.alpha)
        self.rect = rect
    
    def setObject(self, ax):
        ax.add_patch(self.rect)

# -----

class CandleChart:
    DATE_FORMAT_TIME = '%H:%M'
    DATE_FORMAT_DAY = '%m-%d'
    DATE_FORMAT_DATE_TIME = '%m-%d %H:%M'
    DATE_FORMAT_DAY_HOUR = '%d/%H'
    
    def __init__(self, fig, ax, title=None, comment=None, write_time_range=False, date_format=None):
        if date_format is None:
            date_format = self.DATE_FORMAT_TIME
        self.fig = fig
        self.ax = ax
        self.title = title
        self.comment = comment
        self.write_time_range = write_time_range
        self.ax.grid(True)
        self.ax.xaxis_date()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        
    def drawCandle(self, Time, Open, High, Low, Close, bar_width=None, tick_minutes=60, xlabel=False):
        self.time = Time
        vmin = min(Low)
        vmax = max(High)
        if self.title is not None:
            self.ax.set_title(self.title)
        n = len(Time)
        t0 = awarePyTime2Float(Time[0])
        t1 = awarePyTime2Float(Time[-1])
        if bar_width is None:
            self.box_width = (t1 - t0 ) / n / 2.0
        else:
            self.box_width = bar_width
        self.graphic_objects = []
        for i in range(n):
            t = Time[i]
            value = [Open[i], High[i], Low[i], Close[i]]
            obj = CandleGraphic(t, value, self.box_width)
            obj.setObject(self.ax)
            self.graphic_objects.append(obj)
        dw = (vmax - vmin) * 0.1
        self.ylimit([vmin - dw, vmax + dw])
        tick = self.ticks(Time[0], Time[-1], tick_minutes)        
        self.ax.set_xticks(tick)
        self.ax.set_xlim(t0, t1)
        self.drawComments()
        if xlabel == False:
            self.ax.tick_params(labelbottom=False, bottom=False)
        
    def drawLine(self, time, value, color='red', linestyle='solid', linewidth=1.0, ylim=None, label='', xlabel=False):
        self.time = time
        tfloat = awarePyTimeList2Float(time)
        self.ax.plot(tfloat, value, color=color, linestyle=linestyle, linewidth=linewidth, label=label)
        if ylim is not None:
            self.ax.set_ylim(ylim[0], ylim[1])
        self.ax.set_xlim(tfloat[0], tfloat[-1])
        self.ax.grid(True)
        self.drawComments()
        if xlabel == False:
            self.ax.tick_params(labelbottom=False, bottom=False)
        
    def drawBand(self, time, status, colors=None, tick_minutes=60, xlabel=False):
        self.time = time
        n = len(time)
        if n < 2:
            return
        if colors is None:
            colors = ['black', 'blue', 'red', 'pink', 'green', 'cyan', 'brown']
        if self.title is not None:
            self.ax.set_title(self.title)
        box_width = awarePyTime2Float(time[1]) - awarePyTime2Float(time[0])
        self.graphic_objects = []
        for i in range(n):
            t = time[i]
            s = status[i]
            if type(colors) == dict:
                try: 
                    c = colors[s]
                except:
                    c = 'white'
            else:
                c = colors[abs(s) % len(colors)]
            obj = BoxGraphic(t, box_width, 1.0, c)
            obj.setObject(self.ax)
            self.graphic_objects.append(obj)  
        self.ax.autoscale_view()
        tick = self.ticks(time[0], time[-1], tick_minutes)        
        self.ax.set_xticks(tick)
        t0 = awarePyTime2Float(time[0])
        t1 = awarePyTime2Float(time[-1])
        self.ax.set_xlim(t0, t1)
        self.drawComments()
        if xlabel == False:
            self.ax.tick_params(labelbottom=False, bottom=False)
        
    def drawComments(self):
        x = self.time[0]
        s = ''
        if self.comment is not None:
            s +=  self.comment
        if self.write_time_range:
            form = '%Y-%m-%d %H:%M'
            s += '  (' + self.time[0].strftime(form)
            s += ' ... ' + self.time[-1].strftime(form) + ')'
        self.drawText(x, self.yPos(0.92), s)

    def yPos(self, rate):
        r = self.getYlimit()
        return (r[1] - r[0]) * rate + r[0]
    
    def ticks(self, t0, t1, dt_minutes):
        tm = int(t0.minute / dt_minutes) * dt_minutes
        time = datetime(t0.year, t0.month, t0.day, t0.hour, tm, tzinfo=t0.tzinfo)
        ticks = []
        while time < t1:
            ticks.append(awarePyTime2Float(time))
            time += timedelta(minutes=dt_minutes)
        return ticks
        

    
    def hline(self, y, color='black', linewidth=1.0):
        xmin, xmax = self.ax.get_xlim()
        self.ax.hlines(y=y, color=color, linewidth=linewidth, xmin=xmin, xmax=xmax)
        
    def vline(self, x, color='black', linewidth=1.0):
        ymin, ymax = self.ax.get_ylim()
        self.ax.vlines(x=x, color=color, linewidth=linewidth, ymin=ymin, ymax=ymax)
    
    def drawBar(self, time, value, colors=['green', 'red'], ylim=None, label=''):
        t0 = awarePyTime2Float(time[0])
        t1 = awarePyTime2Float(time[9])
        w = (t1 - t0) * 0.9 / 10.0
        for t, v in zip(time, value):
            if v is not None:
                if v >= 0:
                    color = colors[0]
                else:
                    color = colors[1]
                obj = BoxGraphic(t, w, v, color)
                obj.setObject(self.ax)
        if ylim is not None:
            self.ax.set_ylim(ylim[0], ylim[1])
        self.ax.grid()
    
    def drawBar2(self, time, value, color='red', ylim=None):
        t = []
        v = []
        for tt, vv in zip(time, value):
            t.append(tt)
            if vv is None:
                v.append(0)
            else:
                v.append(vv)
                
        t0 = awarePyTime2Float(t[0])
        t1 = awarePyTime2Float(t[1])
        self.ax.bar(t, v, color=color, width= (t1 - t0) * 0.9)
        if ylim is not None:
            self.ax.set_ylim(ylim[0], ylim[1])
        self.ax.grid()
    
    def drawMarkers(self, time, ref, offset_rate, signal, value, marker, color, overlay=None, markersize=20, alpha=0.5):
        for t, r, s in zip(time, ref, signal):
            if s == value:
                lim = self.getYlimit()
                offset = offset_rate * (lim[1] - lim[0])
                self.drawMarker(t, r + offset, marker, color, overlay=overlay, markersize=markersize, alpha=alpha)
        
    def drawMarker(self, time, value, marker, color, overlay=None, markersize=20, alpha=0.5):
        t = awarePyTime2Float(time)
        self.ax.plot(t, value, marker=marker, color=color, markersize=markersize, alpha=alpha)
        if overlay is not None:
            marker = '$' + str(overlay) + '$'
            self.ax.plot(t, value, marker=marker, color='white', markersize=markersize*0.5, alpha=1.0)
    
    def drawText(self, time, value, text, size=10):
        t = awarePyTime2Float(time)
        self.ax.text(t, value, text, size=size)
    
    def xlimit(self, x):
        self.ax.set_xlim(x[0], x[1])
        self.ax.grid(True)
        
    def ylimit(self, yrange):
        self.ax.set_ylim(yrange[0], yrange[1])
        
    def getXlimit(self):
        return self.ax.get_xlim()
    
    def getYlimit(self):
        return self.ax.get_ylim()
        
class BandPlot:
    def __init__(self, fig, ax, title=None, comment=None, date_format=None):
        if date_format is None:
            date_format = CandleChart.DATE_FORMAT_TIME
        self.fig = fig
        self.ax = ax
        self.title = title
        self.comment = comment
        self.ax.grid(True)
        self.ax.xaxis_date()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        
    def boxWidth(self, time1, time2):
        t1 = awarePyTime2Float(time1)
        t2 = awarePyTime2Float(time2)
        return t2 - t1
    
    def ticks(self, t0, t1, dt_minutes):
        tm = int(t0.minute / dt_minutes) * dt_minutes
        time = datetime(t0.year, t0.month, t0.day, t0.hour, tm, tzinfo=t0.tzinfo)
        ticks = []
        while time < t1:
            ticks.append(awarePyTime2Float(time))
            time += timedelta(minutes=dt_minutes)
        return ticks
    
    def drawBand(self, time, status, colors=None, tick_minutes=60): 
        self.time = time
        n = len(time)
        if n < 2:
            return
        if colors is None:
            colors = ['black', 'blue', 'red', 'pink', 'green', 'cyan', 'brown']
        if self.title is not None:
            self.ax.set_title(self.title)
        box_width = self.boxWidth(time[0], time[1])
        self.graphic_objects = []
        for i in range(n):
            t = time[i]
            s = status[i]
            if type(colors) == dict:
                try: 
                    c = colors[s]
                except:
                    c = 'white'
            else:
                c = colors[abs(s) % len(colors)]
            obj = BoxGraphic(t, box_width, 1.0, c)
            obj.setObject(self.ax)
            self.graphic_objects.append(obj)  
        self.ax.autoscale_view()
        tick = self.ticks(time[0], time[-1], tick_minutes)        
        self.ax.set_xticks(tick)
        t0 = awarePyTime2Float(time[0])
        t1 = awarePyTime2Float(time[-1])
        self.ax.set_xlim(t0, t1)
        self.drawComments()
        
    def drawLine(self, time, value, color='red', linestyle='solid', linewidth=1.0, timerange=None):
        self.time = time
        if timerange is not None:
            begin = None
            end = None
            for i in range(len(time)):
                t = time[i]
                if begin is None:
                    if t >= timerange[0]:
                        begin = i
                else:
                    if t > timerange[1]:
                        end = i - 1
                        break
            if begin is None:
                begin = 0
            if end is None:
                end = len(time) - 1
            time2 = time[begin: end + 1]
            value2 = value[begin: end + 1]
        else:
            time2 = time
            value2 = value
        vmin = np.nanmin(value2)
        vmax = np.nanmax(value2)
        dw = (vmax - vmin) * 0.2
        vmax += dw
        vmin -= dw
        self.ylimit((vmin, vmax))
        self.ax.plot(time2, value2, color=color, linestyle=linestyle, linewidth=linewidth)
        self.ax.grid(True)
        self.fig.show()

    def yPos(self, rate):
        r = self.getYlimit()
        return (r[1] - r[0]) * rate + r[0]
        
    def drawComments(self):
        x = self.time[0]
        y = 0.95
        if self.comment is not None:
            self.drawText(x, self.yPos(y), self.comment)
            
    def drawText(self, time, value, text, size=10):
        t = awarePyTime2Float(time)
        self.ax.text(t, value, text, size=size)
            
    def xlimit(self, trange):
        self.ax.set_xlim(trange[0], trange[1])
        
    def ylimit(self, yrange):
        self.ax.set_ylim(yrange[0], yrange[1])
          