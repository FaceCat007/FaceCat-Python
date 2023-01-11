# -*- coding:utf-8 -*-
#! python3

# FaceCat-Python-Wasm(OpenSource)
#Shanghai JuanJuanMao Information Technology Co., Ltd 

import win32gui
import win32api
from win32con import *
from xml.etree import ElementTree as ET
import math
import requests
import time
from requests.adapters import HTTPAdapter
from facecat import *
import facecat
import qstock as qs
#pip install qstock
#https://mp.weixin.qq.com/s/Ivue6tCQaH3RvD9u0Yy2pA

#更新悬浮状态
#views:视图集合
def updateView(views):
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
			updateView(subViews)

#设置属性
#view:视图
#node:xml节点
def setAttribute(view, child):
	if(view.m_paint != None):
		if(view.m_paint.m_defaultUIStyle == "dark"):
			view.m_backColor = "rgb(0,0,0)"
			view.m_borderColor = "rgb(100,100,100)"
			view.m_textColor = "rgb(255,255,255)"
		elif(view.m_paint.m_defaultUIStyle == "light"):
			view.m_backColor = "rgb(255,255,255)"
			view.m_borderColor = "rgb(150,150,150)"
			view.m_textColor = "rgb(0,0,0)"
		for key in child.attrib:
			name = key.lower()
			value = child.attrib[key]
			if(name == "location"):
				view.m_location = FCPoint(int(value.split(',')[0]), int(value.split(',')[1]))
			elif(name == "size"):
				view.m_size = FCSize(int(value.split(',')[0]), int(value.split(',')[1]))
			elif(name == "text"):
				view.m_text = value
			elif(name == "backcolor"):
				lowerStr = value.lower()
				if(lowerStr.find("rgb") == 0):
					view.m_backColor = value
				else:
					view.m_backColor = "none"
			elif(name == "bordercolor"):
				lowerStr = value.lower()
				if(lowerStr.find("rgb") == 0):
					view.m_borderColor = value
				else:
					view.m_borderColor = "none"
			elif(name == "textcolor"):
				lowerStr = value.lower()
				if(lowerStr.find("rgb") == 0):
					view.m_textColor = value
				else:
					view.m_textColor = "none"
			elif(name == "layoutstyle"):
				view.m_layoutStyle = value.lower()
			elif(name == "dock"):
				view.m_dock = value;
			elif(name == "font"):
				family = value.split(',')[0]
				if(family == "Default"):
					family = "Arial"
				view.m_font = value.split(',')[1] + "px " + family
			elif(name == "headerheight"):
				view.m_headerHeight = float(value)
			elif(name == "splitmode"):
				view.m_splitMode = value.lower()
			elif(name == "autowrap"):
				view.m_autoWrap = (value.lower() == "true")
			elif(name == "name"):
				view.m_name = value;
			elif(name == "showvscrollbar"):
				view.m_showVScrollBar = (value.lower() == "true")
			elif(name == "showhscrollbar"):
				view.m_showHScrollBar = (value.lower() == "true")
			elif(name == "visible"):
				view.m_visible =  (value.lower() == "true")
			elif(name == "displayoffset"):
				view.m_visible =  (value.lower() == "true")
			elif(name == "checked"):
				view.m_checked =  (value.lower() == "true")
			elif(name == "buttonsize"):
				view.m_buttonSize = FCSize(int(value.split(',')[0]), int(value.split(',')[1]))
			elif(name == "topmost"):
				view.m_topMost =  (value.lower() == "true")
			elif(name == "selectedindex"):
				view.m_selectedIndex = int(value)
			elif(name == "src"):
				view.m_src = value
			elif(name == "backimage"):
				view.m_backImage = value
			elif(name == "allowdrag"):
				view.m_allowDrag =  (value.lower() == "true")
    
