# -*- coding:utf-8 -*-
#! python3

# FaceCat-Python-Wasm(OpenSource)
#Shanghai JuanJuanMao Information Technology Co., Ltd 

import win32gui
import win32api
from win32con import *
import math
import time
from operator import attrgetter

#坐标结构
class FCPoint(object):
	def __init__(self, x, y):
		self.x = x #横坐标
		self.y = y #纵坐标
	
#大小结构
class FCSize(object):
	def __init__(self, cx, cy):
		self.cx = cx #长
		self.cy = cy #宽

#矩形结构
class FCRect(object):
	def __init__(self, left, top, right, bottom):
		self.left = left #左侧
		self.top = top #上侧
		self.right = right #右侧
		self.bottom = bottom #底部

#边距信息
class FCPadding(object):
	def __init__(self, left, top, right, bottom):
		self.left = left #左侧
		self.top = top #上侧
		self.right = right #右侧
		self.bottom = bottom #底部

#转换颜色
#strColor:颜色字符
def toColor(strColor):
	strColor = strColor.replace("(", "").replace(")","")
	if(strColor.find("rgba") == 0):
		strColor = strColor.replace("rgba", "")
		strs = strColor.split(",")
		if(len(strs) >= 4):
			return win32api.RGB(int(strs[0]),int(strs[1]),int(strs[2]))
	elif(strColor.find("rgb") == 0):
		strColor = strColor.replace("rgb", "")
		strs = strColor.split(",")
		if(len(strs) >= 3):
			return win32api.RGB(int(strs[0]),int(strs[1]),int(strs[2]))
	elif(strColor != "none" and len(strColor) > 0):
		return int(float(strColor))
	return 0

