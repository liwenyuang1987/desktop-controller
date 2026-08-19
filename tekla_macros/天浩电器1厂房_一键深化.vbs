'======================================================================
' 天浩电器1#生产车间 - Tekla参数化一键深化宏
' 依据：结施 刚架简图（图12-1）+ 结构计算书
' 功能：轴网 → 刚架柱(变截面) → 抗风柱 → 屋面梁 → 柱间支撑 → 屋面支撑 → 檩条
' 单位：mm
'======================================================================
Option Explicit

'========================= 项目参数区 =========================
' --- 工程信息 ---
Const PROJECT_NAME   = "天浩电器1#生产车间"
Const STRUCTURE_TYPE = "门式刚架轻型房屋钢结构"
Const MATERIAL       = "Q355B"

' --- 跨度方向柱布置（X方向，7根柱6段）---
' 柱距数组（从左到右），单位mm
Dim COLUMN_SPANS(5)
COLUMN_SPANS(0) = 5700
COLUMN_SPANS(1) = 5000
COLUMN_SPANS(2) = 5850
COLUMN_SPANS(3) = 5850
COLUMN_SPANS(4) = 5000
COLUMN_SPANS(5) = 5700

' 柱顶标高数组（对应7根柱，从左到右），单位mm
Dim COLUMN_HEIGHTS(6)
COLUMN_HEIGHTS(0) = 8000   ' 左端柱（刚架柱，变截面）
COLUMN_HEIGHTS(1) = 8590   ' 抗风柱
COLUMN_HEIGHTS(2) = 9090   ' 抗风柱
COLUMN_HEIGHTS(3) = 9670   ' 中柱（刚架柱，变截面，最高）
COLUMN_HEIGHTS(4) = 9090   ' 抗风柱
COLUMN_HEIGHTS(5) = 8590   ' 抗风柱
COLUMN_HEIGHTS(6) = 8000   ' 右端柱（刚架柱，变截面）

' 柱类型：0=抗风柱(等截面), 1=刚架柱(变截面)
Dim COLUMN_TYPES(6)
COLUMN_TYPES(0) = 1
COLUMN_TYPES(1) = 0
COLUMN_TYPES(2) = 0
COLUMN_TYPES(3) = 1
COLUMN_TYPES(4) = 0
COLUMN_TYPES(5) = 0
COLUMN_TYPES(6) = 1

' --- 纵向（Y方向）刚架榀数和间距 ---
Const FRAME_COUNT    = 6     ' 刚架榀数（纵向）
Const FRAME_SPACING  = 6000  ' 刚架间距 mm（需根据实际平面图调整）

' --- 截面参数 ---
Const COLUMN_PROFILE_VAR  = "I(300-500)*250*6*12"  ' 变截面刚架柱（小头300→大头500）
Const COLUMN_PROFILE_EQ   = "I300*250*6*12"        ' 等截面抗风柱
Const BEAM_PROFILE        = "I400*180*6*10"        ' 屋面梁
Const BRACE_PROFILE       = "L100*10"               ' 支撑角钢
Const PURLIN_PROFILE      = "C160*60*20*2.5"       ' 檩条C型钢
Const TIE_BAR_PROFILE     = "D114*4"                ' 系杆圆管

' --- 布置参数 ---
Const PURLIN_SPACING    = 1500   ' 檩条间距 mm
Const EAVE_PURLIN       = True   ' 是否布置檐口檩条
Const BRACE_BAY_START   = 1      ' 柱间支撑起始开间（从1开始）
Const BRACE_BAY_INTERVAL = 3     ' 每隔几开间布置支撑
Const ROOF_BRACE_BAY    = 1      ' 屋面水平支撑开间
Const COLUMN_BASE_Z     = 0      ' 柱底标高
Const ROOF_SLOPE        = 10     ' 屋面坡度 %（1:10）

'======================================================================
' 连接模型
'======================================================================
Dim model
Set model = CreateObject("Tekla.Structures.Model.Model")