#读取Xml
#paint 绘图对象
#node节点
#parent 父视图
def readXmlNode(paint, node, parent):
	for child in node:
		view = None
		typeStr = ""
		nodeName = child.tag.replace("{facecat}", "").lower()
		if(nodeName == "div" or nodeName == "view"):
			if "type" in child.attrib:
				typeStr = child.attrib["type"]
			if(typeStr == "splitlayout"):
				view = FCSplitLayoutDiv()
			elif(typeStr == "layout"):
				view = FCLayoutDiv()
			elif(typeStr == "tab"):
				view = FCTabView()
			elif(typeStr == "tabpage"):
				view = FCTabPage()
			elif(typeStr == "radio"):
				view = FCRadioButton()
				view.m_backColor = "none"
			elif(typeStr == "checkbox"):
				view = FCCheckBox()
				view.m_backColor = "none"
			elif(typeStr == "button"):
				view = FCView()
				view.m_type = "button"
			elif(typeStr == "text" or typeStr == "range" or typeStr == "datetime"):
				view = FCView()
				view.m_type = "textbox"
			else:
				view = FCView()
				view.m_type = "div"
		elif(nodeName == "table"):
			view = FCGrid()
		elif(nodeName == "chart"):
			view = FCChart()
		elif(nodeName == "tree"):
			view = FCTree()
		elif(nodeName == "select"):
			view = FCView()
			view.m_type = "combobox"
		elif(nodeName == "input" ):
			if "type" in child.attrib:
				typeStr = child.attrib["type"]
			if(typeStr == "radio"):
				view = FCRadioButton()
				view.m_backColor = "none"
			elif(typeStr == "checkbox"):
				view = FCCheckBox()
				view.m_backColor = "none"
			elif(typeStr == "button"):
				view = FCView()
				view.m_type = "button"
			elif(typeStr == "text" or typeStr == "range" or typeStr == "datetime"):
				view = FCView()
				view.m_type = "textbox"
			else:
				view = FCView()
				view.m_type = "button"
		else:
			view = FCView()
		view.m_paint = paint
		view.m_parent = parent
		setAttribute(view, child)
		if(nodeName == "label"):
			view.m_type = "label"
			view.m_borderColor = "none"
		if(view != None):
			if(typeStr == "tabpage"):
				tabButton = FCView()
				tabButton.m_type = "tabbutton"
				if "headersize" in child.attrib:
					atrHeaderSize = child.attrib["headersize"]
					tabButton.m_size = FCSize(int(atrHeaderSize.split(',')[0]), int(atrHeaderSize.split(',')[1]))
				else:
					tabButton.m_size = FCSize(100, 20)
				if(view.m_paint.m_defaultUIStyle == "dark"):
					tabButton.m_backColor = "rgb(0,0,0)"
					tabButton.m_borderColor = "rgb(100,100,100)"
					tabButton.m_textColor = "rgb(255,255,255)"
				elif(view.m_paint.m_defaultUIStyle == "light"):
					tabButton.m_backColor = "rgb(255,255,255)"
					tabButton.m_borderColor = "rgb(150,150,150)"
					tabButton.m_textColor = "rgb(0,0,0)"
				tabButton.m_text = view.m_text
				tabButton.m_paint = paint
				addTabPage(view.m_parent, view, tabButton)
			else:
				if(parent != None):
					parent.m_views.append(view)
				else:
					paint.m_views.append(view)
			if(typeStr == "splitlayout"):
				if "datumsize" in child.attrib:
					atrDatum = child.attrib["datumsize"]
					view.m_size = FCSize(int(atrDatum.split(',')[0]), int(atrDatum.split(',')[1]))
				splitter = FCView()
				splitter.m_paint = paint
				splitter.m_parent = view
				if(view.m_paint.m_defaultUIStyle == "dark"):
					splitter.m_backColor = "rgb(100,100,100)"
				elif(view.m_paint.m_defaultUIStyle == "light"):
					splitter.m_backColor = "rgb(150,150,150)"
				if "candragsplitter" in child.attrib:
					if(child.attrib["candragsplitter"] == "true"):
						splitter.m_allowDrag = TRUE
				view.m_splitter = splitter
				splitterposition = child.attrib["splitterposition"]
				splitStr = splitterposition.split(',')
				if(len(splitStr) >= 4):
					splitRect = FCRect(float(splitStr[0]), float(splitStr[1]), float(splitStr[2]), float(splitStr[3]))
					splitter.m_location = FCPoint(splitRect.left, splitRect.top)
					splitter.m_size = FCSize(splitRect.right - splitRect.left, splitRect.bottom - splitRect.top)
				else:
					sSize = float(splitStr[1])
					sPosition = float(splitStr[0])
					if(view.m_layoutStyle == "lefttoright" or view.m_layoutStyle == "righttoleft"):
						splitter.m_location = FCPoint(sPosition, 0)
						splitter.m_size = FCSize(sSize, view.m_size.cy)
					else:
						splitter.m_location = FCPoint(0, sPosition)
						splitter.m_size = FCSize(view.m_size.cx, sSize)
				readXmlNode(paint, child, view)
				subViews = view.m_views
				view.m_firstView = subViews[0];
				view.m_secondView = subViews[1];
				view.m_views.append(splitter)
				view.m_oldSize = FCSize(view.m_size.cx, view.m_size.cy)
				resetSplitLayoutDiv(view)
			elif(typeStr == "tab"):
				readXmlNode(paint, child, view)
				tabPages = view.m_tabPages
				if(len(tabPages) > 0):
					tabPages[0].m_visible = TRUE
			elif(nodeName == "table"):
				for tChild in child:
					if(tChild.tag.replace("{facecat}", "") == "tr"):
						for sunNode in tChild:
							sunNodeName = sunNode.tag.lower().replace("{facecat}", "")
							if(sunNodeName == "th"):
								gridColumn = FCGridColumn()
								gridColumn.m_width = 100
								if "text" in  sunNode.attrib:
									gridColumn.m_text = sunNode.attrib["text"]
								view.m_columns.append(gridColumn)
								if(view.m_paint.m_defaultUIStyle == "light"):
									gridColumn.m_backColor = "rgb(230,230,230)"
									gridColumn.m_borderColor = "rgb(150,150,150)"
									gridColumn.m_textColor = "rgb(0,0,0)"
			elif(view.m_type == "textbox"):
				view.m_hWnd = win32gui.CreateWindowEx(0, "Edit", view.m_name, WS_VISIBLE|WS_CHILD|SS_CENTERIMAGE, 0, 0, 100, 30, paint.m_hWnd, 0, 0, None)
				win32gui.ShowWindow(view.m_hWnd, SW_HIDE)
				s = win32gui.GetWindowLong(view.m_hWnd, GWL_EXSTYLE)
				win32gui.SetWindowLong(view.m_hWnd, GWL_EXSTYLE, s|ES_CENTER)
				setHWndText(view.m_hWnd, view.m_text)
			elif(view.m_type == "combobox"):
				#https://blog.csdn.net/qq_31178679/article/details/125883494
				view.m_hWnd = win32gui.CreateWindowEx(0, "ComboBox", view.m_name, WS_VISIBLE | WS_CHILD | WS_BORDER | CBS_HASSTRINGS | CBS_DROPDOWNLIST, 0, 0, 100, 30, paint.m_hWnd, 0, 0, None)
				win32gui.ShowWindow(view.m_hWnd, SW_HIDE)
				cIndex = 0
				for tChild in child:
					if(tChild.tag.replace("{facecat}", "") == "option"):
						if "text" in tChild.attrib:
							win32gui.SendMessage(view.m_hWnd, CB_ADDSTRING, cIndex, tChild.attrib["text"])
							cIndex = cIndex + 1
				if "selectedindex" in child.attrib:
					win32gui.SendMessage(view.m_hWnd, CB_SETCURSEL, int(child.attrib["selectedindex"]), 0)
			else:
				readXmlNode(paint, child, view)