class FCPaint(object):
	def __init__(self):
		self.m_moveTo = FALSE
		self.m_offsetX = 0 #横向偏移
		self.m_offsetY = 0 #纵向偏移
		self.m_defaultUIStyle = "dark" #默认样式
		self.m_scaleFactorX = 1 #横向缩放比例
		self.m_scaleFactorY = 1 #纵向缩放比例
		self.m_hdc = None #绘图对象
		self.m_drawHDC = None #双倍缓冲的hdc
		self.m_size = FCSize(0,0) #布局大小
		self.m_isPath = FALSE #是否路径
		self.m_views = [] #子视图
		self.m_hWnd = None #句柄
		self.m_memBM = None #绘图对象
		self.m_innerHDC = None #内部HDC
		self.m_innerBM = None #内部BM
		self.m_clipRect = None #裁剪区域
		self.m_hFont = None #字体
		self.m_hOldFont = None #旧的字体
		self.m_textSize = 19 #当前的字体大小
		self.m_systemFont = "Segoe UI" #系统字体
	#开始绘图 
	#rect:区域
	def beginPaint(self, rect):
		self.m_drawHDC = win32gui.CreateCompatibleDC(self.m_hdc)
		win32gui.SetBkMode(self.m_drawHDC, TRANSPARENT)
		win32gui.SetGraphicsMode(self.m_drawHDC, GM_ADVANCED)
		self.m_memBM = win32gui.CreateCompatibleBitmap(self.m_hdc, int(rect.right - rect.left),  int(rect.bottom - rect.top))
		win32gui.SelectObject(self.m_drawHDC, self.m_memBM)
		self.m_moveTo = FALSE;
		self.m_innerHDC = self.m_drawHDC
		self.m_innerBM = self.m_memBM
		self.m_offsetX = 0
		self.m_offsetY = 0
	#绘制线
	#color:颜色 
	#width:宽度 
	#style:样式 
	#x1:横坐标1 
	#y1:纵坐标1 
	#x2:横坐标2 
	#y2:纵坐标2
	def drawLine(self, color, width, style, x1, y1, x2, y2):
		wd = min(self.m_scaleFactorX, self.m_scaleFactorY) * width
		if(wd < 1):
			wd = 1
		hPen = win32gui.CreatePen(PS_SOLID, int(wd), toColor(color)) 
		hOldPen = win32gui.SelectObject(self.m_innerHDC, hPen)
		win32gui.MoveToEx(self.m_innerHDC, int((x1 + self.m_offsetX) * self.m_scaleFactorX), int((y1 + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.LineTo(self.m_innerHDC, int((x2 + self.m_offsetX) * self.m_scaleFactorX), int((y2 + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.SelectObject(self.m_innerHDC, hOldPen)
		win32gui.DeleteObject(hPen)
	#绘制连续线
	#color:颜色 
	#width:宽度 
	#style:样式 
	#x1:横坐标1 
	#y1:纵坐标1 
	#x2:横坐标2 
	#y2:纵坐标2
	def drawPolyline(self, color, width, style, apt):
		if(len(apt) > 1):
			wd = min(self.m_scaleFactorX, self.m_scaleFactorY) * width
			if(wd < 1):
				wd = 1
			hPen = win32gui.CreatePen(PS_SOLID, int(wd), toColor(color)) 
			hOldPen = win32gui.SelectObject(self.m_innerHDC, hPen)
			for i in range(0,len(apt)):
				x,y = apt[i]
				x = x + self.m_offsetX
				y = y + self.m_offsetY
				if (self.m_scaleFactorX != 1 or self.m_scaleFactorY != 1):
					x = m_scaleFactorX * x;
					y = m_scaleFactorY * y;
				apt[i] = (int(x), int(y))
			win32gui.Polyline(self.m_innerHDC, apt)
			win32gui.SelectObject(self.m_innerHDC, hOldPen)
			win32gui.DeleteObject(hPen)
	#绘制多边形
	#color:颜色 
	#width:宽度 
	#style:样式 
	#x1:横坐标1 
	#y1:纵坐标1 
	#x2:横坐标2 
	#y2:纵坐标2
	def drawPolygon(self, color, width, style, apt):
		if(len(apt) > 1):
			wd = min(self.m_scaleFactorX, self.m_scaleFactorY) * width
			if(wd < 1):
				wd = 1
			hPen = win32gui.CreatePen(PS_SOLID, int(wd), toColor(color)) 
			hOldPen = win32gui.SelectObject(self.m_innerHDC, hPen)
			for i in range(0,len(apt)):
				x,y = apt[i]
				x = x + self.m_offsetX
				y = y + self.m_offsetY
				if (self.m_scaleFactorX != 1 or self.m_scaleFactorY != 1):
					x = m_scaleFactorX * x;
					y = m_scaleFactorY * y;
				if(i == 0):
					win32gui.MoveToEx(self.m_innerHDC, int(x), int(y))
				else:
					win32gui.LineTo(self.m_innerHDC, int(x), int(y))
				if(i == len(apt) - 1):
					fx,fy = apt[0]
					win32gui.LineTo(self.m_innerHDC, int(fx), int(fy))
			win32gui.SelectObject(self.m_innerHDC, hOldPen)
			win32gui.DeleteObject(hPen)
	#绘制矩形 
	#color:颜色 
	#width:宽度 
	#style:样式 
	#left:左侧坐标 
	#top:上方坐标 
	#right:右侧坐标 
	#bottom:下方坐标
	def drawRect(self, color, width, style, left, top, right, bottom):
		wd = min(self.m_scaleFactorX, self.m_scaleFactorY) * width
		if(wd < 1):
			wd = 1
		hPen = win32gui.CreatePen(PS_SOLID, int(wd), toColor(color)) 
		hOldPen = win32gui.SelectObject(self.m_innerHDC, hPen)
		win32gui.MoveToEx(self.m_innerHDC, int((left + self.m_offsetX) * self.m_scaleFactorX), int((top + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.LineTo(self.m_innerHDC, int((right + self.m_offsetX) * self.m_scaleFactorX), int((top + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.LineTo(self.m_innerHDC, int((right + self.m_offsetX) * self.m_scaleFactorX), int((bottom + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.LineTo(self.m_innerHDC, int((left + self.m_offsetX) * self.m_scaleFactorX), int((bottom + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.LineTo(self.m_innerHDC, int((left + self.m_offsetX) * self.m_scaleFactorX), int((top + self.m_offsetY) * self.m_scaleFactorY))
		#win32gui.Rect(self.m_drawHDC, int((left + self.m_offsetX) * self.m_scaleFactorX), int((top + self.m_offsetY) * self.m_scaleFactorY), int((right + self.m_offsetX) * self.m_scaleFactorX), int((bottom + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.SelectObject(self.m_innerHDC, hOldPen)
		win32gui.DeleteObject(hPen)
	#绘制椭圆 
	#color:颜色 
	#width:宽度 
	#style:样式 
	#left:左侧坐标 
	#top:上方坐标 
	#right:右侧坐标 
	#bottom:下方坐标
	def drawEllipse(self, color, width, style, left, top, right, bottom):
		wd = min(self.m_scaleFactorX, self.m_scaleFactorY) * width
		if(wd < 1):
			wd = 1
		hPen = win32gui.CreatePen(PS_SOLID, int(wd), toColor(color)) 
		hOldPen = win32gui.SelectObject(self.m_innerHDC, hPen)
		xLeft = int((left + self.m_offsetX) * self.m_scaleFactorX)
		yTop = int((top + self.m_offsetY) * self.m_scaleFactorY)
		xRight = int((right + self.m_offsetX) * self.m_scaleFactorX)
		yBottom = int((bottom + self.m_offsetY) * self.m_scaleFactorY)
		xStart = xLeft
		yStart = int(yTop + (yBottom - yTop) / 2)
		xEnd = xLeft
		yEnd = yStart
		if(xLeft == xRight or yTop == yBottom):
			win32gui.MoveToEx(self.m_innerHDC, int((xLeft + self.m_offsetX) * self.m_scaleFactorX), int((yTop + self.m_offsetY) * self.m_scaleFactorY))
			win32gui.LineTo(self.m_innerHDC, int((xRight + self.m_offsetX) * self.m_scaleFactorX), int((yBottom + self.m_offsetY) * self.m_scaleFactorY))
		else:
			win32gui.Arc(self.m_innerHDC, xLeft, yTop, xRight, yBottom, xStart, yStart, xEnd, yEnd)
		win32gui.SelectObject(self.m_innerHDC, hOldPen)
		win32gui.DeleteObject(hPen)
	#绘制文字大小 
	#text:文字 
	#color:颜色 
	#font:字体 
	#x:横坐标 
	#y:纵坐标
	def drawText(self, text, color, font, x, y):
		fontSize = float(font.split(" ")[0].replace("px", "")) + 7
		if(fontSize != self.m_textSize):
			if(self.m_hOldFont != None):
				win32gui.SelectObject(self.m_innerHDC, self.m_hOldFont);
				self.m_hOldFont = None
			lf = win32gui.LOGFONT()
			lf.lfFaceName = self.m_systemFont
			self.m_textSize = fontSize
			lf.lfHeight = self.m_textSize
			#lf.lfWeight = 700
			self.m_hFont = win32gui.CreateFontIndirect(lf)
			self.m_hOldFont = win32gui.SelectObject(self.m_innerHDC, self.m_hFont);
			win32gui.SelectObject(self.m_innerHDC, self.m_hFont)
		win32gui.SetTextColor(self.m_innerHDC, toColor(color))
		textSize = self.textSize(text,font)
		pyRect = (int((x + self.m_offsetX) * self.m_scaleFactorX), int((y + self.m_offsetY) * self.m_scaleFactorY), int((x + textSize.cx + self.m_offsetX) * self.m_scaleFactorX), int((y + textSize.cy + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.DrawText(self.m_innerHDC, text, len(text), pyRect, DT_NOPREFIX|DT_WORD_ELLIPSIS|0)
	#结束绘图
	def endPaint(self):
		if(self.m_clipRect != None):
			win32gui.BitBlt(self.m_hdc, int(self.m_clipRect.left), int(self.m_clipRect.top), int(self.m_clipRect.right - self.m_clipRect.left), int(self.m_clipRect.bottom - self.m_clipRect.top), self.m_drawHDC, int(self.m_clipRect.left), int(self.m_clipRect.top), SRCCOPY)
		else:
			win32gui.BitBlt(self.m_hdc, 0, 0, self.m_size.cx, self.m_size.cy, self.m_drawHDC, 0, 0, SRCCOPY)
		if(self.m_drawHDC != None):
			win32gui.DeleteDC(self.m_drawHDC)
			self.m_drawHDC = None
		if(self.m_memBM != None):
			win32gui.DeleteObject(self.m_memBM)
			self.m_memBM = None
	#填充矩形 
	#color:颜色
	#left:左侧坐标 
	#top:上方坐标 
	#right:右侧坐标 
	#bottom:下方坐标
	def fillRect(self, color, left, top, right, bottom):
		brush = win32gui.CreateSolidBrush(toColor(color))
		win32gui.SelectObject(self.m_innerHDC, brush)
		pyRect = (int((left + self.m_offsetX) * self.m_scaleFactorX), int((top + self.m_offsetY) * self.m_scaleFactorY), int((right + self.m_offsetX + 1) * self.m_scaleFactorX), int((bottom + self.m_offsetY + 1) * self.m_scaleFactorY))
		win32gui.FillRect(self.m_innerHDC, pyRect, brush)
		win32gui.DeleteObject(brush)
	#填充多边形 
	#color:颜色
	#left:左侧坐标 
	#top:上方坐标 
	#right:右侧坐标 
	#bottom:下方坐标
	def fillPolygon(self, color, apt):
		if(len(apt) > 1):
			brush = win32gui.CreateSolidBrush(toColor(color))
			win32gui.SelectObject(self.m_innerHDC, brush)
			for i in range(0,len(apt)):
				x,y = apt[i]
				x = x + self.m_offsetX
				y = y + self.m_offsetY
				if (self.m_scaleFactorX != 1 or self.m_scaleFactorY != 1):
					x = m_scaleFactorX * x;
					y = m_scaleFactorY * y;
				apt[i] = (int(x), int(y))
			win32gui.Polygon(self.m_innerHDC, apt)
			win32gui.DeleteObject(brush)
	#填充椭圆 
	#color:颜色
	#left:左侧坐标 
	#top:上方坐标 
	#right:右侧坐标 
	#bottom:下方坐标
	def fillEllipse(self, color, left, top, right, bottom):
		brush = win32gui.CreateSolidBrush(toColor(color))
		win32gui.SelectObject(self.m_innerHDC, brush)
		pyRect = (int((left + self.m_offsetX) * self.m_scaleFactorX), int((top + self.m_offsetY) * self.m_scaleFactorY), int((right + self.m_offsetX) * self.m_scaleFactorX), int((bottom + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.Ellipse(self.m_innerHDC, int((left + self.m_offsetX) * self.m_scaleFactorX), int((top + self.m_offsetY) * self.m_scaleFactorY), int((right + self.m_offsetX) * self.m_scaleFactorX), int((bottom + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.DeleteObject(brush)
	#填充饼图
	#color:颜色
	#left:左侧坐标 
	#top:上方坐标 
	#right:右侧坐标 
	#bottom:下方坐标
	#startAngle:开始角度
	#sweepAngle:持续角度
	def fillPie(self, color, left, top, right, bottom, startAngle, sweepAngle):
		brush = win32gui.CreateSolidBrush(toColor(color))
		win32gui.SelectObject(self.m_innerHDC, brush)
		oX = (left + (right - left) / 2)
		oY = (top + (bottom - top) / 2)
		rX = (right - left) / 2
		rY = (bottom - top) / 2
		x1 = oX + (rX) * math.cos(startAngle * 3.1415926 / 180)
		y1 = oY + (rY) * math.sin(startAngle * 3.1415926 / 180)
		x2 = oX + (rX) * math.cos((startAngle + sweepAngle) * 3.1415926 / 180)
		y2 = oY + (rY) * math.sin((startAngle + sweepAngle) * 3.1415926 / 180)
		win32gui.Pie(self.m_innerHDC, int((left + self.m_offsetX) * self.m_scaleFactorX), int((top + self.m_offsetY) * self.m_scaleFactorY), int((right + self.m_offsetX) * self.m_scaleFactorX), int((bottom + self.m_offsetY) * self.m_scaleFactorY), int((x1 + self.m_offsetX) * self.m_scaleFactorX), int((y1 + self.m_offsetY) * self.m_scaleFactorY), int((x2 + self.m_offsetX) * self.m_scaleFactorX), int((y2 + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.DeleteObject(brush)
	#设置偏移量
	#offsetX:横向偏移 
	#offsetY:纵向偏移
	def setOffset(self, offsetX, offsetY):
		self.m_offsetX = offsetX
		self.m_offsetY = offsetY
	#获取字体大小 
	#text:文字 
	#font:字体
	def textSize(self, text, font):
		fontSize = float(font.split(" ")[0].replace("px", "")) + 7
		if(fontSize != self.m_textSize):
			if(self.m_hOldFont != None):
				win32gui.SelectObject(self.m_innerHDC, self.m_hOldFont);
				self.m_hOldFont = None
			lf = win32gui.LOGFONT()
			lf.lfFaceName = self.m_systemFont
			self.m_textSize = fontSize
			lf.lfHeight = self.m_textSize
			#lf.lfWeight = 700
			self.m_hFont = win32gui.CreateFontIndirect(lf)
			self.m_hOldFont = win32gui.SelectObject(self.m_innerHDC, self.m_hFont);
			win32gui.SelectObject(self.m_innerHDC, self.m_hFont)
		cx, cy = win32gui.GetTextExtentPoint32(self.m_innerHDC, text)
		return FCSize(cx,cy)
	#绘制矩形 
	#text文字 
	#color:颜色 
	#font:字体 
	#left:左侧坐标 
	#top:上方坐标 
	#right:右侧坐标 
	#bottom:方坐标
	def drawTextAutoEllipsis(self, text, color, font, left, top, right, bottom):
		fontSize = float(font.split(" ")[0].replace("px", "")) + 7
		if(fontSize != self.m_textSize):
			if(self.m_hOldFont != None):
				win32gui.SelectObject(self.m_innerHDC, self.m_hOldFont);
				self.m_hOldFont = None
			lf = win32gui.LOGFONT()
			lf.lfFaceName = self.m_systemFont
			self.m_textSize = fontSize
			lf.lfHeight = self.m_textSize
			#lf.lfWeight = 700
			self.m_hFont = win32gui.CreateFontIndirect(lf)
			self.m_hOldFont = win32gui.SelectObject(self.m_innerHDC, self.m_hFont);
			win32gui.SelectObject(self.m_innerHDC, self.m_hFont)
		win32gui.SetTextColor(self.m_innerHDC, toColor(color))
		textSize = self.textSize(text,font)
		pyRect = (int((left + self.m_offsetX) * self.m_scaleFactorX), int((top + self.m_offsetY) * self.m_scaleFactorY), int((right + textSize.cx + self.m_offsetX) * self.m_scaleFactorX), int((bottom + textSize.cy + self.m_offsetY) * self.m_scaleFactorY))
		win32gui.DrawText(self.m_innerHDC, text, len(text), pyRect, DT_NOPREFIX|DT_WORD_ELLIPSIS|0)
	#开始裁剪
	#rect:区域
	def beginClip(self, rect):
		self.m_innerHDC = win32gui.CreateCompatibleDC(self.m_drawHDC)
		win32gui.SetGraphicsMode(self.m_innerHDC, GM_ADVANCED)
		win32gui.SetBkMode(self.m_innerHDC, TRANSPARENT)
		self.m_offsetX = 0
		self.m_offsetY = 0
		self.m_innerBM = win32gui.CreateCompatibleBitmap(self.m_drawHDC, int(rect.right - rect.left),  int(rect.bottom - rect.top))
		win32gui.SelectObject(self.m_innerHDC, self.m_innerBM)
		lf = win32gui.LOGFONT()
		lf.lfFaceName = self.m_systemFont
		self.m_textSize = 19
		lf.lfHeight = self.m_textSize
		#lf.lfWeight = 700
		self.m_hFont = win32gui.CreateFontIndirect(lf)
		self.m_hOldFont = win32gui.SelectObject(self.m_innerHDC, self.m_hFont);
		win32gui.SelectObject(self.m_innerHDC, self.m_hFont)

	#结束裁剪
	#rect:区域
	#clipRect:裁剪区域
	def endClip(self, rect, clipRect):	
		if(self.m_hOldFont != None):
			win32gui.SelectObject(self.m_innerHDC, self.m_hOldFont);
			self.m_hOldFont = None
		if(self.m_hFont != None):
			win32gui.DeleteObject(self.m_hFont);
			self.m_hFont = None
		win32gui.StretchBlt(self.m_drawHDC, int(clipRect.left), int(clipRect.top), int(clipRect.right - clipRect.left), int(clipRect.bottom - clipRect.top), self.m_innerHDC, int(clipRect.left - rect.left), int(clipRect.top - rect.top), int(clipRect.right - clipRect.left), int(clipRect.bottom - clipRect.top), 13369376)
		if(self.m_innerHDC != None):
			win32gui.DeleteObject(self.m_innerHDC)
			self.m_innerHDC = None
		if(self.m_innerBM != None):
			win32gui.DeleteObject(self.m_innerBM)
			self.m_innerBM = None
		self.m_innerHDC = self.m_drawHDC
		self.m_innerBM = self.m_memBM

#基础视图
class FCView(object):
	def __init__(self):
		self.m_backColor = "" #背景色
		self.m_borderColor = "" #边线色
		self.m_textColor = "" #前景色
		self.m_location = FCPoint(0,0) #坐标
		self.m_name = "" #名称
		self.m_parent = None #父视图
		self.m_size = FCSize(100,30) #大小
		self.m_text = "" #文字
		self.m_visible = TRUE #可见性
		self.m_scrollV = 0 #纵向滚动
		self.m_scrollH = 0 #横向滚动
		self.m_scrollSize = 8 #滚动条的大小
		self.m_showHScrollBar = FALSE #是否显示横向滚动条
		self.m_showVScrollBar = FALSE #是否显示横向滚动条
		self.m_scrollBarColor = "rgb(100,100,100)" #滚动条的颜色
		self.m_allowDragScroll = FALSE #是否允许拖动滚动
		self.m_downScrollHButton = FALSE #是否按下横向滚动条
		self.m_downScrollVButton = FALSE #是否按下纵向滚动条
		self.m_startScrollH = 0 #开始滚动的值
		self.m_startScrollV = 0 #结束滚动的值
		self.m_startPoint = None #起始点
		self.m_mouseDownTime = 0 #鼠标按下的时间
		self.m_displayOffset = TRUE #是否显示偏移量
		self.m_paint = None #绘图对象
		self.m_padding = FCPadding(0,0,0,0) #内边距
		self.m_margin = FCPadding(0,0,0,0) #外边距
		self.m_dock = "none" #悬浮状态
		self.m_backImage = "" #背景图片
		self.m_topMost = FALSE #是否置顶
		self.m_clipRect = None #裁剪区域
		self.m_font = "12px Arial" #字体
		self.m_type = "" #类型
		self.m_views = [] #子视图
		self.m_hWnd = None #子视图句柄
		self.m_hoveredColor = "none" #鼠标悬停时的颜色
		self.m_pushedColor = "rgb(100,100,100)" #鼠标按下时的颜色
		self.m_allowDrag = FALSE #是否允许拖动
		self.m_allowDraw = TRUE #是否允许绘图

m_cancelClick = FALSE #是否退出点击
m_mouseDownView = None #鼠标按下的视图
m_mouseMoveView = None #鼠标移动的视图
m_focusedView = None #焦点视图
m_mouseDownPoint = FCPoint(0,0)
m_paintCallBack = None #绘图回调
m_paintBorderCallBack = None #绘制边线的回调
m_mouseDownCallBack = None #鼠标按下的回调
m_mouseMoveCallBack = None #鼠标移动的回调
m_mouseUpCallBack = None #鼠标抬起的回调
m_mouseWheelCallBack = None #鼠标滚动的回调
m_clickCallBack = None #点击的回调
m_mouseEnterCallBack = None #鼠标进入的回调
m_mouseLeaveCallBack = None #鼠标离开的回调

m_dragBeginPoint = FCPoint(0, 0) #拖动开始时的触摸位置
m_dragBeginRect = FCRect(0, 0, 0, 0) #拖动开始时的区域
m_draggingView = None #正被拖动的控件
	
#复选按钮
class FCCheckBox(FCView):
	def __init__(self):
		super().__init__()
		self.m_displayOffset = TRUE #是否显示偏移量
		self.m_visible = TRUE #是否可见
		self.m_type = "checkbox" #类型
		self.m_buttonSize = FCSize(16,16) #按钮的大小
		self.m_checked = TRUE #是否选中
	pass

#单选按钮
class FCRadioButton(FCView):
	def __init__(self):
		super().__init__()
		self.m_displayOffset = TRUE #是否显示偏移量
		self.m_visible = TRUE #是否可见
		self.m_type = "radiobutton" #类型
		self.m_buttonSize = FCSize(16,16) #按钮的大小
		self.m_checked = FALSE #是否选中
		self.m_groupName = "" #组别
	pass

#页
class FCTabPage(FCView):
	def __init__(self):
		super().__init__()
		self.m_backColor = "rgb(255,255,255)" #背景色
		self.m_borderColor = "rgb(0,0,0)" #边线色
		self.m_type = "tabpage" #类型
		self.m_headerButton = None #页头的按钮
		self.m_visible = FALSE #是否可见
	pass

#多页夹
class FCTabView(FCView):
	def __init__(self):
		super().__init__()
		self.m_layout = "top" #布局方式
		self.m_type = "tabview" #类型
		self.m_underLineColor = "none" #下划线的颜色
		self.m_underLineSize = 0 #下划线的宽度
		self.m_underPoint = None #下划点
		self.m_useAnimation = FALSE #是否使用动画
		self.m_animationSpeed = 20 #动画速度
		self.m_tabPages = [] #子页
	pass

#多布局图层
class FCLayoutDiv(FCView):
	def __init__(self):
		super().__init__()
		self.m_type = "layout" #类型
		self.m_layoutStyle = "lefttoright" #分割方式
		self.m_autoWrap = FALSE #是否自动换行
	pass

#多布局图层
class FCSplitLayoutDiv(FCView):
	def __init__(self):
		super().__init__()
		self.m_type = "split" #类型
		self.m_firstView = None #第一个视图
		self.m_secondView = None #第二个视图
		self.m_splitMode = "absolutesize" #分割模式 percentsize百分比 或absolutesize绝对值
		self.m_splitPercent = -1 #分割百分比
		self.m_splitter = None #分割线 
		self.m_layoutStyle = "lefttoright" #分割方式
		self.m_oldSize = FCSize(0,0) #上次的尺寸
	pass

#表格列
class FCGridColumn(object):	
	def __init__(self):
		self.m_name = "" #名称
		self.m_text = "" #文字
		self.m_type = "" #类型
		self.m_width = 120 #宽度
		self.m_font = "12px Arial" #字体
		self.m_backColor = "rgb(50,50,50)" #背景色
		self.m_borderColor = "rgb(100,100,100)" #边线颜色
		self.m_textColor = "rgb(200,200,200)" #文字颜色
		self.m_frozen = FALSE #是否冻结
		self.m_sort = "none" #排序模式
		self.m_visible = TRUE #是否可见
		self.m_index = -1 #索引
		self.m_bounds = FCRect(0,0,0,0) #区域
		self.m_allowSort = TRUE #是否允许排序

#表格列
class FCGridCell(object):	
	def __init__(self):
		self.m_value = None #值
		self.m_backColor = "none" #背景色
		self.m_borderColor = "none" #边线颜色
		self.m_textColor = "rgb(255,255,255)" #文字颜色
		self.m_font = "12px Arial" #字体
		self.m_colSpan = 1 #列距
		self.m_rowSpan = 1 #行距
		self.m_column = None #所在列

#表格行
class FCGridRow(object):	
	def __init__(self):
		self.m_cells = [] #单元格
		self.m_selected = FALSE #是否选中
		self.m_visible = TRUE #是否可见
		self.m_key = "" #排序键值

#多页夹
class FCGrid(FCView):
	def __init__(self):
		super().__init__()
		self.m_type = "grid" #类型
		self.m_columns = [] #列
		self.m_rows = [] #行
		self.m_rowHeight = 30 #行高
		self.m_headerHeight = 30 #头部高度
		self.m_showHScrollBar = TRUE #是否显示横向滚动条
		self.m_showVScrollBar = TRUE #是否显示横向滚动条
		self.m_seletedRowColor = "rgb(125,125,125)" #选中行的颜色
	pass

#表格列
class FCTreeColumn(object):
	def __init__(self):
		self.m_width = 120 #宽度
		self.m_visible = TRUE #是否可见
		self.m_index = -1 #索引
		self.m_bounds = FCRect(0,0,0,0) #区域

#表格行
class FCTreeRow(object):	
	def __init__(self):
		self.m_cells = [] #单元格
		self.m_selected = FALSE #是否选中
		self.m_visible = TRUE #是否可见
		self.m_index = -1 #索引

#单元格
class FCTreeNode(object):
	def __init__(self):
		self.m_value = None #值
		self.m_backColor = "none" #背景色
		self.m_textColor = "rgb(0,0,0)" #文字颜色
		self.m_font = "14px Arial" #字体
		self.m_column = None #所在列
		self.m_allowCollapsed = TRUE #是否允许折叠
		self.m_collapsed = FALSE #是否折叠
		self.m_parentNode = None #父节点
		self.m_childNodes = [] #子节点
		self.m_indent = 0 #缩进
		self.m_row = None #所在行
		self.m_checked = FALSE #是否选中

#多页夹
class FCTree(FCView):
	def __init__(self):
		super().__init__()
		self.m_type = "tree" #类型
		self.m_columns = [] #列
		self.m_rows = [] #行
		self.m_rowHeight = 30 #行高
		self.m_headerHeight = 30 #头部高度
		self.m_showHScrollBar = TRUE #是否显示横向滚动条
		self.m_showVScrollBar = TRUE #是否显示横向滚动条
		self.m_childNodes = [] #子节点
		self.m_indent = 20 #缩进
		self.m_showCheckBox = FALSE #是否显示复选框
		self.m_checkBoxWidth = 25 #复选框占用的宽度
		self.m_collapsedWidth = 25 #折叠按钮占用的宽度
	pass

#证券数据结构
class SecurityData(object):
	def __init__(self):
		self.m_amount = 0 #成交额
		self.m_close = 0 #收盘价
		self.m_date = 0 #日期，为1970年到现在的秒
		self.m_high = 0 #最高价
		self.m_low = 0 #最低价
		self.m_open = 0 #开盘价
		self.m_volume = 0 #成交额
	#拷贝数值
	def copy(self, securityData):
		self.m_amount = securityData.m_amount
		self.m_close = securityData.m_close
		self.m_date = securityData.m_date
		self.m_high = securityData.m_high
		self.m_low = securityData.m_low
		self.m_open = securityData.m_open
		self.m_volume = securityData.m_volume

#基础图形
class BaseShape(object):
	def __init__(self):
		self.m_divIndex = 0 #所在层
		self.m_type = "line" #类型
		self.m_lineWidth = 1 #线的宽度
		self.m_color = "none" #颜色
		self.m_color2 = "none" #颜色2
		self.m_datas = [] #第一组数据
		self.m_datas2 = [] #第二组数据
		self.m_title = "" #第一个标题
		self.m_title2 = "" #第二个标题
		self.m_name = "" #名称
		self.m_style = "" #样式
		self.m_text = "" #显示的文字
		self.m_value = 0 #显示文字的值
		self.m_showHideDatas = [] #控制显示隐藏的数据

#画线工具结构
class FCPlot(object):
	def __init__(self):
		self.m_plotType = "Line" #线的类型
		self.m_lineColor = "rgb(255,255,255)" #线的颜色
		self.m_pointColor = "rgba(255,255,255,0.5)" #线的颜色
		self.m_lineWidth = 1 #线的宽度
		self.m_key1 = None #第一个键
		self.m_value1 = None #第一个值
		self.m_key2 = None #第二个键
		self.m_value2 = None #第二个值
		self.m_key3 = None #第三个键
		self.m_value3 = None #第三个值
		self.m_startKey1 = None #移动前第一个键
		self.m_startValue1 = None #移动前第一个值
		self.m_startKey2 = None #移动前第二个键
		self.m_startValue2 = None #移动前第二个值
		self.m_startKey3 = None #移动前第三个键
		self.m_startValue3 = None #移动前第三个值

class FCChart(FCView):
	def __init__(self):
		super().__init__()
		self.m_candleDistance = 0 #蜡烛线的距离
		self.m_hScalePixel = 11 #蜡烛线的宽度
		self.m_data = [] #K线数据
		self.m_downColor = "rgb(15,193,118)" #下跌颜色
		self.m_leftVScaleWidth = 0 #左轴宽度
		self.m_rightVScaleWidth = 100 #右轴宽度
		self.m_upColor = "rgb(219,68,83)" #上涨颜色
		self.m_firstVisibleIndex = -1 #起始可见的索引
		self.m_lastVisibleIndex = -1 #结束可见的索引
		self.m_hScaleHeight = 30 #X轴的高度
		self.m_scaleColor = "rgb(100,0,0)" #刻度的颜色
		self.m_candleMax = 0 #蜡烛线的最大值
		self.m_candleMin = 0 #蜡烛线的最小值
		self.m_volMax = 0 #成交量层的最大值
		self.m_volMin = 0 #成交量层的最小值
		self.m_indMax = 0 #指标层的最大值
		self.m_indMin = 0 #指标层的最小值
		self.m_indMax2 = 0 #指标层2的最大值
		self.m_indMin2 = 0 #指标层2的最小值
		self.m_crossTipColor = "rgb(50,50,50)" #十字线标识的颜色
		self.m_crossLineColor = "rgb(100,100,100)" #十字线的颜色
		self.m_font = "12px Arial" #字体
		self.m_candleDigit = 2 #K线层保留小数的位数
		self.m_volDigit = 0 #成交量层保留小数的位数
		self.m_indDigit = 2 #指标层保留小数的位数
		self.m_indDigit2 = 2 #指标层2保留小数的位数
		self.m_lastRecordIsVisible = TRUE #最后记录是否可见
		self.m_lastVisibleKey = 0 #最后可见的主键
		self.m_autoFillHScale = FALSE #是否填充满X轴
		self.m_candleDivPercent = 0.5 #K线层的占比
		self.m_volDivPercent = 0.2 #成交量层的占比
		self.m_indDivPercent = 0.3 #指标层的占比
		self.m_indDivPercent2 = 0.0 #指标层2的占比
		self.m_mainIndicator = "" #主图指标
		self.m_showIndicator = "" #显示指标
		self.m_gridColor = "rgb(100,0,0)" #网格颜色 
		self.m_magnitude = 1 #成交量的比例
		self.m_showCrossLine = TRUE #是否显示十字线
		self.m_candlePaddingTop = 30 #K线层的上边距
		self.m_candlePaddingBottom = 30 #K线层的下边距
		self.m_volPaddingTop = 20 #成交量层的上边距
		self.m_volPaddingBottom = 0 #成交量层的下边距
		self.m_indPaddingTop = 20 #指标层的上边距
		self.m_indPaddingBottom = 20 #指标层的下边距
		self.m_indPaddingTop2 = 20 #指标层2的上边距
		self.m_indPaddingBottom2 = 20 #指标层2的下边距
		self.m_vScaleDistance = 35 #纵轴的间隔
		self.m_vScaleType = "standard" #纵轴的类型 log10代表指数坐标
		self.m_plots = [] #画线的集合
		self.m_selectPlotPoint = -1 ##选中画线的点
		self.m_sPlot = None #选中的画线
		self.m_startMovePlot = FALSE #选中画线
		self.m_crossStopIndex = -1 #鼠标停留位置
		self.m_cycle = "second" #周期
		self.m_mousePosition = FCPoint(0,0) #鼠标坐标
		self.m_lastValidIndex = -1 #最后有效数据索引
		self.m_selectShape = "" #选中的图形
		self.m_selectShapeEx = "" #选中的图形信息
		self.m_type = "chart" #类型
		self.m_allowDragScroll = TRUE #是否允许拖动滚动
		self.m_rightSpace = 0 #右侧空间
		self.m_allema12 = []
		self.m_allema26 = []
		self.m_alldifarr = []
		self.m_alldeaarr = []
		self.m_allmacdarr = []
		self.m_boll_up = []
		self.m_boll_down = []
		self.m_boll_mid = []
		self.m_bias1 = []
		self.m_bias2 = []
		self.m_bias3 = []
		self.m_kdj_k = []
		self.m_kdj_d = []
		self.m_kdj_j = []
		self.m_rsi1 = []
		self.m_rsi2 = []
		self.m_rsi3 = []
		self.m_roc = []
		self.m_roc_ma = []
		self.m_wr1 = []
		self.m_wr2 = []
		self.m_cci = []
		self.m_bbi = []
		self.m_trix = []
		self.m_trix_ma = []
		self.m_dma1 = []
		self.m_dma2 = []
		self.m_ma5 = []
		self.m_ma10 = []
		self.m_ma20 = []
		self.m_ma30 = []
		self.m_ma120 = []
		self.m_ma250 = []
		self.m_shapes = [] #扩展图形
		self.m_hScaleFormat = "" #X轴的格式化字符，例如%Y-%m-%d %H:%M:%S
	pass

m_indicatorColors = [] #指标的颜色
m_indicatorColors.append("rgb(255,255,255)")
m_indicatorColors.append("rgb(255,255,0)")
m_indicatorColors.append("rgb(255,0,255)")
m_indicatorColors.append("rgb(255,0,0)")
m_indicatorColors.append("rgb(0,255,255)")
m_indicatorColors.append("rgb(0,255,0)")
m_indicatorColors.append("rgb(255,255,0)")
m_indicatorColors.append("rgb(255,255,255)")
m_lineWidth_Chart = 1
m_plotPointSize_Chart = 5 #画线的选中点大小
m_firstIndexCache_Chart = -1
m_firstTouchIndexCache_Chart = -1
m_firstTouchPointCache_Chart = FCPoint(0,0)
m_lastIndexCache_Chart = -1
m_secondTouchIndexCache_Chart = -1
m_secondTouchPointCache_Chart = FCPoint(0,0)
m_mouseDownPoint_Chart = FCPoint(0,0)

#添加顶层视图
#view 视图
#paint 绘图对象
def addView(view, paint):
	view.m_paint = paint
	paint.m_views.append(view)

#添加到父视图
#view 视图
#parent 父视图
def addViewToParent(view, parent):
	view.m_parent = parent
	view.m_paint = parent.m_paint
	parent.m_views.append(view)

#移除顶层视图
#view 视图
#paint 绘图对象
def removeView(view, paint):
	for i in range(0, len(paint.m_views)):
		if(paint.m_views[i] == view):
			paint.m_views.remove(view)
			break

#从父视图中移除
#view 视图
#parent 父视图
def removeViewFromParent(view, parent):
	for i in range(0, len(parent.m_views)):
		if(parent.m_views[i] == view):
			parent.m_views.remove(view)
			break

#获取绝对位置X 
#view:视图
def clientX(view):
	if(view != None):
		cLeft = view.m_location.x;
		if(view.m_parent != None):
			if view.m_parent.m_displayOffset:
				return cLeft + clientX(view.m_parent) - view.m_parent.m_scrollH
			else:
				return cLeft + clientX(view.m_parent)
		else:
			return cLeft
	else:
		return 0

#获取绝对位置Y 
#view:视图
def clientY(view):
	if(view != None):
		cTop = view.m_location.y;
		if(view.m_parent != None):
			if view.m_parent.m_displayOffset:
				return cTop + clientY(view.m_parent) - view.m_parent.m_scrollV
			else:
				return cTop + clientY(view.m_parent)
		else:
			return cTop
	else:
		return 0

#是否重绘时可见 
#view:视图
def isPaintVisible(view):
    if(view.m_visible):
        if(view.m_parent != None):
            if(view.m_parent.m_visible):
                return isPaintVisible(view.m_parent)
            else:
                return FALSE
        else:
            return TRUE;
    else:
        return FALSE;

#是否包含坐标 
#view:视图 
#mp:坐标
def containsPoint(view, mp):
	clx = clientX(view)
	cly = clientY(view)
	size = view.m_size
	cp = FCPoint(0,0)
	cp.x = mp.x - clx
	cp.y = mp.y - cly
	if cp.x >= 0 and cp.x <= size.cx and cp.y >= 0 and cp.y <= size.cy:
		return TRUE
	else:
		return FALSE

#根据名称查找视图 
#name:名称
def findViewByName(name, views):
	size = len(views)
	for view in views:
		if(view.m_name == name):
		    return view
		else:
			subViews = view.m_views
			if (len(subViews)) > 0:
				subView = findViewByName(name, subViews)
				if(subView != None):
					return subView
	return None

#获取区域的交集
def getIntersectRect(lpDestRect, lpSrc1Rect, lpSrc2Rect):
	lpDestRect.left = max(lpSrc1Rect.left, lpSrc2Rect.left)
	lpDestRect.right = min(lpSrc1Rect.right, lpSrc2Rect.right)
	lpDestRect.top = max(lpSrc1Rect.top, lpSrc2Rect.top)
	lpDestRect.bottom = min(lpSrc1Rect.bottom, lpSrc2Rect.bottom)
	if (lpDestRect.right > lpDestRect.left) and (lpDestRect.bottom > lpDestRect.top):
		return 1
	else:
		lpDestRect.left = 0
		lpDestRect.right = 0
		lpDestRect.top = 0
		lpDestRect.bottom = 0
		return 0

#根据坐标查找视图 
#mp:坐标 
#views:视图集合
def findView(mp, views):
	size = len(views)
	for i in range(0, size):
		view = views[size - i - 1]
		if(view.m_visible and view.m_topMost):
			if(containsPoint(view, mp)):
				if(view.m_showVScrollBar and view.m_scrollSize > 0):
					clx = clientX(view)
					if(mp.x >= clx + view.m_size.cx - view.m_scrollSize):
						return view
				if(view.m_showHScrollBar and view.m_scrollSize > 0):
					cly = clientY(view);
					if(mp.y >= cly + view.m_size.cy - view.m_scrollSize):
						return view
				subViews = view.m_views
				if(len(subViews) > 0):
					subView = findView(mp, subViews)
					if(subView != None):
						return subView
				return view
	for i in range(0, size):
		view = views[size - i - 1]
		if(view.m_visible and view.m_topMost == FALSE):
			if(containsPoint(view, mp)):
				if(view.m_showVScrollBar and view.m_scrollSize > 0):
					clx = clientX(view)
					if(mp.x >= clx + view.m_size.cx - view.m_scrollSize):
						return view
				if(view.m_showHScrollBar and view.m_scrollSize > 0):
					cly = clientY(view);
					if(mp.y >= cly + view.m_size.cy - view.m_scrollSize):
						return view
				subViews = view.m_views
				if(len(subViews) > 0):
					subView = findView(mp, subViews)
					if(subView != None):
						return subView
				return view
	return None

#重绘复选按钮 
#checkBox:视图 
#paint:绘图对象 
#clipRect:裁剪区域
def drawCheckBox(checkBox, paint, clipRect):
	width = checkBox.m_size.cx
	height = checkBox.m_size.cy
	if(checkBox.m_textColor != "none"):
		eRight = checkBox.m_buttonSize.cx + 10
		eRect = FCRect(1, (height - checkBox.m_buttonSize.cy) / 2, checkBox.m_buttonSize.cx + 1, (height + checkBox.m_buttonSize.cy) / 2)
		paint.drawRect(checkBox.m_textColor, 1, 0, eRect.left, eRect.top, eRect.right, eRect.bottom)
		if(checkBox.m_checked):
			eRect.left += 2
			eRect.top += 2
			eRect.right -= 2
			eRect.bottom -= 2
			paint.fillRect(checkBox.m_textColor, eRect.left, eRect.top, eRect.right, eRect.bottom)
		tSize = paint.textSize(checkBox.m_text, checkBox.m_font)
		paint.drawText(checkBox.m_text, checkBox.m_textColor, checkBox.m_font, eRight, (height - tSize.cy) / 2)		

#重绘单选按钮 
#checkBox:视图 
#paint:绘图对象 
#clipRect:裁剪区域
def drawRadioButton(radioButton, paint, clipRect):
	width = radioButton.m_size.cx
	height = radioButton.m_size.cy
	if(radioButton.m_textColor != "none"):
		eRight = radioButton.m_buttonSize.cx + 10
		eRect = FCRect(1, (height - radioButton.m_buttonSize.cy) / 2, radioButton.m_buttonSize.cx + 1, (height + radioButton.m_buttonSize.cy) / 2)
		paint.drawEllipse(radioButton.m_textColor, 1, 0, eRect.left, eRect.top, eRect.right, eRect.bottom)
		if(radioButton.m_checked):
			eRect.left += 2
			eRect.top += 2
			eRect.right -= 2
			eRect.bottom -= 2
			paint.fillEllipse(radioButton.m_textColor, eRect.left, eRect.top, eRect.right, eRect.bottom)
		tSize = paint.textSize(radioButton.m_text, radioButton.m_font)
		paint.drawText(radioButton.m_text, radioButton.m_textColor, radioButton.m_font, eRight, (height - tSize.cy) / 2)		

#点击复选按钮 
#checkBox:视图
def clickCheckBox(checkBox, mp):
	if(checkBox.m_checked):
		checkBox.m_checked = FALSE
	else:
		checkBox.m_checked = TRUE

#点击单选按钮 
#radioButton:视图
def clickRadioButton(radioButton, mp):
	hasOther = FALSE
	if(radioButton.m_parent != None and len(radioButton.m_parent.m_views) > 0):
		for i in range(0, len(radioButton.m_parent.m_views)):
			rView = radioButton.m_parent.m_views[i]
			if(rView.m_type == "radiobutton"):
				if(rView != radioButton and rView.m_groupName == radioButton.m_groupName):
					rView.m_checked = FALSE
	radioButton.m_checked = TRUE

#重绘按钮 
#button:视图 
#paint:绘图对象 
#clipRect:裁剪区域
def drawButton(button, paint, clipRect):
	if(button == m_mouseDownView):
		if(button.m_pushedColor != "none"):
			paint.fillRect(button.m_pushedColor, 0, 0, button.m_size.cx, button.m_size.cy)
		else:
			if(button.m_backColor != "none"):
				paint.fillRect(button.m_backColor, 0, 0, button.m_size.cx, button.m_size.cy)
	elif(button == m_mouseMoveView):
		if(button.m_hoveredColor != "none"):
			paint.fillRect(button.m_hoveredColor, 0, 0, button.m_size.cx, button.m_size.cy)
		else:
			if(button.m_backColor != "none"):
				paint.fillRect(button.m_backColor, 0, 0, button.m_size.cx, button.m_size.cy)
	elif(button.m_backColor != "none"):
		paint.fillRect(button.m_backColor, 0, 0, button.m_size.cx, button.m_size.cy)
	if(button.m_textColor != "none" and len(button.m_text) > 0):
		tSize = paint.textSize(button.m_text, button.m_font)
		paint.drawText(button.m_text, button.m_textColor, button.m_font, (button.m_size.cx - tSize.cx) / 2, (button.m_size.cy  - tSize.cy) / 2)
	if(button.m_borderColor != "none"):
		paint.drawRect(button.m_borderColor, 1, 0, 0, 0, button.m_size.cx - 1, button.m_size.cy - 1)

#获取内容的宽度 
#div:图层
def getDivContentWidth(div):
	cWidth = 0
	subViews = div.m_views
	for view in subViews:
		if(view.m_visible):
			if(cWidth < view.m_location.x + view.m_size.cx):
			        cWidth = view.m_location.x + view.m_size.cx
	return cWidth

#获取内容的高度 
#div:图层
def getDivContentHeight(div):
	cHeight = 0
	subViews = div.m_views
	for view in subViews:
		if(view.m_visible):
			if(cHeight < view.m_location.y + view.m_size.cy):
			        cHeight = view.m_location.y + view.m_size.cy
	return cHeight

#绘制滚动条 
#div:图层 
#paint:绘图对象 
#clipRect:裁剪区域
def drawDivScrollBar(div, paint, clipRect):
	if (div.m_showHScrollBar):
		contentWidth = getDivContentWidth(div);
		if (contentWidth > div.m_size.cx):
			sLeft = div.m_scrollH / contentWidth * div.m_size.cx
			sRight = (div.m_scrollH + div.m_size.cx) / contentWidth * div.m_size.cx
			if (sRight - sLeft < div.m_scrollSize):
				sRight = sLeft + div.m_scrollSize
			paint.fillRect(div.m_scrollBarColor, sLeft, div.m_size.cy - div.m_scrollSize, sRight, div.m_size.cy)
	if(div.m_showVScrollBar):
		contentHeight = getDivContentHeight(div)	
		if (contentHeight > div.m_size.cy):
			sTop = div.m_scrollV / contentHeight * div.m_size.cy
			sBottom = sTop + (div.m_size.cy / contentHeight * div.m_size.cy)
			if (sBottom - sTop < div.m_scrollSize):
				sBottom = sTop + div.m_scrollSize
			paint.fillRect(div.m_scrollBarColor, div.m_size.cx - div.m_scrollSize, sTop, div.m_size.cx, sBottom)

#重绘图层边线 
#div:视图 
#paint:绘图对象 
#clipRect:裁剪区域
def drawDivBorder(div, paint, clipRect):
	if(div.m_borderColor != "none"):
		paint.drawRect(div.m_borderColor, 1, 0, 0, 0, div.m_size.cx - 1, div.m_size.cy - 1)

#重绘图形 
#div:视图 
#paint:绘图对象 
#clipRect:裁剪区域
def drawDiv(div, paint, clipRect):
	if(div.m_backColor != "none"):
		paint.fillRect(div.m_backColor, 0, 0, div.m_size.cx, div.m_size.cy)

#图层的鼠标滚轮方法 
#div:图层 
#delta:滚轮值
def mouseWheelDiv(div, delta):
	oldScrollV = div.m_scrollV
	if (delta > 0):
		oldScrollV -= 10
	elif (delta < 0):
		oldScrollV += 10
	contentHeight = getDivContentHeight(div)
	if (contentHeight < div.m_size.cy):
		div.m_scrollV = 0
	else:
		if (oldScrollV < 0):
			oldScrollV = 0
		elif (oldScrollV > contentHeight - div.m_size.cy):
			oldScrollV = contentHeight - div.m_size.cy
		div.m_scrollV = oldScrollV;


#图层的鼠标抬起方法 
#div: 图层 
#firstTouch:是否第一次触摸 
#secondTouch:是否第二次触摸 
#firstPoint:第一次触摸的坐标 
#secondPoint:第二次触摸的坐标
def mouseUpDiv(div, firstTouch, secondTouch, firstPoint, secondPoint):
	div.m_downScrollHButton = FALSE
	div.m_downScrollVButton = FALSE

#图层的鼠标按下方法 
#div: 图层 
#firstTouch:是否第一次触摸 
#secondTouch:是否第二次触摸 
#firstPoint:第一次触摸的坐标 
#secondPoint:第二次触摸的坐标
def mouseDownDiv(div, firstTouch, secondTouch, firstPoint, secondPoint):
	mp = firstPoint
	div.m_startPoint = mp
	div.m_downScrollHButton = FALSE
	div.m_downScrollVButton = FALSE
	if (div.m_showHScrollBar):
		contentWidth = getDivContentWidth(div)
		if (contentWidth > div.m_size.cx):
			sLeft = div.m_scrollH / contentWidth * div.m_size.cx
			sRight = (div.m_scrollH + div.m_size.cx) / contentWidth * div.m_size.cx
			if (sRight - sLeft < div.m_scrollSize):
				sRight = sLeft + div.m_scrollSize
			if (mp.x >= sLeft and mp.x <= sRight and mp.y >= div.m_size.cy - div.m_scrollSize and mp.y <= div.m_size.cy):
				div.m_downScrollHButton = TRUE
				div.m_startScrollH = div.m_scrollH
				return
	if (div.m_showVScrollBar):
		contentHeight = getDivContentHeight(div)
		if (contentHeight > div.m_size.cy):
			sTop = div.m_scrollV / contentHeight * div.m_size.cy
			sBottom = (div.m_scrollV + div.m_size.cy) / contentHeight * div.m_size.cy
			if (sBottom - sTop < div.m_scrollSize):
				sBottom = sTop + div.m_scrollSize
			if (mp.x >= div.m_size.cx - div.m_scrollSize and mp.x <= div.m_size.cx and mp.y >= sTop and mp.y <= sBottom):
				div.m_downScrollVButton = TRUE
				div.m_startScrollV = div.m_scrollV
				return
	if (div.m_allowDragScroll):
		div.m_startScrollH = div.m_scrollH
		div.m_startScrollV = div.m_scrollV

#图层的鼠标移动方法 
#div: 图层 
#firstTouch:是否第一次触摸 
#secondTouch:是否第二次触摸 
#firstPoint:第一次触摸的坐标 
#secondPoint:第二次触摸的坐标
def mouseMoveDiv(div, firstTouch, secondTouch, firstPoint, secondPoint):
	if (firstTouch):
		mp = firstPoint;
		if (div.m_showHScrollBar or div.m_showVScrollBar):
			if (div.m_downScrollHButton):
				contentWidth = getDivContentWidth(div)
				subX = (mp.x - div.m_startPoint.x) / div.m_size.cx * contentWidth
				newScrollH = div.m_startScrollH + subX
				if (newScrollH < 0):
					newScrollH = 0
				elif (newScrollH > contentWidth - div.m_size.cx):
					newScrollH = contentWidth - div.m_size.cx
				div.m_scrollH = newScrollH
				m_cancelClick = TRUE
				return
			elif (div.m_downScrollVButton):
				contentHeight = getDivContentHeight(div)
				subY = (mp.y - div.m_startPoint.y) / div.m_size.cy * contentHeight
				newScrollV = div.m_startScrollV + subY
				if (newScrollV < 0):
					newScrollV = 0
				elif (newScrollV > contentHeight - div.m_size.cy):
					newScrollV = contentHeight - div.m_size.cy;
				div.m_scrollV = newScrollV
				m_cancelClick = TRUE
				return
		if (div.m_allowDragScroll):
			contentWidth = getDivContentWidth(div)
			if (contentWidth > div.m_size.cx):
				subX = div.m_startPoint.x - mp.x
				newScrollH = div.m_startScrollH + subX
				if (newScrollH < 0):
					newScrollH = 0
				elif (newScrollH > contentWidth - div.m_size.cx):
					newScrollH = contentWidth - div.m_size.cx
				div.m_scrollH = newScrollH
				if(abs(subX) > 5):
				    m_cancelClick = TRUE
			contentHeight = getDivContentHeight(div)
			if (contentHeight > div.m_size.cy):
				subY = div.m_startPoint.y - mp.y
				newScrollV = div.m_startScrollV + subY
				if (newScrollV < 0):
					newScrollV = 0
				elif (newScrollV > contentHeight - div.m_size.cy):
					newScrollV = contentHeight - div.m_size.cy;
				div.m_scrollV = newScrollV;
				if(abs(subY) > 5):
				    m_cancelClick = TRUE

#重绘多页加 
#tabView:多页夹 
#paint:绘图对象 
#clipRect:裁剪区域
def drawTabViewBorder(tabView, paint, clipRect):
	if(tabView.m_underLineColor != "none"):
		tabPages = tabView.m_tabPages
		for tp in tabPages:
			if(tp.m_visible):
				headerButton = tp.m_headerButton
				location = FCPoint(headerButton.m_location.x, headerButton.m_location.y)
				size = headerButton.m_size
				if(tabView.m_useAnimation):
					if(tabView.m_underPoint != None):
						location.x = tabView.m_underPoint.x
						location.y = tabView.m_underPoint.y
				if(tabView.m_layout == "bottom"):
					paint.fillRect(tabView.m_underLineColor, location.x, location.y, location.x + size.cx, location.y + tabView.m_underLineSize)
				elif(tabView.m_layout == "left"):
					paint.fillRect(tabView.m_underLineColor, location.x + size.cx - tabView.m_underLineSize, location.y, location.x + size.cx, location.y + size.cy)
				elif(tabView.m_layout == "top"):
					paint.fillRect(tabView.m_underLineColor, location.x, location.y + size.cy - tabView.m_underLineSize, location.x + size.cx, location.y + size.cy)
				elif(tabView.m_layout == "right"):
					paint.fillRect(tabView.m_underLineColor, location.x, location.y, location.x + tabView.m_underLineSize, location.y + size.cy)
				break

#更新页的布局 
#tabView:多页夹 
#tabPage:页 
#left:左侧坐标 
#top:上方坐标 
#width:宽度 
#height:高度 
#tw:页头按钮的宽度 
#th:页头按钮的高度
def updataPageLayout(tabView, tabPage, left, top, width, height, tw, th):
	newBounds = FCRect(0, 0, 0, 0)
	if(tabView.m_layout == "bottom"):
		newBounds.left = 0
		newBounds.top = 0
		newBounds.right = width
		newBounds.bottom = height - th
		tabPage.m_headerButton.m_location = FCPoint(left, height - th)
	elif(tabView.m_layout == "left"):
		newBounds.left = tw
		newBounds.top = 0
		newBounds.right = width
		newBounds.bottom = height
		tabPage.m_headerButton.m_location = FCPoint(0, top)
	elif(tabView.m_layout == "right"):
		newBounds.left = 0
		newBounds.top = 0
		newBounds.right = width - tw
		newBounds.bottom = height
		tabPage.m_headerButton.m_location = FCPoint(width - tw, top)
	elif(tabView.m_layout == "top"):
		newBounds.left = 0
		newBounds.top = th
		newBounds.right = width
		newBounds.bottom = height
		tabPage.m_headerButton.m_location = FCPoint(left, 0)
	tabPage.m_location = FCPoint(newBounds.left, newBounds.top)
	tabPage.m_size = FCSize(newBounds.right - newBounds.left, newBounds.bottom - newBounds.top)

#更新多页夹的布局 
#tabView:多页夹
def updateTabLayout(tabView):
	width = tabView.m_size.cx
	height = tabView.m_size.cy
	left = 0
	top = 0
	tabPages = tabView.m_tabPages
	for tabPage in tabPages:
		headerButton = tabPage.m_headerButton
		if(headerButton.m_visible):
			tw = headerButton.m_size.cx;
			th = headerButton.m_size.cy;
			updataPageLayout(tabView, tabPage, left, top, width, height, tw, th)
			left += tw
			top += th
		else:
			tabPage.m_visible = FALSE

#添加页 
#tabView:多页夹 
#tabPage:页 
#tabButton:页头按钮
def addTabPage(tabView, tabPage, tabButton):
	tabPage.m_headerButton = tabButton
	tabPage.m_parent = tabView
	tabPage.m_paint = tabView.m_paint
	tabButton.m_parent = tabView
	tabButton.m_paint = tabView.m_paint
	tabView.m_tabPages.append(tabPage)
	tabView.m_views.append(tabPage)
	tabView.m_views.append(tabButton)

#选中页 
#tabView:多页夹 
#tabPage:页
def selectTabPage(tabView, tabPage):
	tabPages = tabView.m_tabPages
	for tp in tabPages:
		if(tp == tabPage):
			tp.m_visible = TRUE
		else:
			tp.m_visible = FALSE
	updateTabLayout(tabView)

#重置布局图层 
#layout:布局层
def resetLayoutDiv(layout):
	reset = FALSE
	padding = layout.m_padding
	vPos = 0
	left = padding.left
	top = padding.top
	width = layout.m_size.cx - padding.left - padding.right
	height = layout.m_size.cy - padding.top - padding.bottom
	i = 0
	subViews = layout.m_views
	for view in subViews:
		if(view.m_visible):
			size = FCSize(view.m_size.cx, view.m_size.cy)
			margin = view.m_margin
			cLeft = view.m_location.x
			cTop = view.m_location.y
			cWidth = size.cx
			cHeight = size.cy
			nLeft = cLeft
			nTop = cTop
			nWidth = cWidth
			nHeight = cHeight
			if(layout.m_layoutStyle == "bottomtotop"):
				if (i == 0):
					top = height - padding.top
				lWidth = 0
				if (layout.m_autoWrap):
					lWidth = size.cx
					lTop = top - margin.top - cHeight - margin.bottom
					if (lTop < padding.top):
						if(vPos != 0):
							left += cWidth + margin.left
						top = height - padding.top
				else:
					lWidth = width - margin.left - margin.right
				top -= cHeight + margin.bottom
				nLeft = left + margin.left
				nWidth = lWidth
				nTop = top
			elif(layout.m_layoutStyle == "lefttoright"):
				lHeight = 0;
				if (layout.m_autoWrap):
					lHeight = size.cy
					lRight = left + margin.left + cWidth + margin.right
					if (lRight > width):
						left = padding.left
						if(vPos != 0):
							top += cHeight + margin.top
				else:
					lHeight = height - margin.top - margin.bottom
				left += margin.left
				nLeft = left
				nTop = top + margin.top
				nHeight = lHeight
				left += cWidth + margin.right
			elif(layout.m_layoutStyle == "righttoleft"):
				if (i == 0):
					left = width - padding.left
				lHeight = 0
				if (layout.m_autoWrap):
					lHeight = size.cy
					lLeft = left - margin.left - cWidth - margin.right
					if (lLeft < padding.left):
						left = width - padding.left
						if(vPos != 0):
							top += cHeight + margin.top
				else:
					lHeight = height - margin.top - margin.bottom
				left -= cWidth + margin.left
				nLeft = left
				nTop = top + margin.top
				nHeight = lHeight
			elif(layout.m_layoutStyle == "toptobottom"):
				lWidth = 0
				if (layout.m_autoWrap):
					lWidth = size.cx;
					lBottom = top + margin.top + cHeight + margin.bottom
					if (lBottom > height):
						if(vPos != 0):
							left += cWidth + margin.left + margin.right
						top = padding.top
				else:
					lWidth = width - margin.left - margin.right
					top += margin.top
					nTop = top
					nLeft = left + margin.left
					nWidth = lWidth
					top += cHeight + margin.bottom
			if (cLeft != nLeft or cTop != nTop or cWidth != nWidth or cHeight != nHeight):
				view.m_location = FCPoint(nLeft, nTop)
				view.m_size = FCSize(nWidth, nHeight)
				reset = TRUE
			vPos = vPos + 1
			i = i + 1
	return reset

#重置分割线的布局
def resetSplitLayoutDiv(split):
	reset = FALSE
	splitRect = FCRect(0, 0, 0, 0)
	width = split.m_size.cx
	height = split.m_size.cy
	fRect = FCRect(0, 0, 0, 0)
	sRect = FCRect(0, 0, 0, 0)
	splitterSize = FCSize(0, 0)
	if(split.m_splitter.m_visible):
		splitterSize.cx = split.m_splitter.m_size.cx
		splitterSize.cy = split.m_splitter.m_size.cy
	layoutStyle = split.m_layoutStyle 
	if (layoutStyle == "bottomtotop"):
		if (split.m_splitMode == "absolutesize" or split.m_oldSize.cy == 0):
			splitRect.left = 0
			splitRect.top = height - (split.m_oldSize.cy - split.m_splitter.m_location.y)
			splitRect.right = width
			splitRect.bottom = splitRect.top + splitterSize.cy
		elif (split.m_splitMode == "percentsize"):
			splitRect.left = 0
			if (split.m_splitPercent == -1):
				split.m_splitPercent = split.m_splitter.m_location.y / split.m_oldSize.cy
			splitRect.top = height * split.m_splitPercent
			splitRect.right = width
			splitRect.bottom = splitRect.top + splitterSize.cy
		fRect.left = 0
		fRect.top = splitRect.bottom
		fRect.right = width
		fRect.bottom = height
		sRect.left = 0
		sRect.top = 0
		sRect.right = width
		sRect.bottom = splitRect.top
	elif(layoutStyle == "lefttoright"):
		if (split.m_splitMode == "absolutesize" or split.m_oldSize.cx == 0):
			splitRect.left = split.m_splitter.m_location.x
			splitRect.top = 0
			splitRect.right = splitRect.left + splitterSize.cx
			splitRect.bottom = height
		elif (split.m_splitMode == "percentsize"):
			if(split.m_splitPercent == -1):
				split.m_splitPercent = split.m_splitter.m_location.x / split.m_oldSize.cx
			splitRect.left = width * split.m_splitPercent
			splitRect.top = 0
			splitRect.right = splitRect.left + splitterSize.cx
			splitRect.bottom = height
		fRect.left = 0
		fRect.top = 0
		fRect.right = splitRect.left
		fRect.bottom = height
		sRect.left = splitRect.right
		sRect.top = 0
		sRect.right = width
		sRect.bottom = height
	elif(layoutStyle == "righttoleft"):
		if (split.m_splitMode == "absolutesize" or split.m_oldSize.cx == 0):
			splitRect.left = width - (split.m_oldSize.cx - split.m_splitter.m_location.x)
			splitRect.top = 0
			splitRect.right = splitRect.left + splitterSize.cx
			splitRect.bottom = height
		elif(split.m_splitMode == "percentsize"):
			if(split.m_splitPercent == -1):
				split.m_splitPercent = split.m_splitter.m_location.x / split.m_oldSize.cx
			splitRect.left = width * split.m_splitPercent
			splitRect.top = 0
			splitRect.right = splitRect.left + splitterSize.cx
			splitRect.bottom = height
		fRect.left = splitRect.right
		fRect.top = 0
		fRect.right = width
		fRect.bottom = height
		sRect.left = 0
		sRect.top = 0
		sRect.right = splitRect.left
		sRect.bottom = height
	elif(layoutStyle == "toptobottom"):
		if (split.m_splitMode == "absolutesize" or split.m_oldSize.cy == 0):
			splitRect.left = 0
			splitRect.top = split.m_splitter.m_location.y
			splitRect.right = width
			splitRect.bottom = splitRect.top + splitterSize.cy
		elif (split.m_splitMode == "percentsize"):
			splitRect.left = 0
			if(split.m_splitPercent == -1):
				split.m_splitPercent = split.m_splitter.m_location.y / split.m_oldSize.cy
			splitRect.top = height * split.m_splitPercent
			splitRect.right = width
			splitRect.bottom = splitRect.top + splitterSize.cy
		fRect.left = 0
		fRect.top = 0
		fRect.right = width
		fRect.bottom = splitRect.top
		sRect.left = 0
		sRect.top = splitRect.bottom
		sRect.right = width
		sRect.bottom = height
	if(split.m_splitter.m_visible):
		spRect = FCRect(split.m_splitter.m_location.x,  split.m_splitter.m_location.y, split.m_splitter.m_location.x + split.m_splitter.m_size.cx, split.m_splitter.m_location.y + split.m_splitter.m_size.cy)
		if (spRect.left != splitRect.left or spRect.top != splitRect.top or spRect.right != splitRect.right or spRect.bottom != splitRect.bottom):
			split.m_splitter.m_location = FCPoint(splitRect.left, splitRect.top)
			split.m_splitter.m_size = FCSize(splitRect.right - splitRect.left, splitRect.bottom - splitRect.top)
			reset = TRUE
	fcRect = FCRect(split.m_firstView.m_location.x,  split.m_firstView.m_location.y, split.m_firstView.m_location.x + split.m_firstView.m_size.cx, split.m_firstView.m_location.y + split.m_firstView.m_size.cy)
	if (fcRect.left != fRect.left or fcRect.top != fRect.top or fcRect.right != fRect.right or fcRect.bottom != fRect.bottom):
		reset = TRUE;
		split.m_firstView.m_location = FCPoint(fRect.left, fRect.top)
		split.m_firstView.m_size = FCSize(fRect.right - fRect.left, fRect.bottom - fRect.top)
	scRect = FCRect(split.m_secondView.m_location.x,  split.m_secondView.m_location.y, split.m_secondView.m_location.x + split.m_secondView.m_size.cx, split.m_secondView.m_location.y + split.m_secondView.m_size.cy)
	if (scRect.left != sRect.left or scRect.top != sRect.top or scRect.right != sRect.right or scRect.bottom != sRect.bottom):
		reset = TRUE;
		split.m_secondView.m_location = FCPoint(sRect.left, sRect.top)
		split.m_secondView.m_size = FCSize(sRect.right - sRect.left, sRect.bottom - sRect.top)
	split.m_oldSize = FCSize(width, height)
	return reset

#表格的鼠标滚轮方法 
#grid:表格 
#delta:滚轮值
def mouseWheelGrid(grid, delta):
	oldScrollV = grid.m_scrollV;
	if (delta > 0):
		oldScrollV -= grid.m_rowHeight
	elif (delta < 0):
		oldScrollV += grid.m_rowHeight
	contentHeight = getGridContentHeight(grid)
	if (contentHeight < grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize):
		grid.m_scrollV = 0
	else:
		if (oldScrollV < 0):
			oldScrollV = 0
		elif (oldScrollV > contentHeight - grid.m_size.cy + grid.m_headerHeight + grid.m_scrollSize):
		    oldScrollV = contentHeight - grid.m_size.cy + grid.m_headerHeight + grid.m_scrollSize
		grid.m_scrollV = oldScrollV

#绘制单元格 
#grid:表格 
#row:行 
#column:列 
#cell:单元格
#paint:绘图对象 
#left:左侧坐标 
#top:上方坐标 
#right:右侧坐标 
#bottom:下方坐标
def drawGridCell(grid, row, column, cell, paint, left, top, right, bottom):
	if (cell.m_backColor != "none"):
		paint.fillRect(cell.m_backColor, left, top, right, bottom)
	if(row.m_selected):
		if(grid.m_seletedRowColor != "none"):
			paint.fillRect(grid.m_seletedRowColor, left, top, right, bottom)
	if (cell.m_borderColor != "none"):
		paint.drawRect(cell.m_borderColor, 1, 0, left, top, right, bottom)
	if (cell.m_value != None):
		tSize = paint.textSize(str(cell.m_value), cell.m_font)
		paint.drawText(str(cell.m_value), cell.m_textColor, cell.m_font, left + 2, top + grid.m_rowHeight / 2 - tSize.cy / 2)
		#if (tSize.cx > column.m_width):
			#paint.drawTextAutoEllipsis(str(cell.m_value), cell.m_textColor, cell.m_font, left + 2, top + grid.m_rowHeight / 2, left + 2 + column.m_width, top + grid.m_rowHeight / 2)
		#else:
			

#获取内容的宽度 
#grid:表格
def getGridContentWidth(grid):
	cWidth = 0
	for column in grid.m_columns:
		if (column.m_visible):
			cWidth += column.m_width
	return cWidth

#获取内容的高度 
#grid:表格
def getGridContentHeight(grid):
	cHeight = 0
	for row in grid.m_rows:
		if (row.m_visible):
			cHeight += grid.m_rowHeight
	return cHeight

#绘制列 
#grid:表格 
#column:列
#paint:绘图对象 
#left:左侧坐标 
#top:上方坐标 
#right:右侧坐标 
#bottom:下方坐标
def drawGridColumn(grid, column, paint, left, top, right, bottom):
	tSize = paint.textSize(column.m_text, column.m_font)
	if (column.m_backColor != "none"):
		paint.fillRect(column.m_backColor, left, top, right, bottom)
	if (column.m_borderColor != "none"):
		paint.drawRect(column.m_borderColor, 1, 0, left, top, right, bottom)
	paint.drawText(column.m_text, column.m_textColor, column.m_font, left + (column.m_width - tSize.cx) / 2, top + grid.m_headerHeight / 2 - tSize.cy / 2)
	if (column.m_sort == "asc"):
		cR = (bottom - top) / 4
		oX = right - cR * 2
		oY = top + (bottom - top) / 2
		drawPoints = []
		drawPoints.append((oX, oY - cR))
		drawPoints.append((oX - cR, oY + cR))
		drawPoints.append((oX + cR, oY + cR))
		paint.fillPolygon(column.m_textColor, drawPoints)
	elif (column.m_sort == "desc"):
		cR = (bottom - top) / 4
		oX = right - cR * 2
		oY = top + (bottom - top) / 2
		drawPoints = []
		drawPoints.append((oX, oY + cR))
		drawPoints.append((oX - cR, oY - cR))
		drawPoints.append((oX + cR, oY - cR))
		paint.fillPolygon(column.m_textColor, drawPoints)
	
	

m_paintGridCellCallBack = None #绘制单元格回调
m_paintGridColumnCallBack = None #绘制列头的回调
m_clickGridCellCallBack = None #点击单元格的回调
m_clickGridColumnCallBack = None #点击列头的回调

#绘制表格 
#grid:表格
#paint:绘图对象 
#clipRect:裁剪区域
def drawGrid(grid, paint, clipRect):
	cLeft = -grid.m_scrollH
	cTop = -grid.m_scrollV + grid.m_headerHeight
	colLeft = 0
	for i in range(0, len(grid.m_columns)):
		column = grid.m_columns[i]
		colRect = FCRect(colLeft, 0, colLeft + grid.m_columns[i].m_width, grid.m_headerHeight)
		column.m_bounds = colRect
		column.m_index = i
		colLeft += column.m_width
	for i in range(0, len(grid.m_rows)):
		row = grid.m_rows[i]
		if(row.m_visible):
			rTop = cTop
			rBottom = cTop + grid.m_rowHeight
			if (rBottom >= 0 and cTop <= grid.m_size.cy):
				for j in range(0, len(row.m_cells)):
					cell = row.m_cells[j]
					gridColumn = cell.m_column;
					if (gridColumn == None):
						gridColumn = grid.m_columns[j]
					if (gridColumn.m_visible):
						if (gridColumn.m_frozen == FALSE):
							cellWidth = gridColumn.m_width
							colSpan = cell.m_colSpan
							if (colSpan > 1):
								for n in range(1,colSpan):
									spanColumn = grid.m_columns[gridColumn.m_index + n]
									if (spanColumn != None and spanColumn.m_visible):
										cellWidth += spanColumn.m_width
							cellHeight = grid.m_rowHeight
							rowSpan = cell.m_rowSpan
							if (rowSpan > 1):
								for n in range(1,rowSpan):
									spanRow = grid.m_rows[i + n]
									if (spanRow != None and spanRow.m_visible):
										cellHeight += grid.m_rowHeight
							cRect = FCRect(gridColumn.m_bounds.left - grid.m_scrollH, rTop, gridColumn.m_bounds.left + cellWidth - grid.m_scrollH, rTop + cellHeight)
							if (cRect.right >= 0 and cRect.left < grid.m_size.cx):
								if(m_paintGridCellCallBack != None):
									m_paintGridCellCallBack(grid, row, gridColumn, cell, paint, cRect.left, cRect.top, cRect.right, cRect.bottom)
								else:
									drawGridCell(grid, row, gridColumn, cell, paint, cRect.left, cRect.top, cRect.right, cRect.bottom)
			if (rBottom >= 0 and cTop <= grid.m_size.cy):
				for j in range(0, len(row.m_cells)):
					cell = row.m_cells[j]
					gridColumn = cell.m_column;
					if (gridColumn == None):
						gridColumn = grid.m_columns[j]
					if (gridColumn.m_visible):
						if (gridColumn.m_frozen):
							cellWidth = gridColumn.m_width
							colSpan = cell.m_colSpan
							if (colSpan > 1):
								for n in range(1,colSpan):
									spanColumn = grid.m_columns[gridColumn.m_index + n]
									if (spanColumn != None and spanColumn.m_visible):
										cellWidth += spanColumn.m_width
							cellHeight = grid.m_rowHeight
							rowSpan = cell.m_rowSpan
							if (rowSpan > 1):
								for n in range(1,rowSpan):
									spanRow = grid.m_rows[i + n]
									if (spanRow != None and spanRow.m_visible):
										cellHeight += grid.m_rowHeight
							cRect = FCRect(gridColumn.m_bounds.left, rTop, gridColumn.m_bounds.left + cellWidth, rTop + cellHeight)
							if (cRect.right >= 0 and cRect.left < grid.m_size.cx):
								if(m_paintGridCellCallBack != None):
									m_paintGridCellCallBack(grid, row, gridColumn, cell, paint, cRect.left, cRect.top, cRect.right, cRect.bottom)
								else:
									drawGridCell(grid, row, gridColumn, cell, paint, cRect.left, cRect.top, cRect.right, cRect.bottom)
			if (cTop > grid.m_size.cy):
				break;
			cTop += grid.m_rowHeight
	if (grid.m_headerHeight > 0):
		for gridColumn in grid.m_columns:
			if (gridColumn.m_visible):
				if (gridColumn.m_frozen == FALSE):
					if(m_paintGridColumnCallBack != None):
						m_paintGridColumnCallBack(grid, gridColumn, paint, cLeft, 0, cLeft + gridColumn.m_width, grid.m_headerHeight)
					else:
						drawGridColumn(grid, gridColumn, paint, cLeft, 0, cLeft + gridColumn.m_width, grid.m_headerHeight)
				cLeft += gridColumn.m_width
		cLeft = 0;
		for gridColumn in grid.m_columns:
			if (gridColumn.m_visible):
				if (gridColumn.m_frozen):
					if(m_paintGridColumnCallBack != None):
						m_paintGridColumnCallBack(grid, gridColumn, paint, cLeft, 0, cLeft + gridColumn.m_width, grid.m_headerHeight)
					else:
						drawGridColumn(grid, gridColumn, paint, cLeft, 0, cLeft + gridColumn.m_width, grid.m_headerHeight)
				cLeft += gridColumn.m_width

#绘制表格的滚动条 
#grid:表格 
#paint:绘图对象
#clipRect:裁剪区域
def drawGridScrollBar(grid, paint, clipRect):
	if (grid.m_showHScrollBar):
		contentWidth = getGridContentWidth(grid)
		if (contentWidth > grid.m_size.cx):
			sLeft = grid.m_scrollH / contentWidth * grid.m_size.cx
			sRight = (grid.m_scrollH + grid.m_size.cx) / contentWidth * grid.m_size.cx
			if (sRight - sLeft < grid.m_scrollSize):
				sRight = sLeft + grid.m_scrollSize
			paint.fillRect(grid.m_scrollBarColor, sLeft, grid.m_size.cy - grid.m_scrollSize, sRight, grid.m_size.cy)
	if(grid.m_showVScrollBar):
		contentHeight = getGridContentHeight(grid)
		if (contentHeight > grid.m_size.cy - grid.m_headerHeight):
			sTop = grid.m_headerHeight + grid.m_scrollV / contentHeight * (grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize)
			sBottom = sTop + ((grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize)) / contentHeight * (grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize)
			if (sBottom - sTop < grid.m_scrollSize):
				sBottom = sTop + grid.m_scrollSize
			paint.fillRect(grid.m_scrollBarColor, grid.m_size.cx - grid.m_scrollSize, sTop, grid.m_size.cx, sBottom)

#表格的鼠标移动方法 
#grid: 表格 
#firstTouch:是否第一次触摸 
#secondTouch:是否第二次触摸 
#firstPoint:第一次触摸的坐标 
#secondPoint:第二次触摸的坐标
def mouseMoveGrid(grid, firstTouch, secondTouch, firstPoint, secondPoint):
	if (firstTouch):
		mp = firstPoint;
		if (grid.m_showHScrollBar or grid.m_showVScrollBar):
			if (grid.m_downScrollHButton):
				contentWidth = getGridContentWidth(grid)
				subX = (mp.x - grid.m_startPoint.x) / grid.m_size.cx * contentWidth
				newScrollH = grid.m_startScrollH + subX
				if (newScrollH < 0):
					newScrollH = 0
				elif (newScrollH > contentWidth - grid.m_size.cx):
					newScrollH = contentWidth - grid.m_size.cx
				grid.m_scrollH = newScrollH
				m_cancelClick = TRUE
				return
			elif(grid.m_downScrollVButton):
				contentHeight = getGridContentHeight(grid)
				subY = (mp.y - grid.m_startPoint.y) / (grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize) * contentHeight
				newScrollV = grid.m_startScrollV + subY
				if (newScrollV < 0):
					newScrollV = 0
				elif (newScrollV > contentHeight - (grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize)):
					newScrollV = contentHeight - (grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize)
				grid.m_scrollV = newScrollV
				m_cancelClick = TRUE
				return
		if (grid.m_allowDragScroll):
			contentWidth = getGridContentWidth(grid)
			if (contentWidth > grid.m_size.cx - grid.m_scrollSize):
				subX = grid.m_startPoint.x - mp.x
				newScrollH = grid.m_startScrollH + subX
				if (newScrollH < 0):
					newScrollH = 0
				elif (newScrollH > contentWidth - grid.m_size.cx):
					newScrollH = contentWidth - grid.m_size.cx
				grid.m_scrollH = newScrollH
				if(abs(subX) > 5):
				    m_cancelClick = TRUE
			contentHeight = getGridContentHeight(grid)
			if (contentHeight > grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize):
				subY = grid.m_startPoint.y - mp.y
				newScrollV = grid.m_startScrollV + subY
				if (newScrollV < 0):
					newScrollV = 0
				elif (newScrollV > contentHeight - (grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize)):
					newScrollV = contentHeight - (grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize)
				grid.m_scrollV = newScrollV
				if(abs(subY) > 5):
				    m_cancelClick = TRUE

#表格的鼠标按下方法 
#grid: 表格 
#firstTouch:是否第一次触摸 
#secondTouch:是否第二次触摸 
#firstPoint:第一次触摸的坐标 
#secondPoint:第二次触摸的坐标
def mouseDownGrid(grid, firstTouch, secondTouch, firstPoint, secondPoint):
	mp = firstPoint
	grid.m_startPoint = mp
	grid.m_downScrollHButton = FALSE
	grid.m_downScrollVButton = FALSE
	if (grid.m_showHScrollBar):
		contentWidth = getGridContentWidth(grid)
		if (contentWidth > grid.m_size.cx - grid.m_scrollSize):
			sLeft = grid.m_scrollH / contentWidth * grid.m_size.cx
			sRight = (grid.m_scrollH + grid.m_size.cx) / contentWidth * grid.m_size.cx
			if (sRight - sLeft < grid.m_scrollSize):
				sRight = sLeft + grid.m_scrollSize
			if (mp.x >= sLeft and mp.x <= sRight and mp.y >= grid.m_size.cy - grid.m_scrollSize and mp.y <= grid.m_size.cy):
				grid.m_downScrollHButton = TRUE
				grid.m_startScrollH = grid.m_scrollH
				return
	if(grid.m_showVScrollBar):
		contentHeight = getGridContentHeight(grid)
		if (contentHeight > grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize):
			sTop = grid.m_headerHeight + grid.m_scrollV / contentHeight * (grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize)
			sBottom = grid.m_headerHeight + (grid.m_scrollV + (grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize)) / contentHeight * (grid.m_size.cy - grid.m_headerHeight - grid.m_scrollSize)
			if (sBottom - sTop < grid.m_scrollSize):
				sBottom = sTop + grid.m_scrollSize
			if (mp.x >= grid.m_size.cx - grid.m_scrollSize and mp.x <= grid.m_size.cx and mp.y >= sTop and mp.y <= sBottom):
				grid.m_downScrollVButton = TRUE
				grid.m_startScrollV = grid.m_scrollV
				return
	if (grid.m_allowDragScroll):
		grid.m_startScrollH = grid.m_scrollH
		grid.m_startScrollV = grid.m_scrollV

#表格的鼠标抬起方法 
#grid: 表格 
#firstTouch:是否第一次触摸
#secondTouch:是否第二次触摸 
#firstPoint:第一次触摸的坐标 
#secondPoint:第二次触摸的坐标
def mouseUpGrid(grid, firstTouch, secondTouch, firstPoint, secondPoint):
	grid.m_downScrollHButton = FALSE
	grid.m_downScrollVButton = FALSE
	if(m_cancelClick):
	    return
	cLeft = -grid.m_scrollH
	cTop = -grid.m_scrollV + grid.m_headerHeight
	colLeft = 0
	for i in range(0, len(grid.m_columns)):
		column = grid.m_columns[i]
		colRect = FCRect(colLeft, 0, colLeft + grid.m_columns[i].m_width, grid.m_headerHeight)
		column.m_bounds = colRect
		column.m_index = i
		colLeft += column.m_width
	for i in range(0, len(grid.m_rows)):
		row = grid.m_rows[i]
		if(row.m_visible):
			rTop = cTop
			rBottom = cTop + grid.m_rowHeight
			if (rBottom >= 0 and cTop <= grid.m_size.cy):
				for j in range(0, len(row.m_cells)):
					cell = row.m_cells[j]
					gridColumn = cell.m_column;
					if (gridColumn == None):
						gridColumn = grid.m_columns[j]
					if (gridColumn.m_visible):
						if (gridColumn.m_frozen == FALSE):
							cellWidth = gridColumn.m_width
							colSpan = cell.m_colSpan
							if (colSpan > 1):
								for n in range(1,colSpan):
									spanColumn = grid.m_columns[gridColumn.m_index + n]
									if (spanColumn != None and spanColumn.m_visible):
										cellWidth += spanColumn.m_width
							cellHeight = grid.m_rowHeight
							rowSpan = cell.m_rowSpan
							if (rowSpan > 1):
								for n in range(1,rowSpan):
									spanRow = grid.m_rows[i + n]
									if (spanRow != None and spanRow.m_visible):
										cellHeight += grid.m_rowHeight
							cRect = FCRect(gridColumn.m_bounds.left - grid.m_scrollH, rTop, gridColumn.m_bounds.left + cellWidth - grid.m_scrollH, rTop + cellHeight)
							if (cRect.right >= 0 and cRect.left < grid.m_size.cx):
								if(firstPoint.x >= cRect.left and firstPoint.x <= cRect.right and firstPoint.y >= cRect.top and firstPoint.y <= cRect.bottom):
									for subRow in grid.m_rows:
										if(subRow == row):
											subRow.m_selected = TRUE
										else:
											subRow.m_selected = FALSE
									if(m_clickGridCellCallBack != None):
										m_clickGridCellCallBack(grid, row, gridColumn, cell, firstTouch, secondTouch, firstPoint, secondPoint)
									return;
			if (rBottom >= 0 and cTop <= grid.m_size.cy):
				for j in range(0, len(row.m_cells)):
					cell = row.m_cells[j]
					gridColumn = cell.m_column;
					if (gridColumn == None):
						gridColumn = grid.m_columns[j]
					if (gridColumn.m_visible):
						if (gridColumn.m_frozen):
							cellWidth = gridColumn.m_width
							colSpan = cell.m_colSpan
							if (colSpan > 1):
								for n in range(1,colSpan):
									spanColumn = grid.m_columns[gridColumn.m_index + n]
									if (spanColumn != None and spanColumn.m_visible):
										cellWidth += spanColumn.m_width
							cellHeight = grid.m_rowHeight
							rowSpan = cell.m_rowSpan
							if (rowSpan > 1):
								for n in range(1,rowSpan):
									spanRow = grid.m_rows[i + n]
									if (spanRow != None and spanRow.m_visible):
										cellHeight += grid.m_rowHeight
							cRect = FCRect(gridColumn.m_bounds.left, rTop, gridColumn.m_bounds.left + cellWidth, rTop + cellHeight)
							if (cRect.right >= 0 and cRect.left < grid.m_size.cx):
								if(firstPoint.x >= cRect.left and firstPoint.x <= cRect.right and firstPoint.y >= cRect.top and firstPoint.y <= cRect.bottom):
									for subRow in grid.m_rows:
										if(subRow == row):
											subRow.m_selected = TRUE
										else:
											subRow.m_selected = FALSE
									if(m_clickGridCellCallBack != None):
										m_clickGridCellCallBack(grid, row, gridColumn, cell, firstTouch, secondTouch, firstPoint, secondPoint)
									return
			if (cTop > grid.m_size.cy):
				break;
			cTop += grid.m_rowHeight
	if (grid.m_headerHeight > 0 and firstPoint.y <= grid.m_headerHeight):
		for gridColumn in grid.m_columns:
			if (gridColumn.m_visible):
				if (gridColumn.m_frozen):
					if(firstPoint.x >= cLeft and firstPoint.x <= cLeft + gridColumn.m_width):
						for j in range(0, len(grid.m_columns)):
							tColumn = grid.m_columns[j]
							if (tColumn == gridColumn):
								if (tColumn.m_allowSort):
									for r in range(0, len(grid.m_rows)):
										if(len(grid.m_rows[r].m_cells) > j):
											grid.m_rows[r].m_key = grid.m_rows[r].m_cells[j].m_value
									if (tColumn.m_sort == "none" or tColumn.m_sort == "desc"):
										tColumn.m_sort = "asc"
										grid.m_rows = sorted(grid.m_rows, key=attrgetter('m_key'), reverse=False)
									else:
										tColumn.m_sort = "desc"
										grid.m_rows = sorted(grid.m_rows, key=attrgetter('m_key'), reverse=True)
								else:
									tColumn.m_sort = "none"
							else:
								tColumn.m_sort = "none"
						if(m_clickGridColumnCallBack != None):
							m_clickGridColumnCallBack(grid, gridColumn, firstTouch, secondTouch, firstPoint, secondPoint)
						return
				cLeft += gridColumn.m_width
		cLeft = 0;
		for gridColumn in grid.m_columns:
			if (gridColumn.m_visible):
				if (gridColumn.m_frozen == FALSE):
					if(firstPoint.x >= cLeft and firstPoint.x <= cLeft + gridColumn.m_width):
						for j in range(0, len(grid.m_columns)):
							tColumn = grid.m_columns[j]
							if (tColumn == gridColumn):
								if (tColumn.m_allowSort):
									for r in range(0, len(grid.m_rows)):
										if(len(grid.m_rows[r].m_cells) > j):
											grid.m_rows[r].m_key = grid.m_rows[r].m_cells[j].m_value
									if (tColumn.m_sort == "none" or tColumn.m_sort == "desc"):
										tColumn.m_sort = "asc"
										grid.m_rows = sorted(grid.m_rows, key=attrgetter('m_key'), reverse=False)
									else:
										tColumn.m_sort = "desc"
										grid.m_rows = sorted(grid.m_rows, key=attrgetter('m_key'), reverse=True)
								else:
									tColumn.m_sort = "none"
							else:
								tColumn.m_sort = "none"
						if(m_clickGridColumnCallBack != None):
							m_clickGridColumnCallBack(grid, gridColumn, firstTouch, secondTouch, firstPoint, secondPoint)
						return
				cLeft += gridColumn.m_width

#获取内容的宽度
#tree:树
def getTreeContentWidth(tree):
	cWidth = 0
	for column in tree.m_columns:
		if (column.m_visible):
			cWidth += column.m_width
	return cWidth

#获取内容的高度
#tree:树
def getTreeContentHeight(tree):
	cHeight = 0;
	for row in tree.m_rows:
		if (row.m_visible):
			cHeight += tree.m_rowHeight
	return cHeight

#绘制滚动条
#tree:树
#paint:绘图对象
#clipRect:裁剪区域
def drawTreeScrollBar(tree, paint, clipRect):
	if (tree.m_showHScrollBar):
		contentWidth = getTreeContentWidth(tree)
		if (contentWidth > tree.m_size.cx):
			sLeft = tree.m_scrollH / contentWidth * tree.m_size.cx
			sRight = (tree.m_scrollH + tree.m_size.cx) / contentWidth * tree.m_size.cx
			if (sRight - sLeft < tree.m_scrollSize):
				sRight = sLeft + tree.m_scrollSize
			paint.fillRect(tree.m_scrollBarColor, sLeft, tree.m_size.cy - tree.m_scrollSize, sRight, tree.m_size.cy)
	if(tree.m_showVScrollBar):
		contentHeight = getTreeContentHeight(tree)	
		if (contentHeight > tree.m_size.cy):
			sTop = tree.m_headerHeight + tree.m_scrollV / contentHeight * (tree.m_size.cy - tree.m_headerHeight - tree.m_scrollSize)
			sBottom = sTop + ((tree.m_size.cy - tree.m_headerHeight)) / contentHeight * (tree.m_size.cy - tree.m_headerHeight - tree.m_scrollSize)
			if (sBottom - sTop < tree.m_scrollSize):
				sBottom = sTop + tree.m_scrollSize
			paint.fillRect(tree.m_scrollBarColor, tree.m_size.cx - tree.m_scrollSize, sTop, tree.m_size.cx, sBottom)

#绘制单元格
#tree:树
#row:行
#column:列
#node:节点
#paint:绘图对象
#left:左侧坐标
#top:上方坐标
#right:右侧坐标
#bottom:下方坐标
def drawTreeNode(tree, row, column, node, paint, left, top, right, bottom):
	if (node.m_backColor != "none"):
		paint.fillRect(node.m_backColor, left, top, right, bottom)
	if (node.m_value != None):
		tSize = paint.textSize(str(node.m_value), node.m_font)
		tLeft = left + 2 + getTotalIndent(node)
		wLeft = tLeft;
		cR = tree.m_checkBoxWidth / 3
		if (tree.m_showCheckBox):
			wLeft += tree.m_checkBoxWidth;
			if (node.m_checked):
				paint.fillRect(node.m_textColor, tLeft + (tree.m_checkBoxWidth - cR) / 2, top + (tree.m_rowHeight - cR) / 2, tLeft + (tree.m_checkBoxWidth + cR) / 2, top + (tree.m_rowHeight + cR) / 2)
			else:
				paint.drawRect(node.m_textColor, 1, 0, tLeft + (tree.m_checkBoxWidth - cR) / 2, top + (tree.m_rowHeight - cR) / 2, tLeft + (tree.m_checkBoxWidth + cR) / 2, top + (tree.m_rowHeight + cR) / 2)

		if (len(node.m_childNodes) > 0):
			drawPoints = []
			if (node.m_collapsed):
				drawPoints.append((wLeft + (tree.m_collapsedWidth + cR) / 2, top + tree.m_rowHeight / 2))
				drawPoints.append((wLeft + (tree.m_collapsedWidth - cR) / 2, top + (tree.m_rowHeight - cR) / 2))
				drawPoints.append((wLeft + (tree.m_collapsedWidth - cR) / 2, top + (tree.m_rowHeight + cR) / 2))
			else:
				drawPoints.append((wLeft + (tree.m_collapsedWidth - cR) / 2, top + (tree.m_rowHeight - cR) / 2))
				drawPoints.append((wLeft + (tree.m_collapsedWidth + cR) / 2, top + (tree.m_rowHeight - cR) / 2))
				drawPoints.append((wLeft + tree.m_collapsedWidth / 2, top + (tree.m_rowHeight + cR) / 2))
			paint.fillPolygon(node.m_textColor, drawPoints)
			wLeft += tree.m_collapsedWidth
		if (tSize.cx > column.m_width):
			paint.drawTextAutoEllipsis(str(node.m_value), node.m_textColor, node.m_font, wLeft, top + tree.m_rowHeight / 2, wLeft + column.m_width, top + tree.m_rowHeight / 2)
		else:
			paint.drawText(str(node.m_value), node.m_textColor, node.m_font, wLeft, top + tree.m_rowHeight / 2 - tSize.cy / 2)

#更新行的索引
#tree:树
def updateTreeRowIndex(tree):
	for i in range(0,len(tree.m_rows)):
		tree.m_rows[i].m_index = i

m_paintTreeNodeCallBack = None #绘图树节点的回调
m_clickTreeNode = None #点击树节点的事件

#绘制树
#tree:树
#paint:绘图对象
#clipRect:裁剪区域
def drawTree(tree, paint, clipRect):
	cLeft = -tree.m_scrollH
	cTop = -tree.m_scrollV + tree.m_headerHeight
	colLeft = 0
	for i in range(0,len(tree.m_columns)):
		colRect = FCRect(colLeft, 0, colLeft + tree.m_columns[i].m_width, tree.m_headerHeight)
		tree.m_columns[i].m_bounds = colRect
		tree.m_columns[i].m_index = i
		colLeft += tree.m_columns[i].m_width
	updateTreeRowIndex(tree);
	for i in range(0,len(tree.m_rows)):
		row = tree.m_rows[i]
		if (row.m_visible):
			rTop = cTop
			rBottom = cTop + tree.m_rowHeight
			if (rBottom >= 0 and cTop <= tree.m_size.cy):
				for j in range(0,len(row.m_cells)):
					node = row.m_cells[j]
					treeColumn = node.m_column
					if (treeColumn == None):
						treeColumn = tree.m_columns[j]
					if (treeColumn.m_visible):
						nodeWidth = treeColumn.m_width
						nodeHeight = tree.m_rowHeight
						cRect = FCRect(treeColumn.m_bounds.left - tree.m_scrollH, rTop, treeColumn.m_bounds.left + nodeWidth - tree.m_scrollH, rTop + nodeHeight)
						if (cRect.right >= 0 and cRect.left < tree.m_size.cx):
							if(m_paintTreeNodeCallBack != None):
								m_paintTreeNodeCallBack(tree, row, treeColumn, node, paint, cRect.left, cRect.top, cRect.right, cRect.bottom);
							else:
								drawTreeNode(tree, row, treeColumn, node, paint, cRect.left, cRect.top, cRect.right, cRect.bottom);
			if (cTop > tree.m_size.cy):
				break
			cTop += tree.m_rowHeight

#获取最后一行的索引 
#node:树节点
def getTreeLastNodeRowIndex(node):
	rowIndex = node.m_row.m_index
	for i in range(0,len(node.m_childNodes)):
		rIndex = getTreeLastNodeRowIndex(node.m_childNodes[i])
		if (rowIndex < rIndex):
			rowIndex = rIndex
	return rowIndex

#添加节点
#tree:树
#node:要添加的节点
#parentNode:父节点
def appendTreeNode(tree, node, parentNode):
	if (parentNode == None):
		newRow = FCTreeRow()
		tree.m_rows.append(newRow)
		node.m_row = newRow
		newRow.m_cells.append(node)
		tree.m_childNodes.append(node)
	else:
		newRow = FCTreeRow();
		if (len(parentNode.m_childNodes) == 0):
			tree.m_rows.insert(parentNode.m_row.m_index + 1, newRow)
		else:
			tree.m_rows.insert(getTreeLastNodeRowIndex(parentNode) + 1, newRow)
		node.m_parentNode = parentNode
		node.m_indent = tree.m_indent
		node.m_row = newRow
		newRow.m_cells.append(node)
		parentNode.m_childNodes.append(node)
		if (parentNode.m_collapsed):
			newRow.m_visible = FALSE
	updateTreeRowIndex(tree)

#移除节点
#tree:树
#node:要添加的节点
def removeTreeNode(tree, node):
	if (node.m_parentNode == None):
		nodesSize = len(tree.m_childNodes)
		for i in range(0,nodesSize):
			if (tree.m_childNodes[i] == node):
				tree.m_childNodes.pop(i)
				break
	else:
		nodesSize = len(node.m_parentNode.m_childNodes)
		for i in range(0,nodesSize):
			if (node.m_parentNode.m_childNodes[i] == node):
				node.m_parentNode.m_childNodes.pop(i)
				break
	tree.m_rows.pop(node.m_row.m_index)
	updateTreeRowIndex(tree)

#展开或折叠节点
#node:节点
#visible:是否可见
def hideOrShowTreeNode(node, visible):
	if (len(node.m_childNodes) > 0):
		for i in range(0,len(node.m_childNodes)):
			node.m_childNodes[i].m_row.m_visible = visible
			hideOrShowTreeNode(node.m_childNodes[i], visible)

#展开或折叠节点
#node:节点
#checked:是否选中
def checkOrUnCheckTreeNode(node, checked):
	node.m_checked = checked
	if (len(node.m_childNodes) > 0):
		for i in range(0,len(node.m_childNodes)):
			checkOrUnCheckTreeNode(node.m_childNodes[i], checked)

#树的鼠标滚轮方法
#tree:树
#delta:滚轮值
def mouseWheelTree(tree, delta):
	oldScrollV = tree.m_scrollV
	if (delta > 0):
		oldScrollV -= tree.m_rowHeight
	elif (delta < 0):
		oldScrollV += tree.m_rowHeight
	contentHeight = getTreeContentHeight(tree)
	if (contentHeight < tree.m_size.cy):
		tree.m_scrollV = 0
	else:
		if (oldScrollV < 0):
			oldScrollV = 0
		elif (oldScrollV > contentHeight - tree.m_size.cy + tree.m_headerHeight + tree.m_scrollSize):
		    oldScrollV = contentHeight - tree.m_size.cy + tree.m_headerHeight + tree.m_scrollSize
		tree.m_scrollV = oldScrollV

#树的鼠标移动方法
#tree: 树
#firstTouch:是否第一次触摸
#secondTouch:是否第二次触摸
#firstPoint:第一次触摸的坐标
#secondPoint:第二次触摸的坐标
def mouseMoveTree(tree, firstTouch, secondTouch, firstPoint, secondPoint):
	if (firstTouch):
		mp = firstPoint;
		if (tree.m_showHScrollBar or tree.m_showVScrollBar):
			if (tree.m_downScrollHButton):
				contentWidth = getTreeContentWidth(tree)
				subX = (mp.x - tree.m_startPoint.x) / tree.m_size.cx * contentWidth
				newScrollH = tree.m_startScrollH + subX
				if (newScrollH < 0):
					newScrollH = 0
				elif(newScrollH > contentWidth - tree.m_size.cx):
					newScrollH = contentWidth - tree.m_size.cx
				tree.m_scrollH = newScrollH
				m_cancelClick = TRUE
				return
			elif (tree.m_downScrollVButton):
				contentHeight = getTreeContentHeight(tree)
				subY = (mp.y - tree.m_startPoint.y) / (tree.m_size.cy - tree.m_headerHeight - tree.m_scrollSize) * contentHeight
				newScrollV = tree.m_startScrollV + subY
				if (newScrollV < 0):
					newScrollV = 0
				elif (newScrollV > contentHeight - (tree.m_size.cy - tree.m_headerHeight - tree.m_scrollSize)):
					newScrollV = contentHeight - (tree.m_size.cy - tree.m_headerHeight - tree.m_scrollSize)
				tree.m_scrollV = newScrollV
				m_cancelClick = TRUE
				return
		if (tree.m_allowDragScroll):
			contentWidth = getTreeContentWidth(tree)
			if (contentWidth > tree.m_size.cx):
				subX = tree.m_startPoint.x - mp.x
				newScrollH = tree.m_startScrollH + subX
				if (newScrollH < 0):
					newScrollH = 0
				elif (newScrollH > contentWidth - tree.m_size.cx):
					newScrollH = contentWidth - tree.m_size.cx
				tree.m_scrollH = newScrollH
				if(abs(subX) > 5):
				    m_cancelClick = TRUE
			contentHeight = getTreeContentHeight(tree)
			if (contentHeight > tree.m_size.cy):
				subY = tree.m_startPoint.y - mp.y
				newScrollV = tree.m_startScrollV + subY
				if (newScrollV < 0):
					newScrollV = 0
				elif (newScrollV > contentHeight - (tree.m_size.cy - tree.m_headerHeight - tree.m_scrollSize)):
					newScrollV = contentHeight - (tree.m_size.cy - tree.m_headerHeight - tree.m_scrollSize)
				tree.m_scrollV = newScrollV
				if(abs(subY) > 5):
				    m_cancelClick = TRUE

#树的鼠标按下方法
#tree: 树
#firstTouch:是否第一次触摸
#secondTouch:是否第二次触摸
#firstPoint:第一次触摸的坐标
#secondPoint:第二次触摸的坐标
def mouseDownTree(tree, firstTouch, secondTouch, firstPoint, secondPoint):
	mp = firstPoint
	tree.m_startPoint = mp
	tree.m_downScrollHButton = FALSE
	tree.m_downScrollVButton = FALSE
	if (tree.m_showHScrollBar):
		contentWidth = getTreeContentWidth(tree)
		if (contentWidth > tree.m_size.cx):
			sLeft = tree.m_scrollH / contentWidth * tree.m_size.cx
			sRight = (tree.m_scrollH + tree.m_size.cx) / contentWidth * tree.m_size.cx
			if (sRight - sLeft < tree.m_scrollSize):
				sRight = sLeft + tree.m_scrollSize
			if (mp.x >= sLeft and mp.x <= sRight and mp.y >= tree.m_size.cy - tree.m_scrollSize and mp.y <= tree.m_size.cy):
				tree.m_downScrollHButton = TRUE
				tree.m_startScrollH = tree.m_scrollH
				return
	if (tree.m_showVScrollBar):
		contentHeight = getTreeContentHeight(tree)
		if (contentHeight > tree.m_size.cy):
			sTop = tree.m_headerHeight + tree.m_scrollV / contentHeight * (tree.m_size.cy - tree.m_headerHeight - tree.m_scrollSize)
			sBottom = tree.m_headerHeight + (tree.m_scrollV + (tree.m_size.cy - tree.m_headerHeight - tree.m_scrollSize)) / contentHeight * (tree.m_size.cy - tree.m_headerHeight - tree.m_scrollSize)
			if (sBottom - sTop < tree.m_scrollSize):
				sBottom = sTop + tree.m_scrollSize
			if (mp.x >= tree.m_size.cx - tree.m_scrollSize and mp.x <= tree.m_size.cx and mp.y >= sTop and mp.y <= sBottom):
				tree.m_downScrollVButton = TRUE
				tree.m_startScrollV = tree.m_scrollV
				return
	if (tree.m_allowDragScroll):
		tree.m_startScrollH = tree.m_scrollH
		tree.m_startScrollV = tree.m_scrollV

#获取总的偏移量
#node:树节点
def getTotalIndent(node):
	if (node.m_parentNode != None):
		return node.m_indent + getTotalIndent(node.m_parentNode)
	else:
		return node.m_indent

#树的鼠标抬起方法
#tree: 树
#firstTouch:是否第一次触摸
#secondTouch:是否第二次触摸
#firstPoint:第一次触摸的坐标
#secondPoint:第二次触摸的坐标
def mouseUpTree(tree, firstTouch, secondTouch, firstPoint, secondPoint):
	tree.m_downScrollHButton = FALSE
	tree.m_downScrollVButton = FALSE
	if(m_cancelClick):
	    return
	cLeft = -tree.m_scrollH
	cTop = -tree.m_scrollV + tree.m_headerHeight
	for i in range(0,len(tree.m_rows)):
		row = tree.m_rows[i]
		if (row.m_visible):
			if (firstPoint.y >= cTop and firstPoint.y <= cTop + tree.m_rowHeight):
				node = row.m_cells[0]
				tLeft = cLeft + 2 + getTotalIndent(node)
				wLeft = tLeft
				if (tree.m_showCheckBox):
					wLeft += tree.m_checkBoxWidth
					if (firstPoint.x < wLeft):
						if(node.m_checked):
							checkOrUnCheckTreeNode(node, FALSE)
						else:
							checkOrUnCheckTreeNode(node, TRUE)
						if(tree.m_paint):
							invalidateView(tree, tree.m_paint)
						break
				if (len(node.m_childNodes) > 0):
					wLeft += tree.m_collapsedWidth
					if (firstPoint.x < wLeft):
						if(node.m_collapsed):
							node.m_collapsed = FALSE
							hideOrShowTreeNode(node, TRUE)
						else:
							node.m_collapsed = TRUE
							hideOrShowTreeNode(node, FALSE)
						break
				if(m_clickTreeNode != None):
					m_clickTreeNode(tree, node, firstTouch, secondTouch, firstPoint, secondPoint)
			cTop += tree.m_rowHeight

m_k_Chart = 0
m_b_Chart = 0
m_oX_Chart = 0
m_oY_Chart = 0
m_r_Chart = 0
m_gridStep_Chart = 0 #网格计算临时变量
m_gridDigit_Chart = 0 #网格计算临时变量

#计算直线参数 
#mp:坐标 
#x1:横坐标1 
#y1:纵坐标1 
#x2:横坐标2 
#y2:纵坐标2 
#oX:坐标起始X 
#oY:坐标起始Y
def lineXY(x1, y1, x2, y2, oX, oY):
	global m_k_Chart
	global m_b_Chart
	m_k_Chart = 0
	m_b_Chart = 0
	if ((x1 - oX) != (x2 - oX)) :
		m_k_Chart = ((y2 - oY) - (y1 - oY)) / ((x2 - oX) - (x1 - oX))
		m_b_Chart = (y1 - oY) - m_k_Chart * (x1 - oX)

#判断是否选中直线 
#mp:坐标 
#x1:横坐标1 
#y1:纵坐标1 
#x2:横坐标2 
#y2:纵坐标2
def selectLine(mp, x1, y1, x2, y2):
    lineXY(x1, y1, x2, y2, 0, 0)
    if (m_k_Chart != 0 or m_b_Chart != 0):
        if (mp.y / (mp.x * m_k_Chart + m_b_Chart) >= 0.9 and mp.y / (mp.x * m_k_Chart + m_b_Chart) <= 1.1):
            return TRUE
    else:
        if (mp.x >= x1 - m_plotPointSize_Chart and mp.x <= x1 + m_plotPointSize_Chart):
            return TRUE
    return FALSE

#判断是否选中射线 
#mp:坐标 
#x1:横坐标1 
#y1:纵坐标1 
#x2:横坐标2 
#y2:纵坐标2
def selectRay(mp, x1, y1, x2, y2):
	lineXY(x1, y1, x2, y2, 0, 0)
	if (m_k_Chart != 0 or m_b_Chart != 0):
		if (mp.y / (mp.x * m_k_Chart + m_b_Chart) >= 0.9 and mp.y / (mp.x * m_k_Chart + m_b_Chart) <= 1.1):
			if (x1 >= x2):
				if (mp.x > x1 + m_plotPointSize_Chart):
					return FALSE
			elif (x1 < x2):
				if (mp.x < x1 - m_plotPointSize_Chart):
					return FALSE
			return TRUE;
	else:
		if (mp.x >= x1 - m_plotPointSize_Chart and mp.x <= x1 + m_plotPointSize_Chart):
			if (y1 >= y2):
				if (mp.y <= y1 - m_plotPointSize_Chart):
					return TRUE
			else:
				if (mp.y >= y1 - m_plotPointSize_Chart):
					return TRUE
	return FALSE

#判断是否选中线段 
#mp:坐标 
#x1:横坐标1 
#y1:纵坐标1 
#x2:横坐标2 
#y2:纵坐标2
def selectSegment(mp, x1, y1, x2, y2):
	lineXY(x1, y1, x2, y2, 0, 0)
	smallX = x2;
	if(x1 <= x2):
		smallX = x1
	smallY = y2;
	if(y1 <= y2):
		smallY = y1
	bigX = x2
	if(x1 > x2):
		bigX = x1
	bigY = y2;
	if(y1 > y2):
		bigY = y1
	if (mp.x >= smallX - 2 and mp.x <= bigX + 2 and mp.y >= smallY - 2 and mp.y <= bigY + 2):
		if (m_k_Chart != 0 or m_b_Chart != 0):
			if (mp.y / (mp.x * m_k_Chart + m_b_Chart) >= 0.9 and mp.y / (mp.x * m_k_Chart + m_b_Chart) <= 1.1):
				return TRUE
		else:
			if (mp.x >= x1 - m_plotPointSize_Chart and mp.x <= x1 + m_plotPointSize_Chart):
				return TRUE
	return FALSE;

# 根据三点计算圆心 
#x1:横坐标 
#y1:纵坐标1 
#x2:横坐标2 
#y2:纵坐标2 
#x3:横坐标3 
#y3:纵坐标3
def ellipseOR(x1, y1, x2, y2, x3, y3):
	global m_oX_Chart
	global m_oY_Chart
	global m_r_Chart
	m_oX_Chart = ((y3 - y1) * (y2 * y2 - y1 * y1 + x2 * x2 - x1 * x1) + (y2 - y1) * (y1 * y1 - y3 * y3 + x1 * x1 - x3 * x3)) / (2 * (x2 - x1) * (y3 - y1) - 2 * (x3 - x1) * (y2 - y1))
	m_oY_Chart = ((x3 - x1) * (x2 * x2 - x1 * x1 + y2 * y2 - y1 * y1) + (x2 - x1) * (x1 * x1 - x3 * x3 + y1 * y1 - y3 * y3)) / (2 * (y2 - y1) * (x3 - x1) - 2 * (y3 - y1) * (x2 - x1))
	m_r_Chart = math.sqrt((x1 - m_oX_Chart) * (x1 - m_oX_Chart) + (y1 - m_oY_Chart) * (y1 - m_oY_Chart))

#判断点是否在椭圆上
#x:横坐标 
#y:纵坐标 
#oX:坐标起始X 
#oY:坐标起始Y 
#a:椭圆参数a 
#b:椭圆参数b
def ellipseHasPoint(x, y, oX, oY, a, b):
	x -= oX
	y -= oY
	if (a == 0 and b == 0 and x == 0 and y == 0):
		return TRUE
	if (a == 0):
		if (x == 0 and y >= -b and y <= b):
			return FALSE
	if (b == 0):
		if (y == 0 and x >= -a and x <= a):
			return TRUE
	if a != 0 and b != 0:
		if ((x * x) / (a * a) + (y * y) / (b * b) >= 0.8 and (x * x) / (a * a) + (y * y) / (b * b) <= 1.2):
			return TRUE
	return FALSE

#计算线性回归 
#list:集合
def linearRegressionEquation(list):
	global m_k_Chart
	global m_b_Chart
	result = 0
	sumX = 0
	sumY = 0
	sumUp = 0
	sumDown = 0
	xAvg = 0
	yAvg = 0
	m_k_Chart = 0
	m_b_Chart = 0
	length = len(list)
	if(length > 1):
		for i in range(0, length):
			sumX += i + 1
			sumY += list[i]
		xAvg = sumX / length
		yAvg = sumY / length
		for i in range(0, length):
			sumUp += (i + 1 - xAvg) * (list[i] - yAvg)
			sumDown += (i + 1 - xAvg) * (i + 1 - xAvg)
		m_k_Chart = sumUp / sumDown
		m_b_Chart = yAvg - m_k_Chart * xAvg
	return result

#计算最大值 
#list:集合
def maxValue(list):
	length = len(list)
	max = 0
	for i in range(0, length):
		if (i == 0):
			max = list[i]
		else:
			if (max < list[i]):
				max = list[i]
	return max

#计算最小值 
#list:集合
def minValue(list):
    length = len(list)
    min = 0
    for i in range(0, length):
        if (i == 0):
            min = list[i]
        else:
            if (min > list[i]):
                min = list[i]
    return min

#计算平均值 
#list:集合
def avgValue(list):
	sum = 0
	length = len(list)
	if (length > 0):
		for i in range(0, length):
			sum += list[i]
		return sum / length
	return

m_x4_Chart = 0
m_y4_Chart = 0
	
#计算平行四边形参数 
#x1:横坐标1 
#y1:纵坐标1 
#x2:横坐标2 
#y2:纵坐标2 
#x3:横坐标3 
#y3:纵坐标3
def parallelogram(x1, y1, x2, y2, x3, y3):
	global m_x4_Chart
	global m_y4_Chart
	m_x4_Chart = x1 + x3 - x2
	m_y4_Chart = y1 + y3 - y2

#计算斐波那契数列 
#index:索引
def fibonacciValue(index):
	if (index < 1):
		return 0
	else:
		vList = []
		for i in range(0, index):
			vList.append(0)
		result = 0
		for i in range(0, index):
			if (i == 0 or i == 1):
				vList[i] = 1
			else:
				vList[i] = vList[i - 1] + vList[i - 2]
		result = vList[index - 1]
		return result

# 获取百分比线的刻度 
#y1: 纵坐标1 
#y2: 纵坐标2
def getPercentParams(y1, y2):
	y0 = 0
	y25 = 0
	y50 = 0
	y75 = 0
	y100 = 0
	y0 = y1;
	if(y1 <= y2):
		y25 = y1 + (y2 - y1) / 4.0
		y50 = y1 + (y2 - y1) / 2.0
		y75 = y1 + (y2 - y1) * 3.0 / 4.0
	else:
		y25 = y2 + (y1 - y2) * 3.0 / 4.0
		y50 = y2 + (y1 - y2) / 2.0
		y75 = y2 + (y1 - y2) / 4.0
	y100 = y2
	list = []
	list.append(y0)
	list.append(y25)
	list.append(y50)
	list.append(y75)
	list.append(y100)
	return list

m_x_Chart = 0
m_y_Chart = 0
m_w_Chart = 0
m_h_Chart = 0

#根据坐标计算矩形
#x1:横坐标1
#y1:纵坐标1
#x2:横坐标2
#y2:纵坐标2
def rectangleXYWH(x1, y1, x2, y2):
	global m_x_Chart
	global m_y_Chart
	global m_w_Chart
	global m_h_Chart
	m_x_Chart = x2
	if(x1 < x2):
		m_x_Chart = x1
	m_y_Chart = y2;
	if(y1 < y2):
		m_y_Chart = y1
	m_w_Chart = abs(x1 - x2)
	m_h_Chart = abs(y1 - y2)
	if (m_w_Chart <= 0):
		m_w_Chart = 4
	if (m_h_Chart <= 0):
		m_h_Chart = 4


#根据位置计算索引
#chart:K线
#mp:坐标
def getChartIndex(chart, mp):
	if (chart.m_data != None and len(chart.m_data) == 0):
		return -1
	if(mp.x <= 0):
		return 0
	intX = int(mp.x - chart.m_leftVScaleWidth - chart.m_hScalePixel)
	index = int(chart.m_firstVisibleIndex + intX / chart.m_hScalePixel)
	if(intX % chart.m_hScalePixel != 0):
		index = index + 1
	if(index < 0):
		 index = 0
	elif (chart.m_data and index > len(chart.m_data) - 1):
		index = len(chart.m_data) - 1
	return index

#获取最大显示记录条数
#chart:K线
#hScalePixel:间隔
#pureH:横向距离
def getChartMaxVisibleCount(chart, hScalePixel, pureH):
    count = int((pureH - hScalePixel) / hScalePixel)
    if(count < 0):
        count = 0
    return count

#获取K线层的高度
#chart:K线
def getCandleDivHeight(chart):
	height = chart.m_size.cy - chart.m_hScaleHeight
	if(height > 0):
		return height * chart.m_candleDivPercent
	else:
		return 0

#获取成交量层的高度
#chart:K线
def getVolDivHeight(chart):
	height = chart.m_size.cy - chart.m_hScaleHeight
	if(height > 0):
		return height * chart.m_volDivPercent
	else:
		return 0

#获取指标层的高度
#chart:K线
def getIndDivHeight(chart):
	height = chart.m_size.cy - chart.m_hScaleHeight
	if(height > 0):
		return height * chart.m_indDivPercent
	else:
		return 0

#获取指标层2的高度
#chart:K线
def getIndDivHeight2(chart):
	height = chart.m_size.cy - chart.m_hScaleHeight
	if(height > 0):
		return height * chart.m_indDivPercent2
	else:
		return 0

#获取横向工作区
#chart:K线
def getChartWorkAreaWidth(chart):
    return chart.m_size.cx - chart.m_leftVScaleWidth - chart.m_rightVScaleWidth - chart.m_rightSpace

#根据索引获取横坐标
#chart:K线
#index:索引
def getChartX(chart, index):
    return chart.m_leftVScaleWidth + (index - chart.m_firstVisibleIndex) * chart.m_hScalePixel + chart.m_hScalePixel

#根据日期获取索引
#chart:K线
#date:日期
def getChartIndexByDate(chart, date):
	index = -1
	for i in range(0, len(chart.m_data)):
		if(chart.m_data[i].m_date == date):
			index = i
			break
	return index

#根据索引获取日期
#chart:K线
#index:索引
def getChartDateByIndex(chart, index):
    date = ""
    if(index >= 0 and index < len(chart.m_data)):
        date = chart.m_data[index].m_date
    return date

#检查最后可见索引
#chart:K线
def checkChartLastVisibleIndex(chart):
    if (chart.m_lastVisibleIndex > len(chart.m_data) - 1):
        chart.m_lastVisibleIndex = len(chart.m_data) - 1
    if (len(chart.m_data) > 0):
        chart.m_lastVisibleKey = chart.m_data[chart.m_lastVisibleIndex].m_date
        if (chart.m_lastVisibleIndex == len(chart.m_data) - 1):
            chart.m_lastRecordIsVisible = TRUE
        else:
            chart.m_lastRecordIsVisible = FALSE
    else:
        chart.m_lastVisibleKey = 0
        chart.m_lastRecordIsVisible = TRUE

#自动设置首先可见和最后可见的记录号
#chart:K线
def resetChartVisibleRecord(chart):
    rowsCount = len(chart.m_data)
    workingAreaWidth = getChartWorkAreaWidth(chart)
    if (chart.m_autoFillHScale):
        if (workingAreaWidth > 0 and rowsCount > 0):
            chart.m_hScalePixel = workingAreaWidth / rowsCount
            chart.m_firstVisibleIndex = 0
            chart.m_lastVisibleIndex = rowsCount - 1
    else:
        maxVisibleRecord = getChartMaxVisibleCount(chart, chart.m_hScalePixel, workingAreaWidth)
        if (rowsCount == 0):
            chart.m_firstVisibleIndex = -1
            chart.m_lastVisibleIndex = -1
        else:
            if (rowsCount < maxVisibleRecord):
                chart.m_lastVisibleIndex = rowsCount - 1
                chart.m_firstVisibleIndex = 0
            else:
                if (chart.m_firstVisibleIndex != -1 and chart.m_lastVisibleIndex != -1 and chart.m_lastRecordIsVisible == FALSE):
                    index = getChartIndexByDate(chart, chart.m_lastVisibleKey)
                    if (index != -1):
                        chart.m_lastVisibleIndex = index
                    chart.m_firstVisibleIndex = chart.m_lastVisibleIndex - maxVisibleRecord + 1
                    if (chart.m_firstVisibleIndex < 0):
                        chart.m_firstVisibleIndex = 0
                        chart.m_lastVisibleIndex = chart.m_firstVisibleIndex + maxVisibleRecord
                        checkChartLastVisibleIndex(chart)
                else:
                    chart.m_lastVisibleIndex = rowsCount - 1
                    chart.m_firstVisibleIndex = chart.m_lastVisibleIndex - maxVisibleRecord + 1
                    if (chart.m_firstVisibleIndex > chart.m_lastVisibleIndex):
                        chart.m_firstVisibleIndex = chart.m_lastVisibleIndex

#设置可见索引
#chart:K线
#firstVisibleIndex:起始索引
#lastVisibleIndex:结束索引
def setChartVisibleIndex(chart, firstVisibleIndex, lastVisibleIndex):
    xScalePixel = getChartWorkAreaWidth(chart) / (lastVisibleIndex - firstVisibleIndex + 1)
    if (xScalePixel < 1000000):
        chart.m_firstVisibleIndex = firstVisibleIndex
        chart.m_lastVisibleIndex = lastVisibleIndex
        if (lastVisibleIndex != len(chart.m_data) - 1):
            chart.m_lastRecordIsVisible = FALSE
        else:
            chart.m_lastRecordIsVisible = TRUE
        chart.m_hScalePixel = xScalePixel
        checkChartLastVisibleIndex(chart)

#计算数值在层中的位置
#chart:K线
#divIndex:所在层
#chart:数值
def getChartY(chart, divIndex, value):
	if(divIndex == 0):
		if(chart.m_candleMax > chart.m_candleMin):
			cValue = value
			cMax = chart.m_candleMax
			cMin = chart.m_candleMin
			if(chart.m_vScaleType != "standard"):
				if (cValue > 0):
					cValue = log10(cValue)
				elif (cValue < 0):
					cValue = -log10(abs(cValue))
				if (cMax > 0):
					cMax = log10(cMax)
				elif(cMax < 0):
					cMax = -log10(abs(cMax))
				if (cMin > 0):
					cMin = log10(cMin)
				elif (cMin < 0):
					cMin = -log10(abs(cMin))
			rate = (cValue - cMin) / (cMax - cMin)
			divHeight = getCandleDivHeight(chart)
			return divHeight - chart.m_candlePaddingBottom - (divHeight - chart.m_candlePaddingTop - chart.m_candlePaddingBottom) * rate
		else:
			return 0
	elif(divIndex == 1):
		if(chart.m_volMax > chart.m_volMin):
			rate = (value - chart.m_volMin) / (chart.m_volMax - chart.m_volMin)
			candleHeight = getCandleDivHeight(chart)
			volHeight = getVolDivHeight(chart)
			return candleHeight + volHeight - chart.m_volPaddingBottom - (volHeight - chart.m_volPaddingTop - chart.m_volPaddingBottom) * rate
		else:
			return 0
	elif(divIndex == 2):
		if(chart.m_indMax > chart.m_indMin):
			rate = (value - chart.m_indMin) / (chart.m_indMax - chart.m_indMin)
			candleHeight = getCandleDivHeight(chart)
			volHeight = getVolDivHeight(chart)
			indHeight = getIndDivHeight(chart)
			return candleHeight + volHeight + indHeight - chart.m_indPaddingBottom - (indHeight - chart.m_indPaddingTop - chart.m_indPaddingBottom) * rate
		else:	
			return 0
	elif(divIndex == 3):
		if(chart.m_indMax2 > chart.m_indMin2):
			rate = (value - chart.m_indMin2) / (chart.m_indMax2 - chart.m_indMin2)
			candleHeight = getCandleDivHeight(chart)
			volHeight = getVolDivHeight(chart)
			indHeight = getIndDivHeight(chart)
			indHeight2 = getIndDivHeight2(chart)
			return candleHeight + volHeight + indHeight + indHeight2- chart.m_indPaddingBottom2 - (indHeight2 - chart.m_indPaddingTop2 - chart.m_indPaddingBottom2) * rate
		else:	
			return 0
	return 0


#根据坐标获取对应的值
#chart:K线
#point:坐标
def getChartValue(chart, point):
	candleHeight = getCandleDivHeight(chart)
	volHeight = getVolDivHeight(chart)
	indHeight = getIndDivHeight(chart)
	indHeight2 = getIndDivHeight2(chart)
	if(point.y <= candleHeight):
		rate = (candleHeight - chart.m_candlePaddingBottom - point.y) / (candleHeight - chart.m_candlePaddingTop - chart.m_candlePaddingBottom)
		cMin = chart.m_candleMin
		cMax = chart.m_candleMax
		if(chart.m_vScaleType != "standard"):
			if (cMax > 0):
				cMax = log10(cMax)
			elif (cMax < 0):
				cMax = -log10(abs(cMax))
			if (cMin > 0):
				cMin = log10(cMin)
			elif (cMin < 0):
				cMin = -log10(abs(cMin))
		result = cMin + (cMax - cMin) * rate
		if(chart.m_vScaleType != "standard"):
			return pow(10, result)
		else:
			return result
	elif(point.y > candleHeight and point.y <= candleHeight + volHeight):
		rate = (volHeight - chart.m_volPaddingBottom - (point.y - candleHeight)) / (volHeight - chart.m_volPaddingTop - chart.m_volPaddingBottom)
		return chart.m_volMin + (chart.m_volMax - chart.m_volMin) * rate
	elif(point.y > candleHeight + volHeight and point.y <= candleHeight + volHeight + indHeight):
		rate = (indHeight - chart.m_indPaddingBottom - (point.y - candleHeight - volHeight)) / (indHeight - chart.m_indPaddingTop - chart.m_indPaddingBottom)
		return chart.m_indMin + (chart.m_indMax - chart.m_indMin) * rate
	elif(point.y > candleHeight + volHeight + indHeight and point.y <= candleHeight + volHeight + indHeight + indHeight2):
		rate = (indHeight2 - chart.m_indPaddingBottom2 - (point.y - candleHeight - volHeight - indHeight)) / (indHeight2 - chart.m_indPaddingTop2 - chart.m_indPaddingBottom2)
		return chart.m_indMin2 + (chart.m_indMax2 - chart.m_indMin2) * rate
	return 0

#根据坐标获取K线层对应的值
#chart:K线
#point:坐标
def getCandleDivValue(chart, point):
	candleHeight = getCandleDivHeight(chart)
	rate = (candleHeight - chart.m_candlePaddingBottom - point.y) / (candleHeight - chart.m_candlePaddingTop - chart.m_candlePaddingBottom)
	cMin = chart.m_candleMin
	cMax = chart.m_candleMax
	if(chart.m_vScaleType != "standard"):
		if (cMax > 0):
			cMax = log10(cMax)
		elif (cMax < 0):
			cMax = -log10(abs(cMax))
		if (cMin > 0):
			cMin = log10(cMin)
		elif (cMin < 0):
			cMin = -log10(abs(cMin))
	result = cMin + (cMax - cMin) * rate
	if(chart.m_vScaleType != "standard"):
		return pow(10, result)
	else:
		return result

#清除缓存数据方法
#chart:K线
def clearDataArr(chart):
	chart.m_closearr = []
	chart.m_allema12 = []
	chart.m_allema26 = []
	chart.m_alldifarr = []
	chart.m_alldeaarr = []
	chart.m_allmacdarr = []
	chart.m_boll_mid = []
	chart.m_boll_up = []
	chart.m_boll_down = []
	chart.m_bias1 = []
	chart.m_bias2 = []
	chart.m_bias3 = []
	chart.m_dma1 = []
	chart.m_dma2 = []
	chart.m_kdj_k = []
	chart.m_kdj_d = []
	chart.m_kdj_j = []
	chart.m_bbi = []
	chart.m_roc = []
	chart.m_roc_ma = []
	chart.m_rsi1 = []
	chart.m_rsi2 = []
	chart.m_rsi3 = []
	chart.m_wr1 = []
	chart.m_wr2 = []
	chart.m_trix = []
	chart.m_trix_ma = []
	chart.m_cci = []

#获取数据
#chart:K线
def calcChartIndicator(chart):
	clearDataArr(chart)
	closeArr = []
	highArr = []
	lowArr = []
	if(chart.m_data != None and len(chart.m_data) > 0):
		for i in range(0,len(chart.m_data)):
			chart.m_closearr.append(chart.m_data[i].m_close)
			closeArr.append(chart.m_data[i].m_close)
			highArr.append(chart.m_data[i].m_high)
			lowArr.append(chart.m_data[i].m_low)
	if (chart.m_mainIndicator == "MA"):
		chart.m_ma5 = MA(closeArr, 5)
		chart.m_ma10 = MA(closeArr, 10)
		chart.m_ma20 = MA(closeArr, 20)
		chart.m_ma30 = MA(closeArr, 30)
		chart.m_ma120 = MA(closeArr, 120)
		chart.m_ma250 = MA(closeArr, 250)
	elif(chart.m_mainIndicator == "BOLL"):
		getBollData(closeArr, chart.m_boll_up, chart.m_boll_mid, chart.m_boll_down)
	if (chart.m_showIndicator == "MACD"):
		chart.m_allema12.append(chart.m_closearr[0])
		chart.m_allema26.append(chart.m_closearr[0])
		chart.m_alldeaarr.append(0)
		for i in range(1,len(chart.m_closearr)):
			chart.m_allema12.append(getEMA(12, chart.m_closearr[i], chart.m_allema12[i - 1]))
			chart.m_allema26.append(getEMA(26, chart.m_closearr[i], chart.m_allema26[i - 1]))
		chart.m_alldifarr = getDIF(chart.m_allema12, chart.m_allema26)
		for i in range(1,len(chart.m_alldifarr)):
			chart.m_alldeaarr.append(chart.m_alldeaarr[i - 1] * 8 / 10 + chart.m_alldifarr[i] * 2 / 10)
		chart.m_allmacdarr = getMACD(chart.m_alldifarr, chart.m_alldeaarr)
	elif(chart.m_showIndicator == "BIAS"):
		getBIASData(chart.m_closearr, chart.m_bias1, chart.m_bias2, chart.m_bias3)
	elif(chart.m_showIndicator == "TRIX"):
		getTRIXData(chart.m_closearr, chart.m_trix, chart.m_trix_ma)
	elif(chart.m_showIndicator == "CCI"):
		getCCIData(closeArr, highArr, lowArr, chart.m_cci)
	elif(chart.m_showIndicator == "BBI"):
		getBBIData(closeArr, chart.m_bbi)
	elif(chart.m_showIndicator == "ROC"):
		getRocData(closeArr, chart.m_roc, chart.m_roc_ma)
	elif(chart.m_showIndicator == "WR"):
		getWRData(closeArr, highArr, lowArr, chart.m_wr1, chart.m_wr2)
	elif(chart.m_showIndicator == "DMA"):
		getDMAData(closeArr, chart.m_dma1, chart.m_dma2)
	elif(chart.m_showIndicator == "RSI"):
		getRSIData(closeArr, chart.m_rsi1, chart.m_rsi2, chart.m_rsi3)
	elif(chart.m_showIndicator == "KDJ"):
		getKDJData(highArr, lowArr, closeArr, chart.m_kdj_k, chart.m_kdj_d, chart.m_kdj_j)
	global m_calculteMaxMin
	if(m_calculteMaxMin != None):
		m_calculteMaxMin(chart)
	else:
		calculateChartMaxMin(chart)

#计算最大最小值
#chart:K线
def calculateChartMaxMin(chart):
	chart.m_candleMax = 0
	chart.m_candleMin = 0
	chart.m_volMax = 0
	chart.m_volMin = 0
	chart.m_indMin = 0
	chart.m_indMin = 0
	isTrend = FALSE
	if(chart.m_cycle == "trend"):
		isTrend = TRUE
	firstOpen = 0
	load1 = FALSE
	load2 = FALSE
	load3 = FALSE
	load4 = FALSE
	if (chart.m_data != None and len(chart.m_data) > 0):
		lastValidIndex = chart.m_lastVisibleIndex
		if(chart.m_lastValidIndex != -1):
			lastValidIndex = chart.m_lastValidIndex
		for i in range(chart.m_firstVisibleIndex,lastValidIndex + 1):
			if (i == chart.m_firstVisibleIndex):
				if (isTrend):
					chart.m_candleMax = chart.m_data[i].m_close
					chart.m_candleMin = chart.m_data[i].m_close
					firstOpen = chart.m_data[i].m_close
				else:
					chart.m_candleMax = chart.m_data[i].m_high
					chart.m_candleMin = chart.m_data[i].m_low
				load1 = TRUE
				load2 = TRUE
				chart.m_volMax = chart.m_data[i].m_volume
				if (chart.m_showIndicator == "MACD"):
					chart.m_indMax = chart.m_alldifarr[i]
					chart.m_indMin = chart.m_alldifarr[i]
					load3 = TRUE
				elif (chart.m_showIndicator == "KDJ"):
					chart.m_indMax = chart.m_kdj_k[i]
					chart.m_indMin = chart.m_kdj_k[i]
					load3 = TRUE
				elif (chart.m_showIndicator == "RSI"):
					chart.m_indMax = chart.m_rsi1[i]
					chart.m_indMin = chart.m_rsi1[i]
					load3 = TRUE
				elif (chart.m_showIndicator == "BIAS"):
					chart.m_indMax = chart.m_bias1[i]
					chart.m_indMin = chart.m_bias1[i]
					load3 = TRUE
				elif (chart.m_showIndicator == "ROC"):
					chart.m_indMax = chart.m_roc[i]
					chart.m_indMin = chart.m_roc[i]
					load3 = TRUE
				elif (chart.m_showIndicator == "WR"):
					chart.m_indMax = chart.m_wr1[i]
					chart.m_indMin = chart.m_wr1[i]
					load3 = TRUE
				elif (chart.m_showIndicator == "CCI"):
					chart.m_indMax = chart.m_cci[i]
					chart.m_indMin = chart.m_cci[i]
					load3 = TRUE
				elif (chart.m_showIndicator == "BBI"):
					chart.m_indMax = chart.m_bbi[i]
					chart.m_indMin = chart.m_bbi[i]
					load3 = TRUE
				elif (chart.m_showIndicator == "TRIX"):
					chart.m_indMax = chart.m_trix[i]
					chart.m_indMin = chart.m_trix[i]
					load3 = TRUE
				elif (chart.m_showIndicator == "DMA"):
					chart.m_indMax = chart.m_dma1[i]
					chart.m_indMin = chart.m_dma1[i]
					load3 = TRUE
			else:
				if (isTrend):
					if (chart.m_candleMax < chart.m_data[i].m_close):
						chart.m_candleMax = chart.m_data[i].m_close
					if (chart.m_candleMin > chart.m_data[i].m_close):
						chart.m_candleMin = chart.m_data[i].m_close
				else:
					if (chart.m_candleMax < chart.m_data[i].m_high):
						chart.m_candleMax = chart.m_data[i].m_high
					if (chart.m_candleMin > chart.m_data[i].m_low):
						chart.m_candleMin = chart.m_data[i].m_low
				if (chart.m_volMax < chart.m_data[i].m_volume):
					chart.m_volMax = chart.m_data[i].m_volume
				if (chart.m_showIndicator == "MACD"):
					if (chart.m_indMax < chart.m_alldifarr[i]):
						chart.m_indMax = chart.m_alldifarr[i]
					if (chart.m_indMax < chart.m_alldeaarr[i]):
						chart.m_indMax = chart.m_alldeaarr[i]
					if (chart.m_indMax < chart.m_allmacdarr[i]):
						chart.m_indMax = chart.m_allmacdarr[i]
					if (chart.m_indMin > chart.m_alldifarr[i]):
						chart.m_indMin = chart.m_alldifarr[i]
					if (chart.m_indMin > chart.m_alldeaarr[i]):
						chart.m_indMin = chart.m_alldeaarr[i]
					if (chart.m_indMin > chart.m_allmacdarr[i]):
						chart.m_indMin = chart.m_allmacdarr[i]
				elif (chart.m_showIndicator == "KDJ"):
					if (chart.m_indMax < chart.m_kdj_k[i]):
						chart.m_indMax = chart.m_kdj_k[i]
					if (chart.m_indMax < chart.m_kdj_d[i]):
						chart.m_indMax = chart.m_kdj_d[i]
					if (chart.m_indMax < chart.m_kdj_j[i]):
						chart.m_indMax = chart.m_kdj_j[i]
					if (chart.m_indMin > chart.m_kdj_k[i]):
						chart.m_indMin = chart.m_kdj_k[i]
					if (chart.m_indMin > chart.m_kdj_d[i]):
						chart.m_indMin = chart.m_kdj_d[i]
					if (chart.m_indMin > chart.m_kdj_j[i]):
						chart.m_indMin = chart.m_kdj_j[i]
				elif (chart.m_showIndicator == "RSI"):
					if (chart.m_indMax < chart.m_rsi1[i]):
						chart.m_indMax = chart.m_rsi1[i]
					if (chart.m_indMax < chart.m_rsi2[i]):
						chart.m_indMax = chart.m_rsi2[i]
					if (chart.m_indMax < chart.m_rsi3[i]):
						chart.m_indMax = chart.m_rsi3[i]
					if (chart.m_indMin > chart.m_rsi1[i]):
						chart.m_indMin = chart.m_rsi1[i]
					if (chart.m_indMin > chart.m_rsi2[i]):
						chart.m_indMin = chart.m_rsi2[i]
					if (chart.m_indMin > chart.m_rsi3[i]):
						chart.m_indMin = chart.m_rsi3[i]
				elif (chart.m_showIndicator == "BIAS"):
					if (chart.m_indMax < chart.m_bias1[i]):
						chart.m_indMax = chart.m_bias1[i]
					if (chart.m_indMax < chart.m_bias2[i]):
						chart.m_indMax = chart.m_bias2[i]
					if (chart.m_indMax < chart.m_bias3[i]):
						chart.m_indMax = chart.m_bias3[i]
					if (chart.m_indMin > chart.m_bias1[i]):
						chart.m_indMin = chart.m_bias1[i]
					if (chart.m_indMin > chart.m_bias2[i]):
						chart.m_indMin = chart.m_bias2[i]
					if (chart.m_indMin > chart.m_bias3[i]):
						chart.m_indMin = chart.m_bias3[i]
				elif (chart.m_showIndicator == "ROC"):
					if (chart.m_indMax < chart.m_roc[i]):
						chart.m_indMax = chart.m_roc[i]
					if (chart.m_indMax < chart.m_roc_ma[i]):
						chart.m_indMax = chart.m_roc_ma[i]
					if (chart.m_indMin > chart.m_roc[i]):
						chart.m_indMin = chart.m_roc[i]
					if (chart.m_indMin > chart.m_roc_ma[i]):
						chart.m_indMin = chart.m_roc_ma[i]
				elif (chart.m_showIndicator == "WR"):
					if (chart.m_indMax < chart.m_wr1[i]):
						chart.m_indMax = chart.m_wr1[i]
					if (chart.m_indMax < chart.m_wr2[i]):
						chart.m_indMax = chart.m_wr2[i]
					if (chart.m_indMin > chart.m_wr1[i]):
						chart.m_indMin = chart.m_wr1[i]
					if (chart.m_indMin > chart.m_wr2[i]):
						chart.m_indMin = chart.m_wr2[i]
				elif (chart.m_showIndicator == "CCI"):
					if (chart.m_indMax < chart.m_cci[i]):
						chart.m_indMax = chart.m_cci[i]
					if (chart.m_indMin > chart.m_cci[i]):
						chart.m_indMin = chart.m_cci[i]
				elif (chart.m_showIndicator == "BBI"):
					if (chart.m_indMax < chart.m_bbi[i]):
						chart.m_indMax = chart.m_bbi[i]
					if (chart.m_indMin > chart.m_bbi[i]):
						chart.m_indMin = chart.m_bbi[i]
				elif (chart.m_showIndicator == "TRIX"):
					if (chart.m_indMax < chart.m_trix[i]):
						chart.m_indMax = chart.m_trix[i]
					if (chart.m_indMax < chart.m_trix_ma[i]):
						chart.m_indMax = chart.m_trix_ma[i]
					if (chart.m_indMin > chart.m_trix[i]):
						chart.m_indMin = chart.m_trix[i]
					if (chart.m_indMin > chart.m_trix_ma[i]):
						chart.m_indMin = chart.m_trix_ma[i]
				elif (chart.m_showIndicator == "DMA"):
					if (chart.m_indMax < chart.m_dma1[i]):
						chart.m_indMax = chart.m_dma1[i]
					if (chart.m_indMax < chart.m_dma2[i]):
						chart.m_indMax = chart.m_dma2[i]
					if (chart.m_indMin > chart.m_dma1[i]):
						chart.m_indMin = chart.m_dma1[i]
					if (chart.m_indMin > chart.m_dma2[i]):
						chart.m_indMin = chart.m_dma2[i]
	if(len(chart.m_shapes) > 0):
		lastValidIndex = chart.m_lastVisibleIndex
		if(chart.m_lastValidIndex != -1):
			lastValidIndex = chart.m_lastValidIndex
		for s in range(0, len(chart.m_shapes)):
			shape = chart.m_shapes[s]
			if(len(shape.m_datas) > 0):
				for i in range(chart.m_firstVisibleIndex,lastValidIndex + 1):
					if (shape.m_divIndex == 0):
						if (load1 == FALSE and i == chart.m_firstVisibleIndex):
							chart.m_candleMax = shape.m_datas[i]
							chart.m_candleMin = shape.m_datas[i]
							load1 = TRUE
						else:
							if (shape.m_datas[i] > chart.m_candleMax):
								chart.m_candleMax = shape.m_datas[i]
							if (shape.m_datas[i] < chart.m_candleMin):
								chart.m_candleMin = shape.m_datas[i]
					elif (shape.m_divIndex == 1):
						if (load2 == FALSE and i == chart.m_firstVisibleIndex):
							chart.m_volMax = shape.m_datas[i]
							chart.m_volMin = shape.m_datas[i]
							load2 = TRUE
						else:
							if (shape.m_datas[i] > chart.m_volMax):
								chart.m_volMax = shape.m_datas[i]
							if (shape.m_datas[i] < chart.m_volMin):
								chart.m_volMin = shape.m_datas[i]
					elif (shape.m_divIndex == 2):
						if (load3 == FALSE and i == chart.m_firstVisibleIndex):
							chart.m_indMax = shape.m_datas[i]
							chart.m_indMin = shape.m_datas[i]
							load3 = TRUE
						else:
							if (shape.m_datas[i] > chart.m_indMax):
								chart.m_indMax = shape.m_datas[i]
							if (shape.m_datas[i] < chart.m_indMin):
								chart.m_indMin = shape.m_datas[i]
					elif (shape.m_divIndex == 3):
						if (load4 == FALSE and i == chart.m_firstVisibleIndex):
							chart.m_indMax2 = shape.m_datas[i]
							chart.m_indMin2 = shape.m_datas[i]
							load4 = TRUE
						else:
							if (shape.m_datas[i] > chart.m_indMax2):
								chart.m_indMax2 = shape.m_datas[i]
							if (shape.m_datas[i] < chart.m_indMin2):
								chart.m_indMin2 = shape.m_datas[i]
			if(len(shape.m_datas2) > 0):
				for i in range(chart.m_firstVisibleIndex,lastValidIndex + 1):
					if (shape.m_divIndex == 0):
						if (shape.m_datas2[i] > chart.m_candleMax):
							chart.m_candleMax = shape.m_datas2[i]
						if (shape.m_datas2[i] < chart.m_candleMin):
							chart.m_candleMin = shape.m_datas2[i]
					elif (shape.m_divIndex == 1):
						if (shape.m_datas2[i] > chart.m_volMax):
							chart.m_volMax = shape.m_datas2[i]
						if (shape.m_datas2[i] < chart.m_volMin):
							chart.m_volMin = shape.m_datas2[i]
					elif (shape.m_divIndex == 2):
						if (shape.m_datas2[i] > chart.m_indMax):
							chart.m_indMax = shape.m_datas2[i]
						if (shape.m_datas2[i] < chart.m_indMin):
							chart.m_indMin = shape.m_datas2[i]
					elif (shape.m_divIndex == 3):
						if (shape.m_datas2[i] > chart.m_indMax2):
							chart.m_indMax2 = shape.m_datas2[i]
						if (shape.m_datas2[i] < chart.m_indMin2):
							chart.m_indMin2 = shape.m_datas2[i]
					
	if (isTrend):
		subMax = max(abs(chart.m_candleMax - firstOpen), abs(chart.m_candleMin - firstOpen))
		chart.m_candleMax = firstOpen + subMax
		chart.m_candleMin = firstOpen - subMax
	else:
		if(chart.m_candleMax == 0 and chart.m_candleMin == 0):
			chart.m_candleMax = 1
			chart.m_candleMin = -1
		if(chart.m_volMax == 0 and chart.m_volMin == 0):
			chart.m_volMax = 1
			chart.m_volMin = -1
		if(chart.m_indMax == 0 and chart.m_indMin == 0):
			chart.m_indMax = 1
			chart.m_indMin = -1
		if(chart.m_indMax2 == 0 and chart.m_indMin2 == 0):
			chart.m_indMax2 = 1
			chart.m_indMin2 = -1

#缩小
#chart:K线
def zoomOutChart(chart):
	if (chart.m_autoFillHScale == FALSE):
		hScalePixel = chart.m_hScalePixel
		oldX = getChartX(chart, chart.m_crossStopIndex)
		pureH = getChartWorkAreaWidth(chart)
		oriMax = -1
		maxValue = -1
		deal = 0
		dataCount = len(chart.m_data)
		findex = chart.m_firstVisibleIndex
		lindex = chart.m_lastVisibleIndex
		if (hScalePixel < 500):
			oriMax = getChartMaxVisibleCount(chart, hScalePixel, pureH)
			if (dataCount < oriMax):
				deal = 1
			if (hScalePixel > 3):
				hScalePixel += 1
			else:
				if (hScalePixel == 1):
					hScalePixel = 2
				else:
					hScalePixel = hScalePixel * 1.5
					if (hScalePixel > 3):
						hScalePixel = int(hScalePixel)
			maxValue = getChartMaxVisibleCount(chart, hScalePixel, pureH)
			if (dataCount >= maxValue):
				if (deal == 1):
					lindex = dataCount - 1
				findex = lindex - maxValue + 1
				if (findex < 0):
					findex = 0
		chart.m_hScalePixel = hScalePixel
		chart.m_firstVisibleIndex = findex
		chart.m_lastVisibleIndex = lindex
		if (chart.m_showCrossLine):
			newX = getChartX(chart, chart.m_crossStopIndex)
			if (newX > oldX):
				while (chart.m_lastVisibleIndex < len(chart.m_data) - 1):
					chart.m_firstVisibleIndex = chart.m_firstVisibleIndex + 1
					chart.m_lastVisibleIndex = chart.m_lastVisibleIndex + 1
					newX = getChartX(chart, chart.m_crossStopIndex)
					if (newX <= oldX):
						break
			elif (newX < oldX):
				while (chart.m_firstVisibleIndex > 0):
					chart.m_firstVisibleIndex = chart.m_firstVisibleIndex - 1
					chart.m_lastVisibleIndex = chart.m_lastVisibleIndex - 1
					newX = getChartX(chart, chart.m_crossStopIndex)
					if (newX >= oldX):
						break
		checkChartLastVisibleIndex(chart)
		global m_calculteMaxMin
		if(m_calculteMaxMin != None):
			m_calculteMaxMin(chart)
		else:
			calculateChartMaxMin(chart)

#放大
#chart:K线
def zoomInChart(chart):
	if (chart.m_autoFillHScale == FALSE):
		hScalePixel = chart.m_hScalePixel
		oldX = getChartX(chart, chart.m_crossStopIndex)
		pureH = getChartWorkAreaWidth(chart)
		maxValue = -1
		dataCount = len(chart.m_data)
		findex = chart.m_firstVisibleIndex
		lindex = chart.m_lastVisibleIndex
		if (hScalePixel > 3):
			hScalePixel -= 1
		else:
			hScalePixel = hScalePixel * 2 / 3
			if (hScalePixel > 3):
				hScalePixel = int(hScalePixel)
		maxValue = getChartMaxVisibleCount(chart, hScalePixel, pureH)
		if (maxValue >= dataCount):
			if (hScalePixel < 1):
				hScalePixel = pureH / maxValue
			findex = 0
			lindex = dataCount - 1
		else:
			findex = lindex - maxValue + 1
			if (findex < 0):
				findex = 0
		chart.m_hScalePixel = hScalePixel
		chart.m_firstVisibleIndex = findex
		chart.m_lastVisibleIndex = lindex
		if (chart.m_showCrossLine):
			newX = getChartX(chart, chart.m_crossStopIndex)
			if (newX > oldX):
				while (chart.m_lastVisibleIndex < len(chart.m_data) - 1):
					chart.m_firstVisibleIndex = chart.m_firstVisibleIndex + 1
					chart.m_lastVisibleIndex = chart.m_lastVisibleIndex + 1
					newX = getChartX(chart, chart.m_crossStopIndex)
					if (newX <= oldX):
						break
			elif (newX < oldX):
				while (chart.m_firstVisibleIndex > 0):
					chart.m_firstVisibleIndex = chart.m_firstVisibleIndex - 1
					chart.m_lastVisibleIndex = chart.m_lastVisibleIndex - 1
					newX = getChartX(chart, chart.m_crossStopIndex)
					if (newX >= oldX):
						break
		checkChartLastVisibleIndex(chart)
		global m_calculteMaxMin
		if(m_calculteMaxMin != None):
			m_calculteMaxMin(chart)
		else:
			calculateChartMaxMin(chart)

#计算坐标轴
#min:最小值
#max:最大值
#yLen:长度
#maxSpan:最大间隔
#minSpan:最小间隔
#defCount:数量
def chartGridScale(minValue, maxValue, yLen, maxSpan, minSpan, defCount):
	if(defCount > 0 and maxSpan > 0 and minSpan > 0):
		global m_gridStep_Chart
		global m_gridDigit_Chart
		sub = maxValue - minValue
		nMinCount = int(math.ceil(yLen / maxSpan))
		nMaxCount = int(math.floor(yLen / minSpan))
		nCount = defCount
		logStep = sub / nCount
		start = FALSE
		divisor = 0
		i = 15
		nTemp = 0
		m_gridStep_Chart = 0
		m_gridDigit_Chart = 0
		nCount = max(nMinCount, nCount)
		nCount = min(nMaxCount, nCount)
		nCount = max(nCount, 1)
		while(i >= -6):
			divisor = math.pow(10.0, i)
			if (divisor < 1):
				m_gridDigit_Chart = m_gridDigit_Chart + 1
			nTemp = int(math.floor(logStep / divisor))
			if (start):
				if (nTemp < 4):
					if (m_gridDigit_Chart > 0):
						m_gridDigit_Chart = m_gridDigit_Chart - 1
				elif (nTemp >= 4 and nTemp <= 6):
					nTemp = 5
					m_gridStep_Chart = m_gridStep_Chart + nTemp * divisor
				else:
					m_gridStep_Chart = m_gridStep_Chart + 10 * divisor
					if (m_gridDigit_Chart > 0):
						m_gridDigit_Chart = m_gridDigit_Chart - 1
				break
			elif (nTemp > 0):
				m_gridStep_Chart = nTemp * divisor + m_gridStep_Chart
				logStep = logStep - m_gridStep_Chart
				start = TRUE
			i = i - 1
		return 1
	return 0

m_upSubValue = 0
m_downSubValue = 0

#计算线性回归上下限
#chart:K线
#plot:画线
#a:直线k
#b:直线b
def getLRBandRange(chart, plot, a, b):
	global m_upSubValue
	global m_downSubValue
	bIndex = getChartIndexByDate(chart, plot.m_key1)
	eIndex = getChartIndexByDate(chart, plot.m_key2)
	tempBIndex = min(bIndex, eIndex)
	tempEIndex = max(bIndex, eIndex)
	bIndex = tempBIndex;
	eIndex = tempEIndex;
	upList = []
	downList = []
	for i in range(bIndex,eIndex + 1):
		high = chart.m_data[i].m_high
		low = chart.m_data[i].m_low
		midValue = (i - bIndex + 1) * a + b
		upList.append(high - midValue)
		downList.append(midValue - low)
	m_upSubValue = maxValue(upList)
	m_downSubValue = maxValue(downList)

m_nHigh_Chart = 0
m_nLow_Chart = 0

#获取K线的区域
#chart: K线
#plot: 画线
def getCandleRange(chart, plot):
	global m_nHigh_Chart
	global m_nLow_Chart
	bIndex = getChartIndexByDate(chart, plot.m_key1)
	eIndex = getChartIndexByDate(chart, plot.m_key2)
	tempBIndex = min(bIndex, eIndex)
	tempEIndex = max(bIndex, eIndex)
	bIndex = tempBIndex
	eIndex = tempEIndex
	highList = []
	lowList = []
	for i in range(bIndex,eIndex + 1):
		highList.append(chart.m_data[i].m_high)
		lowList.append(chart.m_data[i].m_low)
	m_nHigh_Chart = maxValue(highList)
	m_nLow_Chart = minValue(lowList)

#判断是否选中线条
#chart:K线
#mp:坐标
#divIndex:层索引
#datas:数据
#curIndex:当前索引
def selectLines(chart, mp, divIndex, datas, curIndex):
	topY = getChartY(chart, divIndex, datas[curIndex])
	if (chart.m_hScalePixel <= 1):
		if(mp.y >= topY - 8 and mp.y <= topY + 8):
			return TRUE
	else:
		index = curIndex
		scaleX = getChartX(chart, index)
		judgeTop = 0
		judgeScaleX = scaleX
		if (mp.x >= scaleX):
			leftIndex = curIndex + 1
			if (curIndex < chart.m_lastVisibleIndex):
				rightValue = datas[leftIndex]
				judgeTop = getChartY(chart, divIndex, rightValue)
			else:
				judgeTop = topY
		else:
			judgeScaleX = scaleX - chart.m_hScalePixel
			rightIndex = curIndex - 1
			if (curIndex > 0):
				leftValue = datas[rightIndex]
				judgeTop = getChartY(chart, divIndex, leftValue)
			else:
				judgeTop = topY
		lineWidth = 4
		judgeX = 0
		judgeY = 0
		judgeW = 0
		judgeH = 0
		if (judgeTop >= topY):
			judgeX = judgeScaleX
			judgeY = topY - 2 - lineWidth
			judgeW = chart.m_hScalePixel
			judgeH = judgeTop - topY + 4 + lineWidth
			if(judgeH < 4):
				judgeH = 4
		else:
			judgeX = judgeScaleX
			judgeY = judgeTop - 2 - lineWidth / 2
			judgeW = chart.m_hScalePixel
			judgeH = topY - judgeTop + 4 + lineWidth
			if(judgeH < 4):
				judgeH = 4
		if (mp.x >= judgeX and mp.x <= judgeX + judgeW and mp.y >= judgeY and mp.y <= judgeY + judgeH):
			return TRUE
	return FALSE

#判断是否选中图形
#chart:K线
#mp:坐标
def selectShape(chart, mp):
	if(chart.m_data != None and len(chart.m_data) > 0):
		chart.m_selectShape = ""
		chart.m_selectShapeEx = ""
		candleHeight = getCandleDivHeight(chart)
		volHeight = getVolDivHeight(chart)
		indHeight = getIndDivHeight(chart)
		index = getChartIndex(chart, mp)
		if (mp.y >= candleHeight + volHeight and mp.y <= candleHeight + volHeight + indHeight):
			if (chart.m_showIndicator == "MACD"):
				macdY = getChartY(chart, 2, chart.m_allmacdarr[index])
				zeroY = getChartY(chart, 2, 0)
				if (selectLines(chart, mp, 2, chart.m_allmacdarr, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "MACD"
				if (selectLines(chart, mp, 2, chart.m_alldifarr, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "DIF"
				elif (selectLines(chart, mp, 2, chart.m_alldeaarr, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "DEA"
			elif (chart.m_showIndicator == "KDJ"):
				if (selectLines(chart, mp, 2, chart.m_kdj_k, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "K"
				elif (selectLines(chart, mp, 2, chart.m_kdj_d, index)):	
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "D"
				elif (selectLines(chart, mp, 2, chart.m_kdj_j, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "J"
			elif (chart.m_showIndicator == "RSI"):
				if (selectLines(chart, mp, 2, chart.m_rsi1, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "6"
				elif (selectLines(chart, mp, 2, chart.m_rsi2, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "12"
				elif (selectLines(chart, mp, 2, chart.m_rsi3, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "24"
			elif (chart.m_showIndicator == "BIAS"):
				if (selectLines(chart, mp, 2, chart.m_bias1, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "1"
				elif (selectLines(chart, mp, 2, chart.m_bias2, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "2"
				elif (selectLines(chart, mp, 2, chart.m_bias3, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "3"
			elif (chart.m_showIndicator == "ROC"):
				if (selectLines(chart, mp, 2, chart.m_roc, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "ROC"
				elif (selectLines(chart, mp, 2, chart.m_roc_ma, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "ROCMA"
			elif (chart.m_showIndicator == "WR"):
				if (selectLines(chart, mp, 2, chart.m_wr1, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "1"
				elif (selectLines(chart, mp, 2, chart.m_wr2, index)):
					chart.m_selectShape = "WR"
					chart.m_selectShapeEx = "2"
			elif (chart.m_showIndicator == "CCI"):
				if (selectLines(chart, mp, 2, chart.m_cci, index)):
					chart.m_selectShape = chart.m_showIndicator
			elif (chart.m_showIndicator == "BBI"):
				if (selectLines(chart, mp, 2, chart.m_bbi, index)):
					chart.m_selectShape = chart.m_showIndicator
			elif (chart.m_showIndicator == "TRIX"):
				if (selectLines(chart, mp, 2, chart.m_trix, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "TRIX"
				elif (selectLines(chart, mp, 2, chart.m_trix_ma, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "TRIXMA"
			elif (chart.m_showIndicator == "DMA"):
				if (selectLines(chart, mp, 2, chart.m_dma1, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "DIF"
				elif (selectLines(chart, mp, 2, chart.m_dma2, index)):
					chart.m_selectShape = chart.m_showIndicator
					chart.m_selectShapeEx = "DIFMA"
		elif(mp.y >= candleHeight and mp.y <= candleHeight + volHeight):
			volY = getChartY(chart, 1, chart.m_data[index].m_volume)
			zeroY = getChartY(chart, 1, 0);
			if (mp.y >= min(volY, zeroY) and mp.y <= max(volY, zeroY)):
				chart.m_selectShape = "VOL"
		elif (mp.y >= 0 and mp.y <= candleHeight):
			isTrend = FALSE
			if(chart.m_cycle == "trend"):
				isTrend = TRUE
			if (isTrend == FALSE):
				if (chart.m_mainIndicator == "BOLL"):
					if (selectLines(chart, mp, 0, chart.m_boll_mid, index)):
						chart.m_selectShape = chart.m_mainIndicator
						chart.m_selectShapeEx = "MID"
					elif (selectLines(chart, mp, 0, chart.m_boll_up, index)):
						chart.m_selectShape = chart.m_mainIndicator
						chart.m_selectShapeEx = "UP"
					elif (selectLines(chart, mp, 0, chart.m_boll_down, index)):
						chart.m_selectShape = chart.m_mainIndicator
						chart.m_selectShapeEx = "DOWN"
				elif (chart.m_mainIndicator == "MA"):
					if (selectLines(chart, mp, 0, chart.m_ma5, index)):
						chart.m_selectShape = chart.m_mainIndicator
						chart.m_selectShapeEx = "5"
					elif (selectLines(chart, mp, 0, chart.m_ma10, index)):
						chart.m_selectShape = chart.m_mainIndicator
						chart.m_selectShapeEx = "10"
					elif (selectLines(chart, mp, 0, chart.m_ma20, index)):
						chart.m_selectShape = chart.m_mainIndicator
						chart.m_selectShapeEx = "20"
					elif (selectLines(chart, mp, 0, chart.m_ma30, index)):
						chart.m_selectShape = chart.m_mainIndicator
						chart.m_selectShapeEx = "30"
					elif (selectLines(chart, mp, 0, chart.m_ma120, index)):
						chart.m_selectShape = chart.m_mainIndicator
						chart.m_selectShapeEx = "120"
					elif (selectLines(chart, mp, 0, chart.m_ma250, index)):
						chart.m_selectShape = chart.m_mainIndicator
						chart.m_selectShapeEx = "250"
			if (chart.m_selectShape == ""):
				highY = getChartY(chart, 0, chart.m_data[index].m_high)
				lowY = getChartY(chart, 0, chart.m_data[index].m_low)
				if (isTrend):
					if (selectLines(chart, mp, 0, chart.m_closearr, index)):
						chart.m_selectShape = "CANDLE"
				else:
					if (mp.y >= min(lowY, highY) and mp.y <= max(lowY, highY)):
						chart.m_selectShape = "CANDLE"
		if(len(chart.m_shapes) > 0):
			for i in range(0, len(chart.m_shapes)):
				shape = chart.m_shapes[i]
				if (selectLines(chart, mp, shape.m_divIndex, shape.m_datas, index)):
					chart.m_selectShape = shape.m_name
					break


#绘制线条
#chart:K线
#paint:绘图对象
#clipRect:裁剪区域
#divIndex:图层
#datas:数据
#color:颜色
#selected:是否选中
def drawChartLines(chart, paint, clipRect, divIndex, datas, color, selected):
	maxVisibleRecord = getChartMaxVisibleCount(chart, chart.m_hScalePixel, getChartWorkAreaWidth(chart))
	lastValidIndex = chart.m_lastVisibleIndex
	if(chart.m_lastValidIndex != -1):
		lastValidIndex = chart.m_lastValidIndex
	drawPoints = []
	for i in range(chart.m_firstVisibleIndex,lastValidIndex + 1):
		x = getChartX(chart, i)
		value = datas[i]
		y = getChartY(chart, divIndex, value)
		drawPoints.append((x, y))
		if (selected):
			kPInterval = int(maxVisibleRecord / 30)
			if (kPInterval < 2):
				kPInterval = 3
			if (i % kPInterval == 0):
				paint.fillRect(color, x - 3, y - 3, x + 3, y + 3)
	paint.drawPolyline(color, m_lineWidth_Chart, 0, drawPoints)

#数值转字符串，可以设置保留位数
#value 数值
#digit 小数位数
def toFixed(value, digit):
	return str(round(value, digit))

#计算EMA
#n:周期
#value:当前数据
#lastEMA:上期数据
def getEMA(n, value, lastEMA):
	return(value * 2 + lastEMA * (n - 1)) / (n + 1)

#计算MACD
#dif:DIF数据
#dea:DEA数据
def getMACD(dif, dea):
	result = []
	for i in range(0,len(dif)):
		result.append((dif[i] - dea[i]) * 2)
	return result

#计算DIF
#close12:12日数据
#close26:26日数据
def getDIF(close12, close26):
	result = []
	for i in range(0,len(close12)):
		result.append(close12[i] - close26[i])
	return result

#REF函数
#ticks:数据
#days:日数
def REF(ticks, days):
	refArr = []
	length = len(ticks)
	for i in range(0,length):
		ref = 0
		if(i >= days):
			ref = ticks[i - days]
		else:
			ref = ticks[0]
		refArr.append(ref)
	return refArr

#计算最大值
#ticks 最高价数组
#days
def HHV(ticks, days):
	hhv = []
	maxValue = ticks[0];
	for i in range(0,len(ticks)):
		if(i >= days):
			maxValue = ticks[i];
			j = i
			while(j > i - days):
				if(maxValue < ticks[j]):
					maxValue = ticks[j]
				j = j - 1
			hhv.append(maxValue)
		else:
			if(maxValue < ticks[i]):
				maxValue = ticks[i]
			hhv.append(maxValue)
	return hhv

#计算最小值
#ticks 最低价数组
#days
def LLV(ticks, days):
	llv = []
	minValue = ticks[0]
	for i in range(0,len(ticks)):
		if(i >= days):
			minValue = ticks[i]
			j = i
			while(j > i - days):
				if(minValue > ticks[j]):
					minValue = ticks[j]
				j = j - 1
			llv.append(minValue)
		else:
			if(minValue > ticks[i]):
				minValue = ticks[i]
			llv.append(minValue);
	return llv

#MA数据计算
#ticks 收盘价数组
#days 天数
def MA(ticks, days):
	maSum = 0
	mas = []
	last = 0
	for i in range(0,len(ticks)):
		ma = 0
		if(i >= days):
			last = ticks[i - days]
			maSum = maSum + ticks[i] - last
			ma = maSum / days
		else:
			maSum += ticks[i]
			ma = maSum / (i + 1)
		mas.append(ma)
	return mas

#计算ROC数据
#ticks 收盘价数组
def getRocData(ticks, roc, maroc):
	n = 12
	m = 6
	for i in range(0,len(ticks)):
		currRoc = 0
		if(i >= n):
			currRoc = 100 * (ticks[i] - ticks[i - n]) / ticks[i - n]
			roc.append(currRoc)
		else:
			currRoc = 100 * (ticks[i] - ticks[0]) / ticks[0]
			roc.append(currRoc)
	marocMA = MA(roc, m)
	for i in range(0, len(marocMA)):
		maroc.append(marocMA[i])

#计算rsi指标,分别返回以6日，12日，24日为参考基期的RSI值
def getRSIData(ticks, rsi1, rsi2, rsi3):
	n1 = 6
	n2 = 12
	n3 = 24
	lastClosePx = ticks[0]
	lastSm1 = 0
	lastSa1 = 0
	lastSm2 = 0
	lastSa2 = 0
	lastSm3 = 0
	lastSa3 = 0
	for i in range(0, len(ticks)):
		c = ticks[i]
		m = max(c - lastClosePx, 0)
		a = abs(c - lastClosePx)
		if(i == 0):
			lastSm1 = 0
			lastSa1 = 0
			rsi1.append(0)
		else:
			lastSm1 = (m + (n1 - 1) * lastSm1) / n1
			lastSa1 = (a + (n1 - 1) * lastSa1)/ n1
			if(lastSa1 != 0):
				rsi1.append(lastSm1 / lastSa1 * 100)
			else:
				rsi1.append(0)

		if(i == 0):
			lastSm2 = 0
			lastSa2 = 0
			rsi2.append(0)
		else:
			lastSm2 = (m + (n2 - 1) * lastSm2) / n2
			lastSa2 = (a + (n2 - 1) * lastSa2)/ n2
			if(lastSa2 != 0):
				rsi2.append(lastSm2 / lastSa2 * 100)
			else:
				rsi2.append(0)

		if(i == 0):
			lastSm3 = 0
			lastSa3 = 0
			rsi3.append(0)
		else:
			lastSm3 = (m + (n3 - 1) * lastSm3) / n3
			lastSa3 = (a + (n3 - 1) * lastSa3)/ n3
			if(lastSa3 != 0):
				rsi3.append(lastSm3 / lastSa3 * 100)
			else:
				rsi3.append(0.0)
		lastClosePx =  c;

#获取方差数据
def standardDeviationSum(listValue, avg_value, param):
	target_value = listValue[len(listValue) - 1]
	sumValue = (target_value - avg_value) * (target_value - avg_value)
	for i in range(0, len(listValue) - 1):
		ileft = listValue[i]
		sumValue = sumValue + (ileft - avg_value) * (ileft - avg_value)
	return sumValue

#计算boll指标,ma的周期为20日
def getBollData(ticks, ups, mas, lows):
	maDays = 20
	tickBegin = maDays - 1
	maSum  = 0
	p = 0
	for i in range(0, len(ticks)):
		c = ticks[i]
		ma = 0
		md = 0
		bstart = 0
		mdSum = 0
		maSum = maSum + c
		if(i >= tickBegin):
			maSum = maSum - p;
			ma = maSum / maDays
			bstart = i - tickBegin
			p = ticks[bstart]
			mas.append(ma);
			bstart = i - tickBegin;
			p = ticks[bstart]
			values = []
			for j in range(bstart, bstart + maDays):
				values.append(ticks[j])
			mdSum = standardDeviationSum(values, ma, 2)
			md = math.sqrt(mdSum / maDays)
			ups.append(ma + 2 * md)
			lows.append(ma - 2 * md)
		else:
			ma = maSum / (i + 1)
			mas.append(ma);
			values = []
			for j in range(0, i + 1):
				values.append(ticks[j])
			mdSum = standardDeviationSum(values, ma, 2)
			md = math.sqrt(mdSum / (i + 1))
			ups.append(ma + 2 * md)
			lows.append(ma - 2 * md)

m_maxHigh = 0
m_minLow = 0

#获取最大最小值区间
#ticks:数据
def getMaxHighAndMinLow(highArr, lowArr):
	global m_maxHigh
	global m_minLow
	for i in range(0, len(lowArr)):
		high = highArr[i]
		low = lowArr[i]
		if(high > m_maxHigh):
			m_maxHigh = high
		if(low < m_minLow):
			m_minLow = low

#计算kdj指标,rsv的周期为9日
def getKDJData(highArr, lowArr, closeArr, ks, ds, js):
	global m_maxHigh
	global m_minLow
	days = 9
	rsvs = []
	lastK = 0
	lastD = 0
	curK = 0
	curD = 0
	for i in range(0, len(highArr)):
		highList = []
		lowList = []
		startIndex = i - days
		if(startIndex < 0):
			startIndex = 0
		for j in range(startIndex, (i + 1)):
			highList.append(highArr[j])
			lowList.append(lowArr[j])
		m_maxHigh = 0
		m_minLow = 0
		close = closeArr[i]
		getMaxHighAndMinLow(highList, lowList)
		if(m_maxHigh == m_minLow):
			rsvs.append(0)
		else:
			rsvs.append((close - m_minLow) / (m_maxHigh - m_minLow) * 100)
		if(i == 0):
			lastK = rsvs[i]
			lastD = rsvs[i]
		curK = 2.0 / 3.0 * lastK + 1.0 / 3.0 * rsvs[i]
		ks.append(curK)
		lastK = curK

		curD = 2.0 / 3.0 * lastD + 1.0 / 3.0 * curK
		ds.append(curD)
		lastD = curD

		js.append(3.0 * curK - 2.0 * curD)

#获取BIAS的数据
#ticks 收盘价数组
def getBIASData(ticks, bias1Arr, bias2Arr, bias3Arr):
	n1 = 6
	n2 = 12
	n3 = 24
	ma1 = MA(ticks, n1)
	ma2 = MA(ticks, n2)
	ma3 = MA(ticks, n3)
	for i in range(0,len(ticks)):
		b1 = (ticks[i] - ma1[i]) / ma1[i] * 100
		b2 = (ticks[i] - ma2[i]) / ma2[i] * 100
		b3 = (ticks[i] - ma3[i]) / ma3[i] * 100
		bias1Arr.append(b1)
		bias2Arr.append(b2)
		bias3Arr.append(b3)

#计算DMA（平均差）
#ticks 收盘价数组
def getDMAData(ticks, difArr, difmaArr):
	n1 = 10
	n2 = 50
	ma10 = MA(ticks, n1)
	ma50 = MA(ticks, n2)
	for i in range(0,len(ticks)):
		dif = ma10[i] - ma50[i]
		difArr.append(dif)
	difma = MA(difArr, n1)
	for i in range(0,len(difma)):
		difmaArr.append(difma[i])

#计算BBI(多空指标)
#ticks
def getBBIData(ticks, bbiArr):
	ma3 = MA(ticks, 3)
	ma6 = MA(ticks, 6)
	ma12 = MA(ticks, 12)
	ma24 = MA(ticks, 24)
	for i in range(0,len(ticks)):
		bbi = (ma3[i] + ma6[i] + ma12[i] + ma24[i]) / 4
		bbiArr.append(bbi)

#计算WR(威廉指标)
#ticks 含最高价,最低价, 收盘价的二维数组
#days
def getWRData(closeArr, highArr, lowArr, wr1Arr, wr2Arr):
	n1 = 5
	n2 = 10
	for i in range(0,len(closeArr)):
		highArr.append(highArr[i])
		lowArr.append(lowArr[i])
		closeArr.append(closeArr[i])
	highArr1 = HHV(highArr, n1)
	highArr2 = HHV(highArr, n2)
	lowArr1 = LLV(lowArr, n1)
	lowArr2 = LLV(lowArr, n2)
	for i in range(0,len(closeArr)):
		high1 = highArr1[i]
		low1 = lowArr1[i]
		high2 = highArr2[i]
		low2 = lowArr2[i]
		close = closeArr[i]
		wr1 = 100 * (high1 - close) / (high1 - low1)
		wr2 = 100 * (high2 - close) / (high2 - low2)
		wr1Arr.append(wr1)
		wr2Arr.append(wr2)

#CCI(顺势指标)计算  CCI（N日）=（TP－MA）÷MD÷0.015
#ticks 带最高价，最低价，收盘价的二维数组
def getCCIData(closeArr, highArr, lowArr, cciArr):
	n = 14
	tpArr = []
	for i in range(0,len(closeArr)):
		tpArr.append((closeArr[i] + highArr[i] + lowArr[i]) / 3)
	maClose = MA(closeArr, n)

	mdArr = []
	for i in range(0,len(closeArr)):
		mdArr.append(maClose[i] - closeArr[i])

	maMD = MA(mdArr, n)
	for i in range(0,len(closeArr)):
		cci = 0
		if(maMD[i] > 0):
			cci = (tpArr[i] - maClose[i]) / (maMD[i] * 0.015)
		cciArr.append(cci)
	return cciArr

#获取TRIX的数据
#ticks:数据
def getTRIXData(ticks, trixArr, matrixArr):
	mtrArr = []
	n = 12
	m = 9

	emaArr1 = []
	emaArr1.append(ticks[0])
	for i in range(1,len(ticks)):
		emaArr1.append(getEMA(12, ticks[i], emaArr1[i - 1]))

	emaArr2 = []
	emaArr2.append(emaArr1[0])
	for i in range(1,len(ticks)):
		emaArr2.append(getEMA(12, emaArr1[i], emaArr2[i - 1]))

	mtrArr.append(emaArr2[0])
	for i in range(1,len(ticks)):
		mtrArr.append(getEMA(12, emaArr2[i], mtrArr[i - 1]))

	ref = REF(mtrArr, 1)
	for i in range(0,len(ticks)):
		trix = 100 * (mtrArr[i] - ref[i]) / ref[i]
		trixArr.append(trix)
	matrixMa = MA(trixArr, m)
	for i in range(0, len(matrixMa)):
		matrixArr.append(matrixMa[i])

#绘制画线工具
#chart:K线
#pPaint:绘图对象
#clipRect:裁剪区域
def drawChartPlot(chart, pPaint, clipRect):
	if(len(chart.m_plots)):
		paint = FCPaint()
		paint.m_drawHDC = pPaint.m_innerHDC
		paint.m_memBM = pPaint.m_innerBM
		paint.m_scaleFactorX = pPaint.m_scaleFactorX
		paint.m_scaleFactorY = pPaint.m_scaleFactorY
		divHeight = getCandleDivHeight(chart)
		cRect = FCRect(chart.m_leftVScaleWidth, 0, chart.m_size.cx, divHeight)
		paint.beginClip(cRect)
		for i in range(0,len(chart.m_plots)):
			plot = chart.m_plots[i]
			m_index1 = 0
			m_index2 = 0
			m_index3 = 0
			mpx1 = 0
			mpy1 = 0
			mpx2 = 0
			mpy2 = 0
			mpx3 = 0
			mpy3 = 0
			if(plot.m_plotType == "LRLine" or plot.m_plotType == "LRChannel" or plot.m_plotType == "LRBand"):
				listValue = []
				m_index1 = getChartIndexByDate(chart, plot.m_key1)
				m_index2 = getChartIndexByDate(chart, plot.m_key2)
				minIndex = min(m_index1, m_index2)
				maxIndex = max(m_index1, m_index2)
				for j in range(minIndex,maxIndex + 1):
					listValue.append(chart.m_data[j].m_close)
				linearRegressionEquation(listValue)
				plot.m_value1 = m_b_Chart
				plot.m_value2 = m_k_Chart * (maxIndex - minIndex + 1) + m_b_Chart
			elif(plot.m_plotType == "BoxLine" or plot.m_plotType == "TironeLevels" or plot.m_plotType == "QuadrantLines"):
				getCandleRange(chart, plot)
				nHigh = m_nHigh_Chart
				nLow = m_nLow_Chart
				m_index1 = getChartIndexByDate(chart, plot.m_key1)
				m_index2 = getChartIndexByDate(chart, plot.m_key2)
				plot.m_key1 = getChartDateByIndex(chart, min(m_index1, m_index2))
				plot.m_key2 = getChartDateByIndex(chart, max(m_index1, m_index2))
				plot.m_value1 = nHigh
				plot.m_value2 = nLow
			if(plot.m_key1 != None):
				m_index1 = getChartIndexByDate(chart, plot.m_key1)
				mpx1 = getChartX(chart, m_index1)
				mpy1 = getChartY(chart, 0, plot.m_value1)
				if (chart.m_sPlot == plot):
					paint.fillEllipse(plot.m_pointColor, mpx1 - m_plotPointSize_Chart, mpy1 - m_plotPointSize_Chart, mpx1 + m_plotPointSize_Chart, mpy1 + m_plotPointSize_Chart)
			if(plot.m_key2 != None):
				m_index2 = getChartIndexByDate(chart, plot.m_key2)
				mpx2 = getChartX(chart, m_index2)
				mpy2 = getChartY(chart, 0, plot.m_value2)
				if (chart.m_sPlot == plot):
					paint.fillEllipse(plot.m_pointColor, mpx2 - m_plotPointSize_Chart, mpy2 - m_plotPointSize_Chart, mpx2 + m_plotPointSize_Chart, mpy2 + m_plotPointSize_Chart)
			if(plot.m_key3 != None):
				m_index3 = getChartIndexByDate(chart, plot.m_key3)
				mpx3 = getChartX(chart, m_index3)
				mpy3 = getChartY(chart, 0, plot.m_value3)
				if (chart.m_sPlot == plot):
					paint.fillEllipse(plot.m_pointColor, mpx3 - m_plotPointSize_Chart, mpy3 - m_plotPointSize_Chart, mpx3 + m_plotPointSize_Chart, mpy3 + m_plotPointSize_Chart)
			if(plot.m_plotType == "Line"):
				lineXY(mpx1, mpy1, mpx2, mpy2, 0, 0)
				if(mpx2 == mpx1):
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, 0, mpx1, divHeight)
				else:
					newX1 = chart.m_leftVScaleWidth
					newY1 = newX1 * m_k_Chart + m_b_Chart
					newX2 = chart.m_size.cx - chart.m_rightVScaleWidth
					newY2 = newX2 * m_k_Chart + m_b_Chart
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, newX1, newY1, newX2, newY2)
			elif (plot.m_plotType == "ArrowSegment"):
				ARROW_Size = 24
				slopy = 0
				cosy = 0
				siny = 0
				slopy = atan2(mpy1 - mpy2, mpx1 - mpx2)
				cosy = cos(slopy)
				siny = sin(slopy)
				ptPoint = FCPoint()
				ptPoint.x = mpx2
				ptPoint.y = mpy2
				pts = []
				pts.append(FCPoint())
				pts.append(FCPoint())
				pts.append(FCPoint())
				pts[0] = ptPoint
				pts[1].x = ptPoint.x + (ARROW_Size * cosy - (ARROW_Size / 2.0 * siny) + 0.5)
				pts[1].y = ptPoint.y + (ARROW_Size * siny + (ARROW_Size / 2.0 * cosy) + 0.5)
				pts[2].x = ptPoint.x + (ARROW_Size * cosy + ARROW_Size / 2.0 * siny + 0.5)
				pts[2].y = ptPoint.y - (ARROW_Size / 2.0 * cosy - ARROW_Size * siny + 0.5)
				ARROW_Size = 20
				ptPoint2 = FCPoint()
				ptPoint2.x = mpx2
				ptPoint2.y = mpy2
				pts2 = []
				pts2.append(FCPoint())
				pts2.append(FCPoint())
				pts2.append(FCPoint())
				pts2[0] = ptPoint2
				pts2[1].x = ptPoint2.x + (ARROW_Size * cosy - (ARROW_Size / 2.0 * siny) + 0.5)
				pts2[1].y = ptPoint2.y + (ARROW_Size * siny + (ARROW_Size / 2.0 * cosy) + 0.5)
				pts2[2].x = ptPoint2.x + (ARROW_Size * cosy + ARROW_Size / 2.0 * siny + 0.5)
				pts2[2].y = ptPoint2.y - (ARROW_Size / 2.0 * cosy - ARROW_Size * siny + 0.5)
				lineXY(pts2[1].x, pts2[1].y, pts2[2].x, pts2[2].y, 0, 0)
				newX1 = 0
				newY1 = 0
				newX2 = 0
				newY2 = 0

				if (pts2[1].x > pts2[2].x):
					newX1 = pts2[2].x + (pts2[1].x - pts2[2].x) / 3
					newX2 = pts2[2].x + (pts2[1].x - pts2[2].x) * 2 / 3
				else:
					newX1 = pts2[1].x + (pts2[2].x - pts2[1].x) / 3
					newX2 = pts2[1].x + (pts2[2].x - pts2[1].x) * 2 / 3
				if (m_k_Chart == 0 and m_b_Chart == 0):
					if (pts2[1].y > pts2[2].y):
						newY1 = pts2[2].y + (pts2[1].y - pts2[2].y) / 3
						newY2 = pts2[2].y + (pts2[1].y - pts2[2].y) * 2 / 3
					else:
						newY1 = pts2[1].y + (pts2[2].y - pts2[1].y) / 3
						newY2 = pts2[1].y + (pts2[2].y - pts2[1].y) * 2 / 3
				else:
					newY1 = (m_k_Chart * newX1) + m_b_Chart
					newY2 = (m_k_Chart * newX2) + m_b_Chart
				pts2[1].x = newX1
				pts2[1].y = newY1
				pts2[2].x = newX2
				pts2[2].y = newY2
				drawPoints = []
				drawPoints.append(FCPoint())
				drawPoints.append(FCPoint())
				drawPoints.append(FCPoint())
				drawPoints.append(FCPoint())
				drawPoints.append(FCPoint())
				drawPoints.append(FCPoint())
				drawPoints[0].x = ptPoint.x
				drawPoints[0].y = ptPoint.y
				drawPoints[1].x = pts[1].x
				drawPoints[1].y = pts[1].y
				if (mpy1 >= mpy2):
					drawPoints[2].x = pts2[1].x
					drawPoints[2].y = pts2[1].y
				else:
					drawPoints[2].x = pts2[2].x
					drawPoints[2].y = pts2[2].y
				drawPoints[3].x = mpx1
				drawPoints[3].y = mpy1
				if (mpy1 >= mpy2):
					drawPoints[4].x = pts2[2].x
					drawPoints[4].y = pts2[2].y
				else:
					drawPoints[4].x = pts2[1].x
					drawPoints[4].y = pts2[1].y
				drawPoints[5].x = pts[2].x
				drawPoints[5].y = pts[2].y

				paint.fillPolygon(plot.m_lineColor, drawPoints)
			elif(plot.m_plotType == "AngleLine"):
				lineXY(mpx1, mpy1, mpx2, mpy2, 0, 0)
				if(mpx2 == mpx1):
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, 0, mpx1, divHeight)
				else:
					newX1 = chart.m_leftVScaleWidth
					newY1 = newX1 * m_k_Chart + m_b_Chart
					newX2 = chart.m_size.cx - chart.m_rightVScaleWidth
					newY2 = newX2 * m_k_Chart + m_b_Chart
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, newX1, newY1, newX2, newY2)
				lineXY(mpx1, mpy1, mpx3, mpy3, 0, 0)
				if(mpx3 == mpx1):
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, 0, mpx1, divHeight)
				else:
					newX1 = chart.m_leftVScaleWidth
					newY1 = newX1 * m_k_Chart + m_b_Chart
					newX2 = chart.m_size.cx - chart.m_rightVScaleWidth
					newY2 = newX2 * m_k_Chart + m_b_Chart
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, newX1, newY1, newX2, newY2)
			elif(plot.m_plotType == "Parallel"):
				lineXY(mpx1, mpy1, mpx2, mpy2, 0, 0)
				if(mpx2 == mpx1):
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, 0, mpx1, divHeight)
				else:
					newX1 = chart.m_leftVScaleWidth
					newY1 = newX1 * m_k_Chart + m_b_Chart
					newX2 = chart.m_size.cx - chart.m_rightVScaleWidth
					newY2 = newX2 * m_k_Chart + m_b_Chart
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, newX1, newY1, newX2, newY2)
					newB = mpy3 - m_k_Chart * mpx3
				if(mpx2 == mpx1):
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx3, 0, mpx3, divHeight)
				else:
					newX1 = chart.m_leftVScaleWidth
					newY1 = newX1 * m_k_Chart + newB
					newX2 = chart.m_size.cx - chart.m_rightVScaleWidth
					newY2 = newX2 * m_k_Chart + newB
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, newX1, newY1, newX2, newY2)
			elif(plot.m_plotType == "Percent"):
				listValue = getPercentParams(mpy1, mpy2)
				texts = []
				texts.append("0%")
				texts.append("25%")
				texts.append("50%")
				texts.append("75%")
				texts.append("100%")
				for j in range(0,len(listValue)):
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, chart.m_leftVScaleWidth, listValue[j], chart.m_size.cx - chart.m_rightVScaleWidth, listValue[j])
					tSize = paint.textSize(texts[j], chart.m_font)
					paint.drawText(texts[j], chart.m_textColor, chart.m_font, chart.m_leftVScaleWidth + 5, listValue[j] - tSize.cy - 2)
			elif(plot.m_plotType == "FiboTimezone"):
				fValue = 1
				aIndex = m_index1
				pos = 1
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, 0, mpx1, divHeight)
				tSize = paint.textSize("1", chart.m_font)
				paint.drawText("1", chart.m_textColor, chart.m_font, mpx1, divHeight - tSize.cy)
				while (aIndex + fValue <= chart.m_lastVisibleIndex):
					fValue = fibonacciValue(pos)
					newIndex = aIndex + fValue
					newX = getChartX(chart, newIndex)
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, newX, 0, newX, divHeight)
					tSize = paint.textSize(str(fValue), chart.m_font)
					paint.drawText(str(fValue), chart.m_textColor, chart.m_font, newX, divHeight - tSize.cy)
					pos = pos + 1
			elif(plot.m_plotType == "SpeedResist"):
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx2, mpy2)
				if (mpx1 != mpx2 and mpy1 != mpy2):
					firstP = FCPoint(mpx2, mpy2 - (mpy2 - mpy1) / 3)
					secondP = FCPoint(mpx2, mpy2 - (mpy2 - mpy1) * 2 / 3)
					startP = FCPoint(mpx1, mpy1)
					fK = 0
					fB = 0
					sK = 0
					sB = 0
					lineXY(startP.x, startP.y, firstP.x, firstP.y, 0, 0)
					fK = m_k_Chart
					fb = m_b_Chart
					lineXY(startP.x, startP.y, secondP.x, secondP.y, 0, 0)
					sK = m_k_Chart
					sB = m_b_Chart
					newYF = 0
					newYS = 0
					newX = 0
					if (mpx2 > mpx1):
						newYF = fK * (chart.m_size.cx - chart.m_rightVScaleWidth) + fB
						newYS = sK * (chart.m_size.cx - chart.m_rightVScaleWidth) + sB
						newX = (chart.m_size.cx - chart.m_rightVScaleWidth)
					else:
						newYF = fB
						newYS = sB
					newX = chart.m_leftVScaleWidth
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, startP.x, startP.y, newX, newYF)
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, startP.x, startP.y, newX, newYS)
			elif(plot.m_plotType == "FiboFanline"):
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx2, mpy2)
				if (mpx1 != mpx2 and mpy1 != mpy2):
					firstP = FCPoint(mpx2, mpy2 - (mpy2 - mpy1) * 0.382)
					secondP = FCPoint(mpx2, mpy2 - (mpy2 - mpy1) * 0.5)
					thirdP = FCPoint(mpx2, mpy2 - (mpy2 - mpy1) * 0.618)
					startP = FCPoint(mpx1, mpy1)
					listP = []
					listP.append(firstP)
					listP.append(secondP)
					listP.append(thirdP);
					listSize = len(listP)
					for j in range(0,listSize):
						lineXY(startP.x, startP.y, listP[j].x, listP[j].y, 0, 0)
						newX = 0;
						newY = 0
						if (mpx2 > mpx1):
							newY = m_k_Chart * (chart.m_size.cx - chart.m_rightVScaleWidth) + m_b_Chart
							newX = (chart.m_size.cx - chart.m_rightVScaleWidth)
						else:
							newY = m_b_Chart
							newX = chart.m_leftVScaleWidth
						paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, startP.x, startP.y, newX, newY)
			elif(plot.m_plotType == "LRLine"):
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx2, mpy2)
			elif(plot.m_plotType == "LRBand"):
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx2, mpy2)
				getLRBandRange(chart, plot, m_k_Chart, m_b_Chart)
				mpy1 = getChartY(chart, 0, plot.m_value1 + m_upSubValue)
				mpy2 = getChartY(chart, 0, plot.m_value2 + m_upSubValue)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx2, mpy2)
				mpy1 = getChartY(chart, 0, plot.m_value1 - m_downSubValue)
				mpy2 = getChartY(chart, 0, plot.m_value2 - m_downSubValue)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx2, mpy2)
			elif(plot.m_plotType == "LRChannel"):
				getLRBandRange(chart, plot, m_k_Chart, m_b_Chart)
				lineXY(mpx1, mpy1, mpx2, mpy2, 0, 0)
				rightX = chart.m_size.cx - chart.m_rightVScaleWidth
				rightY = rightX * m_k_Chart + m_b_Chart
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, rightX, rightY)
				mpy1 = getChartY(chart, 0, plot.m_value1 + m_upSubValue)
				mpy2 = getChartY(chart, 0, plot.m_value2 + m_upSubValue)
				lineXY(mpx1, mpy1, mpx2, mpy2, 0, 0)
				rightY = rightX * m_k_Chart + m_b_Chart
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, rightX, rightY)
				mpy1 = getChartY(chart, 0, plot.m_value1 - m_downSubValue)
				mpy2 = getChartY(chart, 0, plot.m_value2 - m_downSubValue)
				lineXY(mpx1, mpy1, mpx2, mpy2, 0, 0)
				rightY = rightX * m_k_Chart + m_b_Chart
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, rightX, rightY)
			elif(plot.m_plotType == "Segment"):
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx2, mpy2)
			elif(plot.m_plotType == "Ray"):
				lineXY(mpx1, mpy1, mpx2, mpy2, 0, 0)
				if (m_k_Chart != 0 or m_b_Chart != 0):
					leftX = chart.m_leftVScaleWidth
					leftY = leftX * m_k_Chart + m_b_Chart
					rightX = chart.m_size.cx - chart.m_rightVScaleWidth
					rightY = rightX * m_k_Chart + m_b_Chart
					if (mpx1 >= mpx2):
						paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, leftX, leftY, mpx1, mpy1)
					else:
						paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, rightX, rightY)
				else:
					if (mpy1 >= mpy2):
						paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx1, 0)
					else:
						paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx1, divHeight)
			elif(plot.m_plotType == "Triangle"):
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx2, mpy2)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx2, mpy2, mpx3, mpy3)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx3, mpy3)
			elif(plot.m_plotType == "SymmetricTriangle"):
				if (mpx2 != mpx1):
					a = (mpy2 - mpy1) / (mpx2 - mpx1)
					b = mpy1 - a * mpx1
					c = -a
					d = mpy3 - c * mpx3
					leftX = chart.m_leftVScaleWidth
					leftY = leftX * a + b
					rightX = chart.m_size.cx - chart.m_rightVScaleWidth
					rightY = rightX * a + b
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, leftX, leftY, rightX, rightY)
					leftY = leftX * c + d
					rightY = rightX * c + d
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, leftX, leftY, rightX, rightY)
				else:
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, 0, mpx1, divHeight)
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx3, 0, mpx3, divHeight)
			elif (plot.m_plotType == "Rect"):
				sX1 = min(mpx1, mpx2)
				sY1 = min(mpy1, mpy2)
				sX2 = max(mpx1, mpx2)
				sY2 = max(mpy1, mpy2)
				paint.drawRect(plot.m_lineColor, plot.m_lineWidth, 0, sX1, sY1, sX2, sY2)
			elif(plot.m_plotType == "Cycle"):
				r = math.sqrt(abs((mpx2 - mpx1) * (mpx2 - mpx1) + (mpy2 - mpy1) * (mpy2 - mpy1)))
				paint.drawEllipse(plot.m_lineColor, plot.m_lineWidth, 0, mpx1 - r, mpy1 - r, mpx1 + r, mpy1 + r)
			elif(plot.m_plotType == "CircumCycle"):
				ellipseOR(mpx1, mpy1, mpx2, mpy2, mpx3, mpy3)
				paint.drawEllipse(plot.m_lineColor, plot.m_lineWidth, 0, m_oX_Chart - m_r_Chart, m_oY_Chart - m_r_Chart, m_oX_Chart + m_r_Chart, m_oY_Chart + m_r_Chart)
			elif(plot.m_plotType == "Ellipse"):
				x1 = 0
				y1 = 0
				x2 = 0
				y2 = 0
				if(mpx1 <= mpx2):
					x1 = mpx2
					y1 = mpy2
					x2 = mpx1
					y2 = mpy1
				else:
					x1 = mpx1
					y1 = mpy1
					x2 = mpx2
					y2 = mpy2	
				x = x1 - (x1 - x2)
				y = 0
				width = (x1 - x2) * 2
				height = 0
				if (y1 >= y2):
					height = (y1 - y2) * 2
				else:
					height = (y2 - y1) * 2
				y = y2 - height / 2
				paint.drawEllipse(plot.m_lineColor, plot.m_lineWidth, 0, x, y, x + width, y + height)
			elif(plot.m_plotType == "ParalleGram"):
				parallelogram(mpx1, mpy1, mpx2, mpy2, mpx3, mpy3)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx1, mpy1, mpx2, mpy2)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx2, mpy2, mpx3, mpy3)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, mpx3, mpy3, m_x4_Chart, m_y4_Chart)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, m_x4_Chart, m_y4_Chart, mpx1, mpy1)
			elif(plot.m_plotType == "BoxLine"):
				sX1 = min(mpx1, mpx2)
				sY1 = min(mpy1, mpy2)
				sX2 = max(mpx1, mpx2)
				sY2 = max(mpy1, mpy2)
				paint.drawRect(plot.m_lineColor, plot.m_lineWidth, 0, sX1, sY1, sX2, sY2)
				bSize = paint.textSize("COUNT:" + str(abs(m_index2 - m_index1) + 1), chart.m_font)
				paint.drawText("COUNT:" + str(abs(m_index2 - m_index1) + 1), chart.m_textColor, chart.m_font, sX1 + 2, sY1 + 2)
				closeList = []
				for j in range(m_index1,m_index2 + 1):
					closeList.append(chart.m_data[j].m_close)
				avgClose = avgValue(closeList)
				closeY = getChartY(chart, 0, avgClose)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 1, sX1, closeY, sX2, closeY)
				drawAvg = "AVG:" + toFixed(avgClose, chart.m_candleDigit)
				tSize = paint.textSize(drawAvg, chart.m_font)
				paint.drawText(drawAvg, chart.m_textColor, chart.m_font, sX1 + 2, closeY - tSize.cy - 2)
			elif(plot.m_plotType == "TironeLevels"):
				sX1 = min(mpx1, mpx2)
				sY1 = min(mpy1, mpy2)
				sX2 = max(mpx1, mpx2)
				sY2 = max(mpy1, mpy2)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, sX1, sY1, sX2, sY1)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, sX1, sY2, sX2, sY2)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, [5, 5], sX1 + (sX2 - sX1) / 2, sY1, sX1 + (sX2 - sX1) / 2, sY2)
				t1 = m_nHigh_Chart
				t2 = m_nHigh_Chart - (m_nHigh_Chart - m_nLow_Chart) / 3
				t3 = m_nHigh_Chart - (m_nHigh_Chart - m_nLow_Chart) / 2
				t4 = m_nHigh_Chart - 2 * (m_nHigh_Chart - m_nLow_Chart) / 3
				t5 = m_nLow_Chart
				tList = []
				tList.append(t2)
				tList.append(t3)
				tList.append(t4)
				for j in range(0,len(tList)):
					y = getChartY(chart, 0, tList[j])
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, [5,5], chart.m_leftVScaleWidth, y, chart.m_size.cx - chart.m_rightVScaleWidth, y)
					strText = toFixed(tList[j], chart.m_candleDigit)
					tSize = paint.textSize(strText, chart.m_font)
					paint.drawText(strText, chart.m_textColor, chart.m_font, chart.m_leftVScaleWidth + 2, y - tSize.cy - 2)
			elif(plot.m_plotType == "QuadrantLines"):
				sX1 = min(mpx1, mpx2)
				sY1 = min(mpy1, mpy2)
				sX2 = max(mpx1, mpx2)
				sY2 = max(mpy1, mpy2)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, sX1, sY1, sX2, sY1)
				paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, sX1, sY2, sX2, sY2)
				t1 = m_nHigh_Chart
				t2 = m_nHigh_Chart - (m_nHigh_Chart - m_nLow_Chart) / 4
				t3 = m_nHigh_Chart - (m_nHigh_Chart - m_nLow_Chart) / 2
				t4 = m_nHigh_Chart - 3 * (m_nHigh_Chart - m_nLow_Chart) / 4
				t5 = m_nLow_Chart
				tList = []
				tList.append(t2)
				tList.append(t3)
				tList.append(t4)
				for j in range(0,len(tList)):
					y = getChartY(chart, 0, tList[j])
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, sX1, y, sX2, y)
			elif(plot.m_plotType == "GoldenRatio"):
				sX1 = min(mpx1, mpx2)
				sY1 = min(mpy1, mpy2)
				sX2 = max(mpx1, mpx2)
				sY2 = max(mpy1, mpy2)
				ranges = []
				ranges.append(0);
				ranges.append(0.236);
				ranges.append(0.382);
				ranges.append(0.5);
				ranges.append(0.618);
				ranges.append(0.809);
				ranges.append(1);
				ranges.append(1.382);
				ranges.append(1.618);
				ranges.append(2);
				ranges.append(2.382);
				ranges.append(2.618);
				minValue = min(plot.m_value1, plot.m_value2)
				maxValue = max(plot.m_value1, plot.m_value2)
				for j in range(0,len(ranges)):
					newY = sY2 + (sY1 - sY2) * (1 - ranges[j])
					if(sY1 <= sY2):
						newY = sY1 + (sY2 - sY1) * ranges[j]
					paint.drawLine(plot.m_lineColor, plot.m_lineWidth, 0, chart.m_leftVScaleWidth, newY, chart.m_size.cx - chart.m_rightVScaleWidth, newY)
					newPoint = FCPoint(0, newY)
					value = getCandleDivValue(chart, newPoint)
					strText = toFixed(value, chart.m_candleDigit)
					tSize = paint.textSize(strText, chart.m_font)
					paint.drawText(strText, chart.m_textColor, chart.m_font, chart.m_leftVScaleWidth + 2, newY - tSize.cy - 2)
		rect = FCRect(0, 0, cRect.right - cRect.left, cRect.bottom - cRect.top)
		win32gui.StretchBlt(paint.m_drawHDC, int(cRect.left), int(cRect.top), int(cRect.right - cRect.left), int(cRect.bottom - cRect.top), paint.m_innerHDC, int(cRect.left - rect.left), int(cRect.top - rect.top), int(cRect.right - cRect.left), int(cRect.bottom - cRect.top), SRCPAINT)
		if(paint.m_innerHDC != None):
			win32gui.DeleteObject(paint.m_innerHDC)
			paint.m_innerHDC = None
		if(paint.m_innerBM != None):
			win32gui.DeleteObject(paint.m_innerBM)
			paint.m_innerBM = None

#选中直线
#chart: K线
#mp:坐标
def selectPlot(chart, mp):
	sPlot = None
	chart.m_startMovePlot = FALSE
	chart.m_selectPlotPoint = -1
	for i in range(0, len(chart.m_plots)):
		plot = chart.m_plots[i]
		m_index1 = 0
		m_index2 = 0
		m_index3 = 0
		mpx1 = 0
		mpy1 = 0
		mpx2 = 0
		mpy2 = 0
		mpx3 = 0
		mpy3 = 0
		if(plot.m_key1 != None):
			m_index1 = getChartIndexByDate(chart, plot.m_key1)
			mpx1 = getChartX(chart, m_index1)
			mpy1 = getChartY(chart, 0, plot.m_value1)
			if(mp.x >= mpx1 - m_plotPointSize_Chart and mp.x <= mpx1 + m_plotPointSize_Chart and mp.y >= mpy1 - m_plotPointSize_Chart and mp.y <= mpy1 + m_plotPointSize_Chart):
				sPlot = plot
				chart.m_selectPlotPoint = 0
				break
		if(plot.m_key2 != None):
			m_index2 = getChartIndexByDate(chart, plot.m_key2)
			mpx2 = getChartX(chart, m_index2)
			mpy2 = getChartY(chart, 0, plot.m_value2)
			if(mp.x >= mpx2 - m_plotPointSize_Chart and mp.x <= mpx2 + m_plotPointSize_Chart and mp.y >= mpy2 - m_plotPointSize_Chart and mp.y <= mpy2 + m_plotPointSize_Chart):
				sPlot = plot
				chart.m_selectPlotPoint = 1
				break
		if(plot.m_key3 != None):
			m_index3 = getChartIndexByDate(chart, plot.m_key3)
			mpx3 = getChartX(chart, m_index3)
			mpy3 = getChartY(chart, 0, plot.m_value3)
			if(mp.x >= mpx3 - m_plotPointSize_Chart and mp.x <= mpx3 + m_plotPointSize_Chart and mp.y >= mpy3 - m_plotPointSize_Chart and mp.y <= mpy3 + m_plotPointSize_Chart):
				sPlot = plot
				chart.m_selectPlotPoint = 2
				break

		if(chart.m_selectPlotPoint == -1):
			if(plot.m_plotType == "Line"):
				chart.m_startMovePlot = selectLine(mp, mpx1, mpy1, mpx2, mpy2)
			elif (plot.m_plotType == "ArrowSegment"):
				chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, mpx2, mpy2)
			elif(plot.m_plotType == "AngleLine"):
				chart.m_startMovePlot = selectLine(mp, mpx1, mpy1, mpx2, mpy2)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectLine(mp, mpx1, mpy1, mpx3, mpy3)
			elif(plot.m_plotType == "Parallel"):
				chart.m_startMovePlot = selectLine(mp, mpx1, mpy1, mpx2, mpy2)
				if (chart.m_startMovePlot == FALSE):
					lineXY(mpx1, mpy1, mpx2, mpy2, 0, 0)
					newB = mpy3 - m_k_Chart * mpx3
					if(mpx2 == mpx1):
						if(mp.x >= mpx3 - m_plotPointSize_Chart and mp.x <= mpx3 + m_plotPointSize_Chart):
							chart.m_startMovePlot = TRUE
					else:
						newX1 = chart.m_leftVScaleWidth
						newY1 = newX1 * m_k_Chart + newB
						newX2 = chart.m_size.cx - chart.m_rightVScaleWidth
						newY2 = newX2 * m_k_Chart + newB
						chart.m_startMovePlot = selectLine(mp, newX1, newY1, newX2, newY2)
			elif(plot.m_plotType == "LRLine"):
				chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, mpx2, mpy2)
			elif(plot.m_plotType == "Segment"):
				chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, mpx2, mpy2)
			elif(plot.m_plotType == "Ray"):
				chart.m_startMovePlot = selectRay(mp, mpx1, mpy1, mpx2, mpy2)
			elif(plot.m_plotType == "Triangle"):
				chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, mpx2, mpy2)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectSegment(mp, mpx2, mpy2, mpx3, mpy3)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, mpx3, mpy3)
			elif (plot.m_plotType == "SymmetricTriangle"):
				if (mpx2 != mpx1):
					a = (mpy2 - mpy1) / (mpx2 - mpx1)
					b = mpy1 - a * mpx1
					c = -a
					d = mpy3 - c * mpx3
					leftX = chart.m_leftVScaleWidth
					leftY = leftX * a + b
					rightX = chart.m_size.cx - chart.m_rightVScaleWidth
					rightY = rightX * a + b
					chart.m_startMovePlot = selectSegment(mp, leftX, leftY, rightX, rightY)
					if (chart.m_startMovePlot == FALSE):
						leftY = leftX * c + d
						rightY = rightX * c + d
						chart.m_startMovePlot = selectSegment(mp, leftX, leftY, rightX, rightY)
				else:
					chart.m_startMovePlot = selectSegment(mp, mpx1, 0, mpx1, divHeight)
					if (chart.m_startMovePlot == FALSE):		
						chart.m_startMovePlot = selectSegment(mp, mpx3, 0, mpx3, divHeight)
			elif (plot.m_plotType == "Rect"):
				sX1 = min(mpx1, mpx2)
				sY1 = min(mpy1, mpy2)
				sX2 = max(mpx1, mpx2)
				sY2 = max(mpy1, mpy2)
				chart.m_startMovePlot = selectSegment(mp, sX1, sY1, sX2, sY1)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectSegment(mp, sX2, sY1, sX2, sY2)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectSegment(mp, sX1, sY2, sX2, sY2)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectSegment(mp, sX1, sY1, sX1, sY2)
			elif(plot.m_plotType == "BoxLine"):
				sX1 = min(mpx1, mpx2)
				sY1 = min(mpy1, mpy2)
				sX2 = max(mpx1, mpx2)
				sY2 = max(mpy1, mpy2)
				chart.m_startMovePlot = selectSegment(mp, sX1, sY1, sX2, sY1)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectSegment(mp, sX2, sY1, sX2, sY2)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectSegment(mp, sX1, sY2, sX2, sY2)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectSegment(mp, sX1, sY1, sX1, sY2)
			elif(plot.m_plotType == "TironeLevels"):
				sX1 = min(mpx1, mpx2)
				sY1 = min(mpy1, mpy2)
				sX2 = max(mpx1, mpx2)
				sY2 = max(mpy1, mpy2)
				chart.m_startMovePlot = selectSegment(mp, sX1, sY1, sX2, sY1)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectSegment(mp, sX1, sY2, sX2, sY2)
			elif(plot.m_plotType == "QuadrantLines"):
				sX1 = min(mpx1, mpx2)
				sY1 = min(mpy1, mpy2)
				sX2 = max(mpx1, mpx2)
				sY2 = max(mpy1, mpy2)
				chart.m_startMovePlot = selectSegment(mp, sX1, sY1, sX2, sY1)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectSegment(mp, sX1, sY2, sX2, sY2)
			elif(plot.m_plotType == "GoldenRatio"):
				sX1 = min(mpx1, mpx2)
				sY1 = min(mpy1, mpy2)
				sX2 = max(mpx1, mpx2)
				sY2 = max(mpy1, mpy2)
				ranges = []
				ranges.append(0)
				ranges.append(0.236)
				ranges.append(0.382)
				ranges.append(0.5)
				ranges.append(0.618)
				ranges.append(0.809)
				ranges.append(1)
				ranges.append(1.382)
				ranges.append(1.618)
				ranges.append(2)
				ranges.append(2.382)
				ranges.append(2.618)
				minValue = min(plot.m_value1, plot.m_value2)
				maxValue = max(plot.m_value1, plot.m_value2)
				for j in range(0,len(ranges)):
					newY = sY2 + (sY1 - sY2) * (1 - ranges[j])
					if(sY1 <= sY2):
						newY = sY1 + (sY2 - sY1) * ranges[j]
					chart.m_startMovePlot = selectSegment(mp, chart.m_leftVScaleWidth, newY, chart.m_size.cx - chart.m_rightVScaleWidth, newY)
					if (chart.m_startMovePlot):
						break
			elif(plot.m_plotType == "Cycle"):
				r = math.sqrt(abs((mpx2 - mpx1) * (mpx2 - mpx1) + (mpy2 - mpy1) * (mpy2 - mpy1)))
				roundValue = (mp.x - mpx1) * (mp.x - mpx1) + (mp.y - mpy1) * (mp.y - mpy1)
				if (roundValue / (r * r) >= 0.9 and roundValue / (r * r) <= 1.1):
					chart.m_startMovePlot = TRUE
			elif(plot.m_plotType == "CircumCycle"):
				ellipseOR(mpx1, mpy1, mpx2, mpy2, mpx3, mpy3)
				roundValue = (mp.x - m_oX_Chart) * (mp.x - m_oX_Chart) + (mp.y - m_oY_Chart) * (mp.y - m_oY_Chart)
				if (roundValue / (m_r_Chart * m_r_Chart) >= 0.9 and roundValue / (m_r_Chart * m_r_Chart) <= 1.1):
					chart.m_startMovePlot = TRUE
			elif(plot.m_plotType == "Ellipse"):
				x1 = 0
				y1 = 0
				x2 = 0
				y2 = 0
				if(mpx1 <= mpx2):
					x1 = mpx2
					y1 = mpy2
					x2 = mpx1
					y2 = mpy1
				else:
					x1 = mpx1
					y1 = mpy1
					x2 = mpx2
					y2 = mpy2
				x = x1 - (x1 - x2)
				y = 0
				width = (x1 - x2) * 2
				height = 0
				if (y1 >= y2):
					height = (y1 - y2) * 2
				else:
					height = (y2 - y1) * 2
				y = y2 - height / 2
				a = width / 2
				b = height / 2
				chart.m_startMovePlot = ellipseHasPoint(mp.x, mp.y, x + (width / 2), y + (height / 2), a, b)
			elif(plot.m_plotType == "LRBand"):
				chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, mpx2, mpy2)
				if (chart.m_startMovePlot == FALSE):
					listValue = []
					minIndex = min(m_index1, m_index2)
					maxIndex = max(m_index1, m_index2)
					for j in range(minIndex,maxIndex + 1):
						listValue.append(chart.m_data[j].m_close)
					linearRegressionEquation(listValue)
					getLRBandRange(chart, plot, m_k_Chart, m_b_Chart)
					mpy1 = getChartY(chart, 0, plot.m_value1 + m_upSubValue)
					mpy2 = getChartY(chart, 0, plot.m_value2 + m_upSubValue)
					chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, mpx2, mpy2)
					if (chart.m_startMovePlot == FALSE):
						mpy1 = getChartY(chart, 0, plot.m_value1 - m_downSubValue)
						mpy2 = getChartY(chart, 0, plot.m_value2 - m_downSubValue)
						chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, mpx2, mpy2)
			elif(plot.m_plotType == "LRChannel"):
				lineXY(mpx1, mpy1, mpx2, mpy2, 0, 0)
				rightX = chart.m_size.cx - chart.m_rightVScaleWidth
				rightY = rightX * m_k_Chart + m_b_Chart
				chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, rightX, rightY)
				if (chart.m_startMovePlot == FALSE):
					listValue = []
					minIndex = min(m_index1, m_index2)
					maxIndex = max(m_index1, m_index2)
					for j in range(minIndex,maxIndex + 1):
						listValue.append(chart.m_data[j].m_close)
					linearRegressionEquation(listValue)
					getLRBandRange(chart, plot, m_k_Chart, m_b_Chart)
					mpy1 = getChartY(chart, 0, plot.m_value1 + m_upSubValue)
					mpy2 = getChartY(chart, 0, plot.m_value2 + m_upSubValue)
					lineXY(mpx1, mpy1, mpx2, mpy2, 0, 0)
					rightY = rightX * m_k_Chart + m_b_Chart
					chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, rightX, rightY)
					if (chart.m_startMovePlot == FALSE):
						mpy1 = getChartY(chart, 0, plot.m_value1 - m_downSubValue)
						mpy2 = getChartY(chart, 0, plot.m_value2 - m_downSubValue)
						lineXY(mpx1, mpy1, mpx2, mpy2, 0, 0)
						rightY = rightX * m_k_Chart + m_b_Chart
						chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, rightX, rightY)
			elif(plot.m_plotType == "ParalleGram"):
				parallelogram(mpx1, mpy1, mpx2, mpy2, mpx3, mpy3)
				chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, mpx2, mpy2)
				if (chart.m_startMovePlot == FALSE):
					chart.m_startMovePlot = selectSegment(mp, mpx2, mpy2, mpx3, mpy3)
					if (chart.m_startMovePlot == FALSE):
						chart.m_startMovePlot = selectSegment(mp, mpx3, mpy3, m_x4_Chart, m_y4_Chart)
						if (chart.m_startMovePlot == FALSE):
							chart.m_startMovePlot = selectSegment(mp, m_x4_Chart, m_y4_Chart, mpx1, mpy1)
			elif(plot.m_plotType == "SpeedResist"):
				chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, mpx2, mpy2)
				if (chart.m_startMovePlot == FALSE):
					if (mpx1 != mpx2 and mpy1 != mpy2):
						firstP = FCPoint(mpx2, mpy2 - (mpy2 - mpy1) / 3)
						secondP = FCPoint(mpx2, mpy2 - (mpy2 - mpy1) * 2 / 3)
						startP = FCPoint(mpx1, mpy1)
						fK = 0
						fB = 0
						sK = 0
						sB = 0
						lineXY(startP.x, startP.y, firstP.x, firstP.y, 0, 0)
						fK = m_k_Chart
						fb = m_b_Chart
						lineXY(startP.x, startP.y, secondP.x, secondP.y, 0, 0)
						sK = m_k_Chart
						sB = m_b_Chart
						newYF = 0
						newYS = 0
						newX = 0
						if (mpx2 > mpx1):
							newYF = fK * (chart.m_size.cx - chart.m_rightVScaleWidth) + fB
							newYS = sK * (chart.m_size.cx - chart.m_rightVScaleWidth) + sB
							newX = (chart.m_size.cx - chart.m_rightVScaleWidth)
						else:
							newYF = fB
							newYS = sB
							newX = chart.m_leftVScaleWidth
						chart.m_startMovePlot = selectSegment(mp, startP.x, startP.y, newX, newYF)
						if (chart.m_startMovePlot == FALSE):
							chart.m_startMovePlot = selectSegment(mp, startP.x, startP.y, newX, newYS)
			elif(plot.m_plotType == "FiboFanline"):
				chart.m_startMovePlot = selectSegment(mp, mpx1, mpy1, mpx2, mpy2);
				if (chart.m_startMovePlot == FALSE):
					if (mpx1 != mpx2 and mpy1 != mpy2):
						firstP = FCPoint(mpx2, mpy2 - (mpy2 - mpy1) * 0.382)
						secondP = FCPoint(mpx2, mpy2 - (mpy2 - mpy1) * 0.5)
						thirdP = FCPoint(mpx2, mpy2 - (mpy2 - mpy1) * 0.618)
						startP = FCPoint(mpx1, mpy1)
						listP = []
						listP.append(firstP)
						listP.append(secondP)
						listP.append(thirdP)
						listSize = len(listP)
						for j in range(0,listSize):
							lineXY(startP.x, startP.y, listP[j].x, listP[j].y, 0, 0)
							newX = 0
							newY = 0
							if (mpx2 > mpx1):
								newY = m_k_Chart * (chart.m_size.cx - chart.m_rightVScaleWidth) + m_b_Chart
								newX = (chart.m_size.cx - chart.m_rightVScaleWidth)
							else:
								newY = m_b_Chart
								newX = chart.m_leftVScaleWidth
							chart.m_startMovePlot = selectSegment(mp, startP.x, startP.y, newX, newY)
							if (chart.m_startMovePlot):
								break
			elif(plot.m_plotType == "FiboTimezone"):
				fValue = 1
				aIndex = m_index1
				pos = 1
				divHeight = getCandleDivHeight(chart)
				chart.m_startMovePlot = selectSegment(mp, mpx1, 0, mpx1, divHeight)
				if (chart.m_startMovePlot == FALSE):
					while (aIndex + fValue <= chart.m_lastVisibleIndex):
						fValue = fibonacciValue(pos)
						newIndex = aIndex + fValue
						newX = getChartX(chart, newIndex)
						chart.m_startMovePlot = selectSegment(mp, newX, 0, newX, divHeight)
						if (chart.m_startMovePlot):
							break
						pos = pos + 1
			elif(plot.m_plotType == "Percent"):
				listValue = getPercentParams(mpy1, mpy2)
				for j in range(0, len(listValue)):
					chart.m_startMovePlot = selectSegment(mp, chart.m_leftVScaleWidth, listValue[j], chart.m_size.cx - chart.m_rightVScaleWidth, listValue[j])
					if (chart.m_startMovePlot):
						break
			if (chart.m_startMovePlot):
				sPlot = plot
				plot.m_startKey1 = plot.m_key1
				plot.m_startValue1 = plot.m_value1
				plot.m_startKey2 = plot.m_key2
				plot.m_startValue2 = plot.m_value2
				plot.m_startKey3 = plot.m_key3
				plot.m_startValue3 = plot.m_value3
				break
	return sPlot

#K线的鼠标移动方法
#chart: K线
#firstTouch:是否第一次触摸
#secondTouch:是否第二次触摸
#firstPoint:第一次触摸的坐标
#secondPoint:第二次触摸的坐标
def mouseMoveChart(chart, firstTouch, secondTouch, firstPoint, secondPoint):
	global m_firstIndexCache_Chart
	global m_firstTouchIndexCache_Chart
	global m_firstTouchPointCache_Chart
	global m_lastIndexCache_Chart
	global m_secondTouchIndexCache_Chart
	global m_secondTouchPointCache_Chart
	global m_mouseDownPoint_Chart
	global m_calculteMaxMin
	if(chart.m_data == None or len(chart.m_data) == 0):
		return
	mp = firstPoint
	chart.m_crossStopIndex = getChartIndex(chart, mp)
	chart.m_mousePosition = mp
	if(firstTouch and chart.m_sPlot != None):
		newIndex = getChartIndex(chart, mp)
		if(newIndex >= 0 and newIndex < len(chart.m_data)):
			newDate = getChartDateByIndex(chart, newIndex)
			newValue = getCandleDivValue(chart, mp)
			if (chart.m_selectPlotPoint == 0):
				chart.m_sPlot.m_key1 = newDate
				chart.m_sPlot.m_value1 = newValue
			elif (chart.m_selectPlotPoint == 1):
				chart.m_sPlot.m_key2 = newDate
				chart.m_sPlot.m_value2 = newValue
			elif (chart.m_selectPlotPoint == 2):
				chart.m_sPlot.m_key3 = newDate
				chart.m_sPlot.m_value3 = newValue
			elif (chart.m_startMovePlot):
				bValue = getCandleDivValue(chart, m_mouseDownPoint_Chart)
				bIndex = getChartIndex(chart, m_mouseDownPoint_Chart)
				if (chart.m_sPlot.m_key1 != None):
					chart.m_sPlot.m_value1 = chart.m_sPlot.m_startValue1 + (newValue - bValue)
					startIndex1 = getChartIndexByDate(chart, chart.m_sPlot.m_startKey1)
					newIndex1 = startIndex1 + (newIndex - bIndex)
					if(newIndex1 < 0):
						newIndex1 = 0
					elif(newIndex1 > len(chart.m_data) - 1):
						newIndex1 = len(chart.m_data) - 1
					chart.m_sPlot.m_key1 = getChartDateByIndex(chart, newIndex1)
				if (chart.m_sPlot.m_key2 != None):
					chart.m_sPlot.m_value2 = chart.m_sPlot.m_startValue2 + (newValue - bValue)
					startIndex2 = getChartIndexByDate(chart, chart.m_sPlot.m_startKey2)
					newIndex2 = startIndex2 + (newIndex - bIndex)
					if(newIndex2 < 0):
						newIndex2 = 0
					elif(newIndex2 > len(chart.m_data) - 1):
						newIndex2 = len(chart.m_data) - 1
					chart.m_sPlot.m_key2 = getChartDateByIndex(chart, newIndex2)
				if (chart.m_sPlot.m_key3 != None):
					chart.m_sPlot.m_value3 = chart.m_sPlot.m_startValue3 + (newValue - bValue)
					startIndex3 = getChartIndexByDate(chart, chart.m_sPlot.m_startKey3)
					newIndex3 = startIndex3 + (newIndex - bIndex)
					if(newIndex3 < 0):
						newIndex3 = 0
					elif(newIndex3 > len(chart.m_data) - 1):
						newIndex3 = len(chart.m_data) - 1
					chart.m_sPlot.m_key3 = getChartDateByIndex(chart, newIndex3)
		return
	if (firstTouch and secondTouch):
		if (firstPoint.x > secondPoint.x):
			m_firstTouchPointCache_Chart = secondPoint
			m_secondTouchPointCache_Chart = firstPoint
		else:
			m_firstTouchPointCache_Chart = firstPoint
			m_secondTouchPointCache_Chart = secondPoint
		if (m_firstTouchIndexCache_Chart == -1 or m_secondTouchIndexCache_Chart == -1):
			m_firstTouchIndexCache_Chart = getChartIndex(chart, m_firstTouchPointCache_Chart)
			m_secondTouchIndexCache_Chart = getChartIndex(chart, m_secondTouchPointCache_Chart)
			m_firstIndexCache_Chart = chart.m_firstVisibleIndex
			m_lastIndexCache_Chart = chart.m_lastVisibleIndex
	elif (firstTouch):
		m_secondTouchIndexCache_Chart = -1
		if (m_firstTouchIndexCache_Chart == -1):
			m_firstTouchPointCache_Chart = firstPoint
			m_firstTouchIndexCache_Chart = getChartIndex(chart, m_firstTouchPointCache_Chart)
			m_firstIndexCache_Chart = chart.m_firstVisibleIndex
			m_lastIndexCache_Chart = chart.m_lastVisibleIndex

	if (firstTouch and secondTouch):
		if (m_firstTouchIndexCache_Chart != -1 and m_secondTouchIndexCache_Chart != -1):
			fPoint = firstPoint
			sPoint = secondPoint
			if (firstPoint.x > secondPoint.x):
				fPoint = secondPoint
				sPoint = firstPoint
			subX = abs(sPoint.x - fPoint.x)
			subIndex = abs(m_secondTouchIndexCache_Chart - m_firstTouchIndexCache_Chart)
			if (subX > 0 and subIndex > 0) :
				newScalePixel = subX / subIndex
				if (newScalePixel >= 3):
					intScalePixel = int(newScalePixel)
					newScalePixel = intScalePixel
				if (newScalePixel != chart.m_hScalePixel):
					newFirstIndex = m_firstTouchIndexCache_Chart
					thisX = fPoint.x
					thisX -= newScalePixel
					while (thisX > chart.m_leftVScaleWidth + newScalePixel):
						newFirstIndex = newFirstIndex - 1
						if (newFirstIndex < 0):
							newFirstIndex = 0
							break
						thisX -= newScalePixel
					thisX = sPoint.x
					newSecondIndex = m_secondTouchIndexCache_Chart
					thisX += newScalePixel
					while (thisX < chart.m_size.cx - chart.m_rightVScaleWidth - newScalePixel):
						newSecondIndex = newSecondIndex + 1
						if (newSecondIndex > len(chart.m_data) - 1):
							newSecondIndex = len(chart.m_data) - 1
							break
						thisX += newScalePixel
					setChartVisibleIndex(chart, newFirstIndex, newSecondIndex)
					maxVisibleRecord = getChartMaxVisibleCount(chart, chart.m_hScalePixel, getChartWorkAreaWidth(chart))
					while ((maxVisibleRecord < chart.m_lastVisibleIndex - chart.m_firstVisibleIndex + 1) and (chart.m_lastVisibleIndex > chart.m_firstVisibleIndex)):
						chart.m_lastVisibleIndex = chart.m_lastVisibleIndex - 1
					checkChartLastVisibleIndex(chart)
					resetChartVisibleRecord(chart)
					if(m_calculteMaxMin != None):
						m_calculteMaxMin(chart)
					else:
						calculateChartMaxMin(chart)
	elif (firstTouch):
		subIndex = int((m_firstTouchPointCache_Chart.x - firstPoint.x) / chart.m_hScalePixel)
		if (chart.m_lastVisibleIndex + subIndex > len(chart.m_data) - 1):
			subIndex = len(chart.m_data) - 1 - m_lastIndexCache_Chart
		elif (chart.m_firstVisibleIndex + subIndex < 0):
			subIndex = m_firstIndexCache_Chart
		chart.m_firstVisibleIndex = m_firstIndexCache_Chart + subIndex
		chart.m_lastVisibleIndex = m_lastIndexCache_Chart + subIndex
		checkChartLastVisibleIndex(chart)
		resetChartVisibleRecord(chart)
		if(m_calculteMaxMin != None):
			m_calculteMaxMin(chart)
		else:
			calculateChartMaxMin(chart)

#绘制刻度
#chart:K线
#paint:绘图对象
#clipRect:裁剪区域
def drawChartScale(chart, paint, clipRect):
	if(chart.m_leftVScaleWidth > 0):
		paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_leftVScaleWidth, 0, chart.m_leftVScaleWidth, chart.m_size.cy - chart.m_hScaleHeight)
	if(chart.m_rightVScaleWidth > 0):
		paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_size.cx - chart.m_rightVScaleWidth, 0, chart.m_size.cx - chart.m_rightVScaleWidth, chart.m_size.cy - chart.m_hScaleHeight)
	if(chart.m_hScaleHeight > 0):
		paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, 0, chart.m_size.cy - chart.m_hScaleHeight, chart.m_size.cx, chart.m_size.cy - chart.m_hScaleHeight)
	candleDivHeight = getCandleDivHeight(chart)
	volDivHeight = getVolDivHeight(chart)
	indDivHeight = getIndDivHeight(chart)
	indDivHeight2 = getIndDivHeight2(chart)
	if(volDivHeight > 0):
		paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_leftVScaleWidth, candleDivHeight, chart.m_size.cx - chart.m_rightVScaleWidth, candleDivHeight)
	if(indDivHeight > 0):
		paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_leftVScaleWidth, candleDivHeight + volDivHeight, chart.m_size.cx - chart.m_rightVScaleWidth, candleDivHeight + volDivHeight)
	if(indDivHeight2 > 0):
		paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_leftVScaleWidth, candleDivHeight + volDivHeight + indDivHeight, chart.m_size.cx - chart.m_rightVScaleWidth, candleDivHeight + volDivHeight + indDivHeight)
	if(chart.m_data != None and len(chart.m_data) > 0):
		ret = chartGridScale(chart.m_candleMin, chart.m_candleMax,  (candleDivHeight - chart.m_candlePaddingTop - chart.m_candlePaddingBottom) / 2, chart.m_vScaleDistance, chart.m_vScaleDistance / 2, int((candleDivHeight - chart.m_candlePaddingTop - chart.m_candlePaddingBottom) / chart.m_vScaleDistance))
		if(m_gridStep_Chart > 0 and ret > 0):
			drawValues = []
			isTrend = FALSE
			if(chart.m_cycle == "trend"):
				isTrend = TRUE
			firstOpen = 0
			if(isTrend):
				firstOpen = chart.m_data[chart.m_firstVisibleIndex].m_close
				subValue = (chart.m_candleMax - chart.m_candleMin)
				count = int((candleDivHeight - chart.m_candlePaddingTop - chart.m_candlePaddingBottom) / chart.m_vScaleDistance)
				if(count > 0):
					subValue /= count
				start = firstOpen
				while(start < chart.m_candleMax):
					start += subValue
					if(start <= chart.m_candleMax):
						drawValues.append(start)
				start = firstOpen
				while(start > chart.m_candleMin):
					start -= subValue
					if(start >= chart.m_candleMin):
						drawValues.append(start)
			else:
				start = 0
				if (chart.m_candleMin >= 0):
					while (start + m_gridStep_Chart < chart.m_candleMin):
						start += m_gridStep_Chart
				else:
					while (start - m_gridStep_Chart > chart.m_candleMin):
						start -= m_gridStep_Chart

				while (start <= chart.m_candleMax):
					if(start > chart.m_candleMin):
						drawValues.append(start)
					start += m_gridStep_Chart
			drawValues.append(firstOpen);
			for i in range(0,len(drawValues)):
				start = drawValues[i]
				hAxisY = getChartY(chart, 0, start)
				paint.drawLine(chart.m_gridColor, m_lineWidth_Chart, [1,1], chart.m_leftVScaleWidth, int(hAxisY), chart.m_size.cx - chart.m_rightVScaleWidth, int(hAxisY))
				paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_leftVScaleWidth - 8, int(hAxisY), chart.m_leftVScaleWidth, int(hAxisY))
				paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_size.cx - chart.m_rightVScaleWidth, int(hAxisY), chart.m_size.cx - chart.m_rightVScaleWidth + 8, int(hAxisY))
				tSize = paint.textSize(toFixed(start, chart.m_candleDigit), chart.m_font)
				if(isTrend):
					diffRange = ((start - firstOpen) / firstOpen * 100)
					diffRangeStr = toFixed(diffRange, 2) + "%"
					if(diffRange >= 0):
						paint.drawText(diffRangeStr, chart.m_upColor, chart.m_font, chart.m_size.cx - chart.m_rightVScaleWidth + 10, int(hAxisY) - tSize.cy / 2)
					else:
						paint.drawText(diffRangeStr, chart.m_downColor, chart.m_font, chart.m_size.cx - chart.m_rightVScaleWidth + 10, int(hAxisY) - tSize.cy / 2)
				else:
					paint.drawText(toFixed(start, chart.m_candleDigit), chart.m_textColor, chart.m_font, chart.m_size.cx - chart.m_rightVScaleWidth + 10, int(hAxisY) - tSize.cy / 2)
				paint.drawText(toFixed(start, chart.m_candleDigit), chart.m_textColor, chart.m_font, chart.m_leftVScaleWidth - tSize.cx - 10, int(hAxisY) - tSize.cy / 2)
		ret = chartGridScale(chart.m_volMin, chart.m_volMax,  (volDivHeight - chart.m_volPaddingTop - chart.m_volPaddingBottom) / 2, chart.m_vScaleDistance, chart.m_vScaleDistance / 2, int((volDivHeight - chart.m_volPaddingTop - chart.m_volPaddingBottom) / chart.m_vScaleDistance))
		if(m_gridStep_Chart > 0 and ret > 0):
			start = 0
			if (chart.m_volMin >= 0):
				while (start + m_gridStep_Chart < chart.m_volMin):
					start += m_gridStep_Chart
			else:
				while (start - m_gridStep_Chart > chart.m_volMin):
					start -= m_gridStep_Chart
			while (start <= chart.m_volMax):
				if(start > chart.m_volMin):
					hAxisY = getChartY(chart, 1, start)
					paint.drawLine(chart.m_gridColor, m_lineWidth_Chart, [1,1], chart.m_leftVScaleWidth, int(hAxisY), chart.m_size.cx - chart.m_rightVScaleWidth, int(hAxisY))
					paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_leftVScaleWidth - 8, int(hAxisY), chart.m_leftVScaleWidth, int(hAxisY))
					paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_size.cx - chart.m_rightVScaleWidth, int(hAxisY), chart.m_size.cx - chart.m_rightVScaleWidth + 8, int(hAxisY))
					tSize = paint.textSize(toFixed((start/chart.m_magnitude), chart.m_volDigit), chart.m_font)
					paint.drawText(toFixed((start/chart.m_magnitude), chart.m_volDigit), chart.m_textColor, chart.m_font, chart.m_size.cx - chart.m_rightVScaleWidth + 10, int(hAxisY) - tSize.cy / 2)
					paint.drawText(toFixed((start/chart.m_magnitude), chart.m_volDigit), chart.m_textColor, chart.m_font, chart.m_leftVScaleWidth - tSize.cx - 10, int(hAxisY) - tSize.cy / 2)
				start += m_gridStep_Chart
		if(indDivHeight > 0):
			ret = chartGridScale(chart.m_indMin, chart.m_indMax, (indDivHeight - chart.m_indPaddingTop - chart.m_indPaddingBottom) / 2, chart.m_vScaleDistance, chart.m_vScaleDistance / 2, int((indDivHeight - chart.m_indPaddingTop - chart.m_indPaddingBottom) / chart.m_vScaleDistance))
			if(m_gridStep_Chart > 0 and ret > 0):
				start = 0;
				if (chart.m_indMin >= 0):
					while (start + m_gridStep_Chart < chart.m_indMin):
						start += m_gridStep_Chart
				else:
					while (start - m_gridStep_Chart > chart.m_indMin):
						start -= m_gridStep_Chart
				while (start <= chart.m_indMax):
					if(start > chart.m_indMin):
						hAxisY = getChartY(chart, 2, start)
						paint.drawLine(chart.m_gridColor, m_lineWidth_Chart, [1,1], chart.m_leftVScaleWidth, int(hAxisY), chart.m_size.cx - chart.m_rightVScaleWidth, int(hAxisY))
						paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_leftVScaleWidth - 8, int(hAxisY), chart.m_leftVScaleWidth, int(hAxisY))
						paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_size.cx - chart.m_rightVScaleWidth, int(hAxisY), chart.m_size.cx - chart.m_rightVScaleWidth + 8, int(hAxisY))
						tSize = paint.textSize(toFixed(start, chart.m_indDigit), chart.m_font)
						paint.drawText(toFixed(start, chart.m_indDigit), chart.m_textColor, chart.m_font, chart.m_size.cx - chart.m_rightVScaleWidth + 10, int(hAxisY) - tSize.cy / 2)
						paint.drawText(toFixed(start, chart.m_indDigit), chart.m_textColor, chart.m_font, chart.m_leftVScaleWidth - tSize.cx - 10, int(hAxisY) - tSize.cy / 2)
					start += m_gridStep_Chart
		if(indDivHeight2 > 0):
			ret = chartGridScale(chart.m_indMin2, chart.m_indMax2, (indDivHeight2 - chart.m_indPaddingTop2 - chart.m_indPaddingBottom2) / 2, chart.m_vScaleDistance, chart.m_vScaleDistance / 2, int((indDivHeight2 - chart.m_indPaddingTop2 - chart.m_indPaddingBottom2) / chart.m_vScaleDistance))
			if(m_gridStep_Chart > 0 and ret > 0):
				start = 0;
				if (chart.m_indMin2 >= 0):
					while (start + m_gridStep_Chart < chart.m_indMin2):
						start += m_gridStep_Chart
				else:
					while (start - m_gridStep_Chart > chart.m_indMin2):
						start -= m_gridStep_Chart 
				while (start <= chart.m_indMax2):
					if(start > chart.m_indMin2):
						hAxisY = getChartY(chart, 3, start)
						paint.drawLine(chart.m_gridColor, m_lineWidth_Chart, [1,1], chart.m_leftVScaleWidth, int(hAxisY), chart.m_size.cx - chart.m_rightVScaleWidth, int(hAxisY))
						paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_leftVScaleWidth - 8, int(hAxisY), chart.m_leftVScaleWidth, int(hAxisY))
						paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, chart.m_size.cx - chart.m_rightVScaleWidth, int(hAxisY), chart.m_size.cx - chart.m_rightVScaleWidth + 8, int(hAxisY))
						tSize = paint.textSize(toFixed(start, chart.m_indDigit), chart.m_font)
						paint.drawText(toFixed(start, chart.m_indDigit), chart.m_textColor, chart.m_font, chart.m_size.cx - chart.m_rightVScaleWidth + 10, int(hAxisY) - tSize.cy / 2)
						paint.drawText(toFixed(start, chart.m_indDigit), chart.m_textColor, chart.m_font, chart.m_leftVScaleWidth - tSize.cx - 10, int(hAxisY) - tSize.cy / 2)
					start += m_gridStep_Chart
		if(chart.m_data != None and len(chart.m_data) > 0 and chart.m_hScaleHeight > 0):
			dLeft = chart.m_leftVScaleWidth + 10
			for i in range(chart.m_firstVisibleIndex,chart.m_lastVisibleIndex + 1):
				xText = ""
				if (chart.m_cycle == "day"):
					timeArray = time.localtime(chart.m_data[i].m_date)
					xText = time.strftime("%Y-%m-%d", timeArray)
				elif(chart.m_cycle == "minute"):
					timeArray = time.localtime(chart.m_data[i].m_date)
					xText = time.strftime("%Y-%m-%d %H:%M", timeArray)
				elif(chart.m_cycle == "trend"):
					timeArray = time.localtime(chart.m_data[i].m_date)
					xText = time.strftime("%H:%M", timeArray)
				elif(chart.m_cycle == "second"):
					timeArray = time.localtime(chart.m_data[i].m_date)
					xText = time.strftime("%H:%M:%S", timeArray)
				elif(chart.m_cycle == "tick"):
					xText = str(i + 1)
				if (len(chart.m_hScaleFormat) > 0):
					timeArray = time.localtime(chart.m_data[i].m_date)
					xText = time.strftime(chart.m_hScaleFormat, timeArray)
				tSize = paint.textSize(xText, chart.m_font)
				x = getChartX(chart, i)
				dx = x - tSize.cx / 2
				if(dx > dLeft and dx < chart.m_size.cx - chart.m_rightVScaleWidth - 10):
					paint.drawLine(chart.m_scaleColor, m_lineWidth_Chart, 0, x, chart.m_size.cy - chart.m_hScaleHeight, x, chart.m_size.cy - chart.m_hScaleHeight + 8)
					paint.drawText(xText, chart.m_textColor, chart.m_font, dx, chart.m_size.cy - chart.m_hScaleHeight + 8  - tSize.cy / 2)
					dLeft = x + tSize.cx