If Not model.GetConnectionStatus() Then
    MsgBox "未连接到Tekla模型！请先打开模型再运行。", vbCritical, "错误"
    WScript.Quit
End If

model.CommitChanges()

'======================================================================
' 计算柱X坐标
'======================================================================
Dim columnX(6)
columnX(0) = 0
Dim i
For i = 1 To 6
    columnX(i) = columnX(i-1) + COLUMN_SPANS(i-1)
Next

Dim totalSpan
totalSpan = columnX(6)  ' 总跨度 33100

'======================================================================
' 1. 建立轴网
'======================================================================
Dim grid, coordsX(), labelsX(), coordsY(), labelsY(), coordsZ(), labelsZ()
Dim j, totalY

' X方向（跨度方向，7根柱）
ReDim coordsX(6)
ReDim labelsX(6)
For i = 0 To 6
    coordsX(i) = columnX(i)
    labelsX(i) = CStr(i + 1)
Next

' Y方向（纵向，FRAME_COUNT+1根轴线）
totalY = FRAME_COUNT
ReDim coordsY(totalY)
ReDim labelsY(totalY)
For j = 0 To totalY
    coordsY(j) = j * FRAME_SPACING
    labelsY(j) = Chr(65 + j)  ' A, B, C...
Next

' Z方向（标高）
ReDim coordsZ(2)
ReDim labelsZ(2)
coordsZ(0) = 0
labelsZ(0) = "0.000"
coordsZ(1) = 8000
labelsZ(1) = "8.000"
coordsZ(2) = 9670
labelsZ(2) = "9.670"

Set grid = CreateObject("Tekla.Structures.Model.Grid")
grid.CoordinateX = coordsX
grid.LabelX = labelsX
grid.CoordinateY = coordsY
grid.LabelY = labelsY
grid.CoordinateZ = coordsZ
grid.LabelZ = labelsZ
grid.IsMagneticX = True
grid.IsMagneticY = True
grid.IsMagneticZ = False
grid.Insert()

'======================================================================
' 2. 建立钢柱（每榀刚架7根柱，共FRAME_COUNT榀）
'======================================================================
Dim col, k, xPos, yPos, colHeight, colProfile

For k = 0 To FRAME_COUNT   ' 每榀刚架（Y方向）
    yPos = coordsY(k)
    For i = 0 To 6         ' 每根柱（X方向）
        xPos = columnX(i)
        colHeight = COLUMN_HEIGHTS(i)

        If COLUMN_TYPES(i) = 1 Then
            colProfile = COLUMN_PROFILE_VAR  ' 变截面刚架柱
        Else
            colProfile = COLUMN_PROFILE_EQ   ' 等截面抗风柱
        End If

        Set col = CreateObject("Tekla.Structures.Model.Beam")
        col.StartPoint.X = xPos
        col.StartPoint.Y = yPos
        col.StartPoint.Z = COLUMN_BASE_Z
        col.EndPoint.X = xPos
        col.EndPoint.Y = yPos
        col.EndPoint.Z = colHeight
        col.Profile.ProfileString = colProfile
        col.Material.MaterialString = MATERIAL
        col.Position.Plane = 0      ' MIDDLE
        col.Position.Depth = 0      ' MIDDLE
        col.Position.Rotation = 0
        col.Insert()
    Next
Next

'======================================================================
' 3. 建立屋面梁（每榀刚架，沿柱顶折线布置）
'    柱顶标高不同，梁连接相邻柱顶，形成折形屋面
'======================================================================
Dim beam, zStart, zEnd

For k = 0 To FRAME_COUNT
    yPos = coordsY(k)
    For i = 0 To 5
        ' 左坡梁（柱i顶 → 柱i+1顶）
        zStart = COLUMN_HEIGHTS(i)
        zEnd = COLUMN_HEIGHTS(i+1)

        Set beam = CreateObject("Tekla.Structures.Model.Beam")
        beam.StartPoint.X = columnX(i)
        beam.StartPoint.Y = yPos
        beam.StartPoint.Z = zStart
        beam.EndPoint.X = columnX(i+1)
        beam.EndPoint.Y = yPos
        beam.EndPoint.Z = zEnd
        beam.Profile.ProfileString = BEAM_PROFILE
        beam.Material.MaterialString = MATERIAL
        beam.Position.Plane = 0
        beam.Position.Depth = 0
        beam.Insert()
    Next
