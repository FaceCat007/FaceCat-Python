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

m_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<html xmlns=\"facecat\">\r\n  <head>\r\n  </head>\r\n  <body>\r\n    <div type=\"splitlayout\" name=\"divAll\" candragsplitter=\"true\" layoutstyle=\"toptobottom\" dock=\"fill\" size=\"400,505\" splitterposition=\"0,80,400,80\" bordercolor=\"none\">\r\n      <div type=\"tab\" name=\"tabTradeAccount\" bordercolor=\"none\" backcolor=\"none\">\r\n        <div type=\"tabpage\" name=\"pageTradeAccount\" text=\"Position\" headersize=\"100,0\" backcolor=\"none\" bordercolor=\"none\" padding=\"5,5,5,5\">\r\n          <table name=\"gridTradeAccount\" dock=\"fill\" headerheight=\"70\" showhscrollbar=\"false\" bordercolor=\"none\" backcolor=\"-200000000163\">\r\n            <tr>\r\n              <th name=\"colF1\" text=\"colF1\" width=\"120\" location=\"0,0\" size=\"120,70\" />\r\n              <th name=\"colF2\" text=\"colF2\" width=\"120\" />\r\n              <th name=\"colF3\" text=\"colF3\" width=\"120\" />\r\n              <th name=\"colF4\" text=\"colF4\" width=\"120\" location=\"240,0\" size=\"120,70\" />\r\n              <th name=\"colF5\" text=\"colF5\" width=\"120\" />\r\n              <th name=\"colF6\" text=\"colF6\" width=\"120\" />\r\n              <th name=\"colF7\" text=\"colF7\" width=\"120\" />\r\n              <th name=\"colF8\" text=\"colF8\" width=\"120\" />\r\n              <th name=\"colF9\" text=\"colF9\" width=\"120\" />\r\n              <th name=\"colF10\" text=\"colF10\" width=\"120\" />\r\n              <th name=\"colF11\" text=\"colF11\" width=\"120\" />\r\n              <th name=\"colF12\" text=\"colF12\" width=\"120\" />\r\n              <th name=\"colF13\" text=\"colF13\" width=\"120\" />\r\n              <th name=\"colF14\" text=\"colF14\" width=\"120\" />\r\n              <th name=\"colF15\" text=\"colF15\" width=\"120\" />\r\n              <th name=\"colF16\" text=\"colF16\" width=\"120\" />\r\n              <th name=\"colF17\" text=\"colF17\" width=\"120\" />\r\n              <th name=\"colF18\" text=\"colF18\" width=\"120\" />\r\n              <th name=\"colF19\" text=\"colF19\" width=\"120\" />\r\n              <th name=\"colF20\" text=\"colF20\" width=\"120\" />\r\n              <th name=\"colF21\" text=\"colF21\" width=\"120\" />\r\n            </tr>\r\n          </table>\r\n        </div>\r\n      </div>\r\n      <div type=\"splitlayout\" name=\"divBottom\" candragsplitter=\"true\" layoutstyle=\"bottomtotop\" size=\"400,450\" splitterposition=\"0,430,400,430\" bordercolor=\"none\" backcolor=\"none\">\r\n        <div name=\"divStatus\" size=\"966,17\">\r\n          <label name=\"lblTradingTime\" text=\"--\" location=\"3,2\" size=\"100,20\" font=\"Default,12\" />\r\n          <label name=\"lbllog\" text=\"--\" location=\"105,2\" size=\"352,20\" font=\"Default,12\" />\r\n        </div>\r\n        <div type=\"splitlayout\" name=\"divMiddle\" candragsplitter=\"true\" layoutstyle=\"toptobottom\" size=\"600,600\" splitmode=\"percentsize\" splitterposition=\"0,450,400,450\" bordercolor=\"none\" backcolor=\"none\">\r\n          <div type=\"splitlayout\" name=\"divMiddleTop\" candragsplitter=\"true\" layoutstyle=\"bottomtotop\" size=\"600,600\" splitterposition=\"0,330,400,330\" bordercolor=\"none\" backcolor=\"none\">\r\n            <div bordercolor=\"none\" padding=\"5,5,5,5\" backcolor=\"none\">\r\n              <div type=\"splitlayout\" name=\"divMain\" dock=\"fill\" candragsplitter=\"true\" layoutstyle=\"lefttoright\" size=\"420,420\" splitterposition=\"310,0,310,300\" bordercolor=\"none\" backcolor=\"none\">\r\n                <div bordercolor=\"none\" backcolor=\"none\" padding=\"0,0,5,0\">\r\n                  <div type=\"tab\" name=\"tabTradeMain\" selectedindex=\"0\" location=\"0,0\" size=\"1166,270\" dock=\"fill\" bordercolor=\"-200000000193\" backcolor=\"-200000000163\">\r\n                    <div type=\"tabpage\" name=\"pageTrade\" text=\"StandardTrade\" backcolor=\"none\" bordercolor=\"none\">\r\n                      <div name=\"divTrade\" size=\"310,250\" dock=\"fill\" location=\"0,0\" bordercolor=\"none\" backcolor=\"none\">\r\n                        <label name=\"lblContract\" text=\"Code\" location=\"8,18\" size=\"37,20\" font=\"Default,14\" />\r\n                        <label name=\"lblBuySell\" text=\"BidSell\" location=\"8,49\" size=\"38,19\" font=\"Default,14\" />\r\n                        <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnOpenCloseMode\" text=\"Auto\" location=\"3,76\" size=\"46,20\" />\r\n                        <label name=\"lblVolume\" text=\"Volume\" location=\"8,109\" size=\"38,19\" font=\"Default,14\" />\r\n                        <input type=\"radio\" name=\"rbOpen\" backcolor=\"rgba(43,138,195,100)\" checked=\"true\" text=\"Open\" location=\"52,76\" size=\"65,20\" groupname=\"OpenClose\" />\r\n                        <input type=\"radio\" name=\"rbCloseToday\" text=\"CloseToday\" location=\"120,76\" size=\"65,20\" groupname=\"OpenClose\" />\r\n                        <input type=\"radio\" name=\"rbClose\" text=\"Close\" location=\"182,76\" size=\"65,20\" groupname=\"OpenClose\" />\r\n                        <input type=\"radio\" name=\"rbBuy\" backcolor=\"rgba(255,0,0,100)\" checked=\"true\" text=\"Bid\" location=\"53,47\" size=\"64,20\" groupname=\"BuySell\" />\r\n                        <input type=\"radio\" name=\"rbSell\" text=\"Sell\" location=\"119,47\" size=\"64,20\" groupname=\"BuySell\" />\r\n                        <input type=\"text\" name=\"txtIssueCode\" font=\"Default,20\" location=\"53,11\" size=\"163,28\" lineheight=\"28\" multiline=\"false\" />\r\n                        <input type=\"checkbox\" name=\"cbLock\" text=\"Lock\" location=\"220,15\" size=\"73,20\" canfocus=\"false\" buttonsize=\"16,16\" />\r\n                        <input type=\"range\" name=\"spinVolume\" font=\"Default,20\" digit=\"0\" location=\"52,102\" size=\"115,28\" lineheight=\"28\" maximum=\"100000000\" minimum=\"1\" textalign=\"far\" />\r\n                        <input type=\"range\" name=\"spinPrice\" digit=\"2\" font=\"Default,20\" location=\"52,142\" size=\"115,24\" lineheight=\"28\" maximum=\"100000000\" textalign=\"far\" />\r\n                        <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnOrder\" font=\"Default,16\" text=\"Order\" backcolor=\"rgb(15,193,118)\" location=\"8,179\" size=\"211,48\" />\r\n                        <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnCancel\" text=\"Cancel\" location=\"226,184\" backcolor=\"rgb(248,73,96)\" size=\"74,24\" font=\"Default,12\" />\r\n                        <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnPreCondition\" text=\"Condition\" location=\"226,209\" size=\"74,23\" font=\"Default,12\" />\r\n                        <label name=\"lblLess\" text=\"&lt;=\" location=\"185,104\" size=\"26,21\" font=\"Default,16\" />\r\n                        <label name=\"lblMaxVolume\" text=\"0\" location=\"206,104\" size=\"16,21\" font=\"Default,16\" />\r\n                        <label name=\"lblUp\" text=\"0\" location=\"188,121\" size=\"100,20\" opacity=\"1\" />\r\n                        <label name=\"lblAskPrice\" text=\"0\" location=\"188,135\" size=\"53,20\" />\r\n                        <label name=\"lblBidPrice\" text=\"0\" location=\"188,149\" size=\"51,21\" />\r\n                        <label name=\"lblDown\" text=\"0\" location=\"188,163\" size=\"48,20\" />\r\n                        <label name=\"Label\" text=\"/\" location=\"241,136\" size=\"17,20\" font=\"Default,12\" />\r\n                        <label name=\"Label1\" text=\"/\" location=\"239,150\" size=\"16,20\" font=\"Default,12\" />\r\n                        <label name=\"lblAskVolume\" text=\"0\" location=\"250,136\" size=\"57,18\" />\r\n                        <label name=\"lblBidVolume\" text=\"0\" location=\"250,150\" size=\"57,20\" />\r\n                        <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnTradeMode\" text=\"Follow\" location=\"3,143\" size=\"46,20\" />\r\n                        <select name=\"ComboBox\" location=\"175,45\" size=\"100,20\" selectedindex=\"0\">\r\n                          <option text=\"选项1\" />\r\n                          <option text=\"选项2\" />\r\n                        </select>\r\n                      </div>\r\n                    </div>\r\n                    <div type=\"tabpage\" name=\"pageTradeSetting\" text=\"Settings\" backcolor=\"none\" bordercolor=\"none\">\r\n                      <div name=\"divTradeSettings\" dock=\"fill\" backcolor=\"none\" bordercolor=\"none\">\r\n                        <input type=\"checkbox\" name=\"cbStartFastTrading\" text=\"StartFastTrade\" location=\"171,66\" size=\"115,20\" checked=\"true\" />\r\n                        <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnHotKeySetting\" font=\"Default,12\" text=\"FastTradeSettings\" location=\"14,59\" size=\"155,30\" />\r\n                        <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnAutoCloseSetting\" font=\"Default,12\" text=\"AutoCloseSttings\" location=\"14,96\" size=\"155,30\" />\r\n                        <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnAllCloseOrCancelSetting\" font=\"Default,12\" text=\"AllCloseOrCancelSetting\" location=\"14,134\" size=\"155,30\" />\r\n                        <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnAutoCancelSetting\" font=\"Default,12\" text=\"AutoCancelSetting\" location=\"14,172\" size=\"155,30\" />\r\n                        <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnDefaultVolumeSetting\" font=\"Default,12\" text=\"DefaultVolumeSetting\" location=\"14,22\" size=\"155,30\" />\r\n                        <input type=\"checkbox\" name=\"cbStartAutoClose\" text=\"StartAutoClose\" location=\"171,103\" size=\"113,20\" checked=\"true\" />\r\n                        <input type=\"checkbox\" name=\"cbStartAutoCancel\" text=\"StartAutoCancel\" location=\"173,172\" size=\"110,21\" checked=\"true\" />\r\n                      </div>\r\n                    </div>\r\n                  </div>\r\n                </div>\r\n                <div type=\"splitlayout\" name=\"divMain\" dock=\"fill\" candragsplitter=\"true\" layoutstyle=\"righttoleft\" size=\"420,420\" splitterposition=\"100,0\" bordercolor=\"none\" backcolor=\"none\">\r\n                  <div bordercolor=\"none\" backcolor=\"none\" padding=\"5,0,0,0\">\r\n                    <div type=\"tab\" name=\"tabOrder2\" selectedindex=\"1\" backcolor=\"-200000000163\" bordercolor=\"-200000000193\" dock=\"fill\">\r\n                      <div type=\"tabpage\" name=\"pageChart\" text=\"Chart\" bordercolor=\"none\" backcolor=\"none\">\r\n                        <div type=\"splitlayout\" name=\"divChart\" dock=\"fill\" layoutstyle=\"toptobottom\" size=\"400,400\" splitterposition=\"0,30,400,30\" bordercolor=\"none\" backcolor=\"none\">\r\n                          <div bordercolor=\"none\" backcolor=\"none\">\r\n                            <label name=\"lblKLineCode\" text=\"cu1906\" location=\"10,7\" size=\"56,22\" font=\"Default,14\" />\r\n                            <input type=\"radio\" name=\"rbday\" text=\"DayLine\" location=\"427,6\" size=\"68,20\" />\r\n                            <input type=\"radio\" name=\"rb5m\" text=\"5M\" location=\"104,6\" size=\"72,20\" checked=\"True\" />\r\n                            <input type=\"radio\" name=\"rb15m\" text=\"15M\" location=\"181,6\" size=\"74,20\" />\r\n                            <input type=\"radio\" name=\"rb30m\" text=\"30M\" location=\"262,6\" size=\"70,20\" />\r\n                            <input type=\"radio\" name=\"rb60m\" text=\"60M\" location=\"341,6\" size=\"75,20\" />\r\n                          </div>\r\n                          <chart name=\"chart\" dock=\"fill\" />\r\n                        </div>\r\n                      </div>\r\n                    </div>\r\n                  </div>\r\n                  <div type=\"tab\" name=\"tabOrder\" selectedindex=\"1\" backcolor=\"-200000000163\" bordercolor=\"-200000000193\">\r\n                    <div type=\"tabpage\" name=\"pageNoTrade\" text=\"NoTrade\" backcolor=\"none\" bordercolor=\"none\">\r\n                      <div type=\"splitlayout\" name=\"divNoTrade\" dock=\"fill\" layoutstyle=\"righttoleft\" size=\"400,400\" splitterposition=\"320,0,320,400\" backcolor=\"none\" bordercolor=\"none\">\r\n                        <div name=\"divCancelOrder\" location=\"285,0\" size=\"78,338\" backcolor=\"none\" bordercolor=\"none\">\r\n                          <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnCancelOrder\" checked=\"true\" size=\"60,60\" text=\"Cancel\" location=\"7,12\" />\r\n                          <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnCancelAllOrders\" location=\"7,75\" size=\"60,60\" text=\"CancelAll\" />\r\n                        </div>\r\n                        <table name=\"gridNoTrade\" location=\"122,50\" size=\"209,248\" backcolor=\"none\" bordercolor=\"none\">\r\n                          <tr>\r\n                            <th name=\"colU11\" columntype=\"no\" horizontalalign=\"far\" text=\"colU11\" allowsort=\"false\" width=\"80\" />\r\n                            <th name=\"colU1\" columntype=\"text\" text=\"colU1\" width=\"80\" />\r\n                            <th name=\"colU2\" columntype=\"text\" text=\"colU2\" width=\"80\" />\r\n                            <th name=\"colU3\" columntype=\"text\" horizontalalign=\"center\" text=\"colU3\" width=\"60\" />\r\n                            <th name=\"colU4\" columntype=\"text\" horizontalalign=\"center\" text=\"colU4\" width=\"60\" />\r\n                            <th name=\"colU5\" columntype=\"int\" horizontalalign=\"far\" text=\"colU5\" width=\"80\" />\r\n                            <th name=\"colU6\" columntype=\"int\" horizontalalign=\"far\" text=\"colU6\" width=\"80\" />\r\n                            <th name=\"colU7\" columntype=\"double\" horizontalalign=\"far\" text=\"colU7\" width=\"80\" />\r\n                            <th name=\"colU8\" columntype=\"text\" horizontalalign=\"center\" text=\"colU8\" width=\"80\" />\r\n                            <th name=\"colU9\" columntype=\"double\" horizontalalign=\"far\" text=\"colU9\" width=\"80\" />\r\n                            <th name=\"colU10\" columntype=\"double\" horizontalalign=\"far\" text=\"colU10\" width=\"80\" />\r\n                            <th name=\"colU12\" columntype=\"text\" text=\"colU12\" width=\"80\" />\r\n                            <th name=\"colU13\" columntype=\"text\" horizontalalign=\"center\" text=\"colU13\" width=\"60\" />\r\n                            <th name=\"colU14\" columntype=\"int\" horizontalalign=\"far\" text=\"colU14\" width=\"60\" />\r\n                            <th name=\"colU15\" columntype=\"text\" text=\"colU15\" width=\"100\" />\r\n                            <th name=\"colU16\" columntype=\"text\" text=\"colU16\" width=\"100\" />\r\n                            <th name=\"colU17\" columntype=\"text\" text=\"colU17\" width=\"80\" />\r\n                            <th name=\"colU18\" columntype=\"text\" horizontalalign=\"center\" text=\"colU18\" width=\"100\" />\r\n                            <th name=\"colU19\" columntype=\"double\" text=\"colU19\" width=\"80\" />\r\n                            <th name=\"colU20\" columntype=\"text\" horizontalalign=\"center\" text=\"colU20\" width=\"80\" />\r\n                            <th name=\"colU21\" columntype=\"text\" text=\"colU21\" width=\"80\" />\r\n                            <th name=\"colU22\" columntype=\"text\" text=\"colU22\" width=\"80\" />\r\n                            <th name=\"colU23\" columntype=\"text\" text=\"colU23\" width=\"200\" />\r\n                            <th name=\"colU24\" columntype=\"text\" text=\"colU24\" width=\"80\" />\r\n                            <th name=\"colU25\" columntype=\"text\" text=\"colU25\" width=\"100\" />\r\n                            <th name=\"colU26\" columntype=\"text\" text=\"colU26\" width=\"80\" />\r\n                          </tr>\r\n                        </table>\r\n                      </div>\r\n                    </div>\r\n                    <div type=\"tabpage\" name=\"pageAllOrders\" text=\"AllOrder\" backcolor=\"none\" bordercolor=\"none\">\r\n                      <div type=\"splitlayout\" name=\"divOrder\" dock=\"fill\" layoutstyle=\"bottomtotop\" size=\"400,400\" splitterposition=\"0,370,400,370\" backcolor=\"none\" bordercolor=\"none\">\r\n                        <div name=\"divDealRecordType\" backcolor=\"none\" bordercolor=\"none\">\r\n                          <input type=\"radio\" name=\"rdAllOrders\" groupname=\"allOrders\" checked=\"true\" location=\"0,6\" text=\"AllOrders\" size=\"100,20\" />\r\n                          <input type=\"radio\" name=\"rdOrder\" groupname=\"allOrders\" location=\"100,6\" text=\"Order\" size=\"100,20\" />\r\n                          <input type=\"radio\" name=\"rdDeal\" groupname=\"allOrders\" location=\"200,6\" text=\"Deal\" size=\"100,20\" />\r\n                          <input type=\"radio\" name=\"rdCancel\" groupname=\"allOrders\" location=\"300,6\" text=\"Cancel\" size=\"120,20\" />\r\n                          <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnCancelOrder2\" location=\"450,2\" size=\"100,26\" text=\"Cancel\" />\r\n                          <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnCancelAllOrder2\" location=\"570,2\" size=\"100,26\" text=\"CancelAll\" />\r\n                        </div>\r\n                        <table name=\"gridOrder\" dock=\"Fill\" size=\"569,330\" backcolor=\"none\" bordercolor=\"none\">\r\n                          <tr>\r\n                            <th name=\"colA17\" columntype=\"no\" horizontalalign=\"far\" text=\"colA17\" allowsort=\"false\" width=\"80\" />\r\n                            <th name=\"colA1\" columntype=\"text\" text=\"colA1\" width=\"80\" />\r\n                            <th name=\"colA2\" columntype=\"text\" text=\"colA2\" width=\"80\" />\r\n                            <th name=\"colA3\" columntype=\"text\" horizontalalign=\"center\" text=\"colA3\" width=\"60\" />\r\n                            <th name=\"colA4\" columntype=\"text\" horizontalalign=\"center\" text=\"colA4\" width=\"60\" />\r\n                            <th name=\"colA5\" columntype=\"text\" horizontalalign=\"center\" text=\"colA5\" width=\"140\" />\r\n                            <th name=\"colA6\" columntype=\"double\" horizontalalign=\"far\" text=\"colA6\" width=\"80\" />\r\n                            <th name=\"colA7\" columntype=\"int\" horizontalalign=\"far\" text=\"colA7\" width=\"80\" />\r\n                            <th name=\"colA8\" columntype=\"int\" horizontalalign=\"far\" text=\"colA8\" width=\"80\" />\r\n                            <th name=\"colA9\" columntype=\"int\" horizontalalign=\"far\" text=\"colA9\" width=\"80\" />\r\n                            <th name=\"colA10\" columntype=\"text\" horizontalalign=\"center\" text=\"colA10\" width=\"60\" />\r\n                            <th name=\"colA11\" columntype=\"text\" horizontalalign=\"center\" text=\"colA11\" width=\"80\" />\r\n                            <th name=\"colA12\" columntype=\"double\" horizontalalign=\"far\" text=\"colA12\" width=\"80\" />\r\n                            <th name=\"colA13\" columntype=\"double\" horizontalalign=\"far\" text=\"colA13\" width=\"80\" />\r\n                            <th name=\"colA14\" columntype=\"double\" horizontalalign=\"far\" text=\"colA14\" width=\"80\" />\r\n                            <th name=\"colA15\" columntype=\"text\" horizontalalign=\"center\" text=\"colA15\" width=\"60\" />\r\n                            <th name=\"colA16\" columntype=\"text\" text=\"colA16\" width=\"80\" />\r\n                            <th name=\"colA18\" columntype=\"text\" horizontalalign=\"center\" text=\"colA18\" width=\"100\" />\r\n                            <th name=\"colA19\" columntype=\"text\" text=\"colA19\" width=\"200\" />\r\n                            <th name=\"colA20\" columntype=\"text\" horizontalalign=\"center\" text=\"colA20\" width=\"60\" />\r\n                            <th name=\"colA21\" columntype=\"text\" horizontalalign=\"center\" text=\"colA21\" width=\"80\" />\r\n                            <th name=\"colA22\" columntype=\"text\" horizontalalign=\"center\" text=\"colA22\" width=\"80\" />\r\n                            <th name=\"colA23\" columntype=\"text\" text=\"colA23\" width=\"80\" />\r\n                            <th name=\"colA24\" columntype=\"text\" text=\"colA24\" width=\"80\" />\r\n                            <th name=\"colA25\" columntype=\"text\" text=\"colA25\" width=\"60\" />\r\n                          </tr>\r\n                        </table>\r\n                      </div>\r\n                    </div>\r\n                    <div type=\"tabpage\" name=\"pageParkedOrder\" text=\"ParkedOrder\" backcolor=\"none\" bordercolor=\"none\">\r\n                      <div type=\"splitlayout\" name=\"divParkedOrder\" dock=\"fill\" layoutstyle=\"bottomtotop\" size=\"400,400\" splitterposition=\"0,350,400,350\" backcolor=\"none\" bordercolor=\"none\">\r\n                        <div name=\"divDealRecordType\" location=\"-1,200\" backcolor=\"none\" bordercolor=\"none\">\r\n                          <input type=\"radio\" name=\"rdAllCondition\" groupname=\"condition\" checked=\"true\" location=\"0,4\" text=\"AllCondition\" size=\"100,20\" />\r\n                          <input type=\"radio\" name=\"rdPreCondition\" groupname=\"condition\" location=\"80,4\" text=\"PreCondition\" size=\"100,20\" />\r\n                          <input type=\"radio\" name=\"rdCondition\" groupname=\"condition\" location=\"160,4\" text=\"Condition\" size=\"100,20\" />\r\n                          <input type=\"radio\" name=\"rdSend\" groupname=\"condition\" location=\"240,4\" text=\"Send\" size=\"100,20\" />\r\n                          <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnDeleteCondition\" location=\"320,2\" size=\"100,26\" text=\"DeleteCondition\" />\r\n                          <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnSendCondition\" location=\"424,2\" size=\"100,26\" text=\"SendCondition\" />\r\n                          <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnClearCondition\" location=\"528,2\" size=\"100,26\" text=\"ClearCondition\" />\r\n                          <label name=\"lblConditionTip\" textcolor=\"rgba(255,0,0,255)\" location=\"10,30\" size=\"500,20\" text=\"ConditionTip\" />\r\n                        </div>\r\n                        <table name=\"gridParkedOrder\" backcolor=\"none\" bordercolor=\"none\">\r\n                          <tr>\r\n                            <th name=\"colI1\" columntype=\"text\" text=\"colI1\" width=\"100\" />\r\n                            <th name=\"colI2\" columntype=\"text\" text=\"colI2\" width=\"80\" />\r\n                            <th name=\"colI3\" columntype=\"text\" text=\"colI3\" width=\"250\" />\r\n                            <th name=\"colI4\" columntype=\"text\" text=\"colI4\" width=\"60\" />\r\n                            <th name=\"colI5\" columntype=\"text\" horizontalalign=\"center\" text=\"colI5\" width=\"80\" />\r\n                            <th name=\"colI6\" columntype=\"text\" horizontalalign=\"center\" text=\"colI6\" width=\"80\" />\r\n                            <th name=\"colI7\" columntype=\"double\" horizontalalign=\"far\" text=\"colI7\" width=\"80\" />\r\n                            <th name=\"colI8\" columntype=\"int\" horizontalalign=\"far\" text=\"colI8\" width=\"80\" />\r\n                            <th name=\"colI9\" columntype=\"text\" horizontalalign=\"center\" text=\"colI9\" width=\"80\" />\r\n                            <th name=\"colI10\" columntype=\"text\" text=\"colI10\" width=\"60\" />\r\n                            <th name=\"colI11\" columntype=\"text\" horizontalalign=\"center\" text=\"colI11\" width=\"80\" />\r\n                            <th name=\"colI12\" columntype=\"text\" horizontalalign=\"center\" text=\"colI12\" width=\"120\" />\r\n                          </tr>\r\n                        </table>\r\n                      </div>\r\n                    </div>\r\n                    <div type=\"tabpage\" name=\"pageTradeRecord\" text=\"TradeRecord\" backcolor=\"none\" bordercolor=\"none\">\r\n                      <div type=\"splitlayout\" name=\"divTradeRecord\" dock=\"fill\" layoutstyle=\"bottomtotop\" size=\"400,400\" splitterposition=\"0,370,400,370\" backcolor=\"none\" bordercolor=\"none\">\r\n                        <div name=\"divTradeRecordType\" backcolor=\"none\" bordercolor=\"none\">\r\n                          <input type=\"radio\" name=\"rdDetail\" groupname=\"tradeRecordType\" checked=\"true\" location=\"0,5\" text=\"Detail\" size=\"100,20\" />\r\n                          <input type=\"radio\" name=\"rdSummary\" groupname=\"tradeRecordType\" location=\"100,5\" text=\"Summary\" size=\"100,20\" />\r\n                        </div>\r\n                        <div name=\"divTradeRecordInner\" backcolor=\"none\" bordercolor=\"none\">\r\n                          <table name=\"gridTradeRecord\" dock=\"fill\" backcolor=\"none\" bordercolor=\"none\">\r\n                            <tr>\r\n                              <th name=\"colR1\" columntype=\"text\" text=\"colR1\" width=\"80\" />\r\n                              <th name=\"colR2\" columntype=\"text\" text=\"colR2\" width=\"80\" />\r\n                              <th name=\"colR3\" columntype=\"text\" horizontalalign=\"center\" text=\"colR3\" width=\"60\" />\r\n                              <th name=\"colR4\" columntype=\"text\" horizontalalign=\"center\" text=\"colR4\" width=\"60\" />\r\n                              <th name=\"colR5\" columntype=\"double\" horizontalalign=\"far\" text=\"colR5\" width=\"80\" />\r\n                              <th name=\"colR6\" columntype=\"int\" horizontalalign=\"far\" text=\"colR6\" width=\"80\" />\r\n                              <th name=\"colR7\" columntype=\"text\" horizontalalign=\"center\" text=\"colR7\" width=\"80\" />\r\n                              <th name=\"colR8\" columntype=\"text\" horizontalalign=\"center\" text=\"colR8\" width=\"80\" />\r\n                              <th name=\"colR9\" columntype=\"text\" horizontalalign=\"center\" text=\"colR9\" width=\"80\" />\r\n                              <th name=\"colR10\" columntype=\"text\" horizontalalign=\"center\" text=\"colR10\" width=\"60\" />\r\n                              <th name=\"colR11\" columntype=\"text\" text=\"colR11\" width=\"80\" />\r\n                              <th name=\"colR12\" columntype=\"double\" horizontalalign=\"far\" text=\"colR12\" width=\"80\" />\r\n                            </tr>\r\n                          </table>\r\n                          <table name=\"gridTradeStatistics\" dock=\"fill\" visible=\"false\" backcolor=\"none\" bordercolor=\"none\">\r\n                            <tr>\r\n                              <th name=\"colS1\" columntype=\"text\" text=\"colS1\" width=\"80\" />\r\n                              <th name=\"colS2\" columntype=\"text\" text=\"colS2\" width=\"80\" />\r\n                              <th name=\"colS3\" columntype=\"text\" horizontalalign=\"center\" text=\"colS3\" width=\"80\" />\r\n                              <th name=\"colS4\" columntype=\"text\" horizontalalign=\"center\" text=\"colS4\" width=\"80\" />\r\n                              <th name=\"colS5\" columntype=\"double\" horizontalalign=\"far\" text=\"colS5\" width=\"100\" />\r\n                              <th name=\"colS6\" columntype=\"int\" horizontalalign=\"far\" text=\"colS6\" width=\"100\" />\r\n                              <th name=\"colS7\" columntype=\"double\" horizontalalign=\"far\" text=\"colS7\" width=\"100\" />\r\n                              <th name=\"colS8\" columntype=\"text\" horizontalalign=\"center\" text=\"colS8\" width=\"60\" />\r\n                            </tr>\r\n                          </table>\r\n                        </div>\r\n                      </div>\r\n                    </div>\r\n                  </div>\r\n                </div>\r\n              </div>\r\n            </div>\r\n            <div bordercolor=\"none\" backcolor=\"none\" padding=\"5,5,5,5\">\r\n              <div type=\"tab\" name=\"tabQuote\" selectedindex=\"0\" size=\"400,400\" backcolor=\"-200000000163\" dock=\"fill\" bordercolor=\"-200000000193\">\r\n                <div type=\"tabpage\" name=\"pagePageQuote\" text=\"PageQuote\" bordercolor=\"none\" backcolor=\"none\">\r\n                  <table name=\"gridLatestData\" dock=\"fill\" location=\"0,0\" size=\"914,160\" bordercolor=\"none\" backcolor=\"none\">\r\n                    <tr>\r\n                      <th name=\"colQ1\" columntype=\"text\" text=\"colQ1\" width=\"80\" />\r\n                      <th name=\"colQ2\" columntype=\"text\" text=\"colQ2\" width=\"100\" />\r\n                      <th name=\"colQ3\" columntype=\"double\" horizontalalign=\"far\" text=\"colQ3\" width=\"60\" />\r\n                      <th name=\"colQ4\" columntype=\"double\" horizontalalign=\"far\" text=\"colQ4\" width=\"60\" />\r\n                      <th name=\"colQ5\" columntype=\"double\" horizontalalign=\"far\" text=\"colQ5\" width=\"60\" location=\"300,0\" size=\"60,20\" />\r\n                      <th name=\"colQ6\" columntype=\"int\" horizontalalign=\"far\" text=\"colQ6\" width=\"60\" location=\"360,0\" size=\"60,20\" />\r\n                      <th name=\"colQ7\" columntype=\"double\" horizontalalign=\"far\" text=\"colQ7\" width=\"60\" />\r\n                      <th name=\"colQ8\" columntype=\"int\" horizontalalign=\"far\" text=\"colQ8\" width=\"60\" />\r\n                      <th name=\"colQ9\" columntype=\"int\" horizontalalign=\"far\" text=\"colQ9\" width=\"60\" />\r\n                      <th name=\"colQ10\" columntype=\"int\" horizontalalign=\"far\" text=\"colQ10\" width=\"60\" />\r\n                      <th name=\"colQ11\" columntype=\"double\" horizontalalign=\"far\" text=\"colQ11\" width=\"60\" />\r\n                      <th name=\"colQ12\" columntype=\"double\" horizontalalign=\"far\" text=\"colQ12\" width=\"60\" />\r\n                      <th name=\"colQ13\" columntype=\"double\" horizontalalign=\"far\" text=\"colQ13\" width=\"60\" />\r\n                      <th name=\"colQ14\" columntype=\"double\" horizontalalign=\"far\" text=\"colQ14\" width=\"60\" />\r\n                      <th name=\"colQ15\" columntype=\"double\" horizontalalign=\"far\" text=\"colQ15\" width=\"60\" />\r\n                      <th name=\"colQ16\" columntype=\"double\" horizontalalign=\"far\" text=\"colQ16\" width=\"60\" />\r\n                      <th name=\"colQ17\" columntype=\"int\" horizontalalign=\"far\" text=\"colQ17\" width=\"60\" />\r\n                      <th name=\"colQ18\" columntype=\"percent\" horizontalalign=\"far\" text=\"colQ18\" width=\"60\" />\r\n                      <th name=\"colQ19\" columntype=\"double\" horizontalalign=\"far\" text=\"colQ19\" width=\"60\" />\r\n                      <th name=\"colQ20\" columntype=\"thousands\" horizontalalign=\"far\" text=\"colQ20\" width=\"100\" />\r\n                      <th name=\"colQ21\" columntype=\"text\" text=\"colQ21\" width=\"60\" />\r\n                      <th name=\"colQ22\" columntype=\"text\" horizontalalign=\"center\" text=\"colQ22\" width=\"100\" />\r\n                      <th name=\"colQ23\" columntype=\"double\" text=\"colQ23\" width=\"60\" />\r\n                      <th name=\"colQ24\" columntype=\"double\" text=\"colQ24\" width=\"60\" />\r\n                      <th name=\"colQ25\" columntype=\"double\" text=\"colQ25\" width=\"60\" />\r\n                      <th name=\"colQ26\" columntype=\"double\" text=\"colQ26\" width=\"80\" />\r\n                      <th name=\"colQ27\" columntype=\"int\" text=\"colQ27\" width=\"80\" />\r\n                      <th name=\"colQ28\" columntype=\"double\" text=\"colQ28\" width=\"80\" />\r\n                      <th name=\"colQ29\" columntype=\"int\" text=\"colQ29\" width=\"80\" />\r\n                      <th name=\"colQ30\" columntype=\"double\" text=\"colQ30\" width=\"80\" />\r\n                      <th name=\"colQ31\" columntype=\"int\" text=\"colQ31\" width=\"80\" />\r\n                      <th name=\"colQ32\" columntype=\"int\" text=\"colQ32\" width=\"80\" />\r\n                    </tr>\r\n                  </table>\r\n                </div>\r\n                <div type=\"tabpage\" name=\"pageContracts\" text=\"Contracts\" bordercolor=\"none\" backcolor=\"none\">\r\n                  <table name=\"gridContracts\" dock=\"fill\" bordercolor=\"none\" backcolor=\"none\">\r\n                    <tr>\r\n                      <th name=\"colC1\" columntype=\"text\" text=\"colC1\" width=\"80\" />\r\n                      <th name=\"colC2\" columntype=\"text\" text=\"colC2\" width=\"60\" />\r\n                      <th name=\"colC3\" columntype=\"text\" text=\"colC3\" width=\"100\" />\r\n                      <th name=\"colC4\" columntype=\"text\" text=\"colC4\" width=\"60\" />\r\n                      <th name=\"colC5\" columntype=\"int\" horizontalalign=\"far\" text=\"colC5\" width=\"100\" />\r\n                      <th name=\"colC6\" columntype=\"double\" horizontalalign=\"far\" text=\"colC6\" width=\"100\" />\r\n                      <th name=\"colC7\" columntype=\"text\" horizontalalign=\"center\" text=\"colC7\" width=\"100\" />\r\n                      <th name=\"colC8\" columntype=\"text\" horizontalalign=\"center\" text=\"colC8\" width=\"100\" />\r\n                      <th name=\"colC9\" columntype=\"percent\" horizontalalign=\"far\" text=\"colC9\" width=\"100\" />\r\n                      <th name=\"colC10\" columntype=\"percent\" horizontalalign=\"far\" text=\"colC10\" width=\"100\" />\r\n                      <th name=\"colC11\" columntype=\"double\" horizontalalign=\"far\" text=\"colC11\" width=\"100\" />\r\n                      <th name=\"colC12\" columntype=\"double\" horizontalalign=\"far\" text=\"colC12\" width=\"100\" />\r\n                      <th name=\"colC13\" columntype=\"double\" horizontalalign=\"far\" text=\"colC13\" width=\"100\" />\r\n                      <th name=\"colC14\" columntype=\"percent\" horizontalalign=\"far\" text=\"colC14\" width=\"100\" />\r\n                      <th name=\"colC15\" columntype=\"percent\" horizontalalign=\"far\" text=\"colC15\" width=\"100\" />\r\n                      <th name=\"colC16\" columntype=\"percent\" horizontalalign=\"far\" text=\"colC16\" width=\"100\" />\r\n                      <th name=\"colC17\" columntype=\"int\" horizontalalign=\"far\" text=\"colC17\" width=\"100\" />\r\n                      <th name=\"colC18\" columntype=\"int\" horizontalalign=\"far\" text=\"colC18\" width=\"100\" />\r\n                    </tr>\r\n                  </table>\r\n                </div>\r\n              </div>\r\n            </div>\r\n          </div>\r\n          <div bordercolor=\"none\" padding=\"5,5,5,5\" backcolor=\"-200000000163\">\r\n            <div type=\"tab\" name=\"tabInvestorPosition\" selectedindex=\"0\" dock=\"fill\" bordercolor=\"-200000000193\" backcolor=\"none\">\r\n              <div type=\"tabpage\" name=\"pagePageInvestorPosition\" text=\"InvestorPosition\" bordercolor=\"none\" backcolor=\"none\">\r\n                <div type=\"splitlayout\" name=\"divInvestorPosition\" dock=\"fill\" layoutstyle=\"bottomtotop\" size=\"400,400\" splitterposition=\"0,370,400,370\" bordercolor=\"none\" backcolor=\"none\">\r\n                  <div name=\"divInvestorPositionBottom\" bordercolor=\"none\" backcolor=\"none\">\r\n                    <input type=\"radio\" name=\"cbInvestorPosition\" checked=\"true\" location=\"5,5\" groupname=\"InvestorPosition\" size=\"80,20\" text=\"InvestorPosition\" />\r\n                    <input type=\"radio\" name=\"cbInvestorPositionDetail\" groupname=\"InvestorPosition\" location=\"80,5\" size=\"80,20\" text=\"InvestorPositionDetail\" />\r\n                    <input type=\"radio\" name=\"cbCompPosition\" groupname=\"InvestorPosition\" location=\"180,3\" size=\"80,23\" text=\"CompPosition\" visible=\"false\" />\r\n                    <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnOpenInterestIP\" location=\"300,3\" size=\"80,23\" text=\"OpenInterest\" height=\"24\" />\r\n                    <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnMarketPositionIP\" location=\"390,3\" size=\"80,23\" text=\"MarketPosition\" height=\"24\" />\r\n                    <input type=\"custom\" cid=\"ribbonbutton2\" name=\"btnMarketBackhandIP\" location=\"480,3\" size=\"80,23\" text=\"MarketBackhand\" height=\"24\" />\r\n                  </div>\r\n                  <div name=\"divInvestorPositionTop\" bordercolor=\"none\" backcolor=\"none\">\r\n                    <table name=\"gridInvestorPosition\" dock=\"fill\" bordercolor=\"none\" backcolor=\"none\">\r\n                      <tr>\r\n                        <th name=\"colP1\" columntype=\"text\" text=\"colP1\" width=\"80\" />\r\n                        <th name=\"colP2\" columntype=\"text\" horizontalalign=\"center\" text=\"colP2\" width=\"60\" />\r\n                        <th name=\"colP3\" columntype=\"int\" horizontalalign=\"far\" text=\"colP3\" width=\"60\" />\r\n                        <th name=\"colP4\" columntype=\"int\" horizontalalign=\"far\" text=\"colP4\" width=\"60\" />\r\n                        <th name=\"colP5\" columntype=\"int\" horizontalalign=\"far\" text=\"colP5\" width=\"60\" />\r\n                        <th name=\"colP6\" columntype=\"int\" horizontalalign=\"far\" text=\"colP6\" width=\"60\" />\r\n                        <th name=\"colP7\" columntype=\"double\" horizontalalign=\"far\" text=\"colP7\" width=\"80\" />\r\n                        <th name=\"colP8\" columntype=\"thousands\" horizontalalign=\"far\" text=\"colP8\" width=\"150\" />\r\n                        <th name=\"colP9\" columntype=\"thousands\" horizontalalign=\"far\" text=\"colP9\" width=\"100\" />\r\n                        <th name=\"colP10\" columntype=\"text\" horizontalalign=\"center\" text=\"colP10\" width=\"60\" />\r\n                        <th name=\"col111\" columntype=\"text\" text=\"colP11\" width=\"80\" />\r\n                        <th name=\"colP12\" columntype=\"int\" horizontalalign=\"far\" text=\"colP12\" width=\"60\" />\r\n                        <th name=\"colP13\" columntype=\"int\" horizontalalign=\"far\" text=\"colP13\" width=\"60\" />\r\n                        <th name=\"colP14\" columntype=\"int\" horizontalalign=\"far\" text=\"colP14\" width=\"60\" />\r\n                        <th name=\"colP15\" columntype=\"int\" horizontalalign=\"far\" text=\"colP15\" width=\"60\" />\r\n                        <th name=\"colP16\" columntype=\"int\" horizontalalign=\"far\" text=\"colP16\" width=\"100\" />\r\n                        <th name=\"colP17\" columntype=\"int\" horizontalalign=\"far\" text=\"colP17\" width=\"100\" />\r\n                        <th name=\"colP18\" columntype=\"int\" horizontalalign=\"far\" text=\"colP18\" width=\"100\" />\r\n                        <th name=\"colP19\" columntype=\"int\" horizontalalign=\"far\" text=\"colP19\" width=\"100\" />\r\n                        <th name=\"colP20\" columntype=\"int\" horizontalalign=\"far\" text=\"colP20\" width=\"100\" />\r\n                        <th name=\"colP21\" columntype=\"int\" horizontalalign=\"far\" text=\"colP21\" width=\"80\" />\r\n                        <th name=\"col122\" columntype=\"int\" horizontalalign=\"far\" text=\"colP22\" width=\"80\" />\r\n                        <th name=\"colP23\" columntype=\"double\" horizontalalign=\"far\" text=\"colP23\" width=\"100\" />\r\n                        <th name=\"colP24\" columntype=\"double\" horizontalalign=\"far\" text=\"colP24\" width=\"100\" />\r\n                        <th name=\"colP25\" columntype=\"double\" horizontalalign=\"far\" text=\"colP25\" width=\"100\" />\r\n                        <th name=\"colP26\" columntype=\"thousands\" horizontalalign=\"far\" text=\"colP26\" width=\"100\" />\r\n                        <th name=\"colP27\" columntype=\"thousands\" horizontalalign=\"far\" text=\"colP27\" width=\"80\" />\r\n                        <th name=\"colP28\" columntype=\"int\" horizontalalign=\"far\" text=\"colP28\" width=\"80\" />\r\n                        <th name=\"colP29\" columntype=\"int\" horizontalalign=\"far\" text=\"colP29\" width=\"80\" />\r\n                        <th name=\"colP30\" columntype=\"double\" horizontalalign=\"far\" text=\"colP30\" width=\"80\" />\r\n                        <th name=\"colP31\" columntype=\"double\" horizontalalign=\"far\" text=\"colP31\" width=\"80\" />\r\n                        <th name=\"colP32\" columntype=\"text\" text=\"colP32\" width=\"100\" />\r\n                        <th name=\"colP33\" columntype=\"text\" text=\"colP33\" width=\"100\" />\r\n                        <th name=\"colP34\" columntype=\"text\" text=\"colP34\" width=\"100\" />\r\n                      </tr>\r\n                    </table>\r\n                    <table name=\"gridInvestorPositionDetail\" dock=\"fill\" visible=\"false\" bordercolor=\"none\" backcolor=\"none\">\r\n                      <tr>\r\n                        <th name=\"colT1\" columntype=\"text\" text=\"colT1\" width=\"80\" />\r\n                        <th name=\"colT2\" columntype=\"text\" text=\"colT2\" width=\"80\" />\r\n                        <th name=\"colT3\" columntype=\"text\" horizontalalign=\"center\" text=\"colT3\" width=\"60\" />\r\n                        <th name=\"colT4\" columntype=\"int\" horizontalalign=\"far\" text=\"colT4\" width=\"60\" />\r\n                        <th name=\"colT5\" columntype=\"double\" horizontalalign=\"far\" text=\"colT5\" width=\"80\" />\r\n                        <th name=\"colT6\" columntype=\"thousands\" horizontalalign=\"far\" text=\"colT6\" width=\"100\" />\r\n                        <th name=\"colT7\" columntype=\"text\" text=\"colT7\" width=\"80\" />\r\n                        <th name=\"colT8\" columntype=\"text\" horizontalalign=\"center\" text=\"colT8\" width=\"60\" />\r\n                        <th name=\"colT9\" columntype=\"text\" horizontalalign=\"center\" text=\"colT9\" width=\"100\" />\r\n                        <th name=\"colT10\" columntype=\"thousands\" horizontalalign=\"far\" text=\"colT10\" width=\"100\" />\r\n                        <th name=\"colT11\" columntype=\"thousands\" horizontalalign=\"far\" text=\"colT11\" width=\"100\" />\r\n                        <th name=\"colT12\" columntype=\"text\" text=\"colT12\" width=\"80\" />\r\n                        <th name=\"colT13\" columntype=\"text\" text=\"colT13\" width=\"100\" />\r\n                        <th name=\"colT14\" columntype=\"double\" horizontalalign=\"far\" text=\"colT14\" width=\"80\" />\r\n                        <th name=\"colT15\" columntype=\"int\" horizontalalign=\"far\" text=\"colT15\" width=\"80\" />\r\n                        <th name=\"colT16\" columntype=\"thousands\" horizontalalign=\"far\" text=\"colT16\" width=\"100\" />\r\n                        <th name=\"colT17\" columntype=\"double\" horizontalalign=\"far\" text=\"colT17\" width=\"80\" />\r\n                        <th name=\"colT18\" columntype=\"int\" horizontalalign=\"far\" text=\"colT18\" width=\"100\" />\r\n                      </tr>\r\n                    </table>\r\n                    <table name=\"gridInvestorCombinePositionDetail\" dock=\"fill\" visible=\"false\" bordercolor=\"none\" backcolor=\"none\">\r\n                      <tr>\r\n                        <th name=\"colM1\" columntype=\"text\" text=\"colM1\" width=\"120\" />\r\n                        <th name=\"colM2\" columntype=\"text\" horizontalalign=\"center\" text=\"colM2\" width=\"60\" />\r\n                        <th name=\"colM3\" columntype=\"int\" horizontalalign=\"far\" text=\"colM3\" width=\"60\" />\r\n                        <th name=\"colM4\" columntype=\"double\" horizontalalign=\"far\" text=\"colM4\" width=\"100\" />\r\n                        <th name=\"colM5\" columntype=\"text\" horizontalalign=\"center\" text=\"colM5\" width=\"60\" />\r\n                      </tr>\r\n                    </table>\r\n                  </div>\r\n                </div>\r\n              </div>\r\n            </div>\r\n          </div>\r\n        </div>\r\n      </div>\r\n    </div>\r\n  </body>\r\n</html>\r\n"

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