#绘制视图
#view:视图
#paint:绘图对象
#clipRect:区域
def onViewPaint(view, paint, clipRect):
	if(view.m_type == "radiobutton"):
		drawRadioButton(view, paint, clipRect)
	elif(view.m_type == "checkbox"):
		drawCheckBox(view, paint, clipRect)
	elif(view.m_type == "chart"):
		resetChartVisibleRecord(view)
		checkChartLastVisibleIndex(view)
		calculateChartMaxMin(view)
		drawChart(view, paint, clipRect)
	elif(view.m_type == "grid"):
		drawDiv(view, paint, clipRect)
		drawGrid(view, paint, clipRect)
	elif(view.m_type == "tree"):
		drawDiv(view, paint, clipRect)
		drawTree(view, paint, clipRect)
	elif(view.m_type == "label"):
		if(view.m_textColor != "none"):
			tSize = paint.textSize(view.m_text, view.m_font)
			paint.drawText(view.m_text, view.m_textColor, view.m_font, 0, (view.m_size.cy - tSize.cy) / 2)
	elif(view.m_type == "div" or view.m_type =="tabpage" or view.m_type =="tabview" or view.m_type =="layout"):
		drawDiv(view, paint, clipRect)
	else:
		drawButton(view, paint, clipRect)

#绘制视图边线
#view:视图
#paint:绘图对象
#clipRect:区域
def onViewPaintBorder(view, paint, clipRect):
	if(view.m_type == "grid"):
		drawGridScrollBar(view, paint, clipRect)
	elif(view.m_type == "tree"):
		drawTreeScrollBar(view, paint, clipRect)
	elif(view.m_type == "div" or view.m_type =="tabpage" or view.m_type =="tabview" or view.m_type =="layout"):
		drawDivScrollBar(view, paint, clipRect)
		drawDivBorder(view, paint, clipRect)

#视图的鼠标移动方法
#view 视图
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
def onViewMouseMove(view, mp, buttons, clicks, delta):
	firstTouch = FALSE
	secondTouch = FALSE
	firstPoint = mp
	secondPoint = mp
	if (buttons == 1):
		firstTouch = TRUE
	if (view.m_type == "grid"):
		mouseMoveGrid(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "tree"):
		mouseMoveTree(view, firstTouch, secondTouch, firstPoint, secondPoint)
	elif(view.m_type == "chart"):
		mouseMoveChart(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "div" or view.m_type =="layout"):
		mouseMoveDiv(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "button"):
		invalidateView(view, view.m_paint)
		
#视图的鼠标按下方法
#view 视图
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
def onViewMouseDown(view, mp, buttons, clicks, delta):
	global m_addingPlot_Chart
	firstTouch = FALSE
	secondTouch = FALSE
	firstPoint = mp
	secondPoint = mp
	if (buttons == 1):
		firstTouch = TRUE
	if (view.m_type == "grid"):
		mouseDownGrid(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "tree"):
		mouseDownTree(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "chart"):
		view.m_selectShape = ""
		view.m_selectShapeEx = ""
		facecat.m_mouseDownPoint_Chart = mp;
		if (view.m_sPlot == None):
			selectShape(view, mp)
	elif(view.m_type == "div" or view.m_type =="layout"):
		mouseDownDiv(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "button"):
		invalidateView(view, view.m_paint)

#视图的鼠标抬起方法
#view 视图
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
def onViewMouseUp(view, mp, buttons, clicks, delta):
	firstTouch = FALSE
	secondTouch = FALSE
	firstPoint = mp
	secondPoint = mp
	if (buttons == 1):
		firstTouch = TRUE
	if (view.m_type == "grid"):
		mouseUpGrid(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "tree"):
		mouseUpTree(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "div" or view.m_type =="layout"):
		mouseUpDiv(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "chart"):
		facecat.m_firstTouchIndexCache_Chart = -1
		facecat.m_secondTouchIndexCache_Chart = -1
		invalidateView(view, view.m_paint)
	elif(view.m_type == "button"):
		invalidateView(view, view.m_paint)