Next

'======================================================================
' 4. 建立柱间交叉支撑（纵向相邻刚架间，指定开间）
'======================================================================
Dim brace, midZ, bayIdx

For bayIdx = BRACE_BAY_START - 1 To 5 Step BRACE_BAY_INTERVAL
    If bayIdx + 1 <= 5 Then
        For k = 0 To FRAME_COUNT - 1
            ' 每根柱位置做交叉支撑（沿Y方向，相邻两榀之间）
            For i = 0 To 6
                xPos = columnX(i)
                colHeight = COLUMN_HEIGHTS(i)

                ' 交叉支撑第1根（左下→右上）
                Set brace = CreateObject("Tekla.Structures.Model.Beam")
                brace.StartPoint.X = xPos
                brace.StartPoint.Y = coordsY(k)
                brace.StartPoint.Z = COLUMN_BASE_Z
                brace.EndPoint.X = xPos
                brace.EndPoint.Y = coordsY(k+1)
                brace.EndPoint.Z = colHeight
                brace.Profile.ProfileString = BRACE_PROFILE
                brace.Material.MaterialString = MATERIAL
                brace.Insert()

                ' 交叉支撑第2根（左上→右下）
                Set brace = CreateObject("Tekla.Structures.Model.Beam")
                brace.StartPoint.X = xPos
                brace.StartPoint.Y = coordsY(k)
                brace.StartPoint.Z = colHeight
                brace.EndPoint.X = xPos
                brace.EndPoint.Y = coordsY(k+1)
                brace.EndPoint.Z = COLUMN_BASE_Z
                brace.Profile.ProfileString = BRACE_PROFILE
                brace.Material.MaterialString = MATERIAL
                brace.Insert()
            Next
        Next
    End If
Next

'======================================================================
' 5. 建立屋面水平支撑（两端开间，沿屋面交叉）
'======================================================================
Dim rb, zRoofLeft, zRoofRight
For k = 0 To FRAME_COUNT - 1 Step FRAME_COUNT - 1  ' 第一榀和最后一榀之间
    For i = 0 To 5
        zRoofLeft = COLUMN_HEIGHTS(i)
        zRoofRight = COLUMN_HEIGHTS(i+1)

        ' 交叉支撑1
        Set rb = CreateObject("Tekla.Structures.Model.Beam")
        rb.StartPoint.X = columnX(i)
        rb.StartPoint.Y = coordsY(k)
        rb.StartPoint.Z = zRoofLeft
        rb.EndPoint.X = columnX(i+1)
        rb.EndPoint.Y = coordsY(k+1)
        rb.EndPoint.Z = zRoofRight
        rb.Profile.ProfileString = BRACE_PROFILE
        rb.Material.MaterialString = MATERIAL
        rb.Insert()

        ' 交叉支撑2
        Set rb = CreateObject("Tekla.Structures.Model.Beam")
        rb.StartPoint.X = columnX(i+1)
        rb.StartPoint.Y = coordsY(k)
        rb.StartPoint.Z = zRoofRight
        rb.EndPoint.X = columnX(i)
        rb.EndPoint.Y = coordsY(k+1)
        rb.EndPoint.Z = zRoofLeft
        rb.Profile.ProfileString = BRACE_PROFILE
        rb.Material.MaterialString = MATERIAL
        rb.Insert()
    Next
Next

'======================================================================
' 6. 建立檩条（沿Y方向通长，垂直于刚架，按屋面坡度布置）
'======================================================================
Dim purlin, zPur, distAlong, stepCount, halfSpan, xPur