#绘制十字线
#chart:K线
#paint:绘图对象
#clipRect:裁剪区域
def drawChartCrossLine(chart, paint, clipRect):
	if(chart.m_data == None or len(chart.m_data) == 0):
		return
	candleDivHeight = getCandleDivHeight(chart)
	volDivHeight = getVolDivHeight(chart)
	indDivHeight = getIndDivHeight(chart)
	indDivHeight2 = getIndDivHeight2(chart)
	crossLineIndex = chart.m_crossStopIndex
	if (crossLineIndex == -1):
		crossLineIndex = chart.m_lastVisibleIndex
	if(volDivHeight > 0):
		drawTitles = []
		drawColors = []
		drawTitles.append("VOL " + toFixed(chart.m_data[crossLineIndex].m_volume, chart.m_volDigit))
		drawColors.append(chart.m_textColor)
		if(len(chart.m_shapes) > 0):
			for i in range(0, len(chart.m_shapes)):
				shape = chart.m_shapes[i]
				if(shape.m_divIndex == 1):
					if(len(shape.m_title) > 0):
						if(shape.m_type == "bar"  and shape.m_style == "2color"):
							drawTitles.append(shape.m_title + " " + toFixed(shape.m_datas[crossLineIndex], chart.m_indDigit2))
							drawColors.append(shape.m_color2)
						else:
							if(shape.m_type != "text"):
								drawTitles.append(shape.m_title + " " + toFixed(shape.m_datas[crossLineIndex], chart.m_indDigit2))
								drawColors.append(shape.m_color)
								if(len(shape.m_datas2) > 0):
									drawTitles.append(shape.m_title2 + " " + toFixed(shape.m_datas2[crossLineIndex], chart.m_indDigit2))
									drawColors.append(shape.m_color2)
						
					
		iLeft = chart.m_leftVScaleWidth + 5
		for i in range(0,len(drawTitles)):
			tSize = paint.textSize(drawTitles[i], chart.m_font)
			paint.drawText(drawTitles[i], drawColors[i], chart.m_font, iLeft, candleDivHeight + 5)
			iLeft += tSize.cx + 5
	if (chart.m_cycle == "trend"):
		drawTitles = []
		drawColors = []
		drawTitles.append("CLOSE" + toFixed(chart.m_data[crossLineIndex].m_close, chart.m_candleDigit))
		drawColors.append(chart.m_textColor)
		iLeft = chart.m_leftVScaleWidth + 5
		if(len(chart.m_shapes) > 0):
			for i in range(0, len(chart.m_shapes)):
				shape = chart.m_shapes[i]
				if(shape.m_divIndex == 0):
					if(len(shape.m_title) > 0):
						if(shape.m_type == "bar"  and shape.m_style == "2color"):
							drawTitles.append(shape.m_title + " " + toFixed(shape.m_datas[crossLineIndex], chart.m_indDigit2))
							drawColors.append(shape.m_color2)
						else:
							if(shape.m_type != "text"):
								drawTitles.append(shape.m_title + " " + toFixed(shape.m_datas[crossLineIndex], chart.m_indDigit2))
								drawColors.append(shape.m_color)
								if(len(shape.m_datas2) > 0):
									drawTitles.append(shape.m_title2 + " " + toFixed(shape.m_datas2[crossLineIndex], chart.m_indDigit2))
									drawColors.append(shape.m_color2)
		for i in range(0,len(drawTitles)):
			tSize = paint.textSize(drawTitles[i], chart.m_font)
			paint.drawText(drawTitles[i], drawColors[i], chart.m_font, iLeft, 5)
			iLeft += tSize.cx + 5
	else:
		drawTitles = []
		drawColors = []
		if (chart.m_mainIndicator == "MA"):
			drawTitles.append("MA5 " + toFixed(chart.m_ma5[crossLineIndex], chart.m_candleDigit))
			drawTitles.append("MA10 " + toFixed(chart.m_ma10[crossLineIndex], chart.m_candleDigit))
			drawTitles.append("MA20 " + toFixed(chart.m_ma20[crossLineIndex], chart.m_candleDigit))
			drawTitles.append("MA30 " + toFixed(chart.m_ma30[crossLineIndex], chart.m_candleDigit))
			drawTitles.append("MA120 " + toFixed(chart.m_ma120[crossLineIndex], chart.m_candleDigit))
			drawTitles.append("MA250 " + toFixed(chart.m_ma250[crossLineIndex], chart.m_candleDigit))
			drawColors.append(m_indicatorColors[0])
			drawColors.append(m_indicatorColors[1])
			drawColors.append(m_indicatorColors[2])
			drawColors.append(m_indicatorColors[5])
			drawColors.append(m_indicatorColors[4])
			drawColors.append(m_indicatorColors[3])
		elif (chart.m_mainIndicator == "BOLL"):
			drawTitles.append("MID " + toFixed(chart.m_boll_mid[crossLineIndex], chart.m_candleDigit))
			drawTitles.append("UP " + toFixed(chart.m_boll_up[crossLineIndex], chart.m_candleDigit))
			drawTitles.append("LOW " + toFixed(chart.m_boll_down[crossLineIndex], chart.m_candleDigit))
			drawColors.append(m_indicatorColors[0])
			drawColors.append(m_indicatorColors[1])
			drawColors.append(m_indicatorColors[2])
		if(len(chart.m_shapes) > 0):
			for i in range(0, len(chart.m_shapes)):
				shape = chart.m_shapes[i]
				if(shape.m_divIndex == 0):
					if(len(shape.m_title) > 0):
						if(shape.m_type == "bar" and shape.m_style == "2color"):
							drawTitles.append(shape.m_title + " " + toFixed(shape.m_datas[crossLineIndex], chart.m_indDigit2))
							drawColors.append(shape.m_color2)
						else:
							if(shape.m_type != "text"):
								drawTitles.append(shape.m_title + " " + toFixed(shape.m_datas[crossLineIndex], chart.m_indDigit2))
								drawColors.append(shape.m_color)
								if(len(shape.m_datas2) > 0):
									drawTitles.append(shape.m_title2 + " " + toFixed(shape.m_datas2[crossLineIndex], chart.m_indDigit2))
									drawColors.append(shape.m_color2)
		iLeft = chart.m_leftVScaleWidth + 5
		for i in range(0, len(drawTitles)):
			tSize = paint.textSize(drawTitles[i], chart.m_font)
			paint.drawText(drawTitles[i], drawColors[i], chart.m_font, iLeft, 5)
			iLeft += tSize.cx + 5
	if(indDivHeight > 0):
		drawTitles = []
		drawColors = []
		if(chart.m_showIndicator == "MACD"):
			drawTitles.append("DIF " + toFixed(chart.m_alldifarr[crossLineIndex], chart.m_indDigit))
			drawTitles.append("DEA " + toFixed(chart.m_alldeaarr[crossLineIndex], chart.m_indDigit))
			drawTitles.append("MACD " + toFixed(chart.m_allmacdarr[crossLineIndex], chart.m_indDigit))
			drawColors.append(m_indicatorColors[0])
			drawColors.append(m_indicatorColors[1])
			drawColors.append(m_indicatorColors[4])
		elif(chart.m_showIndicator == "KDJ"):
			drawTitles.append("K " + toFixed(chart.m_kdj_k[crossLineIndex], chart.m_indDigit))
			drawTitles.append("D " + toFixed(chart.m_kdj_d[crossLineIndex], chart.m_indDigit))
			drawTitles.append("J " + toFixed(chart.m_kdj_j[crossLineIndex], chart.m_indDigit))
			drawColors.append(m_indicatorColors[0])
			drawColors.append(m_indicatorColors[1])
			drawColors.append(m_indicatorColors[2])
		elif(chart.m_showIndicator == "RSI"):
			drawTitles.append("RSI6 " + toFixed(chart.m_rsi1[crossLineIndex], chart.m_indDigit))
			drawTitles.append("RSI12 " + toFixed(chart.m_rsi2[crossLineIndex], chart.m_indDigit))
			drawTitles.append("RSI24 " + toFixed(chart.m_rsi3[crossLineIndex], chart.m_indDigit))
			drawColors.append(m_indicatorColors[5])
			drawColors.append(m_indicatorColors[1])
			drawColors.append(m_indicatorColors[2])
		elif(chart.m_showIndicator == "BIAS"):
			drawTitles.append("BIAS6 " + toFixed(chart.m_bias1[crossLineIndex], chart.m_indDigit))
			drawTitles.append("BIAS12 " + toFixed(chart.m_bias2[crossLineIndex], chart.m_indDigit))
			drawTitles.append("BIAS24 " + toFixed(chart.m_bias3[crossLineIndex], chart.m_indDigit))
			drawColors.append(m_indicatorColors[5])
			drawColors.append(m_indicatorColors[1])
			drawColors.append(m_indicatorColors[2])
		elif(chart.m_showIndicator == "ROC"):
			drawTitles.append("ROC " + toFixed(chart.m_roc[crossLineIndex], chart.m_indDigit))
			drawTitles.append("ROCMA " + toFixed(chart.m_roc_ma[crossLineIndex], chart.m_indDigit))
			drawColors.append(m_indicatorColors[0])
			drawColors.append(m_indicatorColors[1])       
		elif(chart.m_showIndicator == "WR"):
			drawTitles.append("WR5 " + toFixed(chart.m_wr1[crossLineIndex], chart.m_indDigit))
			drawTitles.append("WR10 " + toFixed(chart.m_wr2[crossLineIndex], chart.m_indDigit))
			drawColors.append(m_indicatorColors[0])
			drawColors.append(m_indicatorColors[1])
		elif(chart.m_showIndicator == "CCI"):
			drawTitles.append("CCI " + toFixed(chart.m_cci[crossLineIndex], chart.m_indDigit))
			drawColors.append(m_indicatorColors[0])
		elif(chart.m_showIndicator == "BBI"):
			drawTitles.append("BBI " + toFixed(chart.m_bbi[crossLineIndex], chart.m_indDigit))
			drawColors.append(m_indicatorColors[0])
		elif(chart.m_showIndicator == "TRIX"):
			drawTitles.append("TRIX " + toFixed(chart.m_trix[crossLineIndex], chart.m_indDigit))
			drawTitles.append("TRIXMA " + toFixed(chart.m_trix_ma[crossLineIndex], chart.m_indDigit))
			drawColors.append(m_indicatorColors[0])
			drawColors.append(m_indicatorColors[1])
		elif(chart.m_showIndicator == "DMA"):
			drawTitles.append("MA10 " + toFixed(chart.m_dma1[crossLineIndex], chart.m_indDigit))
			drawTitles.append("MA50 " + toFixed(chart.m_dma2[crossLineIndex], chart.m_indDigit))
			drawColors.append(m_indicatorColors[0])
			drawColors.append(m_indicatorColors[1])
		if(len(chart.m_shapes) > 0):
			for i in range(0, len(chart.m_shapes)):
				shape = chart.m_shapes[i]
				if(shape.m_divIndex == 2):
					if(len(shape.m_title) > 0):
						if(shape.m_type == "bar"  and shape.m_style == "2color"):
							drawTitles.append(shape.m_title + " " + toFixed(shape.m_datas[crossLineIndex], chart.m_indDigit2))
							drawColors.append(shape.m_color2)
						else:
							if(shape.m_type != "text"):
								drawTitles.append(shape.m_title + " " + toFixed(shape.m_datas[crossLineIndex], chart.m_indDigit2))
								drawColors.append(shape.m_color)
								if(len(shape.m_datas2) > 0):
									drawTitles.append(shape.m_title2 + " " + toFixed(shape.m_datas2[crossLineIndex], chart.m_indDigit2))
									drawColors.append(shape.m_color2)
		iLeft = chart.m_leftVScaleWidth + 5
		for i in range(0,len(drawTitles)):
			tSize = paint.textSize(drawTitles[i], chart.m_font)
			paint.drawText(drawTitles[i], drawColors[i], chart.m_font, iLeft, candleDivHeight + volDivHeight + 5)
			iLeft += tSize.cx + 5
	if(indDivHeight2 > 0):
		drawTitles = []
		drawColors = []
		if(len(chart.m_shapes) > 0):
			for i in range(0, len(chart.m_shapes)):
				shape = chart.m_shapes[i]
				if(shape.m_divIndex == 3):
					if(len(shape.m_title) > 0):
						if(shape.m_type == "bar"  and shape.m_style == "2color"):
							drawTitles.append(shape.m_title + " " + toFixed(shape.m_datas[crossLineIndex], chart.m_indDigit2))
							drawColors.append(shape.m_color2)
						else:
							if(shape.m_type != "text"):
								drawTitles.append(shape.m_title + " " + toFixed(shape.m_datas[crossLineIndex], chart.m_indDigit2))
								drawColors.append(shape.m_color)
								if(len(shape.m_datas2) > 0):
									drawTitles.append(shape.m_title2 + " " + toFixed(shape.m_datas2[crossLineIndex], chart.m_indDigit2))
									drawColors.append(shape.m_color2)
			if(len(drawTitles) > 0):
				iLeft = chart.m_leftVScaleWidth + 5
				for i in range(0,len(drawTitles)):
					tSize = paint.textSize(drawTitles[i], chart.m_font)
					paint.drawText(drawTitles[i], drawColors[i], chart.m_font, iLeft, candleDivHeight + volDivHeight + indDivHeight + 5)
					iLeft += tSize.cx + 5
	if(chart.m_showCrossLine):
		rightText = ""
		if(chart.m_mousePosition.y < candleDivHeight):
			rightText = toFixed(getChartValue(chart, chart.m_mousePosition), chart.m_candleDigit)	
		elif(chart.m_mousePosition.y > candleDivHeight and chart.m_mousePosition.y < candleDivHeight + volDivHeight):
			rightText = toFixed(getChartValue(chart, chart.m_mousePosition), chart.m_volDigit)
		elif(chart.m_mousePosition.y > candleDivHeight + volDivHeight and chart.m_mousePosition.y < candleDivHeight + volDivHeight + indDivHeight):
			rightText = toFixed(getChartValue(chart, chart.m_mousePosition), chart.m_indDigit)
		elif(chart.m_mousePosition.y > candleDivHeight + volDivHeight + indDivHeight and chart.m_mousePosition.y < candleDivHeight + volDivHeight + indDivHeight + indDivHeight2):
			rightText = toFixed(getChartValue(chart, chart.m_mousePosition), chart.m_indDigit2)
		drawY = chart.m_mousePosition.y
		if(drawY > chart.m_size.cy - chart.m_hScaleHeight):
			drawY = chart.m_size.cy - chart.m_hScaleHeight
		tSize = paint.textSize(rightText, chart.m_font)
		if(chart.m_leftVScaleWidth > 0):
			paint.fillRect(chart.m_crossTipColor, chart.m_leftVScaleWidth - tSize.cx, drawY - tSize.cy / 2 - 4, chart.m_leftVScaleWidth, drawY + tSize.cy / 2 + 3)
			paint.drawText(rightText, chart.m_textColor, chart.m_font, chart.m_leftVScaleWidth - tSize.cx, drawY - tSize.cy / 2)
		if(chart.m_rightVScaleWidth > 0):
			paint.fillRect(chart.m_crossTipColor, chart.m_size.cx - chart.m_rightVScaleWidth, drawY - tSize.cy / 2 - 4, chart.m_size.cx - chart.m_rightVScaleWidth + tSize.cx, drawY + tSize.cy / 2 + 3)
			paint.drawText(rightText, chart.m_textColor, chart.m_font, chart.m_size.cx - chart.m_rightVScaleWidth, drawY - tSize.cy / 2)
		drawX = chart.m_mousePosition.x;
		if(drawX < chart.m_leftVScaleWidth):
			drawX = chart.m_leftVScaleWidth
		if(drawX > chart.m_size.cx - chart.m_rightVScaleWidth):
			drawX = chart.m_size.cx - chart.m_rightVScaleWidth
		if(chart.m_sPlot == None and chart.m_selectShape == ""):
			paint.drawLine(chart.m_crossLineColor, m_lineWidth_Chart, 0, chart.m_leftVScaleWidth, drawY, chart.m_size.cx - chart.m_rightVScaleWidth, drawY)
			paint.drawLine(chart.m_crossLineColor, m_lineWidth_Chart, 0, drawX, 0, drawX, chart.m_size.cy - chart.m_hScaleHeight)
		if (chart.m_crossStopIndex != -1):
			xText = ""
			if (chart.m_cycle == "day"):
				timeArray = time.localtime(chart.m_data[chart.m_crossStopIndex].m_date)
				xText = time.strftime("%Y-%m-%d", timeArray)
			elif(chart.m_cycle == "minute"):
				timeArray = time.localtime(chart.m_data[chart.m_crossStopIndex].m_date)
				xText = time.strftime("%Y-%m-%d %H:%M", timeArray)
			elif(chart.m_cycle == "trend"):
				timeArray = time.localtime(chart.m_data[chart.m_crossStopIndex].m_date)
				xText = time.strftime("%H:%M", timeArray)
			elif(chart.m_cycle == "second"):
				timeArray = time.localtime(chart.m_data[chart.m_crossStopIndex].m_date)
				xText = time.strftime("%H:%M:%S", timeArray)
			elif(chart.m_cycle == "tick"):
				xText = str(chart.m_crossStopIndex + 1)
			if (len(chart.m_hScaleFormat) > 0):
				timeArray = time.localtime(chart.m_data[chart.m_crossStopIndex].m_date)
				xText = time.strftime(chart.m_hScaleFormat, timeArray)
			xSize = paint.textSize(xText, chart.m_font)
			paint.fillRect(chart.m_crossTipColor, drawX - xSize.cx / 2 - 2, candleDivHeight + volDivHeight + indDivHeight, drawX + xSize.cx / 2 + 2, candleDivHeight + volDivHeight + indDivHeight + xSize.cy + 6)
			paint.drawText(xText, chart.m_textColor, chart.m_font, drawX - xSize.cx / 2, candleDivHeight + volDivHeight + indDivHeight + 3)