#视图的鼠标点击方法
#view 视图
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
def onViewClick(view, mp, buttons, clicks, delta):
	global m_addingPlot_Chart
	if(view.m_type == "radiobutton"):
		clickRadioButton(view, mp)
		if(view.m_parent != None):
			invalidateView(view.m_parent, view.m_parent.m_paint)
		else:
			invalidateView(view, view.m_paint)
	elif(view.m_type == "checkbox"):
		clickCheckBox(view, mp)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "tabbutton"):
		tabView = view.m_parent
		for i in range(0, len(tabView.m_tabPages)):
			if(tabView.m_tabPages[i].m_headerButton == view):
				selectTabPage(tabView, tabView.m_tabPages[i])
		invalidateView(tabView, tabView.m_paint)
	#沪深A股
	if(view.m_name == "Button"):
		df = qs.realtime_data()
		bindDataFrame(df)
	#可转债
	elif(view.m_name == "Button2"):
		#获取可转债最新行情指标
		df = qs.realtime_data('可转债')
		bindDataFrame(df)
	#期货
	elif(view.m_name == "Button3"):
		#获取期货最新行情指标
		df = qs.realtime_data('期货')
		bindDataFrame(df)
	#美股
	elif(view.m_name == "Button4"):
		#获取美股最新行情指标
		df = qs.realtime_data('美股')
		bindDataFrame(df)
	#港股
	elif(view.m_name == "Button5"):
		#获取港股最新行情指标
		df = qs.realtime_data('港股')
		bindDataFrame(df)
	#行业板块
	elif(view.m_name == "Button6"):
		#获取行业板块最新行情指标
		df = qs.realtime_data('行业板块')
		bindDataFrame(df)
	#概念板块
	elif(view.m_name == "Button7"):
		#获取概念板块最新行情指标
		df = qs.realtime_data('概念板块')
		bindDataFrame(df)
	#ETF
	elif(view.m_name == "Button8"):
		#获取ETF最新行情指标
		df = qs.realtime_data('ETF')
		bindDataFrame(df)
	#个股行情
	elif(view.m_name == "Button9"):
		df = qs.realtime_data(code=['中国平安','300684','锂电池ETF','BK0679','上证指数'])
		bindDataFrame(df)
	#股票日内交易
	elif(view.m_name == "Button10"):
		#股票日内交易数据
		df = qs.intraday_data('中国平安')
		bindDataFrame(df)
	#基金日内交易
	elif(view.m_name == "Button11"):
		#基金日内交易数据
		df = qs.intraday_data('有色50ETF')
		bindDataFrame(df)
	#个股交易快照
	elif(view.m_name == "Button12"):
		df = qs.stock_snapshot('中国平安')
		bindDataFrame(df)
	#实时盘口
	elif(view.m_name == "Button13"):
		#异动类型：火箭发射
		df = qs.realtime_change(1)
		bindDataFrame(df)
	#龙虎榜数据
	elif(view.m_name == "Button14"):
		df = qs.stock_billboard('20220901','20221011')
		bindDataFrame(df)
	#日K线
	elif(view.m_name == "Button15"):
		#默认日频率、前复权所有历史数据
		#open：开盘价，high：最高价，low：最低价，close：收盘价
		#vol：成交量，turnover：成交金额，turnover_rate:换手率
		#在notebook上输入"qs.get_data?"可查看数据接口的相应参数
		df = qs.get_data('601318')
		bindDataFrame(df)
	#5分钟线
	elif(view.m_name == "Button16"):
		#个股code_list可以输入代码或简称或多个股票的list
		#获取中国平安2022年9月28日至今的5分钟数据，默认前复权
		df = qs.get_data('中国平安',start='20220928',freq=5)
		bindDataFrame(df)
	#后复权数据
	elif(view.m_name == "Button17"):
		#后复权数据,频率为周
		df = qs.get_data('中国平安',fqt=2,freq='w')
		bindDataFrame(df)
	#美股K线
	elif(view.m_name == "Button18"):
		df = qs.get_data('AAPL')
		bindDataFrame(df)
	#期货K线
	elif(view.m_name == "Button19"):
		df = qs.get_data('棕榈油2302')
		bindDataFrame(df)
	#指数历史数据
	elif(view.m_name == "Button20"):
		code_list=['sh','sz']
		df = qs.get_data(code_list)
		bindDataFrame(df)
	#全球指数
	elif(view.m_name == "Button21"):
		#全球指数可参见：https://quote.eastmoney.com/center/qqzs.html
		global_indexs=['道琼斯','标普500','纳斯达克','恒生指数','英国富时','法国CAC40','德国DAX',
					  '日经225','韩国KOSPI','澳大利亚标普200','印度孟买SENSEX','俄罗斯RTS','加拿大S&P',
					   '台湾加权','美元指数','路透CRB商品指数']
		df = qs.get_data(global_indexs)
		bindDataFrame(df)
	#多只证券历史数据
	elif(view.m_name == "Button22"):
		code_list = ['中国平安','300684','锂电池ETF','BK0679','上证指数']
		df = qs.get_price(code_list)
		bindDataFrame(df)
	#上证50成份股
	elif(view.m_name == "Button23"):
		df = qs.index_member('sz50')
		bindDataFrame(df)
	#沪深300成分股
	elif(view.m_name == "Button24"):
		df = qs.index_member('hs300')
		bindDataFrame(df)
	#概念板块名称
	elif(view.m_name == "Button25"):
		name_list=qs.ths_index_name('行业')
		print(name_list)
	#概念板块成分股
	elif(view.m_name == "Button26"):
		#种植业与林业成分股
		df = qs.ths_index_member('种植业与林业')
		bindDataFrame(df)
	#概念指数行情数据
	elif(view.m_name == "Button27"):
		df = qs.ths_index_data('有机硅概念')
		bindDataFrame(df)
	#日内资金流数据
	elif(view.m_name == "Button28"):
		#注意要在交易日交易时段才能获取到相应数据
		df = qs.intraday_money('中国平安')
		bindDataFrame(df)
	#历史资金流向数据
	elif(view.m_name == "Button29"):
		df = qs.hist_money('中国平安')
		bindDataFrame(df)
	#个股n日资金流
	elif(view.m_name == "Button30"):
		#默认ndays=[3, 5, 10, 20]
		df = qs.stock_money('中国平安')
		bindDataFrame(df)
	#同花顺个股20日资金流数据
	elif(view.m_name == "Button31"):
		df = qs.ths_money('个股',n=20)
		bindDataFrame(df)
	#同花顺行业板块10日资金流数据
	elif(view.m_name == "Button32"):
		df = qs.ths_money('行业',n=10)
		bindDataFrame(df)
	#概念板块5日资金流数据
	elif(view.m_name == "Button33"):
		df = qs.ths_money('概念',n=5)
		bindDataFrame(df)
	#北向资金每日净流入数据
	elif(view.m_name == "Button34"):
		df = qs.north_money()
		bindDataFrame(df)
	#北向资金增持行业板块
	elif(view.m_name == "Button35"):
		df = qs.north_money('行业',5)
		bindDataFrame(df)
	#北向资金增持概念板块
	elif(view.m_name == "Button36"):
		df = qs.north_money('概念',5)
		bindDataFrame(df)
	#北向资金增持个股情况
	elif(view.m_name == "Button37"):
		#有个小bug，列名没有对应起来，该函数调用将报错，将在新版本中修正。
		df = qs.north_money('个股',5)
		bindDataFrame(df)
	#股票前十大股东信息
	elif(view.m_name == "Button38"):
		df = qs.stock_holder_top10('中国平安', n=2)
		bindDataFrame(df)
	#沪深个股股东数量
	elif(view.m_name == "Button39"):
		df = qs.stock_holder_num('20220930')
		bindDataFrame(df)
	#大股东增减持变动明细
	elif(view.m_name == "Button40"):
		df = qs.stock_holder_change()
		bindDataFrame(df)
	#机构持股
	elif(view.m_name == "Button41"):
		#2022年2季度
		df = qs.institute_hold('20222')
		bindDataFrame(df)
	#主营业务收入数据
	elif(view.m_name == "Button42"):
		df = qs.main_business('丰元股份')
		bindDataFrame(df)
	#业绩报表
	elif(view.m_name == "Button43"):
		df = qs.financial_statement('业绩报表',date='20220930')
		bindDataFrame(df)
	#业绩预告
	elif(view.m_name == "Button44"):
		df = qs.financial_statement('yjyg')
		bindDataFrame(df)
	#业绩快报
	elif(view.m_name == "Button45"):
		df = qs.financial_statement('yjkb')
		bindDataFrame(df)
	#资产负债表
	elif(view.m_name == "Button46"):
		df = qs.financial_statement('资产负债表')
		bindDataFrame(df)
	#利润表
	elif(view.m_name == "Button47"):
		df = qs.financial_statement('利润表')
		bindDataFrame(df)
	#现金流量表
	elif(view.m_name == "Button48"):
		df = qs.financial_statement('现金流量表')
		bindDataFrame(df)
	#个股基本财务指标
	elif(view.m_name == "Button49"):
		code_list = ['300139','中国平安','西部建设','贵州茅台','丰元股份','002432']
		df = qs.stock_basics(code_list)
		bindDataFrame(df)
	#个股详细财务指标
	elif(view.m_name == "Button50"):
		df = qs.stock_indicator('中国平安')
		bindDataFrame(df)
	#每股收益预测
	elif(view.m_name == "Button51"):
		df = qs.eps_forecast()
		bindDataFrame(df)
	#GDP数据
	elif(view.m_name == "Button52"):
		df = qs.macro_data('gdp')
		bindDataFrame(df)
	#CPI物价指数
	elif(view.m_name == "Button53"):
		df = qs.macro_data('cpi')
		bindDataFrame(df)
	#PPI价格指数
	elif(view.m_name == "Button54"):
		df = qs.macro_data('ppi')
		bindDataFrame(df)
	#PML采购经理人指数
	elif(view.m_name == "Button55"):
		df = qs.macro_data('pmi')
		bindDataFrame(df)
	#货币供应量
	elif(view.m_name == "Button56"):
		df = qs.macro_data('ms')
		bindDataFrame(df)
	#贷款基准利率LPR
	elif(view.m_name == "Button57"):
		df = qs.macro_data('lpr')
		bindDataFrame(df)
	#上海银行同业拆借市场
	elif(view.m_name == "Button58"):
		#默认输出上海银行同业拆借市场利率
		#或输入market='sh'
		df = qs.ib_rate()
		bindDataFrame(df)
	#中国银行同业拆借市场
	elif(view.m_name == "Button59"):
		df = qs.ib_rate(market='ch')
		bindDataFrame(df)
	#伦敦银行同业拆借市场
	elif(view.m_name == "Button60"):
		#伦敦简称l，注意是英文字母‘l’(London的首字母小写)，不是数字1！
		#币种可选GBP'英镑',USD'美元',EUR'欧元',JPY'日元'
		df = qs.ib_rate(market='l',fc='GBP')
		bindDataFrame(df)
	#欧洲银行同业拆借市场
	elif(view.m_name == "Button61"):
		df = qs.ib_rate('eu')
		bindDataFrame(df)
	#香港银行同业拆借市场
	elif(view.m_name == "Button62"):
		df = qs.ib_rate('hk','HKD')
		bindDataFrame(df)
	#新加坡市场
	elif(view.m_name == "Button63"):
		df = qs.ib_rate('s','usd')
		bindDataFrame(df)
	#财联社电报新闻数据
	elif(view.m_name == "Button64"):
		#默认参数输出财联社电报新闻数据
		df = qs.news_data()
		bindDataFrame(df)
	#市场快讯数据
	elif(view.m_name == "Button65"):
		df = qs.news_data('js')
		bindDataFrame(df)
	#新闻联播
	elif(view.m_name == "Button66"):
		#参数start起始日期，end结束日期，使用默认参数输出最新日期新闻联播
		df = qs.news_data('cctv',start='20221016',end='20221016')
		bindDataFrame(df)
	#个股新闻
	elif(view.m_name == "Button67"):
		#使用新闻统一接口
		df = qs.news_data('个股',code='天瑞仪器')
		bindDataFrame(df)
	#涨停股
	elif(view.m_name == "Button68"):
		df = qs.limit_pool('u','20221104')
		bindDataFrame(df)
	#跌停股
	elif(view.m_name == "Button69"):
		df = qs.limit_pool('d','20221104')
		bindDataFrame(df)
	#强势股
	elif(view.m_name == "Button70"):
		df = qs.limit_pool('s','20221104')
		bindDataFrame(df)
	#创新高/低股票池
	elif(view.m_name == "Button71"):
		df = qs.ths_pool('一年新高')
		bindDataFrame(df)
	#连续上涨
	elif(view.m_name == "Button72"):
		df = qs.ths_pool('连续上涨')
		bindDataFrame(df)
	#量价齐升
	elif(view.m_name == "Button73"):
		df = qs.ths_pool('量价齐升')
		bindDataFrame(df)
	#突破n日均线
	elif(view.m_name == "Button74"):
		df = qs.ths_pool('u20')
		bindDataFrame(df)
	#价格数据
	elif(view.m_name == "Button75"):
		df = qs.ret_rank(ths_price, w_list=[1,5,20,60,120],c=3)[:10]
		bindDataFrame(df)
	#计算板块收益率
	elif(view.m_name == "Button76"):
		code_list = list(qs.realtime_data('概念')['名称'])
		#排除涨停概念（买不到）
		del_code=['昨日连板_含一字','昨日涨停_含一字','昨日涨停','昨日连板']
		for code in del_code:
			code_list.remove(code)
		all_price = qs.get_price(code_list,start='20220101')
		all_rets=qs.ret_date(all_price, w_list=[1,5,20,60,120])
		#分别按[1,5,20,60,120]收益率排序前10
		df = qs.ret_top(all_rets,10)
		bindDataFrame(df)
	#东方财富热门板块
	elif(view.m_name == "Button77"):
		code_list = list(qs.realtime_data('概念')['名称'])
		#排除涨停概念（买不到）
		del_code=['昨日连板_含一字','昨日涨停_含一字','昨日涨停','昨日连板']
		for code in del_code:
			code_list.remove(code)
		df = qs.get_price(code_list,start='20220101')
		bindDataFrame(df)
		

