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
import websocket
#pip install websocket-client 
import json
import timer
try:
    import thread
except ImportError:
    import _thread as thread

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
		if(view.m_name == "price"):
			view.m_columns[0].m_width = view.m_size.cx
		subViews = view.m_views
		if(len(subViews) > 0):
			updateView(subViews)

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

#绘制列 
#grid:表格 
#column:列
#paint:绘图对象 
#left:左侧坐标 
#top:上方坐标 
#right:右侧坐标 
#bottom:下方坐标
def onPaintGridColumn(grid, column, paint, left, top, right, bottom):
	width = right - left
	height = bottom - top
	font2 = "14px Arial"
	tSize = paint.textSize("市场 / 成交额", font2)
	if (grid.m_paint.m_defaultUIStyle == "dark"):
		paint.fillRect("rgb(0,0,0)", left, top, right, bottom)
		paint.drawText("市场 / 成交额", "rgb(200,200,200)", font2, left + 5, top + height / 2 - tSize.cy / 2)
		paint.drawText("最新价", "rgb(200,200,200)", font2, left + width * 0.4 + 5, top + height / 2 - tSize.cy / 2)
		paint.drawText("24h涨跌", "rgb(200,200,200)", font2, left + width * 0.7 + 5, top + height / 2 - tSize.cy / 2)
	elif (grid.m_paint.m_defaultUIStyle == "light"):
		paint.fillRect("rgb(255,255,255)", left, top, right, bottom)
		paint.drawText("市场 / 成交额", "rgb(50,50,50)", font2, left + 5, top + height / 2 - tSize.cy / 2)
		paint.drawText("最新价", "rgb(50,50,50)", font2, left + width * 0.4 + 5, top + height / 2 - tSize.cy / 2)
		paint.drawText("24h涨跌", "rgb(50,50,50)", font2, left + width * 0.7 + 5, top + height / 2 - tSize.cy / 2)

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
def onPaintGridCell(grid, row, column, cell, paint, left, top, right, bottom):
	width = right - left
	height = bottom - top
	baseUpper = cell.m_data["base"].upper()
	font1 = "16px Arial"
	font2 = "14px Arial"
	font3 = "12px Arial"
	tSize = paint.textSize(baseUpper, font1)
	quoteUpper = " / " + cell.m_data["quote"].upper()
	strVolume = toFixed(cell.m_data["volume"], 6)
	strPrice = toFixed(cell.m_data["price"], 6)
	tSize2 = paint.textSize(strVolume, font3)
	tSize3 = paint.textSize(strPrice, font2)
	strPrice2 = "¥" + toFixed(cell.m_data["price"] * 7.24, 6)
	diffRange = toFixed((cell.m_data["price"] - cell.m_firstPrice) / cell.m_data["price"] * 100, 2) + "%"
	if (grid.m_paint.m_defaultUIStyle == "dark"):
		paint.drawText(baseUpper, "rgb(255,255,255)", font1, left + 5, top + height / 2 - tSize2.cy)
		paint.drawText(quoteUpper, "rgb(200,200,200)", font3, left + 5 + tSize.cx, top + height / 2 - tSize2.cy)
		paint.drawText(strVolume, "rgb(200,200,200)", font3, left + 5, top + height / 2)
	elif (grid.m_paint.m_defaultUIStyle == "light"):
		paint.drawText(baseUpper, "rgb(0,0,0)", font1, left + 5, top + height / 2 - tSize2.cy)
		paint.drawText(quoteUpper, "rgb(50,50,50)", font3, left + 5 + tSize.cx, top + height / 2 - tSize2.cy)
		paint.drawText(strVolume, "rgb(50,50,50)", font3, left + 5, top + height / 2 )
	tSize5 = paint.textSize("100000.00%", font1);
	colRect = FCRect(left + width * 0.7 + 5, top + height / 2 - tSize5.cy / 2, left + width * 0.7 + 5 + tSize5.cx, top + height / 2 + tSize5.cy / 2)
	color = "rgb(15,193,118)"
	if(cell.m_data["price"] >= cell.m_firstPrice):
		color = "rgb(219,68,83)"
	paint.drawText(strPrice, color, font2, left + width * 0.4 + 5, top + height / 2 - tSize3.cy)
	paint.drawText(strPrice2, color, font2, left + width * 0.4 + 5, top + height / 2)
	paint.fillRect(color, colRect.left, colRect.top, colRect.right, colRect.bottom)
	tSize4 = paint.textSize(diffRange, font1)
	if (grid.m_paint.m_defaultUIStyle == "dark"):
		paint.drawText(diffRange, "rgb(255,255,255)", font1, left + width * 0.7 + 5 + tSize5.cx / 2 - tSize4.cx / 2, top + height / 2 - tSize4.cy / 2)
	elif (grid.m_paint.m_defaultUIStyle == "light"):
		paint.drawText(diffRange, "rgb(0,0,0)", font1, left + width * 0.7 + 5 + tSize5.cx / 2 - tSize4.cx / 2, top + height / 2- tSize4.cy / 2)