#绘制K线
#chart:K线
#paint:绘图对象
#clipRect:裁剪区域
def drawChartStock(chart, paint, clipRect):
	if (chart.m_data != None and len(chart.m_data) > 0):
		candleHeight = getCandleDivHeight(chart)
		volHeight = getVolDivHeight(chart)
		indHeight = getIndDivHeight(chart)
		isTrend = FALSE
		if(chart.m_cycle == "trend"):
			isTrend = TRUE
		cWidth = int(chart.m_hScalePixel - 3) / 2
		if (cWidth < 0):
			cWidth = 0
		lastValidIndex = chart.m_lastVisibleIndex
		if(chart.m_lastValidIndex != -1):
			lastValidIndex = chart.m_lastValidIndex
		maxVisibleRecord = getChartMaxVisibleCount(chart, chart.m_hScalePixel, getChartWorkAreaWidth(chart))
		if (isTrend):
			drawPoints = []
			for i in range(chart.m_firstVisibleIndex,lastValidIndex + 1):
				x = getChartX(chart, i)
				close = chart.m_data[i].m_close
				closeY = getChartY(chart, 0, close)
				drawPoints.append((x, closeY))
			paint.drawPolyline(m_indicatorColors[7], m_lineWidth_Chart, 0, drawPoints)
		hasMinTag = FALSE
		hasMaxTag = FALSE
		for i in range(chart.m_firstVisibleIndex,lastValidIndex + 1):
			x = getChartX(chart, i)
			openValue = chart.m_data[i].m_open
			close = chart.m_data[i].m_close
			high = chart.m_data[i].m_high
			low = chart.m_data[i].m_low
			openY = getChartY(chart, 0, openValue)
			closeY = getChartY(chart, 0, close)
			highY = getChartY(chart, 0, high)
			lowY = getChartY(chart, 0, low)
			volY = 0
			zeroY = 0
			if(volHeight > 0):
				volume = chart.m_data[i].m_volume
				volY = getChartY(chart, 1, volume)
				zeroY = getChartY(chart, 1, 0) 
			if (close >= openValue):
				if (isTrend):
					if(volHeight > 0):
						paint.drawLine(m_indicatorColors[6], m_lineWidth_Chart, 0, x, volY, x, zeroY)
				else:
					paint.drawLine(chart.m_upColor, m_lineWidth_Chart, 0, x, highY, x, lowY)
					if (cWidth > 0):
						if (close == openValue):
							paint.drawLine(chart.m_upColor, m_lineWidth_Chart, 0, x - cWidth, closeY, x + cWidth, closeY)
						else:
							paint.fillRect(chart.m_upColor, x - cWidth, closeY, x + cWidth, openY)
						if(volHeight > 0):
							paint.fillRect(chart.m_upColor, x - cWidth, volY, x + cWidth, zeroY)
					else:
						if(volHeight > 0):
							paint.drawLine(chart.m_upColor, m_lineWidth_Chart, 0, x - cWidth, volY, x + cWidth, zeroY)
			else:
				if (isTrend):
					if(volHeight > 0):
						paint.drawLine(m_indicatorColors[6], m_lineWidth_Chart, 0, x, volY, x, zeroY)
				else:
					paint.drawLine(chart.m_downColor, m_lineWidth_Chart, 0, x, highY, x, lowY)
					if (cWidth > 0):
						paint.fillRect(chart.m_downColor, x - cWidth, openY, x + cWidth, closeY)
						if(volHeight > 0):
							paint.fillRect(chart.m_downColor, x - cWidth, volY, x + cWidth, zeroY)
					else:
						if(volHeight > 0):
							paint.drawLine(chart.m_downColor, m_lineWidth_Chart, 0, x - cWidth, volY, x + cWidth, zeroY)
			if (chart.m_selectShape == "CANDLE"):
				kPInterval = int(maxVisibleRecord / 30)
				if (kPInterval < 2):
					kPInterval = 3
				if (i % kPInterval == 0):
					if (isTrend == FALSE):
						paint.fillRect(m_indicatorColors[0], x - 3, closeY - 3, x + 3, closeY + 3)
			elif (chart.m_selectShape == "VOL"):
				kPInterval = int(maxVisibleRecord / 30)
				if (kPInterval < 2):
					kPInterval = 3
				if (i % kPInterval == 0):
					paint.fillRect(m_indicatorColors[0], x - 3, volY - 3, x + 3, volY + 3)
			if (isTrend == FALSE):
				if (hasMaxTag == FALSE):
					if (high == chart.m_candleMax):
						tag = toFixed(high, chart.m_candleDigit)
						tSize = paint.textSize(tag, chart.m_font)
						paint.drawText(tag, chart.m_textColor, chart.m_font, x - tSize.cx / 2, highY - tSize.cy - 2)
						hasMaxTag = TRUE
				if (hasMinTag == FALSE):
					if (low == chart.m_candleMin):
						tag = toFixed(low, chart.m_candleDigit)
						tSize = paint.textSize(tag, chart.m_font)
						paint.drawText(tag, chart.m_textColor, chart.m_font, x - tSize.cx / 2, lowY + 2)
						hasMinTag = TRUE
		if (isTrend == FALSE):
			newPaint = FCPaint()
			newPaint.m_drawHDC = paint.m_innerHDC
			newPaint.m_memBM = paint.m_innerBM
			newPaint.m_scaleFactorX = paint.m_scaleFactorX
			newPaint.m_scaleFactorY = paint.m_scaleFactorY
			divHeight = getCandleDivHeight(chart)
			cRect = FCRect(chart.m_leftVScaleWidth, 0, chart.m_size.cx, divHeight)
			newPaint.beginClip(cRect)
			if (chart.m_mainIndicator == "BOLL"):
				if(chart.m_selectShape == chart.m_mainIndicator and chart.m_selectShapeEx == "MID"):
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_boll_mid, m_indicatorColors[0], TRUE)
				else:
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_boll_mid, m_indicatorColors[0], FALSE)
				if(chart.m_selectShape == chart.m_mainIndicator and chart.m_selectShapeEx == "UP"):
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_boll_up, m_indicatorColors[1], TRUE)
				else:
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_boll_up, m_indicatorColors[1], FALSE)
				if(chart.m_selectShape == chart.m_mainIndicator and chart.m_selectShapeEx == "DOWN"):
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_boll_down, m_indicatorColors[2], TRUE)
				else:
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_boll_down, m_indicatorColors[2], FALSE)
			elif(chart.m_mainIndicator == "MA"):
				if(chart.m_selectShape == chart.m_mainIndicator and chart.m_selectShapeEx == "5"):
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma5, m_indicatorColors[0], TRUE)
				else:
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma5, m_indicatorColors[0], FALSE)
				if(chart.m_selectShape == chart.m_mainIndicator and chart.m_selectShapeEx == "10"):
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma10, m_indicatorColors[1], TRUE)
				else:
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma10, m_indicatorColors[1], FALSE)
				if(chart.m_selectShape == chart.m_mainIndicator and chart.m_selectShapeEx == "20"):
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma20, m_indicatorColors[2], TRUE)
				else:
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma20, m_indicatorColors[2], FALSE)
				if(chart.m_selectShape == chart.m_mainIndicator and chart.m_selectShapeEx == "30"):
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma30, m_indicatorColors[3], TRUE)
				else:
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma30, m_indicatorColors[3], FALSE)
				if(chart.m_selectShape == chart.m_mainIndicator and chart.m_selectShapeEx == "120"):
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma120, m_indicatorColors[4], TRUE)
				else:
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma120, m_indicatorColors[4], FALSE)
				if(chart.m_selectShape == chart.m_mainIndicator and chart.m_selectShapeEx == "250"):
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma250, m_indicatorColors[5], TRUE)
				else:
					drawChartLines(chart, newPaint, clipRect, 0, chart.m_ma250, m_indicatorColors[5], FALSE)
			rect = FCRect(0, 0, cRect.right - cRect.left, cRect.bottom - cRect.top)
			win32gui.StretchBlt(newPaint.m_drawHDC, int(cRect.left), int(cRect.top), int(cRect.right - cRect.left), int(cRect.bottom - cRect.top), newPaint.m_innerHDC, int(cRect.left - rect.left), int(cRect.top - rect.top), int(cRect.right - cRect.left), int(cRect.bottom - cRect.top), SRCPAINT)
			if(newPaint.m_innerHDC != None):
				win32gui.DeleteObject(newPaint.m_innerHDC)
				newPaint.m_innerHDC = None
			if(newPaint.m_innerBM != None):
				win32gui.DeleteObject(newPaint.m_innerBM)
				newPaint.m_innerBM = None
		if (indHeight > 0):
			if (chart.m_showIndicator == "MACD"):
				zeroY = getChartY(chart, 2, 0)
				paint.drawLine(m_indicatorColors[4], m_lineWidth_Chart, 0, chart.m_leftVScaleWidth, zeroY, getChartX(chart, chart.m_lastVisibleIndex), zeroY)
				for i in range(chart.m_firstVisibleIndex,lastValidIndex + 1):
					x = getChartX(chart, i)
					macd = chart.m_allmacdarr[i]
					macdY = getChartY(chart, 2, macd)
					if (macdY < zeroY):
						paint.drawLine(m_indicatorColors[3], m_lineWidth_Chart, 0, x, macdY, x, zeroY)
					else:
						paint.drawLine(m_indicatorColors[4], m_lineWidth_Chart, 0, x, macdY, x, zeroY)
					if (chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "MACD"):
						kPInterval = int(maxVisibleRecord / 30)
						if (kPInterval < 2):
							kPInterval = 3
						if (i % kPInterval == 0):
							paint.fillRect(m_indicatorColors[4], x - 3, macdY - 3, x + 3, macdY + 3)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "DIF"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_alldifarr, m_indicatorColors[0], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_alldifarr, m_indicatorColors[0], FALSE)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "DEA"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_alldeaarr, m_indicatorColors[1], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_alldeaarr, m_indicatorColors[1], FALSE)
			elif (chart.m_showIndicator == "KDJ"):
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "K"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_kdj_k, m_indicatorColors[0], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_kdj_k, m_indicatorColors[0], FALSE)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "D"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_kdj_d, m_indicatorColors[1], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_kdj_d, m_indicatorColors[1], FALSE)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "J"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_kdj_j, m_indicatorColors[2], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_kdj_j, m_indicatorColors[2], FALSE)
			elif (chart.m_showIndicator == "RSI"):
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "6"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_rsi1, m_indicatorColors[5], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_rsi1, m_indicatorColors[5], FALSE)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "12"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_rsi2, m_indicatorColors[1], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_rsi2, m_indicatorColors[1], FALSE)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "24"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_rsi3, m_indicatorColors[2], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_rsi3, m_indicatorColors[2], FALSE)
			elif (chart.m_showIndicator == "BIAS"):
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "1"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_bias1, m_indicatorColors[5], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_bias1, m_indicatorColors[5], FALSE)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "2"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_bias2, m_indicatorColors[1], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_bias2, m_indicatorColors[1], FALSE)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "3"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_bias3, m_indicatorColors[2], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_bias3, m_indicatorColors[2], FALSE)
			elif (chart.m_showIndicator == "ROC"):
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "ROC"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_roc, m_indicatorColors[0], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_roc, m_indicatorColors[0], FALSE)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "ROCMA"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_roc_ma, m_indicatorColors[1], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_roc_ma, m_indicatorColors[1], FALSE)
			elif (chart.m_showIndicator == "WR"):
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "1"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_wr1, m_indicatorColors[0], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_wr1, m_indicatorColors[0], FALSE)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "2"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_wr2, m_indicatorColors[1], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_wr2, m_indicatorColors[1], FALSE)
			elif (chart.m_showIndicator == "CCI"):
				if(chart.m_selectShape == chart.m_showIndicator):
					drawChartLines(chart, paint, clipRect, 2, chart.m_cci, m_indicatorColors[0], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_cci, m_indicatorColors[0], FALSE)
			elif (chart.m_showIndicator == "BBI"):
				if(chart.m_selectShape == chart.m_showIndicator):
					drawChartLines(chart, paint, clipRect, 2, chart.m_bbi, m_indicatorColors[0], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_bbi, m_indicatorColors[0], FALSE)
			elif (chart.m_showIndicator == "TRIX"):
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "TRIX"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_trix, m_indicatorColors[0], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_trix, m_indicatorColors[0], FALSE)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "TRIXMA"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_trix_ma, m_indicatorColors[1], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_trix_ma, m_indicatorColors[1], FALSE)
			elif (chart.m_showIndicator == "DMA"):
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "DIF"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_dma1, m_indicatorColors[0], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_dma1, m_indicatorColors[0], FALSE)
				if(chart.m_selectShape == chart.m_showIndicator and chart.m_selectShapeEx == "DIFMA"):
					drawChartLines(chart, paint, clipRect, 2, chart.m_dma2, m_indicatorColors[1], TRUE)
				else:
					drawChartLines(chart, paint, clipRect, 2, chart.m_dma2, m_indicatorColors[1], FALSE)
	#绘制扩展线条
	if(len(chart.m_shapes) > 0):
		for i in range(0, len(chart.m_shapes)):
			shape = chart.m_shapes[i]
			if(shape.m_type == "bar"):
				for j in range(chart.m_firstVisibleIndex,lastValidIndex + 1):
					if(len(shape.m_showHideDatas) > j and str(shape.m_showHideDatas[j]) == "0"):
						continue
					x = getChartX(chart, j)
					y1 = getChartY(chart, shape.m_divIndex, shape.m_datas[j])
					if(shape.m_style != "2color"):
						y2 = getChartY(chart, shape.m_divIndex, shape.m_datas2[j])
						if(y1 >= y2):
							paint.fillRect(shape.m_color, x - cWidth, y2, x + cWidth, y1)
						else:
							paint.fillRect(shape.m_color, x - cWidth, y1, x + cWidth, y2)
					else:
						y2 = getChartY(chart, shape.m_divIndex, 0)
						if(y1 >= y2):
							paint.drawLine(shape.m_color2, 1, 0, x, y1, x, y2)
						else:
							paint.drawLine(shape.m_color, 1, 0, x, y1, x, y2)
						if(j == lastValidIndex):
							paint.drawLine(shape.m_color2, 1, 0, chart.m_leftVScaleWidth, y2, chart.m_size.cx - chart.m_rightVScaleWidth, y2)
			elif(shape.m_type == "text"):
				for j in range(chart.m_firstVisibleIndex,lastValidIndex + 1):
					x = getChartX(chart, j)
					if(shape.m_datas[j] != 0):
						y1 = getChartY(chart, shape.m_divIndex, shape.m_value)
						drawText = shape.m_text
						tSize = paint.textSize(drawText, "14px Arial")
						paint.drawText(drawText, shape.m_color, "14px Arial", x - tSize.cx / 2, y1 - tSize.cy / 2)
			else:
				if(chart.m_selectShape == shape.m_name):
					drawChartLines(chart, paint, clipRect, shape.m_divIndex, shape.m_datas, shape.m_color, TRUE)
				else:
					drawChartLines(chart, paint, clipRect, shape.m_divIndex, shape.m_datas, shape.m_color, FALSE)