#视图的鼠标滚动方法
#view 视图
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
def onViewMouseWheel(view, mp, buttons, clicks, delta):
	if (view.m_type == "grid"):
		mouseWheelGrid(view, delta)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "tree"):
		mouseWheelTree(view, delta)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "div" or view.m_type =="layout"):
		mouseWheelDiv(view, delta)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "chart"):
		if(delta > 0):
			zoomOutChart(view);
		elif(delta < 0):
			zoomInChart(view);
		invalidateView(view, view.m_paint)

m_xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<html xmlns=\"facecat\">\r\n  <head>\r\n  </head>\r\n  <body>\r\n    <div type=\"splitlayout\" layoutstyle=\"lefttoright\" bordercolor=\"none\" dock=\"fill\" size=\"400,400\" candragsplitter=\"true\" splitmode=\"AbsoluteSize\" splittervisible=\"true\" splitter-bordercolor=\"-200000000105\" splitterposition=\"200,1\">\r\n      <div type=\"layout\" name=\"div1\" showvscrollbar=\"true\" layoutstyle=\"TopToBottom\">\r\n        <input type=\"button\" name=\"Button\" text=\"沪深A股\" location=\"55,35\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button2\" text=\"可转债\" location=\"56,57\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button3\" text=\"期货\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button4\" text=\"美股\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button5\" text=\"港股\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button6\" text=\"行业板块\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button7\" text=\"概念板块\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button8\" text=\"ETF\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button9\" text=\"个股行情\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button10\" text=\"股票日内交易\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button11\" text=\"基金日内交易\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button12\" text=\"个股交易快照\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button13\" text=\"实时盘口\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button14\" text=\"龙虎榜数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button15\" text=\"日K线\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button16\" text=\"5分钟线\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button17\" text=\"后复权数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button18\" text=\"美股K线\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button19\" text=\"期货K线\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button20\" text=\"指数历史数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button21\" text=\"全球指数\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button22\" text=\"多只证券历史数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button23\" text=\"上证50成份股\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button24\" text=\"沪深300成分股\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button25\" text=\"概念板块名称\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button26\" text=\"概念板块成分股\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button27\" text=\"概念指数行情数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button28\" text=\"日内资金流数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button29\" text=\"历史资金流向数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button30\" text=\"个股n日资金流\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button31\" text=\"同花顺个股20日资金流数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button32\" text=\"同花顺行业板块10日资金流数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button33\" text=\"概念板块5日资金流数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button34\" text=\"北向资金每日净流入\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button35\" text=\"北向资金增持行业板块\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button36\" text=\"北向资金增持概念板块\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button37\" text=\"北向资金增持个股情况\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button38\" text=\"股票前十大股东信息\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button39\" text=\"沪深个股股东数量\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button40\" text=\"大股东增减持变动明细\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button41\" text=\"机构持股\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button42\" text=\"主营业务收入数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button43\" text=\"业绩报表\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button44\" text=\"业绩预告\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button45\" text=\"业绩快报\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button46\" text=\"资产负债表\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button47\" text=\"利润表\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button48\" text=\"现金流量表\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button49\" text=\"个股基本财务指标\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button50\" text=\"个股详细财务指标\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button51\" text=\"每股收益预测\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button52\" text=\"GDP数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button53\" text=\"CPI物价指数\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button54\" text=\"PPI价格指数\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button55\" text=\"PML采购经理人指数\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button56\" text=\"货币供应量\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button57\" text=\"贷款基准利率LPR\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button58\" text=\"上海银行同业拆借市场\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button59\" text=\"中国银行同业拆借市场\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button60\" text=\"伦敦银行同业拆借市场\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button61\" text=\"欧洲银行同业拆借市场\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button62\" text=\"香港银行同业拆借市场\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button63\" text=\"新加坡市场\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button64\" text=\"财联社电报新闻数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button65\" text=\"市场快讯数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button66\" text=\"新闻联播\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button67\" text=\"个股新闻\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button68\" text=\"涨停股\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button69\" text=\"跌停股\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button70\" text=\"强势股\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button71\" text=\"创新高/低股票池\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button72\" text=\"连续上涨\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button73\" text=\"量价齐升\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button74\" text=\"突破n日均线\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button75\" text=\"价格数据\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button76\" text=\"计算板块收益率\" location=\"66,156\" size=\"200,40\" />\r\n        <input type=\"button\" name=\"Button77\" text=\"东方财富热门板块\" location=\"66,156\" size=\"200,40\" />\r\n      </div>\r\n      <table name=\"grid\" />\r\n    </div>\r\n  </body>\r\n</html>"

