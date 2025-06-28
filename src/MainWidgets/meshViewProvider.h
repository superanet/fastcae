﻿/**
 * ============================================================================
 * Program:   FastCAE
 *
 * Copyright (c) 青岛数智船海科技有限公司
 * All rights reserved.
 * See License or http://www.fastcae.com/index.html for details.
 *
 * BSD 3-Clause License
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.
 * ==================================================================================
 *
 * @file meshViewProvider.h
 * @brief 根据渲染的模式与渲染的网格数据，生成渲染层对象，并对其进行维护管理
 *
 */
#ifndef MESHVIEWPROVIDER_H_
#define MESHVIEWPROVIDER_H_

#include "mainWidgetsAPI.h"
#include "ModuleBase/ModuleType.h"
#include <QObject>
#include <QHash>
#include <QMultiHash>

class vtkActor;
class vtkDataSet;

namespace GUI
{
	class MainWindow;
}

namespace MeshData
{
	class MeshData;
	class MeshKernal;
	class MeshSet;
}

namespace MainWidget
{
	class PreWindow;
	class MeshKernalViewObj;

	enum DisplayModel
	{
		Node,
		WireFrame,
		Surface,
		SurfaceWithEdge,
	};

	class MAINWIDGETSAPI MeshViewProvider : public QObject
	{
		Q_OBJECT

	public:
		/**
		 * @brief Construct a new Mesh View Provider object
		 * @param  mainwindow       主窗口
		 * @param  preWin           前处理窗口
		 */
		MeshViewProvider(GUI::MainWindow *mainwindow, PreWindow *preWin);
		/**
		 * @brief Destroy the Mesh View Provider object
		 */
		~MeshViewProvider();
		/**
		 * @brief 更新显示模式
		 * @param  k   网格kernal，若为nullptr则全部更新
		 */
		void updateDisplayModel(MeshData::MeshKernal *k = nullptr);
		/**
		 * @brief 更新颜色等渲染选项
		 * @param  k   网格kernal，若为nullptr则全部更新
		 */
		void updateGraphOption(MeshData::MeshKernal *k = nullptr);
		/**
		 * @brief   是否显示Kernal
		 * @param  k     网格Kernal
		 * @param  show  是否显示
		 */
		void showKernal(MeshData::MeshKernal *k, bool show);
		/**
		 * @brief  设置网格交互拾取模式
		 * @param  m   拾取模式
		 */
		void setMeshSelectMode(ModuleBase::SelectModel m);
		/**
		 * @brief 高亮交互拾取的对象
		 * @param  items    交互拾取的对象
		 */
		void highLighSelectItem(QMultiHash<int, int> *items);
		/**
		 * @brief  获取交互选取的网格元素
		 * @return QMultiHash<int, int>*   kernalID-node/element Index  Hash
		 */
		QMultiHash<int, int> *getSelectItem();

	public slots:
		/**
		 * @brief 新建或者删除网格，更新显示
		 */
		void updateMeshActorSlot();

	private slots:
		/**
		 * @brief  高亮网格
		 * @param  k
		 */
		void highLighKernel(MeshData::MeshKernal *k);
		/**
		 * @brief  高亮网格组件
		 * @param  set   网格组件
		 */
		void highLighMeshSet(MeshData::MeshSet *set);
		/**
		 * @brief 清除高亮
		 */
		void clearHighLight();
		/**
		 * @brief 更新网格组件的显示状态
		 * @param  set  需要更新的网格组件
		 */
		void updateMeshSetVisibily(MeshData::MeshSet *set);
		/**
		 * @brief 更新网格组件颜色
		 * @param  set  需要更新的网格组件id
		 */
		void updateMeshSetColor(int setid);

	private:
		/**
		 * @brief 移除显示对象，窗口将不再显示
		 * @param  kernal     要移除显示的Kernal
		 */
		void removeDisplay(MeshData::MeshKernal *kernal);
		/**
		 * @brief  根据显示层数据获取到View Object
		 * @param  data    用于渲染的dataset
		 * @return MeshKernalViewObj*  date对应的ViewObject
		 */
		MeshKernalViewObj *getViewObjByDisplayDataSet(vtkDataSet *data);

	private:
		/**
		 * @brief 前处理窗口
		 */
		PreWindow *_preWindow{};
		/**
		 * @brief 主窗口
		 */
		GUI::MainWindow *_mainWindow{};
		/**
		 * @brief 网格数据
		 */
		MeshData::MeshData *_meshData{};
		/**
		 * @brief 显示对象数据管理hash
		 */
		QHash<MeshData::MeshKernal *, MeshKernalViewObj *> _viewObjects{};
		/**
		 * @brief 交互拾取模式
		 */
		ModuleBase::SelectModel _selectModel{ModuleBase::None};
		/**
		 * @brief 临时记录网格组件高亮对象
		 */
		MeshData::MeshSet *_highLightSet{nullptr};
		/**
		 * @brief 高亮的交互选取的对象
		 */
		QMultiHash<int, int> _highLightSelectItems{};
	};

}

#endif