m_paintChartScale = None #绘制坐标轴回调
m_paintChartStock = None #绘制K线回调
m_paintChartPlot = None #绘制画线回调
m_paintChartCrossLine = None #绘制十字线回调
m_calculteMaxMin = None #计算最大最小值的回调

#清除图形
#chart:K线
#paint:绘图对象
#clipRect:裁剪区域
def drawChart(chart, paint, clipRect):
	global m_paintChartScale
	global m_paintChartStock
	global m_paintChartPlot
	global m_paintChartCrossLine
	if (chart.m_backColor != "none"):
		paint.fillRect(chart.m_backColor, 0, 0, chart.m_size.cx, chart.m_size.cy)
	if(m_paintChartScale != None):
		m_paintChartScale(chart, paint, clipRect)
	else:
		drawChartScale(chart, paint, clipRect)
	if(m_paintChartStock != None):
		m_paintChartStock(chart, paint, clipRect)
	else:
		drawChartStock(chart, paint, clipRect)
	if(m_paintChartPlot != None):
		m_paintChartPlot(chart, paint, clipRect)
	else:
		drawChartPlot(chart, paint, clipRect)
	if(m_paintChartCrossLine != None):
		m_paintChartCrossLine(chart, paint, clipRect)
	else:
		drawChartCrossLine(chart, paint, clipRect)
	if (chart.m_borderColor != "none"):
		paint.drawRect(chart.m_borderColor, m_lineWidth_Chart, 0, 0, 0, chart.m_size.cx - 1, chart.m_size.cy - 1)