m_paint = FCPaint() #创建绘图对象
facecat.m_paintCallBack = onViewPaint 
facecat.m_paintBorderCallBack = onViewPaintBorder 
facecat.m_mouseDownCallBack = onViewMouseDown 
facecat.m_mouseMoveCallBack = onViewMouseMove 
facecat.m_mouseUpCallBack = onViewMouseUp
facecat.m_mouseWheelCallBack = onViewMouseWheel
facecat.m_clickCallBack = onViewClick

def WndProc(hwnd,msg,wParam,lParam):
	if msg == WM_DESTROY:
		win32gui.PostQuitMessage(0)
	if(hwnd == m_paint.m_hWnd):
		if msg == WM_ERASEBKGND:
			return 1
		elif msg == WM_SIZE:
			rect = win32gui.GetClientRect(m_paint.m_hWnd)
			m_paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
			for view in m_paint.m_views:
				if view.m_dock == "fill":
					view.m_size = FCSize(m_paint.m_size.cx, m_paint.m_size.cy)
			updateView(m_paint.m_views)
			invalidate(m_paint)
		elif msg == WM_LBUTTONDOWN:
			mx, my = win32api.GetCursorPos()
			ccx, ccy = win32gui.ScreenToClient(hwnd, (mx, my))
			mp = FCPoint(ccx, ccy)
			onMouseDown(mp, 1, 1, 0, m_paint)
		elif msg == WM_LBUTTONUP:
			mx, my = win32api.GetCursorPos()
			ccx, ccy = win32gui.ScreenToClient(hwnd, (mx, my))
			mp = FCPoint(ccx, ccy)
			onMouseUp(mp, 1, 1, 0, m_paint)
		elif msg == WM_MOUSEWHEEL:
			mx, my = win32api.GetCursorPos()
			ccx, ccy = win32gui.ScreenToClient(hwnd, (mx, my))
			mp = FCPoint(ccx, ccy)
			if(wParam > 4000000000):
				onMouseWheel(mp, 0, 0, -1, m_paint)
			else:
				onMouseWheel(mp, 0, 0, 1, m_paint)
		elif msg == WM_MOUSEMOVE:
			mx, my = win32api.GetCursorPos()
			ccx, ccy = win32gui.ScreenToClient(hwnd, (mx, my))
			mp = FCPoint(ccx, ccy)
			if(wParam == 1):
				onMouseMove(mp, 1, 1, 0, m_paint)
			elif(wParam == 2):
				onMouseMove(mp, 2, 1, 0, m_paint)
			else:
				onMouseMove(mp, 0, 0, 0, m_paint)
		elif msg == WM_PAINT:
			rect = win32gui.GetClientRect(m_paint.m_hWnd)
			m_paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
			for view in m_paint.m_views:
				if view.m_dock == "fill":
					view.m_size = FCSize(m_paint.m_size.cx, m_paint.m_size.cy)
			updateView(m_paint.m_views)
			invalidate(m_paint)
	return win32gui.DefWindowProc(hwnd,msg,wParam,lParam)

