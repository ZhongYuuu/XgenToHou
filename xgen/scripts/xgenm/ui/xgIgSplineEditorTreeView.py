from __future__ import division
from builtins import range
pysideVersion = r'-1'
import PySide2, PySide2.QtCore, PySide2.QtGui, PySide2.QtWidgets
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
pysideVersion = PySide2.__version__

from xgenm.ui.util.xgUtil import *
from xgenm.ui.xgConsts import *
from xgenm.ui.xgIgSplineEditorTreeItem import *

'''
    QTreeView for XGen Interactive Groom Spline Editor
'''
class IgSplineEditorTreeView(QTreeView):

    # Colors
    COLOR_BACKGROUND    = QColor(54, 54, 54)

    # Pens
    PEN_BRANCH          = QPen(QBrush(QColor(130, 130, 130)), DpiScale(1))
    PEN_BRANCH_HILITE   = QPen(QBrush(QColor(146, 166, 179)), DpiScale(1))
    PEN_DROPINDICATOR   = QPen(QBrush(QColor(82,  133, 166)), DpiScale(2))

    # Brushes
    BRUSH_DROPINDICATOR = QBrush(QColor(82,  133, 166, 128))
    BRUSH_ALT_HIGHLIGHT = QBrush(QColor(65,  77,  90))

    # QHeaderView
    headerView          = None

    # Delegations
    iconDelegate        = None
    textDelegate        = None

    # Cached ancestor items of the selections
    cachedAncestors     = None

    # Whether to expand descendents ?
    isExpandDescendents = False

    # Drag & Drop
    mimeType            = None
    dropIndicatorRect   = QRect()

    def __init__(self, model, parent=None):
        ''' Constructor '''
        QTreeView.__init__(self, parent)
        model.setView(self)

        # Override the default QHeaderView
        self.headerView = IgSplineEditorTreeViewHeader()
        self.setHeader(self.headerView)

        # QTreeView properties
        self.setModel(model)
        self.setUniformRowHeights(True)
        self.setExpandsOnDoubleClick(False)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAllColumnsShowFocus(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setIndentation(DpiScale(IgSplineEditorTreeColumn.INDENT))
        self.setIconSize(QSize(DpiScale(24), DpiScale(24)))

        # QHeaderView properties
        if pysideVersion == '1.2.0':
            self.headerView.setMovable(True)
            self.headerView.setResizeMode(QHeaderView.ResizeToContents)
            self.headerView.setResizeMode(IgSplineEditorTreeColumn.NAME, QHeaderView.Interactive)
            self.headerView.setResizeMode(IgSplineEditorTreeColumn.WEIGHT, QHeaderView.Stretch)
        else:
            self.headerView.setSectionsMovable(True)
            self.headerView.setSectionResizeMode(QHeaderView.ResizeToContents)
            self.headerView.setSectionResizeMode(IgSplineEditorTreeColumn.NAME, QHeaderView.Interactive)
            self.headerView.setSectionResizeMode(IgSplineEditorTreeColumn.WEIGHT, QHeaderView.Stretch)
        self.headerView.setDefaultSectionSize(DpiScale(20))
        self.headerView.resizeSection(IgSplineEditorTreeColumn.NAME, DpiScale(200))
        self.headerView.setStretchLastSection(False)
        self.headerView.moveSection(0, 1)

        # Palette
        palette = QPalette()
        palette.setColor(QPalette.Base, self.COLOR_BACKGROUND)
        self.setPalette(palette)

        # Delegations
        self.iconDelegate = IgSplineEditorTreeViewIconDelegate()
        self.textDelegate = IgSplineEditorTreeViewTextDelegate()
        self.setItemDelegateForColumn(IgSplineEditorTreeColumn.ENABLE, self.iconDelegate)
        self.setItemDelegateForColumn(IgSplineEditorTreeColumn.NAME, self.textDelegate)
        self.setItemDelegateForColumn(IgSplineEditorTreeColumn.KEY, self.iconDelegate)

        # Ancestor cache during painting
        self.cachedAncestors = set()

        # Signals
        self.clicked.connect(model.onClicked)
        self.customContextMenuRequested.connect(model.onCustomContextMenuRequested)
        self.collapsed.connect(self.onCollapsed)
        self.expanded.connect(self.onExpanded)
        
        selectionModel = self.selectionModel()
        selectionModel.selectionChanged.connect(model.onSelectionChanged)

        # Force to redraw the whole widget. We highlight the ancestor rows
        # of the current selections. Qt doesn't invalidate the rectangle
        # of these ancestor rows by default.
        selectionModel.selectionChanged.connect(lambda: self.viewport().update())

    def paintEvent(self, event):
        ''' Paint the QTreeView widget '''

        # Cache the ancestors of the selections to speed up row drawing
        self.cachedAncestors.clear()
        for index in self.selectionModel().selectedRows():
            # Go up and cache internal items
            index = index.parent()
            while index.isValid():
                self.cachedAncestors.add(index.internalPointer())
                index = index.parent()

        # Paint the QTreeView widget as usual
        self.executeDelayedItemsLayout()
        painter = QPainter(self.viewport())
        self.drawTree(painter, event.region())

        # Custom painting of the drop indicator
        self.paintDropIndicator(painter)

        # Clear the ancestor cache after painting
        self.cachedAncestors.clear()

    def drawBranches(self, painter, rect, index):
        ''' Draw the branch indicator of a row '''

        # Get the indention level of the row
        level = 0
        tmpIndex = index.parent()
        while tmpIndex.isValid():
            level += 1
            tmpIndex = tmpIndex.parent()

        # Is the row highlighted (selected) ?
        isHighlight = self.selectionModel().isSelected(index)

        # Line width
        lineWidth = DpiScale(1)

        # Cell width
        cellWidth = int(rect.width() / (level + 1))

        # Current cell to draw in
        cellX = rect.x() + cellWidth * level
        cellY = rect.y()
        cellW = cellWidth
        cellH = rect.height()
        
        # Center of the cell
        centerX = cellX + int(cellW / 2) - int(lineWidth / 2)
        centerY = cellY + int(cellH / 2) - int(lineWidth / 2)

        # Backup the old pen
        oldPen   = painter.pen()

        # Draw the branch indicator on the right most
        if self.model().hasChildren(index):
            # Branch icon properties
            rectRadius  = DpiScale(4)
            crossMargin = DpiScale(1)

            # Is the row expanded ?
            isExpanded = self.isExpanded(index)

            # [+] and [-] are using different color when highlighted
            painter.setPen(self.PEN_BRANCH_HILITE if isHighlight else self.PEN_BRANCH)

            # Draw a rectangle [ ] as the branch indicator
            painter.drawRect(centerX - rectRadius,
                             centerY - rectRadius,
                             rectRadius * 2,
                             rectRadius * 2)

            # Draw the '-' into the rectangle. i.e. [-]
            painter.drawLine(centerX - rectRadius + crossMargin + lineWidth,
                             centerY,
                             centerX + rectRadius - crossMargin - lineWidth,
                             centerY)

            # Draw the '|' into the rectangle. i.e. [+]
            if not isExpanded:
                painter.drawLine(centerX,
                                 centerY - rectRadius + crossMargin + lineWidth,
                                 centerX,
                                 centerY + rectRadius - crossMargin - lineWidth)

            # Other ornaments are not highlighted
            painter.setPen(self.PEN_BRANCH)

            # Draw the '|' on the bottom. i.e. [-]
            #                                   |
            if isExpanded:
                painter.drawLine(centerX,
                                 centerY + rectRadius + crossMargin + lineWidth,
                                 centerX,
                                 cellY + cellH)

            # Draw more ornaments when the row is not a top level row
            if level > 0:
                # Draw the '-' on the left. i.e. --[+]
                painter.drawLine(cellX,
                                 centerY,
                                 centerX - rectRadius - crossMargin - lineWidth,
                                 centerY)
        else:
            # Circle is not highlighted
            painter.setPen(self.PEN_BRANCH)

            # Draw the line and circle. i.e. --o
            if level > 0:
                painter.drawLine(cellX, centerY, centerX, centerY)

                # Backup the old brush
                oldBrush = painter.brush()
                painter.setBrush(self.PEN_BRANCH.brush())

                # A filled circle
                circleRadius = DpiScale(2)
                painter.drawEllipse(centerX - circleRadius,
                                    centerY - circleRadius,
                                    circleRadius * 2,
                                    circleRadius * 2)

                # Restore the old brush
                painter.setBrush(oldBrush)

        # Draw other vertical and horizental lines on the left of the indicator
        if level > 0:
            # Move cell window to the left
            cellX   -= cellWidth
            centerX -= cellWidth

            if index.sibling(index.row() + 1, index.column()).isValid():
                # The row has more siblings. i.e. |
                #                                 |--
                #                                 |
                painter.drawLine(centerX, cellY, centerX, cellY + cellH)
                painter.drawLine(centerX, centerY, cellX + cellW, centerY)
            else:
                # The row is the last row.   i.e. |
                #                                 L--
                painter.drawLine(centerX, cellY, centerX, centerY)
                painter.drawLine(centerX, centerY, cellX + cellW, centerY)

            # More vertical lines on the left. i.e. ||||-
            tmpIndex = index.parent()
            for i in range(0, level - 1):
                # Move the cell window to the left
                cellX   -= cellWidth
                centerX -= cellWidth

                # Draw vertical line if the row has silbings at this level
                if tmpIndex.sibling(tmpIndex.row() + 1, tmpIndex.column()).isValid():
                    painter.drawLine(centerX, cellY, centerX, cellY + cellH)
                tmpIndex = tmpIndex.parent()

        # Restore the old pen
        painter.setPen(oldPen)

    def drawRow(self, painter, option, index):
        ''' Draw the row in the tree view that contains the model item index '''

        # Draw an indirect highlight color
        if index.internalPointer() in self.cachedAncestors:
            painter.fillRect(option.rect, self.BRUSH_ALT_HIGHLIGHT)

        # Draw the default row
        QTreeView.drawRow(self, painter, option, index)

    def paintDropIndicator(self, painter):
        ''' Paint the drop indicator when dragging '''

        # Paint the drop indicator
        if self.showDropIndicator() and not self.dropIndicatorRect.isNull():
            painter.save()
            painter.setPen(self.PEN_DROPINDICATOR)
            if self.dropIndicatorRect.height() == 0:
                painter.drawLine(self.dropIndicatorRect.topLeft(), self.dropIndicatorRect.topRight())
            else:
                painter.setBrush(self.BRUSH_DROPINDICATOR)
                painter.drawRect(self.dropIndicatorRect)
            painter.restore()

    def mousePressEvent(self, event):
        ''' The event handler for key press event '''

        # Hijack the mouse press event. When Shift key is pressed, we
        # are going to expand all descendents.
        if QGuiApplication.keyboardModifiers() == Qt.ShiftModifier:
            self.isExpandDescendents = True

        # Reset the drop indicator rectangle
        self.dropIndicatorRect = QRect()

        # Handle mouse press event
        QTreeView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        ''' The event handler for key release event '''

        # Handle mouse release event
        QTreeView.mouseReleaseEvent(self, event)

        # Reset flags
        self.isExpandDescendents = False

    def dragEnterEvent(self, event):
        ''' The event handler for drag enter event '''

        # Handle drag enter event
        QTreeView.dragEnterEvent(self, event)

        # Get the type of the items being dragged. The model can return
        # different flags based on the items being dragged.
        # e.g. We want to drop a sculpt layer onto a sculpt modifier as a
        # top level layer. But we don't want to drop a modifier onto a
        # sculpt modifier.
        self.mimeType = r''
        for mimeType in IgSplineEditorMimeData.MIME_TYPES:
            if event.mimeData().hasFormat(mimeType):
                self.mimeType = mimeType
                break

    def dragMoveEvent(self, event):
        ''' The event handler for drag move event '''

        # Handle drag move event
        QTreeView.dragMoveEvent(self, event)

        # QModelIndex under the cursor
        index = self.indexAt(event.pos())

        # Compute the drop indicator rectangle
        #   Similar to QAbstractItemView::dragMoveEvent()
        if index.isValid() and self.showDropIndicator():
            rect = self.visualRect(index)
            dpos = self.dropIndicatorPosition()

            # Drop above an item (----------)
            if dpos == QAbstractItemView.AboveItem:
                if self.model().flags(index.parent()) & Qt.ItemIsDropEnabled:
                    self.dropIndicatorRect = QRect(rect.left(), rect.top(), rect.width(), 0)
                else:
                    self.dropIndicatorRect = QRect()

            # Drop below an item (----------)
            elif dpos == QAbstractItemView.BelowItem:
                if self.model().flags(index.parent()) & Qt.ItemIsDropEnabled:
                    self.dropIndicatorRect = QRect(rect.left(), rect.bottom(), rect.width(), 0)
                else:
                    self.dropIndicatorRect = QRect()

            # Drop on an item ([        ])
            elif dpos == QAbstractItemView.OnItem:
                if self.model().flags(index) & Qt.ItemIsDropEnabled:
                    self.dropIndicatorRect = rect
                else:
                    self.dropIndicatorRect = QRect()

            # Drop on the background.
            elif dpos == QAbstractItemView.OnViewport:
                self.dropIndicatorRect = QRect()

            # ???
            else:
                self.dropIndicatorRect = QRect()

    def dragLeaveEvent(self, event):
        ''' The event handler for drag leave event '''

        # Handle the drag leave event
        QTreeView.dragLeaveEvent(self, event)

        # Reset the drag type
        self.mimeType = r''

        # Reset the drop indicator rectangle
        self.dropIndicatorRect = QRect()

    def dropEvent(self, event):
        ''' The event handler for drop event '''

        # Handle the drop event
        QTreeView.dropEvent(self, event)

        # Reset the drag type
        self.mimeType = r''

        # Reset the drop indicator rectangle
        self.dropIndicatorRect = QRect()

    def keyPressEvent(self, event):
        ''' The event handler for key press event '''

        # Hijack Shift + Any and bypass to parent widgets. QAbstractItemView
        # by default handles Shift + Any as a keyboard search command.
        # This can be some Maya shotcut key combination as well..
        if event.modifiers() & Qt.ShiftModifier and event.text():
            event.ignore()
            return

        # Hijack Ctrl + A and bypass to parent widgets. Ctrl + A is a key
        # combination in Maya to bring up the Attribute Editor by default.
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_A:
            event.ignore()
            return

        # Handle the key press event
        QTreeView.keyPressEvent(self, event)

    def onCollapsed(self, index):
        ''' Slot when an item is collapsed '''

        # Recursively expand all descendents when Shift is pressed
        if self.isExpandDescendents:
            # One-shot collapse all
            self.isExpandDescendents = False
            self.setDescendentsExpanded(index, False)

    def onExpanded(self, index):
        ''' Slot when an item is expanded '''

        # Recursively expand all descendents when Shift is pressed
        if self.isExpandDescendents:
            # One-shot expand all
            self.isExpandDescendents = False
            self.setDescendentsExpanded(index, True)

    def setDescendentsExpanded(self, index, expanded):
        ''' A recursive version of setExpanded but don't set index itself '''

        for i in range(0, index.model().rowCount(index)):
            childIndex = index.child(i, 0)
            self.setExpanded(childIndex, expanded)
            self.setDescendentsExpanded(childIndex, expanded)


'''
    QHeaderView to draw icon in the center of the cell.
'''
class IgSplineEditorTreeViewHeader(QHeaderView):

    # Icons
    eyeIcon     = None
    eyePixmap   = None

    def __init__(self, parent=None):
        ''' Constructor '''
        QHeaderView.__init__(self, Qt.Horizontal, parent)

        # Load icons
        self.eyeIcon    = CreateIcon(r':/eye.png')
        self.eyeSize    = QSize(DpiScale(20),DpiScale(20))
        self.eyePixmap  = self.eyeIcon.pixmap(self.eyeSize)

    def paintSection(self, painter, rect, logicalIndex):
        ''' Paint the section specified by the given logical index '''

        # Paint the header section as usual
        painter.save()
        QHeaderView.paintSection(self, painter, rect, logicalIndex)
        painter.restore()

        # Overlay the eye icon
        if logicalIndex == IgSplineEditorTreeColumn.ENABLE:
            # Draw the icon in the center of the cell
            mid = ( rect.size() - self.eyeSize ) * 0.5
            painter.drawPixmap(
                rect.x() + int(mid.width()),
                rect.y() + int(mid.height()),
                self.eyePixmap)


'''
    Delegation to draw an icon in the cell. DecorationRole is not able to align
    the icon in the center of the cell by default...
'''
class IgSplineEditorTreeViewIconDelegate(QStyledItemDelegate):

    # Size of the icon
    iconSize    = QSize()

    def __init__(self, parent=None):
        ''' Constructor '''
        QStyledItemDelegate.__init__(self, parent)

        # By default, we show icons in 20 * 20 pixels
        self.iconSize = QSize(DpiScale(20), DpiScale(20))

    def paint(self, painter, option, index):
        ''' Paint the cell '''

        # Paint the highlight
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        # Paint the icon
        icon = index.data(Qt.DecorationRole)
        if isinstance(icon, QIcon):
            rect = option.rect
            mid  = (rect.size() - self.iconSize) * 0.5
            painter.drawPixmap(
                rect.x() + int(mid.width()),
                rect.y() + int(mid.height()),
                icon.pixmap(self.iconSize))

'''
    Delegation to show a QLineEdit with padding...
'''
class IgSplineEditorTreeViewTextDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        ''' Constructor '''
        QStyledItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        ''' Render the delegate using the given painter and style optoin '''

        # Qt draws the text with HighlightedText color instead of the forground
        # role. This is not expected because we want to draw text in gray..
        forground = index.data(Qt.ForegroundRole)
        if forground:
            oldHighlightColor = option.palette.color(QPalette.HighlightedText)
            option.palette.setColor(QPalette.HighlightedText, forground)
            QStyledItemDelegate.paint(self, painter, option, index)
            option.palette.setColor(QPalette.HighlightedText, oldHighlightColor)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)

    def updateEditorGeometry(self, editor, option, index):
        ''' Update the editor for the item specified by index '''
        QStyledItemDelegate.updateEditorGeometry(self, editor, option, index)

        # The default QLineEdit is expanding..
        rect = editor.geometry()
        rect.adjust(DpiScale(0), DpiScale(2), DpiScale(0), DpiScale(-2))
        editor.setGeometry(rect)







# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