#重绘视图 
#views:视图集合 
#paint:绘图对象 
#rect:区域
def renderViews(views, paint, rect):
	global m_paintCallBack
	global m_paintBorderCallBack
	size = len(views)
	for i in range(0, size):
		view = views[size - i - 1]
		if(rect == None):
			subViews = view.m_views
			subViewsSize = len(subViews)
			if(subViewsSize > 0):
				renderViews(subViews, paint, None)
			view.m_clipRect = None
			continue
		if(view.m_topMost == FALSE and isPaintVisible(view) and view.m_allowDraw):
			clx = clientX(view)
			cly = clientY(view)
			drawRect = FCRect(0, 0, view.m_size.cx, view.m_size.cy)
			clipRect = FCRect(clx, cly, clx + view.m_size.cx, cly + view.m_size.cy)
			destRect = FCRect(0, 0, 0, 0)
			if(getIntersectRect(destRect, rect, clipRect) > 0):
				paint.setOffset(0, 0)
				view.m_clipRect = destRect
				paint.setOffset(clx, cly)
				paint.beginClip(clipRect)
				if(m_paintCallBack != None):
					m_paintCallBack(view, paint, rect)
				paint.endClip(clipRect, destRect)
				subViews = view.m_views
				subViewsSize = len(subViews)
				if(subViewsSize > 0):
					renderViews(subViews, paint, destRect)
				paint.setOffset(clx, cly)
				if(m_paintBorderCallBack != None):
					m_paintBorderCallBack(view, paint, rect)
			else:
				subViews = view.m_views
				subViewsSize = len(subViews)
				if(subViewsSize > 0):
					renderViews(subViews, paint, None)
				view.m_clipRect = None
	for i in range(0, size):
		view = views[size - i - 1]
		if(rect == None):
			continue
		if(view.m_topMost and isPaintVisible(view) and view.m_allowDraw):
			clx = clientX(view)
			cly = clientY(view)
			drawRect = FCRect(0, 0, view.m_size.cx, view.m_size.cy)
			clipRect = FCRect(clx, cly, clx + view.m_size.cx, cly + view.m_size.cy)
			destRect = FCRect(0, 0, 0, 0)
			if(getIntersectRect(destRect, rect, clipRect) > 0):
				paint.setOffset(0, 0)
				view.m_clipRect = destRect
				paint.setOffset(clx, cly)
				paint.beginClip(clipRect)
				if(m_paintCallBack != None):
					m_paintCallBack(view, paint, rect)
				paint.endClip(clipRect, destRect)
				subViews = view.m_views
				subViewsSize = len(subViews)
				if(subViewsSize > 0):
					renderViews(subViews, paint, destRect)
				paint.setOffset(clx, cly)
				if(m_paintBorderCallBack != None):
					m_paintBorderCallBack(view, paint, rect)
			else:
				subViews = view.m_views
				subViewsSize = len(subViews)
				if(subViewsSize > 0):
					renderViews(subViews, paint, None)
				view.m_clipRect = None	