wc = win32gui.WNDCLASS()
wc.hbrBackground = COLOR_BTNFACE + 1
wc.hCursor = win32gui.LoadCursor(0,IDI_APPLICATION)
wc.lpszClassName = "facecat-py"
wc.lpfnWndProc = WndProc
reg = win32gui.RegisterClass(wc)
hwnd = win32gui.CreateWindow(reg,'facecat-py',WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN,CW_USEDEFAULT,CW_USEDEFAULT,CW_USEDEFAULT,CW_USEDEFAULT,0,0,0,None)
m_paint.m_hWnd = hwnd

#创建列
#grid:表格
def createGridColumn(grid):
	gridColumn = FCGridColumn()
	if (grid.m_paint.m_defaultUIStyle == "dark"):
		gridColumn.m_backColor = "rgb(0,0,0)"
		gridColumn.m_borderColor = "rgb(150,150,150)"
		gridColumn.m_textColor = "rgb(255,255,255)"
	elif (grid.m_paint.m_defaultUIStyle == "light"):
		gridColumn.m_backColor = "rgb(200,200,200)"
		gridColumn.m_borderColor = "rgb(100,100,100)"
		gridColumn.m_textColor = "rgb(0,0,0)"
	return gridColumn
    
#创建列
#grid:表格
def createGridCell(grid):
	gridCell = FCGridCell()
	if (grid.m_paint.m_defaultUIStyle == "dark"):
		gridCell.m_backColor = "rgb(0,0,0)"
		gridCell.m_borderColor = "rgb(150,150,150)"
		gridCell.m_textColor = "rgb(255,255,255)"
	elif (grid.m_paint.m_defaultUIStyle == "light"):
		gridCell.m_backColor = "rgb(255,255,255)"
		gridCell.m_borderColor = "rgb(100,100,100)"
		gridCell.m_textColor = "rgb(0,0,0)"
	return gridCell