m_paint = FCPaint() #创建绘图对象
facecat.m_paintCallBack = onViewPaint 
facecat.m_paintBorderCallBack = onViewPaintBorder 
facecat.m_mouseDownCallBack = onViewMouseDown 
facecat.m_mouseMoveCallBack = onViewMouseMove 
facecat.m_mouseUpCallBack = onViewMouseUp
facecat.m_mouseWheelCallBack = onViewMouseWheel
facecat.m_clickCallBack = onViewClick
facecat.m_paintGridCellCallBack = onPaintGridCell
facecat.m_paintGridColumnCallBack = onPaintGridColumn

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

def on_message(ws, message):
	global m_priceList
	hasData = FALSE
	newData = json.loads(message)
	key = newData["base"] + "," + newData["quote"]
	rowsSize = len(m_priceList.m_rows)
	for i in range(0, rowsSize):
		thisCell = m_priceList.m_rows[i].m_cells[0]
		if(thisCell.m_value == key):
			hasData = TRUE
			thisCell.m_data = newData
			thisCell.m_update = 1
			break
	if(hasData == FALSE):
		row = FCGridRow()
		m_priceList.m_rows.append(row)
		cell = FCGridCell()
		cell.m_value = key
		cell.m_data = newData
		cell.m_firstPrice = newData["price"]
		cell.m_update = 0
		row.m_cells.append(cell)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("closed")

def on_open(ws):
    print("start")

def startWebSocket():
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp("wss://ws.coincap.io/trades/binance",
								on_open=on_open,
								on_message=on_message,
								on_error=on_error,
								on_close=on_close)

	ws.run_forever()

wc = win32gui.WNDCLASS()
wc.hbrBackground = COLOR_BTNFACE + 1
wc.hCursor = win32gui.LoadCursor(0,IDI_APPLICATION)
wc.lpszClassName = "facecat-py"
wc.lpfnWndProc = WndProc
reg = win32gui.RegisterClass(wc)
hwnd = win32gui.CreateWindow(reg,'facecat-py',WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN,CW_USEDEFAULT,CW_USEDEFAULT,CW_USEDEFAULT,CW_USEDEFAULT,0,0,0,None)
m_paint.m_hWnd = hwnd

#检查CTP的数据
def checkNewData(a='', b=''):
	invalidate(m_paint)

def run(*args):
	startWebSocket()
thread.start_new_thread(run, ())
timer.set_timer(50, checkNewData)
m_priceList = FCGrid()
m_priceList.m_name = "price"
m_priceList.m_rowHeight = 50
m_priceList.m_headerHeight = 20
addView(m_priceList, m_paint)
m_priceList.m_dock = "fill"
column1 = FCGridColumn()
column1.m_text = "id"
column1.m_width = 500
m_priceList.m_columns.append(column1)

rect = win32gui.GetClientRect(hwnd)
m_paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
for view in m_paint.m_views:
	if view.m_dock == "fill":
		view.m_size = FCSize(m_paint.m_size.cx, m_paint.m_size.cy)
updateView(m_paint.m_views)
win32gui.ShowWindow(hwnd,SW_SHOWNORMAL)
win32gui.UpdateWindow(hwnd)
win32gui.PumpMessages()