#全局刷新方法
#views:视图集合
#paint:绘图对象
def invalidate(paint):
	hDC = win32gui.GetDC(paint.m_hWnd)
	paint.m_hdc = hDC
	paint.m_clipRect = None
	rect = win32gui.GetClientRect(paint.m_hWnd)
	paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
	drawRect = FCRect(0, 0, (paint.m_size.cx / paint.m_scaleFactorX), (paint.m_size.cy / paint.m_scaleFactorY))
	paint.beginPaint(drawRect)
	renderViews(paint.m_views, paint, drawRect)
	paint.endPaint()
	win32gui.ReleaseDC(paint.m_hWnd, hDC)
	showOrHideInput(paint, paint.m_views)

#刷新视图方法
#views:视图
#paint:绘图对象
def invalidateView(view, paint):
	if(isPaintVisible(view)):
		hDC = win32gui.GetDC(paint.m_hWnd)
		paint.m_hdc = hDC
		clX = clientX(view)
		clY = clientY(view)
		drawRect = FCRect(clX, clY, clX + view.m_size.cx, clY + view.m_size.cy)
		drawViews = paint.m_views
		paint.m_clipRect = drawRect
		allRect = FCRect(0, 0, (paint.m_size.cx / paint.m_scaleFactorX), (paint.m_size.cy / paint.m_scaleFactorY))
		paint.beginPaint(allRect)
		renderViews(drawViews, paint, drawRect)
		paint.endPaint()
		win32gui.ReleaseDC(paint.m_hWnd, hDC)
		showOrHideInput(paint, drawViews)
		