#绑定数据
def bindDataFrame(df):
	global m_paint
	grid = findViewByName("grid", m_paint.m_views)
	grid.m_columns = []
	grid.m_rows = []
	for i in range(0,len(df.columns)):
		column1 = createGridColumn(grid)
		column1.m_text = df.columns[i]
		column1.m_width = 100
		grid.m_columns.append(column1)
	for i in range(0, len(df)):
		row = FCGridRow()
		grid.m_rows.append(row)
		for c in range(0, len(grid.m_columns)):
			cell = FCGridCell()
			if (grid.m_paint.m_defaultUIStyle == "dark"):
				cell.m_backColor = "rgb(0,0,0)"
			elif(grid.m_paint.m_defaultUIStyle == "light"):
				cell.m_backColor = "rgb(255,255,255)"
			cell.m_value = df.iloc[i][df.columns[c]]
			row.m_cells.append(cell)
	invalidateView(grid, grid.m_paint)

root = ET.fromstring(m_xml)
for child in root:
	if(child.tag == "{facecat}body"):
		readXmlNode(m_paint, child, None)
#获取沪深A股最新行情指标
df = qs.realtime_data('可转债')
bindDataFrame(df)
rect = win32gui.GetClientRect(hwnd)
m_paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
for view in m_paint.m_views:
	if view.m_dock == "fill":
		view.m_size = FCSize(m_paint.m_size.cx, m_paint.m_size.cy)
updateView(m_paint.m_views)
win32gui.ShowWindow(hwnd,SW_SHOWNORMAL)
win32gui.UpdateWindow(hwnd)
win32gui.PumpMessages()