For i = 0 To 5   ' 每个柱距区间
    Dim spanLen
    spanLen = COLUMN_SPANS(i)
    zStart = COLUMN_HEIGHTS(i)
    zEnd = COLUMN_HEIGHTS(i+1)

    ' 按檩条间距在区间内布置
    stepCount = 1
    Do While stepCount * PURLIN_SPACING < spanLen
        distAlong = stepCount * PURLIN_SPACING
        xPur = columnX(i) + distAlong
        ' 线性插值计算檩条处标高
        zPur = zStart + (zEnd - zStart) * distAlong / spanLen

        Set purlin = CreateObject("Tekla.Structures.Model.Beam")
        purlin.StartPoint.X = xPur
        purlin.StartPoint.Y = coordsY(0)
        purlin.StartPoint.Z = zPur
        purlin.EndPoint.X = xPur
        purlin.EndPoint.Y = coordsY(FRAME_COUNT)
        purlin.EndPoint.Z = zPur
        purlin.Profile.ProfileString = PURLIN_PROFILE
        purlin.Material.MaterialString = MATERIAL
        purlin.Insert()

        stepCount = stepCount + 1
    Loop
Next

'======================================================================
' 7. 建立系杆（柱顶位置，沿Y方向通长）
'======================================================================
Dim tieBar
For i = 0 To 6
    xPos = columnX(i)
    zPos = COLUMN_HEIGHTS(i)

    Set tieBar = CreateObject("Tekla.Structures.Model.Beam")
    tieBar.StartPoint.X = xPos
    tieBar.StartPoint.Y = coordsY(0)
    tieBar.StartPoint.Z = zPos
    tieBar.EndPoint.X = xPos
    tieBar.EndPoint.Y = coordsY(FRAME_COUNT)
    tieBar.EndPoint.Z = zPos
    tieBar.Profile.ProfileString = TIE_BAR_PROFILE
    tieBar.Material.MaterialString = MATERIAL
    tieBar.Insert()
Next

'======================================================================
' 完成
'======================================================================
model.CommitChanges()

Dim colCount, beamCount, purlinCount
colCount = (FRAME_COUNT + 1) * 7
beamCount = (FRAME_COUNT + 1) * 6
purlinCount = 0
For i = 0 To 5
    purlinCount = purlinCount + Int(COLUMN_SPANS(i) / PURLIN_SPACING)
Next

MsgBox "天浩电器1#生产车间 一键深化完成！" & vbCrLf & vbCrLf & _
       "跨度方向：" & totalSpan & " mm（7柱6跨）" & vbCrLf & _
       "纵向榀数：" & (FRAME_COUNT + 1) & " 榀，间距 " & FRAME_SPACING & " mm" & vbCrLf & _
       "柱总数：" & colCount & " 根" & vbCrLf & _
       "梁总数：" & beamCount & " 根" & vbCrLf & _
       "檩条约：" & purlinCount & " 根" & vbCrLf & _
       "材质：" & MATERIAL & vbCrLf & vbCrLf & _
       "注意：变截面柱ProfileString需根据Tekla截面库调整，" & vbCrLf & _
       "纵向榀数和间距需根据结构平面图确认。", _
       vbInformation, "完成"

'======================================================================
' 【参数调整说明】
' 1. COLUMN_SPANS: 跨度方向柱距，从图纸刚架简图读取
' 2. COLUMN_HEIGHTS: 各柱顶标高，从刚架简图读取
' 3. COLUMN_TYPES: 1=变截面刚架柱, 0=等截面抗风柱
' 4. FRAME_COUNT / FRAME_SPACING: 纵向榀数和间距，需从结构平面布置图确认
' 5. 变截面柱格式：Tekla中变截面H型钢ProfileString为 "I(小头高-大头高)*翼缘宽*腹板厚*翼缘厚"
'    如小头在下端则 "I(300-500)*250*6*12"，大头在下端则 "I(500-300)*250*6*12"
'    需根据实际受力方向调整，或在Tekla中用变截面梁工具创建后复制ProfileString
' 6. 节点/连接：本宏只创建构件，节点需后续手动或用组件自动添加
' 7. 吊车梁、墙梁、拉条等可参照本宏格式追加
'======================================================================