#显示或隐藏输入框
def showOrHideInput(paint, views):
	for i in range(0, len(views)):
		view = views[i]
		paintVisible = isPaintVisible(view)
		if(len(view.m_views) > 0):
			showOrHideInput(paint, view.m_views)
		if(view.m_hWnd != None):
			clX = clientX(view)
			clY = clientY(view)
			relativeRect = FCRect(clX * paint.m_scaleFactorX, clY * paint.m_scaleFactorY, (clX + view.m_size.cx) * paint.m_scaleFactorX, (clY + view.m_size.cy) * paint.m_scaleFactorY)
			if (view.m_clipRect != None):
				relativeRect = FCRect(view.m_clipRect.left * paint.m_scaleFactorX, view.m_clipRect.top * paint.m_scaleFactorY, view.m_clipRect.right * paint.m_scaleFactorX, view.m_clipRect.bottom * paint.m_scaleFactorY)
			if(paintVisible):
				if(win32gui.IsWindowVisible(view.m_hWnd) == FALSE):
					win32gui.ShowWindow(view.m_hWnd, SW_SHOW)
				win32gui.MoveWindow(view.m_hWnd, int(relativeRect.left), int(relativeRect.top), int(relativeRect.right - relativeRect.left), int(relativeRect.bottom - relativeRect.top), TRUE)
			else:
				if(win32gui.IsWindowVisible(view.m_hWnd)):
					win32gui.ShowWindow(view.m_hWnd, SW_HIDE)

#更新悬浮状态
#views:视图集合
def updateViewDefault(views):
	for i in range(0,len(views)):
		view = views[i]
		if(view.m_dock == "fill"):
			if(view.m_parent != None and view.m_parent.m_type != "split"):
				view.m_location = FCPoint(0, 0)
				view.m_size = FCSize(view.m_parent.m_size.cx, view.m_parent.m_size.cy)
		if(view.m_type == "split"):
			resetSplitLayoutDiv(view)
		elif(view.m_type == "tabview"):
			updateTabLayout(view)
		elif(view.m_type == "layout"):
			resetLayoutDiv(view)
		subViews = view.m_views
		if(len(subViews) > 0):
			updateViewDefault(subViews)

#鼠标移动方法
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
#paint 绘图对象
def onMouseMove(mp, buttons, clicks, delta, paint):
	global m_mouseDownView
	global m_mouseMoveView
	global m_dragBeginRect
	global m_dragBeginPoint
	global m_draggingView
	global m_mouseDownPoint
	global m_mouseMoveCallBack
	if(m_mouseDownView != None):
		m_mouseMoveView = m_mouseDownView
		cmpPoint = FCPoint(mp.x - clientX(m_mouseDownView), mp.y - clientY(m_mouseDownView))
		if(m_mouseMoveCallBack != None):
			m_mouseMoveCallBack(m_mouseDownView, cmpPoint, 1, 1, 0)
		if (m_mouseDownView.m_allowDrag):
			if (abs(mp.x - m_mouseDownPoint.x) > 5 or abs(mp.y - m_mouseDownPoint.y) > 5):
				m_dragBeginRect = FCRect(m_mouseDownView.m_location.x, m_mouseDownView.m_location.y, m_mouseDownView.m_location.x + m_mouseDownView.m_size.cx, m_mouseDownView.m_location.y + m_mouseDownView.m_size.cy)
				m_dragBeginPoint = FCPoint(m_mouseDownPoint.x, m_mouseDownPoint.y)
				m_draggingView = m_mouseDownView
				m_mouseDownView = None
	elif(m_draggingView and buttons == 1):
		offsetX = mp.x - m_dragBeginPoint.x
		offsetY = mp.y - m_dragBeginPoint.y
		newBounds = FCRect(m_dragBeginRect.left + offsetX, m_dragBeginRect.top + offsetY, m_dragBeginRect.right + offsetX, m_dragBeginRect.bottom + offsetY)
		m_draggingView.m_location = FCPoint(newBounds.left, newBounds.top)
		if (m_draggingView.m_parent != None and m_draggingView.m_parent.m_type == "split"):
			resetSplitLayoutDiv(m_draggingView.m_parent)
			updateViewDefault(m_draggingView.m_parent.m_views)
		if (m_draggingView.m_parent != None):
			invalidateView(m_draggingView.m_parent, m_draggingView.m_parent.m_paint)
		else:
			invalidate(m_draggingView.m_paint)
	else:
		topViews = paint.m_views
		view = findView(mp, topViews)
		cmpPoint = FCPoint(mp.x - clientX(view), mp.y - clientY(view))
		if(view != None):
			oldMouseMoveView = m_mouseMoveView
			m_mouseMoveView = view
			if(oldMouseMoveView != None and oldMouseMoveView != view):
				if(m_mouseLeaveCallBack != None):
					m_mouseLeaveCallBack(oldMouseMoveView, cmpPoint, 0, 0, 0)
			if(oldMouseMoveView == None or oldMouseMoveView != view):
				if(m_mouseEnterCallBack != None):
					m_mouseEnterCallBack(view, cmpPoint, 0, 0, 0)				
			if(m_mouseMoveCallBack != None):
				m_mouseMoveCallBack(view, cmpPoint, 0, 0, 0)

#鼠标按下方法
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
#paint 绘图对象
def onMouseDown(mp, buttons, clicks, delta, paint):
	global m_mouseDownView
	global m_cancelClick
	global m_focusedView
	global m_mouseDownPoint
	global m_mouseDownCallBack
	m_cancelClick = FALSE
	m_mouseDownPoint = mp
	topViews = paint.m_views
	m_mouseDownView = findView(mp, topViews)
	if(m_mouseDownView != None):
		m_focusedView = m_mouseDownView
		cmpPoint = FCPoint(mp.x - clientX(m_mouseDownView), mp.y - clientY(m_mouseDownView))
		if(m_mouseDownCallBack != None):
			m_mouseDownCallBack(m_mouseDownView, cmpPoint, 1, 1, 0)

#鼠标抬起方法
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
#paint 绘图对象
def onMouseUp(mp, buttons, clicks, delta, paint):
	global m_mouseDownView
	global m_cancelClick
	global m_mouseUpCallBack
	if(m_mouseDownView != None):
		cmpPoint = FCPoint(mp.x - clientX(m_mouseDownView), mp.y - clientY(m_mouseDownView))
		topViews = paint.m_views
		view = findView(mp, topViews)
		if(view != None and view == m_mouseDownView):
			if(m_cancelClick == FALSE):
				if(m_clickCallBack != None):
					m_clickCallBack(m_mouseDownView, cmpPoint, 1, 1, 0)
		if(m_mouseDownView != None):
			mouseDownView = m_mouseDownView;
			m_mouseDownView = None
			if(m_mouseUpCallBack != None):
				m_mouseUpCallBack(mouseDownView, cmpPoint, 1, 1, 0)
	m_draggingView = None

#鼠标滚动方法
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
#paint 绘图对象
def onMouseWheel(mp, buttons, clicks, delta, paint):
	global m_mouseWheelCallBack
	topViews = paint.m_views
	view = findView(mp, topViews)
	if(view != None):
		cmpPoint = FCPoint(mp.x - clientX(view), mp.y - clientY(view))
		if(m_mouseWheelCallBack != None):
			m_mouseWheelCallBack(view, cmpPoint, 0, 0, delta)

#设置子视图的字符串
#hwnd:句柄
#text:字符串
def setHWndText(hwnd, text):
	win32gui.SendMessage(hwnd, WM_SETTEXT, None, text)

#获取子视图的字符串
#hwnd:句柄
def getHWndText(hwnd):
	length = win32gui.SendMessage(hwnd, WM_GETTEXTLENGTH) + 1
	buf = win32gui.PyMakeBuffer(length)
	win32api.SendMessage(hwnd, WM_GETTEXT, length, buf)
	address, length = win32gui.PyGetBufferAddressAndLen(buf[:-1])
	text = win32gui.PyGetString(address, length)
	return text

#单选按钮
class FCPie(FCView):
	def __init__(self):
		super().__init__()
		self.m_pieRadius = 70 #饼图半径
		self.m_textRadius = TRUE #是否可见
		self.m_startAngle = 0 #开始角度
		self.m_items = [] #数据项
		self.m_type = "pie" #类型
	pass

#饼图项
class FCPieItem(object):
	def __init__(self):
		self.m_value = 0 #数值
		self.m_text = "" #文字
		self.m_color = "rgb(0,0,0)" #颜色

#获取饼图的最大值
#pie 饼图
def getPieMaxValue(pie):
	maxValue = 0
	for i in range(0, len(pie.m_items)):
		item = pie.m_items[i]
		maxValue += item.m_value
	return maxValue

#绘图饼图
#pie:饼图
#paint:绘图对象
#clipRect:裁剪区域
def drawPie(pie, paint, clipRect):
	width = pie.m_size.cx
	height = pie.m_size.cy
	oX = width / 2
	oY = height / 2
	eRect = FCRect(oX - pie.m_pieRadius, oY - pie.m_pieRadius, oX + pie.m_pieRadius, oY + pie.m_pieRadius)
	maxValue = getPieMaxValue(pie)
	if (maxValue > 0):
		startAngle = pie.m_startAngle
		for i in range(0, len(pie.m_items)):
			item = pie.m_items[i]
			sweepAngle = item.m_value / maxValue * 360
			paint.fillPie(item.m_color, eRect.left, eRect.top, eRect.right, eRect.bottom, startAngle, sweepAngle)
			x1 = oX + (pie.m_pieRadius) * math.cos((startAngle + sweepAngle / 2) * 3.1415926 / 180)
			y1 = oY + (pie.m_pieRadius) * math.sin((startAngle + sweepAngle / 2) * 3.1415926 / 180)
			x2 = oX + (pie.m_textRadius) * math.cos((startAngle + sweepAngle / 2) * 3.1415926 / 180)
			y2 = oY + (pie.m_textRadius) * math.sin((startAngle + sweepAngle / 2) * 3.1415926 / 180)
			itemText = str(item.m_value)
			itemTextSize = paint.textSize(itemText, pie.m_font)
			paint.drawLine(pie.m_textColor, 1, 0, x1, y1, x2, y2);
			x3 = oX + (pie.m_textRadius + itemTextSize.cx / 2 + 5) * math.cos((startAngle + sweepAngle / 2) * 3.1415926 / 180)
			y3 = oY + (pie.m_textRadius + itemTextSize.cy / 2 + 5) * math.sin((startAngle + sweepAngle / 2) * 3.1415926 / 180)
			paint.drawText(itemText, pie.m_textColor, pie.m_font, x3 - itemTextSize.cx / 2, y3 - itemTextSize.cy / 2)
			startAngle += sweepAngle
	paint.drawEllipse(pie.m_borderColor, 1, 0, eRect.left, eRect.top, eRect.right, eRect.bottom)