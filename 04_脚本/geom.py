# Nominal geometry for IDEA-05 smart pill box (mm)
W, D, H = 320.0, 70.0, 52.0
WALL = 2.0
CORNER_R = 8.0

BASE_H = 24.0          # base shell incl. battery/PCB/weighing/UI
TRAY_H = 18.0          # cartridge tray (3 floor + 15 cell depth)
CANOPY_H = 10.0        # transparent lid canopy
assert abs(BASE_H + TRAY_H + CANOPY_H - H) < 1e-6

# top opening / lid area
SIDE_MARGIN = 5.0      # left/right margin to lid area
FRONT_BEZEL = 6.0      # front top bezel (before lid area)
BACK_BEZEL = 2.0
LID_AREA_W = W - 2*SIDE_MARGIN          # 310
LID_AREA_D = D - FRONT_BEZEL - BACK_BEZEL  # 62
LID_GAP = 1.0
LID_W = (LID_AREA_W - 6*LID_GAP)/7      # 7 lids
LID_D = LID_AREA_D

# cells 7 x 3
COL_PITCH = LID_W
ROW_GAP = 1.0
DIV = 1.5
ROW_PITCH = (LID_AREA_D - 4.0 - 2*DIV)/3   # inner top plate margins 2 each side
CELL_W = COL_PITCH - DIV
CELL_D = ROW_PITCH - DIV
CELL_DEPTH = 15.0

# UI strip on front face
BAND_H = BASE_H
BTN_D = 20.0
EPD_W, EPD_H = 32.0, 22.0

if __name__ == '__main__':
    print(f'outline {W}x{D}x{H}')
    print(f'lid area {LID_AREA_W}x{LID_AREA_D}, lid {LID_W:.2f}x{LID_D:.2f}')
    print(f'row pitch {ROW_PITCH:.2f}, cell {CELL_W:.2f}x{CELL_D:.2f}x{CELL_DEPTH}, vol {CELL_W*CELL_D*CELL_DEPTH/1000:.1f} ml')
