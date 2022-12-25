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

#绘制视图
#view:视图
#paint:绘图对象
#drawRect:区域
def onViewPaint(view, paint, drawRect):
	if(view.m_type == "radiobutton"):
		drawRadioButton(view, paint, drawRect)
	elif(view.m_type == "checkbox"):
		drawCheckBox(view, paint, drawRect)
	elif(view.m_type == "chart"):
		resetChartVisibleRecord(view)
		checkChartLastVisibleIndex(view)
		calculateChartMaxMin(view)
		drawChart(view, paint, drawRect)
	elif(view.m_type == "grid"):
		drawDiv(view, paint, drawRect)
		drawGrid(view, paint, drawRect)
	elif(view.m_type == "tree"):
		drawDiv(view, paint, drawRect)
		drawTree(view, paint, drawRect)
	elif(view.m_type == "label"):
		if(view.m_textColor != "none"):
			tSize = paint.textSize(view.m_text, view.m_font)
			paint.drawText(view.m_text, view.m_textColor, view.m_font, 0, (view.m_size.cy - tSize.cy) / 2)
	elif(view.m_type == "div" or view.m_type =="tabpage" or view.m_type =="tabview" or view.m_type =="layout"):
		drawDiv(view, paint, drawRect)
	else:
		drawButton(view, paint, drawRect)

#绘制视图边线
#view:视图
#paint:绘图对象
#drawRect:区域
def onViewPaintBorder(view, paint, drawRect):
	if(view.m_type == "grid"):
		drawGridScrollBar(view, paint, drawRect)
	elif(view.m_type == "tree"):
		drawTreeScrollBar(view, paint, drawRect)
	elif(view.m_type == "div" or view.m_type =="tabpage" or view.m_type =="tabview" or view.m_type =="layout"):
		drawDivScrollBar(view, paint, drawRect)
		drawDivBorder(view, paint, drawRect)

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
#tree:树
def createTreeColumn(tree):
	treeColumn = FCTreeColumn()
	if (tree.m_paint.m_defaultUIStyle == "dark"):
		treeColumn.m_backColor = "rgb(0,0,0)"
		treeColumn.m_borderColor = "rgb(255,255,255)"
		treeColumn.m_textColor = "rgb(255,255,255)"
	elif (tree.m_paint.m_defaultUIStyle == "light"):
		treeColumn.m_backColor = "rgb(200,200,200)"
		treeColumn.m_borderColor = "rgb(0,0,0)"
		treeColumn.m_textColor = "rgb(0,0,0)"
	return treeColumn

#创建节点
#tree:树
def createTreeNode(tree):
	treeNode = FCTreeNode()
	if (tree.m_paint.m_defaultUIStyle == "dark"):
		treeNode.m_backColor = "rgb(0,0,0)"
		treeNode.m_borderColor = "rgb(255,255,255)"
		treeNode.m_textColor = "rgb(255,255,255)"
	elif(tree.m_paint.m_defaultUIStyle == "light"):
		treeNode.m_backColor = "rgb(255,255,255)"
		treeNode.m_borderColor = "rgb(0,0,0)"
		treeNode.m_textColor = "rgb(0,0,0)"
	return treeNode

m_tree = FCTree()
addView(m_tree, m_paint)
if (m_tree.m_paint.m_defaultUIStyle == "dark"):
    m_tree.m_backColor = "rgb(0,0,0)"
    m_tree.m_borderColor = "rgb(255,255,255)"
    m_tree.m_textColor = "rgb(255,255,255)"
elif (m_tree.m_paint.m_defaultUIStyle == "light"):
    m_tree.m_backColor = "rgb(255,255,255)"
    m_tree.m_borderColor = "rgb(0,0,0)"
    m_tree.m_textColor = "rgb(0,0,0)"
m_tree.m_dock = "fill"
m_tree.m_headerHeight = 0
m_tree.m_showCheckBox = TRUE

column = createTreeColumn(m_tree)
column.m_width = 500
m_tree.m_columns.append(column)
       
rootNode = createTreeNode(m_tree)
rootNode.m_value = "证监会行业类"
appendTreeNode(m_tree, rootNode, None)

node1 = createTreeNode(m_tree)
node1.m_value = "农、林、牧、渔业"
appendTreeNode(m_tree, node1, rootNode)

strs1 = []
strs1.append("农业")
strs1.append("林业")
strs1.append("畜牧业")
strs1.append("渔业")
strs1.append("农、林、牧、渔服务业")
for i in range(0, len(strs1)):
	subNode1 = createTreeNode(m_tree)
	subNode1.m_value = strs1[i]
	appendTreeNode(m_tree, subNode1, node1)

node2 = createTreeNode(m_tree)
node2.m_value = "采矿业"
appendTreeNode(m_tree, node2, rootNode)

strs2 = []
strs2.append("煤炭开采和洗选业")
strs2.append("石油和天然气开采业")
strs2.append("黑色金属矿采选业")
strs2.append("有色金属矿采选业")
strs2.append("非金属矿采选业")
strs2.append("开采辅助活动")
for i in range(0, len(strs2)):
	subNode2 = createTreeNode(m_tree)
	subNode2.m_value = strs2[i]
	appendTreeNode(m_tree, subNode2, node2)

node3 = createTreeNode(m_tree)
node3.m_value = "制造业"
appendTreeNode(m_tree, node3, rootNode)

strs3 = []
strs3.append("农副食品加工业")
strs3.append("食品制造业")
strs3.append("酒、饮料和精制茶制造业")
strs3.append("纺织业")
strs3.append("纺织服装、服饰业")
strs3.append("皮革、毛皮、羽毛及其制品和制鞋业")
strs3.append("木材加工和木、竹、藤、棕、草制品业")
strs3.append("家具制造业")
strs3.append("造纸和纸制品业")
strs3.append("印刷和记录媒介复制业")
strs3.append("文教、工美、体育和娱乐用品制造业")
strs3.append("石油加工、炼焦和核燃料加工业")
strs3.append("化学原料及化学制品制造业")
strs3.append("医药制造业")
strs3.append("化学纤维制造业")
strs3.append("橡胶和塑料制品业")
strs3.append("非金属矿物制品业")
strs3.append("黑色金属冶炼和压延加工业")
strs3.append("有色金属冶炼和压延加工业")
strs3.append("金属制品业")
strs3.append("通用设备制造业")
strs3.append("专用设备制造业")
strs3.append("汽车制造业")
strs3.append("铁路、船舶、航空航天和其他运输设备制造业")
strs3.append("电气机械和器材制造业")
strs3.append("计算机、通信和其他电子设备制造业")
strs3.append("仪器仪表制造业")
strs3.append("其他制造业")
strs3.append("废弃资源综合利用业")
for i in range(0, len(strs3)):
	subNode3 = createTreeNode(m_tree)
	subNode3.m_value = strs3[i]
	appendTreeNode(m_tree, subNode3, node3)

rect = win32gui.GetClientRect(hwnd)
m_paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
for view in m_paint.m_views:
	if view.m_dock == "fill":
		view.m_size = FCSize(m_paint.m_size.cx, m_paint.m_size.cy)
updateView(m_paint.m_views)
win32gui.ShowWindow(hwnd,SW_SHOWNORMAL)
win32gui.UpdateWindow(hwnd)
win32gui.PumpMessages()