root  = ET.fromstring(m_xml)
for child in root:
	if(child.tag == "{facecat}body"):
		readXmlNode(m_paint, child, None)
showDemoData = TRUE
if(showDemoData):
	gridLatestData = findViewByName("gridLatestData", m_paint.m_views)
	gridNoTrade = findViewByName("gridNoTrade", m_paint.m_views)
	gridInvestorPosition = findViewByName("gridInvestorPosition", m_paint.m_views)
	chart = findViewByName("chart", m_paint.m_views)
	chart.m_candleDivPercent = 0.7
	chart.m_volDivPercent = 0.3
	chart.m_indDivPercent = 0
	try:
		s = requests.Session()
		s.mount('http://', HTTPAdapter(max_retries=3))
		response = s.get('http://quotes.money.163.com/service/chddata.html?code=0000001', timeout=5)
		text = response.text
		strs = text.split("\r\n")
		strLen = len(strs)
		pos = strLen - 2
		for i in range(0, strLen - 3):
			subStrs = strs[pos].split(",")
			if(len(subStrs) > 8):
				data = SecurityData()
				data.m_date = i
				data.m_close = float(subStrs[3])
				data.m_high = float(subStrs[4])
				data.m_low = float(subStrs[5])
				data.m_open = float(subStrs[6])
				lastClose = 0
				if(subStrs[7] != "None"):
					lastClose = float(subStrs[7])
				data.m_volume = float(subStrs[11])
				chart.m_data.append(data)
				if(gridLatestData != None):
					row = FCGridRow()
					gridLatestData.m_rows.append(row)
					for c in range(0, len(gridLatestData.m_columns)):
						cell = FCGridCell()
						if(c < len(subStrs)):
							cell.m_value = subStrs[c]
						row.m_cells.append(cell)
						if(cell.m_value != None):
							if(c >= 3 and c <= 6):
								if(float(cell.m_value) >= lastClose):
									cell.m_textColor = "rgb(219,68,83)"
								else:
									cell.m_textColor = "rgb(15,193,118)"
							elif(c == 0):
								cell.m_textColor = "rgb(255,255,0)"
							elif(c == 1):
								cell.m_textColor = "rgb(0,255,255)"
				if(gridInvestorPosition != None):
					row = FCGridRow()
					gridInvestorPosition.m_rows.append(row)
					for c in range(0, len(gridInvestorPosition.m_columns)):
						cell = FCGridCell()
						if(c < len(subStrs)):
							cell.m_value = subStrs[c]
						row.m_cells.append(cell)
				if(gridNoTrade != None):
					row = FCGridRow()
					gridNoTrade.m_rows.append(row)
					for c in range(0, len(gridNoTrade.m_columns)):
						cell = FCGridCell()
						if(c < len(subStrs)):
							cell.m_value = subStrs[c]
						row.m_cells.append(cell)
			pos = pos - 1
	except requests.exceptions.RequestException as e:
		print(e)
	calcChartIndicator(chart)
rect = win32gui.GetClientRect(hwnd)
m_paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
for view in m_paint.m_views:
	if view.m_dock == "fill":
		view.m_size = FCSize(m_paint.m_size.cx, m_paint.m_size.cy)
updateView(m_paint.m_views)
win32gui.ShowWindow(hwnd,SW_SHOWNORMAL)
win32gui.UpdateWindow(hwnd)
win32gui.PumpMessages()