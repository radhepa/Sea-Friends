"""The Sea Friends job-site blocks and the tide lamp: hand-painted textures plus cuboid models.

Each design function returns a Block: its textures (key -> 16x16 image, written as
textures/block/<name>_<key>.png) and its pixel.Model. Models face north (the front is the north side;
standing in front, east is on your left). Vanilla textures are referenced by id ('mc:...'), never copied.
One texel is always 1/16 block. All of them stand in water, so colours are chosen to survive a blue tint:
pale calcite and sandstone, warm coral and gold, and glowing parts lit with light_emission.
"""
import math
import random

from PIL import Image

import pixel
from pixel import RAMPS as R, raster, stamp
from seakit import NS, pal, blank, put, noise, uv_all, face_sizes


class Block:
    def __init__(self, name, facing=True, light=0, about=''):
        self.name, self.facing, self.light, self.about = name, facing, light, about
        self.model = pixel.Model(NS, name + '_')
        self.textures = {}
        self.particle = None

    def tex(self, key, image):
        self.textures[key] = image
        return image


def sub(region, dx=0, dy=0, w=None, h=None):
    """A rectangle inside an atlas region [u1, v1, u2, v2]: offset (dx, dy), size (w, h) texels."""
    u1, v1, u2, v2 = region
    w = u2 - u1 if w is None else w
    h = v2 - v1 if h is None else h
    return [u1 + dx, v1 + dy, u1 + dx + w, v1 + dy + h]


def sides(region, faces=('north', 'south', 'east', 'west')):
    return {f: list(region) for f in faces}


def extrude(m, tex, image, region, x0, y0, z0, depth, back=None, light=0):
    """Extrudes a sprite (like vanilla's generated item models): one box per opaque run of each row.
    region = (u, v, w, h) in `image` (the texture `tex`); column 0 lands at the high-x end, so it is on
    the left of someone standing in front (north). `back` names a texture with the same layout for the
    south face. Tops and ends sample the run's own texels, stretched through the depth."""
    u, v, w, h = region
    for r in range(h):
        c = 0
        while c < w:
            if image.getpixel((u + c, v + r))[3] == 0:
                c += 1
                continue
            c1 = c
            while c < w and image.getpixel((u + c, v + r))[3]:
                c += 1
            c2 = c
            frm = [x0 + w - c2, y0 + h - r - 1, z0]
            to = [x0 + w - c1, y0 + h - r, z0 + depth]
            row = [u + c1, v + r, u + c2, v + r + 1]
            flip = [u + c2, v + r, u + c1, v + r + 1]
            faces = {'north': row, 'south': flip, 'up': flip, 'down': flip,
                     'east': [u + c1, v + r, u + c1 + 1, v + r + 1], 'west': [u + c2 - 1, v + r, u + c2, v + r + 1]}
            m.box(frm, to, {'south': back or tex, '*': tex}, uv=faces, light=light)


# ====================================================================================================
# Pearl basin (merfolk Pearl Diver)
# ====================================================================================================

BASIN = pal('q=calcite.0 r=calcite.1 s=calcite.2 t=calcite.3 u=calcite.4 v=calcite.5 '
            '1=sand.0 2=sand.1 3=sand.2 4=sand.3 5=sand.4 6=sand.5 7=sand.6 8=sand.7 '
            'n=nautilus.3 N=nautilus.2 W=pearl.7')

# Rows map to heights (auto UVs): 0-1 the bowl's inner wall (used with explicit UVs), 5 the rim lip,
# 6 a band of inlaid pearls, 7 the bowl's belly, 8 the bowl's foot, 9 the collar, 10-13 the fluted stem, 14-15 the plinth.
BASIN_SIDE = """
uttuttttuttttutt
srssrsssrssrsssr
ssssssssssssssss
ssssssssssssssss
ssssssssssssssss
vuvuuvuvuuvuuvuv
55W655W655W655W6
ttsttttsttsttttt
rrqrrrqrrrrqrrqr
4245424542454245
tttttttttttttttt
usqusqusqusqusqu
usqusqusqusqusqu
rqrrqrrqrrqrrqrr
7767n6777n67767n
3232232n32232232
"""

# Pieces used with explicit UVs.
BASIN_PARTS = """
..oRRo....oRRo..
.oRpPRo..oRPPRo.
oRpwWPRooRPwWPRo
RpPwwPcRRpPwwPcR
RpcPwPpRRpcPwPpR
oRcpPcRooRpcPpRo
.oRccRo..oRppRo.
..oRRo....oRRo..
..oRRo..oRRRRRRo
.oRbRbo..obbbbo.
oRbRSbRoPwW.uttu
RbRSRbRRpPw.tqqt
RSbRbRSRcpP.tqrt
oRbRSbRo....uttu
.oRbRRo.....tuut
..oRRo..........
"""
BASIN_PART_PAL = {**BASIN, **pal('o=nautilus.1 R=nautilus.4 b=nautilus.2 S=nautilus.5 '
                                 'p=pearl.2 P=pearl.4 w=pearl.6 W=pearl.7 c=crystal.2')}
BASIN_UV = {'oyster_in': [0, 0, 8, 8], 'lid_in': [8, 0, 16, 8], 'lid_out': [0, 8, 8, 16], 'edge': [8, 8, 16, 10],
            'pearl': [8, 10, 11, 13], 'dish_top': [12, 10, 16, 14], 'dish_side': [12, 14, 16, 15]}


def basin_top():
    """Rim ring (index 1 and 14) of polished calcite around a floor of washed sand, ripples and loose pearls."""
    image = noise((0, 0, 16, 16), [BASIN['5'], BASIN['6'], BASIN['4']], [5, 3, 2], seed=11)
    for y in range(2, 14):
        for x in range(2, 14):
            if (y + (x // 4)) % 3 == 0:
                put(image, x, y, BASIN['3'])
    for i in range(16):
        for x, y in ((i, 0), (0, i), (i, 15), (15, i)):
            put(image, x, y, BASIN['s'])
    for i in range(1, 15):
        tone = BASIN['v'] if i % 3 == 0 else BASIN['u']
        for x, y in ((i, 1), (1, i)):
            put(image, x, y, tone)
        for x, y in ((i, 14), (14, i)):
            put(image, x, y, BASIN['t'] if i % 3 else BASIN['u'])
    for x, y in ((3, 2), (12, 3), (2, 12), (13, 13), (7, 13)):  # loose pearls in the sand
        put(image, x, y, R['pearl'][7])
        put(image, x + 1, y, R['pearl'][3])
    for x, y in ((11, 12), (4, 3)):  # a pink shell bit
        put(image, x, y, R['nautilus'][9])
    return image


def pearl_basin():
    b = Block('pearl_basin', light=6, about='glowing pearl (element light 15)')
    b.tex('side', raster(BASIN_SIDE, BASIN))
    b.tex('top', basin_top())
    b.tex('parts', raster(BASIN_PARTS, BASIN_PART_PAL))
    m, P = b.model, BASIN_UV
    # Plinth, fluted stem, collar.
    m.box([2, 0, 2], [14, 2, 14], {'up': 'mc:sandstone_top', 'down': 'mc:sandstone_bottom', '*': 'side'})
    m.box([5, 2, 5], [11, 6, 11], 'side', skip=('up', 'down'))
    m.box([4, 6, 4], [12, 7, 12], {'down': 'mc:sandstone_bottom', '*': 'side'}, skip=('up',))
    # The bowl: a narrower foot, then a floor and four walls with a polished rim.
    m.box([2, 7, 2], [14, 8, 14], {'down': 'mc:calcite', '*': 'side'}, skip=('up',))
    m.box([1, 8, 1], [15, 9, 15], {'up': 'top', 'down': 'mc:calcite', '*': 'side'})
    wall = {'up': 'top', '*': 'side'}
    m.box([1, 9, 1], [15, 11, 2], wall, uv={'south': [1, 0, 15, 2]}, skip=('down',))
    m.box([1, 9, 14], [15, 11, 15], wall, uv={'north': [1, 0, 15, 2]}, skip=('down',))
    m.box([1, 9, 2], [2, 11, 14], wall, uv={'east': [2, 0, 14, 2]}, only=('west', 'east', 'up'))
    m.box([14, 9, 2], [15, 11, 14], wall, uv={'west': [2, 0, 14, 2]}, only=('west', 'east', 'up'))
    # An open oyster in the middle: nacre inside, rough brown shell outside, the lid hinged at the back.
    m.box([4, 9, 4], [12, 10.5, 12], 'parts', uv={'up': P['oyster_in'], **sides(sub(P['edge'], h=1.5))}, skip=('down',))
    lid = ('x', 60, [8, 10.5, 12])
    m.box([4, 10.5, 4], [12, 11.5, 12], 'parts', rot=lid, uv={'up': P['lid_out'], **sides(sub(P['edge'], h=1))}, skip=('south', 'down'))
    m.box([4, 10.5, 4], [12, 11.5, 12], 'parts', rot=lid, uv={'down': P['lid_in']}, only=('down',), shade='north')
    # The pearl glows.
    m.box([6.5, 10.5, 5.5], [9.5, 13.5, 8.5], 'parts', uv={f: P['pearl'] for f in pixel.FACES}, skip=('down',),
          light=15, shade=False)
    # A little calcite dish of pearls on the rim, front right.
    m.box([1.5, 11, 1.5], [5.5, 12, 5.5], 'parts', uv={'up': P['dish_top'], 'down': P['dish_top'], **sides(P['dish_side'])})
    for frm in ([2, 12, 2], [3.75, 12, 2.25], [2.75, 12, 3.75]):
        to = [frm[0] + 1.5, frm[1] + 1.5, frm[2] + 1.5]
        m.box(frm, to, 'parts', uv={f: sub(P['pearl'], w=1.5, h=1.5) for f in pixel.FACES}, skip=('down',))
    b.particle = 'side'
    return b



# ====================================================================================================
# Kelp rack (merfolk Kelp Farmer)
# ====================================================================================================

DRIFT = pal('1=driftwood.0 2=driftwood.1 3=driftwood.2 4=driftwood.3 5=driftwood.4 6=driftwood.5 7=driftwood.6')


def driftwood():
    """Bleached, sea-worn wood with vertical grain: any two columns make a pole. A few dark cracks and knots."""
    tones = [DRIFT[c] for c in '6566756676565667']
    image = blank()
    rng = random.Random(4)
    for x in range(16):
        for y in range(16):
            tone = tones[x]
            roll = rng.random()
            if roll < .1:
                tone = DRIFT['5']
            elif roll < .16:
                tone = DRIFT['4']
            put(image, x, y, tone)
    for x, y0, n in ((1, 2, 4), (6, 9, 5), (10, 1, 3), (13, 7, 6), (3, 11, 3), (8, 4, 2)):  # cracks
        for y in range(y0, y0 + n):
            put(image, x, y, DRIFT['4'] if y in (y0, y0 + n - 1) else DRIFT['3'])
    for x, y in ((4, 5), (11, 12), (14, 2)):  # knots
        put(image, x, y, DRIFT['3'])
        put(image, x + 1, y, DRIFT['4'])
        put(image, x, y + 1, DRIFT['4'])
    return image


KELP = pal('g=kelp.0 h=kelp.2 i=kelp.3 j=kelp.5 k=kelp.6 '
           'd=dried_kelp.3 e=dried_kelp.6 f=dried_kelp.7 m=pickle.3 n=pickle.2 o=pickle.5')
STRAND = {  # kind -> (light edge, body, shadow, leaf)
    'fresh': ('k', 'j', 'h', 'k'),
    'wilting': ('o', 'i', 'g', 'o'),
    'drying': ('m', 'n', 'f', 'm'),
    'dry': ('f', 'e', 'd', 'f'),
}


def strands(spec):
    """Kelp blades hanging from row 0: spec = [(column, length, kind, phase)]. Two texels wide, lit on the
    left, swaying a texel side to side, a leaf every third row on alternating sides, the tip one texel."""
    image = blank()
    sway = (0, 0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1)
    for col, length, kind, phase in spec:
        light, body, dark, leaf = (KELP[c] for c in STRAND[kind])
        for y in range(length):
            x = col + (sway[(y + phase * 3) % len(sway)] if y > 2 else 0)
            tip = y == length - 1
            put(image, x, y, light if not tip else body)
            if not tip:
                put(image, x + 1, y, body if (y + phase) % 4 else dark)
            if y > 2 and (y + phase) % 3 == 0 and y < length - 2:
                side = x - 1 if (y + phase) % 6 == 0 else x + 2
                put(image, side, y, leaf)
                put(image, side, y + 1, dark)
    return image


FRONT_STRANDS = [(3, 13, 'fresh', 0), (7, 10, 'drying', 1), (11, 12, 'wilting', 2)]
BACK_STRANDS = [(5, 11, 'dry', 1), (9, 13, 'fresh', 2), (13, 9, 'drying', 0)]


def plane(m, x1, x2, y1, y2, z, tex, u1, v1):
    """A two-sided vertical sheet across x at depth z, the same picture seen from both sides."""
    u2, v2 = u1 + (x2 - x1), v1 + (y2 - y1)
    m.box([x1, y1, z], [x2, y2, z], tex, uv={'north': [u1, v1, u2, v2], 'south': [u2, v1, u1, v2]}, only=('north', 'south'))


def kelp_rack():
    b = Block('kelp_rack')
    wood = b.tex('pole', driftwood())
    b.tex('pole_h', wood.transpose(Image.ROTATE_90))
    b.tex('strands', strands(FRONT_STRANDS))
    b.tex('strands_back', strands(BACK_STRANDS))
    m = b.model
    # Two A-frames of driftwood poles, legs splayed front and back, lashed at the top.
    for x in (1, 13):
        for angle in (22.5, -22.5):
            m.box([x, -1, 7], [x + 2, 15, 9], {'*': 'pole', 'up': 'mc:stripped_pale_oak_log_top', 'down': 'mc:stripped_pale_oak_log_top'},
                  rot=('x', angle, [x + 1, 14, 8]), skip=('down',))
    # The drying pole across the apexes, and a low back rail.
    m.box([0.5, 13, 7], [15.5, 15, 9], {'*': 'pole_h', 'east': 'mc:stripped_pale_oak_log_top', 'west': 'mc:stripped_pale_oak_log_top'},
          uv={'east': [6, 6, 8, 8], 'west': [6, 6, 8, 8]})
    m.box([1, 4, 11.25], [15, 5, 12.25], {'*': 'pole_h', 'east': 'pole', 'west': 'pole'})
    # Lashing where the pole meets each frame.
    for x in (1.5, 13.5):
        m.box([x, 12.75, 6.75], [x + 1, 15.25, 9.25], 'mc:dried_kelp_side', uv={f: [7.5, 4, 8.5, 6.5] for f in pixel.FACES})
    # Kelp hung over the pole to dry: a sheet of strands in front, another behind, their tops over the pole.
    plane(m, 2, 14, 2, 15.25, 6.6, 'strands', 2, 0)
    plane(m, 2, 14, 4, 15.25, 9.4, 'strands_back', 2, 0)
    for col, _, kind, _ in FRONT_STRANDS:
        x = 14 - col
        m.box([x, 15, 6.6], [x + 2, 15.25, 9.4], 'strands', uv={"up": [col + 2, 0, col, 2]}, only=('up',))
    # A bundle of dried kelp, tied, lying in front.
    m.box([4, 0, 1], [11, 3, 4], {'*': 'mc:dried_kelp_side', 'east': 'mc:dried_kelp_top', 'west': 'mc:dried_kelp_top'},
          uv={'north': [4, 5, 11, 8], 'south': [4, 5, 11, 8], 'up': [4, 0, 11, 3], 'east': [6, 6, 9, 9], 'west': [6, 6, 9, 9]}, skip=('down',))
    b.particle = 'pole'
    return b



# ====================================================================================================
# Shell bench (merfolk Shellwright)
# ====================================================================================================

SHELL = pal('a=brain.0 b=brain.1 c=brain.2 d=brain.3 e=brain.4 f=brain.5 g=brain.6 '
            'q=calcite.0 r=calcite.1 s=calcite.2 t=calcite.3 u=calcite.4 v=calcite.5 '
            '0=bone.0 1=bone.1 2=bone.2 3=bone.3 4=bone.4 5=bone.5 6=bone.6 '
            'k=nautilus.9 K=nautilus.8 M=nautilus.7 n=nautilus.5 N=nautilus.4 o=nautilus.1 '
            'F=fire.2 G=fire.4 H=horn.1 I=horn.4 T=tube.1 U=tube.4 B=bubble.2 C=bubble.5 x=fire.0 y=horn.0 z=tube.0 w=bubble.0')

# The coral slab: polished pink coral with pale pores; a darker rim at the edge. Shell dust round the
# carving (rows 6-10, the middle) and a scatter of pink chips.
SHELL_TOP = """
bbbbbbbbbbbbbbbb
bfeeefedeefeeedb
bededdeeffdeedeb
beefdedfeedefeeb
bdeeedeedeedfedb
befdeedeefedeefb
bedeeuetsvdedfeb
bdeefsuvtsufeeeb
beedeettseedeedb
bdefeeduedeedfeb
beeddeesededfeeb
bdfeedeefeedeefb
beedekeedeedkedb
befeedeedfeeeeeb
bdeeefedeeedeedb
bbbbbbbbbbbbbbbb
"""
# Rows 6-7 are the slab's edge (auto UVs for y 8..10); the rest only repeats it.
SHELL_SIDE = """
ffgfffgffffgffgf
ddeddcdddedddcdd
ffgfffgffffgffgf
ddeddcdddedddcdd
ffgfffgffffgffgf
ddeddcdddedddcdd
fgffgfffgfffgfff
ccdcdccbcdcdccbc
ddeddcdddedddcdd
ffgfffgffffgffgf
ddeddcdddedddcdd
ffgfffgffffgffgf
ddeddcdddedddcdd
ffgfffgffffgffgf
ddeddcdddedddcdd
ffgfffgffffgffgf
"""
SHELL_BONE = """
4556545565455654
3455434554345543
4565453565455653
2455434554245543
4556545565455654
3454434554345543
4565453565455653
2455434454245543
4556545565455654
3455434554345543
4565453565455653
2455434554245543
4556545565455654
3454434554345543
4565453565455653
2455434554245543
"""
# Parts: the half-carved scallop (front 0,0 8x8: a ribbed fan on the left, the uncut calcite block on the
# right with chisel marks), its back (8,0, laid out to line up), four coral sprigs 4x5 (fire, horn, tube,
# bubble) at y 8, two loose shells 4x3 at y 13.
SHELL_PARTS = """
................
................
................
................
................
................
................
................
G.G...I..U...C.C
GxG.I.I.U.U..CwC
.G..IyI..UzU.C..
.Gx..I..zU...wC.
.x...y...z....w.
.kk..kkk........
knkn.knk........
.oo..oo.........
"""
# A scallop 9 wide, 9 tall: the fan (rows 0-6) and the ears at the hinge (rows 7-8).
SCALLOP = """
...XXX...
.XXXXXXX.
XXXXXXXXX
XXXXXXXXX
XXXXXXXXX
.XXXXXXX.
..XXXXX..
.XXXXXXX.
..XXXXX..
"""


def scallop(back=False):
    """The half-carved scallop, 9x9 at (0, 0): ribs radiating from the hinge. The left half is finished
    (pink and cream ribs, from behind: brown growth rings); the right half is still plain calcite with
    pencilled ribs and chisel gouges. Placed so that the back lines up with the front when mirrored."""
    image = blank()
    shape = [r for r in SCALLOP.strip().splitlines()]
    inside = lambda x, y: 0 <= y < 9 and 0 <= x < 9 and shape[y][x] == 'X'
    for y in range(9):
        for x in range(9):
            if not inside(x, y):
                continue
            edge = not all(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            rib = int((math.degrees(math.atan2(x - 4, 7.5 - y)) + 90) // 20) % 2
            finished = (x < 4) != back
            if y >= 7:  # ears
                tone = (SHELL['N'] if finished else SHELL['r']) if edge else (SHELL['n'] if finished else SHELL['t'])
            elif finished and not back:
                tone = SHELL['M'] if edge else (SHELL['K'] if rib else SHELL['k'])
            elif finished:
                tone = SHELL['o'] if edge else (SHELL['N'] if (y + rib) % 3 else SHELL['K'])
            else:
                tone = SHELL['q'] if edge else (SHELL['u'] if rib else SHELL['s'])
            put(image, 8 - x if back else x, y, tone)
    if not back:
        for x, y in ((6, 2), (7, 3), (5, 4)):  # chisel gouges
            put(image, x, y, SHELL['r'])
        put(image, 4, 1, SHELL['v'])
    return image


def coral_sprig(m, x, y, z, region, h=5):
    """A little branch of coral: two crossed two-sided sheets, 4 wide, sampling a 4 x h sprite."""
    u1, v1, u2, v2 = region
    for angle in (45, -45):
        m.box([x - 2, y, z], [x + 2, y + h, z], 'parts', rot=('y', angle, [x, y, z]),
              uv={'north': [u1, v1, u2, v2], 'south': [u2, v1, u1, v2]}, only=('north', 'south'))


SPRIG = {'fire': [0, 8, 4, 13], 'horn': [4, 8, 8, 13], 'tube': [8, 8, 12, 13], 'bubble': [12, 8, 16, 13]}


def shell_bench():
    b = Block('shell_bench')
    b.tex('top', raster(SHELL_TOP, SHELL))
    b.tex('side', raster(SHELL_SIDE, SHELL))
    b.tex('bone', raster(SHELL_BONE, SHELL))
    b.tex('parts', raster(SHELL_PARTS, SHELL))
    b.tex('scallop', scallop())
    b.tex('scallop_back', scallop(back=True))
    m = b.model
    # The coral slab top, on four bone legs with knobbly ends; a calcite shelf below.
    m.box([0, 8, 1], [16, 10, 15], {'up': 'top', 'down': 'mc:brain_coral_block', '*': 'side'})
    for x in (1, 13):
        for z in (2, 12):
            m.box([x, 1, z], [x + 2, 7, z + 2], 'bone', skip=('up', 'down'))
            m.box([x - .5, 0, z - .5], [x + 2.5, 1.5, z + 2.5], 'bone', skip=('down',))
            m.box([x - .5, 6.5, z - .5], [x + 2.5, 8, z + 2.5], 'bone', skip=('up',))
    m.box([1.5, 2.5, 3.5], [14.5, 3.5, 12.5], 'mc:calcite')
    # On the shelf: coral stock and a raw shell.
    coral_sprig(m, 5, 3.5, 8, SPRIG['fire'])
    coral_sprig(m, 8, 3.5, 9.5, SPRIG['tube'])
    coral_sprig(m, 11, 3.5, 7.5, SPRIG['bubble'])
    m.box([2.5, 3.5, 5], [6.5, 4, 8], 'parts', uv={'up': [0, 13, 4, 16], **sides([0, 13, 4, 13.5])}, skip=('down',))
    # On top: the half-carved scallop held upright between two bone blocks.
    m.box([3.5, 10, 9], [12.5, 19, 10], {'north': 'scallop', 'south': 'scallop_back', '*': 'scallop'},
          uv={'north': [0, 0, 9, 9], 'south': [9, 0, 0, 9], 'west': [8, 0, 9, 9], 'east': [0, 0, 1, 9], 'up': [0, 0, 9, 1]},
          skip=('down',))
    m.box([2, 10, 8.5], [3.5, 12.5, 10.5], 'bone', skip=('down',))
    m.box([12.5, 10, 8.5], [14, 12.5, 10.5], 'bone', skip=('down',))
    # A small hammer: bone handle, prismarine head. A finished scallop beside it.
    m.box([8, 10, 3], [13, 10.75, 3.75], 'bone', skip=('down',))
    m.box([12.75, 10, 1.75], [14.25, 11.5, 5], 'mc:prismarine', skip=('down',))
    m.box([9, 10, 5.5], [13, 10.5, 8.5], 'parts', uv={'up': [4, 13, 8, 16], **sides([4, 13, 8, 13.5])}, skip=('down',))
    # Loose coral pieces, front right.
    coral_sprig(m, 3.5, 10, 4, SPRIG['horn'], h=4)
    coral_sprig(m, 6, 10, 3, SPRIG['fire'], h=4)
    b.particle = 'side'
    return b



# ====================================================================================================
# Conch shrine (merfolk Tide Singer)
# ====================================================================================================

ALTAR = pal('q=calcite.0 r=calcite.1 s=calcite.2 t=calcite.3 u=calcite.4 v=calcite.5 '
            'a=brain.0 b=brain.1 c=brain.2 d=brain.3 e=brain.4 f=brain.5 g=brain.6 '
            'h=horn.2 i=horn.4 j=horn.5 x=fire.3')

# Rows map to heights: 5 the coral slab's edge (y 10-11), 6 a coral band, 7-12 calcite blocks,
# 13 the shadow line, 14-15 the base step. The front repeats it with a square spiral of inlaid coral
# (the old wave-key of the Tide Singers) and two horn-coral studs.
ALTAR_SIDE = """
cdccdcccdccdcccd
cdccdcccdccdcccd
cdccdcccdccdcccd
cdccdcccdccdcccd
cdccdcccdccdcccd
ddeddedddeddedde
ccbccbccbccbccbc
uvuuutuuuvuuuuvu
uuutuuuvuuutuuuu
tuuuuvuuuuuuuvut
uvuutuuuutuuuuuu
uuuuuuvuutuuvuuu
utuvuuuuuuuutuuu
rrqrrrrqrrrrqrrr
vuvuuvuuuvuuvuuv
srsssrssrssssrss
"""
ALTAR_FRONT = """
cdccdcccdccdcccd
cdccdcccdccdcccd
cdccdcccdccdcccd
cdccdcccdccdcccd
cdccdcccdccdcccd
ddeddedddeddedde
ccbccbccbccbccbc
uujuuuuuuuuujuuu
uuhueeeeeeeuhuuu
uuuuevuuuueuuuuu
uutuevdddeeuutuu
uuuuevduuuuuuuuu
uuuuedddddduuuuu
rrqrrrrqrrrrqrrr
vuvuuvuuuvuuvuuv
srsssrssrssssrss
"""


def altar_top():
    """The coral slab's top: a pink coral border round a calcite field worn smooth."""
    image = noise((0, 0, 16, 16), [ALTAR['u'], ALTAR['t'], ALTAR['v']], [6, 2, 2], seed=7)
    for x in range(1, 15):
        for y in range(3, 14):
            if x in (1, 14) or y in (3, 13):
                put(image, x, y, ALTAR['d'] if (x + y) % 3 else ALTAR['e'])
            elif x in (2, 13) or y in (4, 12):
                put(image, x, y, ALTAR['c'])
    return image


CONCH = pal('n=nautilus.5 N=nautilus.4 m=nautilus.3 b=nautilus.2 o=calcite.5 '
            'k=nautilus.9 K=nautilus.8 x=nautilus.7 p=brain.6 w=pearl.6 W=pearl.7')
# The great conch seen from its aperture side, 14 x 9: the spire's point on the left, knobs along the
# shoulder, the glossy pink aperture and its flared lip rising on the right, the siphon canal below.
CONCH_FRONT = """
.........KK...
.....o.o.KkK..
...nonnnnKkkx.
.nnmnnnnKkpwkx
nmnnmnnmKkWwkx
.nnmnnnnKkpkx.
...nnmnnnKkx..
.....mnnnxx...
.......nbb....
"""
# Its back: the same outline, all banded shell.
CONCH_BACK = """
.........NN...
.....o.o.NnN..
...nonnnnnnNb.
.nnmnnnmnnmnnb
nmnnmnnmnnnmnb
.nnmnnnnmnnnb.
...nnmnnnnmb..
.....mnnnbb...
.......nbb....
"""


PICKLE = pal('a=pickle.0 b=pickle.1 c=pickle.2 d=pickle.3 e=pickle.4 f=pickle.5 g=pickle.6 h=pickle.7 i=pickle.8')
# A sea pickle's skin (any 2-wide strip), its top (12,0) and the glowing nubs (12,4).
PICKLE_TEX = """
edfedcfedfedghhg
dcedfedcedcehiih
fedcedfedfedhiih
edfedcedfedcghhg
dcedfedcedcehi..
fedcedfedfedih..
edfedcfedfed....
dcedfedcedce....
fedcedfedfed....
cbccbcbccbcb....
................
................
................
................
................
................
"""


def pickle_candle(m, x, z, h, y=0):
    """A sea pickle standing as a candle: a 2x2 olive body h tall with a glowing nub on top."""
    m.box([x, y, z], [x + 2, y + h, z + 2], 'pickle', uv={**sides([0, 0, 2, h]), 'up': [12, 0, 14, 2], 'down': [0, 9, 2, 10]},
          skip=('down',) if y == 0 else ())
    m.box([x + .5, y + h, z + .5], [x + 1.5, y + h + 1, z + 1.5], 'pickle', uv={f: [12, 4, 13, 5] for f in pixel.FACES},
          skip=('down',), light=15, shade=False)


def conch_shrine():
    b = Block('conch_shrine', light=8, about='sea pickle candles (element light 15)')
    b.tex('side', raster(ALTAR_SIDE, ALTAR))
    b.tex('front', raster(ALTAR_FRONT, ALTAR))
    b.tex('top', altar_top())
    b.tex('pickle', raster(PICKLE_TEX, PICKLE))
    m = b.model
    # The altar: a calcite base step, a calcite body with a coral band, a coral-rimmed slab on top.
    m.box([1, 0, 1], [15, 2, 14], {'up': 'mc:calcite', 'down': 'mc:calcite', 'north': 'front', '*': 'side'})
    m.box([2, 2, 4], [14, 10, 13], {'north': 'front', '*': 'side'}, skip=('up', 'down'))
    m.box([1, 10, 3], [15, 11, 14], {'up': 'top', 'down': 'mc:calcite', '*': 'side'})
    # The great conch, lying along the slab with its aperture and flared pink lip turned to the front.
    front = b.tex('conch', stamp(blank(), CONCH_FRONT, CONCH, 0, 0))
    b.tex('conch_back', stamp(blank(), CONCH_BACK, CONCH, 0, 0))
    extrude(m, 'conch', front, (0, 0, 14, 9), 1, 11, 6, 4, back='conch_back')
    # Sea pickle candles: a pair on the front step, one on its other side, two behind the conch.
    pickle_candle(m, 11.5, 1.5, 3, y=2)
    pickle_candle(m, 13, 2.5, 2, y=2)
    pickle_candle(m, 2, 1.5, 3, y=2)
    pickle_candle(m, 2, 11.5, 3, y=11)
    pickle_candle(m, 12, 11, 4, y=11)
    b.particle = 'side'
    return b



# ====================================================================================================
# Prism lathe (Prismari Lightwright)
# ====================================================================================================

PRISM = pal('0=dark_prism.0 1=dark_prism.1 2=dark_prism.2 3=dark_prism.3 4=dark_prism.4 5=dark_prism.5 '
            'a=prismarine.0 b=prismarine.1 c=prismarine.2 d=prismarine.3 e=prismarine.4 '
            'g=gold.0 h=gold.1 i=gold.2 j=gold.3 k=gold.4 l=gold.5 '
            'L=lantern.0 M=lantern.2 N=lantern.4 O=lantern.5 P=lantern.6 Q=lantern.7 '
            'v=crystal.0 w=crystal.1 x=crystal.2 y=crystal.3 z=crystal.4')

# The base's front (rows 11-14, y 1-5): dark prismarine plates with the Prismari eye: a pale prismarine
# rim, a gold iris and a dark pupil. Above it (rows 0-10) the same plating, for the arms.
LATHE_FRONT = """
3423342334233423
2112211221122112
4234423442344234
1221122112211221
3423342334233423
2112211221122112
4234423442344234
1221122112211221
3423342334233423
2112211221122112
jhjjhjjhjjhjjhjj
2112ddeeeedd2112
421dehj00jhed234
321dehjl0jhed122
1221ddeeeedd1221
0000000000000000
"""
# Plating for the arms and base sides: dark prismarine tiles with a lit bevel every fourth texel.
LATHE_SIDE = """
5444544454445444
4223422342234223
4321432143214321
4211421142114211
5444544454445444
4223422342234223
4321432143214321
4211421142114211
5444544454445444
4223422342234223
jhjjhjjhjjhjjhjj
4223422342234223
4321432143214321
4211421142114211
5444544454445444
1000100010001000
"""
# The spinning crystal's facets (rows 0-2 the brightest, 9-11 middling, 12-14 in shadow; any 5x3 of a
# band dresses one long face) and the core's sea-lantern glow (rows 4-8).
LATHE_GLOW = """
zzzzzyzzzzzzyzzz
zyzzzzzyzzzzzzyz
yzzyzzzzzyzzyzzy
................
LMMMLLMMMLLMMMLL
MPQPMMPQPMMPQPMM
MQQQMMQQQMMQQQMM
MPQPMMPQPMMPQPMM
LMMMLLMMMLLMMMLL
yyxyyyyxyyyxyyyy
yxyyyxyyyyxyyyxy
xyyxyyyyxyyxyyyx
xwxxwxxxwxxwxxxw
wxxxxwxxwxxxwxxx
vwxwwxwvwxwwxwvw
................
"""
FACET = {'north': 0, 'up': 0, 'down': 9, 'south': 12, 'east': 9, 'west': 9}


def facets(frm, to, u):
    """UVs giving each long face of the turned crystal its own brightness."""
    return {f: [u, FACET[f], u + w, FACET[f] + h] for f, (w, h) in face_sizes(frm, to).items()}


def prism_lathe():
    b = Block('prism_lathe', light=10, about='sea-lantern core (element light 15) and crystal (12)')
    b.tex('front', raster(LATHE_FRONT, PRISM))
    b.tex('side', raster(LATHE_SIDE, PRISM))
    b.tex('glow', raster(LATHE_GLOW, PRISM))
    m = b.model
    # An angular base: a dark prismarine foot, the body with the eye on its front, a gold lip.
    m.box([1, 0, 2], [15, 1, 14], {'up': 'mc:dark_prismarine', 'down': 'mc:dark_prismarine', '*': 'side'})
    m.box([2, 1, 3], [14, 5, 13], {'north': 'front', 'up': 'mc:dark_prismarine', '*': 'side'}, skip=('down',))
    m.box([3, 5, 4], [13, 5.75, 12], {'up': 'mc:dark_prismarine', '*': 'mc:gold_block'}, skip=('down',))
    # The core: a sea-lantern heart in a cradle of four dark posts, glowing up into the crystal.
    m.box([5.5, 5.75, 5.5], [10.5, 8.5, 10.5], 'glow', uv=uv_all([5.5, 5.75, 5.5], [10.5, 8.5, 10.5], 5, 4), skip=('down',),
          light=15, shade=False)
    for x in (4.75, 10.25):
        for z in (4.75, 10.25):
            m.box([x, 5.75, z], [x + 1, 9, z + 1], 'side', uv=uv_all([x, 5.75, z], [x + 1, 9, z + 1], 0, 0), skip=('down',))
    # Two angular arms, each topped by a spine, gold-banded, holding the crystal on gold spindles.
    for x0, sign in ((2, 1), (11, -1)):
        m.box([x0, 5, 5], [x0 + 3, 9, 11], 'side', skip=('down',))
        m.box([x0 + .5, 9, 6], [x0 + 2.5, 14, 10], 'side', skip=('down',))
        m.box([x0 + .25, 10, 5.75], [x0 + 2.75, 10.75, 10.25], 'mc:gold_block', skip=('down',))
        m.box([x0 + 1, 14, 7.5], [x0 + 2, 16.5, 8.5], 'mc:prismarine', skip=('down',))
        m.box([x0 + 1, 14, 6], [x0 + 2, 15, 7], 'mc:prismarine', skip=('down',))
        m.box([x0 + 1, 14, 9], [x0 + 2, 15, 10], 'mc:prismarine', skip=('down',))
        sx = x0 + 2.5 if sign > 0 else x0 - .25
        m.box([sx, 10.5, 7.5], [sx + .75, 11.5, 8.5], 'mc:gold_block')
    # The crystal: a square bar turned 45 degrees about its long axis, bright and faceted.
    turn = ('x', 45, [8, 11, 8])
    m.box([5.5, 9.5, 6.5], [10.5, 12.5, 9.5], 'glow', rot=turn, uv=facets([5.5, 9.5, 6.5], [10.5, 12.5, 9.5], 3),
          light=12, shade=False)
    for x in (4.75, 10.5):  # its tapered points
        frm, to = [x, 10.25, 7.25], [x + .75, 11.75, 8.75]
        m.box(frm, to, 'glow', rot=turn, uv=facets(frm, to, 0), light=12, shade=False)
    b.particle = 'side'
    return b



# ====================================================================================================
# Sponge rack (Prismari Spongekeeper)
# ====================================================================================================

SPONGE = pal('a=sponge.0 b=sponge.1 c=sponge.2 d=sponge.3 e=sponge.4 '
             'A=pickle.1 B=pickle.4 C=pickle.5 D=wet_sponge.1 E=pickle.2 F=pickle.0')


def sponge(wet=False, seed=0):
    """A breath-stone: a sponge's yellow body pocked with holes (lit rim above each, shadow below).
    Wet, it is darker and olive, with water beading at the bottom."""
    body, mid, lit, hole, deep = (('C', 'B', 'D', 'E', 'A') if wet else ('d', 'c', 'e', 'a', 'b'))
    image = noise((0, 0, 16, 16), [SPONGE[body], SPONGE[mid]], [3, 2], seed=seed)
    rng = random.Random(seed + 1)
    for _ in range(26):
        x, y = rng.randrange(16), rng.randrange(16)
        put(image, x, y, SPONGE[hole])
        if rng.random() < .5:
            put(image, (x + 1) % 16, y, SPONGE[deep])
        put(image, x, (y - 1) % 16, SPONGE[lit])
    if wet:
        for x in (2, 7, 12):
            put(image, x, 15, SPONGE['F'])
    return image


RACK = pal('0=dark_prism.0 1=dark_prism.1 2=dark_prism.2 3=dark_prism.3 4=dark_prism.4 '
           'a=prism_brick.0 b=prism_brick.1 c=prism_brick.2 d=prism_brick.3 e=prism_brick.4 f=prism_brick.5 '
           'g=prism_brick.6 h=prism_brick.7 j=gold.1 k=gold.3 l=gold.5')
# The crown of the rack (rows 0-2 on its front, y 13-16): prismarine bricks with the Prismari eye.
RACK_CAP = """
hgghgghggghgghgg
fefc2000002cfeef
dcdc0jkllkj0cdcd
"""
# The side panels: prismarine bricks with a carved eye (dark outline, pale sclera, gold iris, dark pupil).
RACK_PANEL = """
hgggghhgggghgggh
gfeedgfeedgfeedf
gedccgedccgedcce
dccbadccbadccbab
hggggh0000gggggh
gfe000hhhh000edf
ge0hhhjkkjhhh0ce
d0hhhjkl00jhhh0b
h0hhhjk000jhhh0h
gf0hhhjkkjhhh0df
ged000hhhh000cce
dccbad0000ccbaab
hgggghhgggghgggh
gfeedgfeedgfeedf
gedccgedccgedcce
cbbaacbbaacbbaaa
"""


def sponge_rack():
    b = Block('sponge_rack')
    b.tex('panel', raster(RACK_PANEL, RACK))
    b.tex('cap', stamp(pixel.vanilla_texture('minecraft:block/prismarine_bricks').copy(), RACK_CAP, RACK, 0, 0))
    b.tex('sponge', sponge(seed=3))
    b.tex('sponge_wet', sponge(wet=True, seed=5))
    m = b.model
    # The frame: carved side panels, a prismarine back, dark prismarine shelves, a crowned top.
    m.box([0, 0, 2], [2, 13, 14], {'east': 'mc:prismarine_bricks', '*': 'panel'}, skip=('up',))
    m.box([14, 0, 2], [16, 13, 14], {'west': 'mc:prismarine_bricks', '*': 'panel'}, skip=('up',))
    m.box([2, 0, 12.5], [14, 13, 14], 'mc:prismarine', skip=('up', 'down'))
    for y in (0, 6):
        m.box([2, y, 2.5], [14, y + 1, 12.5], 'mc:dark_prismarine', skip=('down',) if y else ())
        m.box([2, y + .25, 2], [14, y + 1, 2.5], 'mc:gold_block', only=('north', 'up'))
    m.box([0, 13, 1.5], [16, 16, 14.5], {'up': 'mc:dark_prismarine', '*': 'cap'},
          uv={'east': [1.5, 0, 14.5, 3], 'west': [1.5, 0, 14.5, 3], 'north': [0, 0, 16, 3], 'south': [0, 0, 16, 3]})
    for x in (0.5, 7.5, 14.5):  # spines along the crown
        m.box([x, 16, 7.5], [x + 1, 17.5, 8.5], 'mc:prismarine', skip=('down',))
    # Breath-stones on the shelves: three dry, one wet and dark.
    def stone(frm, to, key, u, v):
        m.box(frm, to, key, uv=uv_all(frm, to, u, v), skip=('down',))
    stone([2.5, 1, 4], [7, 5, 8.5], 'sponge', 1, 2)
    stone([8, 1, 3.5], [13, 4.5, 8], 'sponge', 7, 9)
    stone([9.5, 4.5, 5], [12.5, 6, 7.5], 'sponge', 3, 11)
    stone([2.5, 7, 3.5], [7.5, 11.5, 8.5], 'sponge_wet', 2, 3)
    stone([8.5, 7, 4.5], [13, 10.5, 9], 'sponge', 10, 1)
    b.particle = 'panel'
    return b



# ====================================================================================================
# Tide lamp (light 15)
# ====================================================================================================

LAMP = pal('0=dark_prism.0 1=dark_prism.1 2=dark_prism.2 3=dark_prism.3 4=dark_prism.4 5=dark_prism.5 '
           'c=prism_brick.3 d=prism_brick.5 e=prism_brick.6 f=prism_brick.7 j=gold.1 k=gold.3 l=gold.5 '
           'G=glow.4 H=glow.5 I=glow.6 V=verdant.4 W=verdant.6')
# The cage (0,0) 9 x 9: prismarine posts and bands round tall windows, a gold rail. The glowing core's
# sides (0,9) 7 x 7 and its top (9,0) 5 x 5.
LAMP_TEX = """
fefeffefeIHIHI..
d..d.d..dHIWIH..
e..e.e..eIWWWI..
d..d.d..dHIWIH..
dkjdjdjkdIHIHI..
d..d.d..d.......
e..e.e..e.......
d..d.d..d.......
cdcccccdc.......
GHIHGHI.........
HIVIHIV.........
IVWVIVW.........
IWWWIWW.........
IVWVIVW.........
HIVIHIV.........
GHIHGHI.........
"""


def tide_lamp():
    b = Block('tide_lamp', facing=False, light=15, about='the core (element light 15)')
    b.tex('lamp', raster(LAMP_TEX, LAMP))
    m = b.model
    # A dark prismarine foot, the glowing sea-green core inside a prismarine cage, a stepped cap and a spine.
    m.box([3, 0, 3], [13, 1.5, 13], 'mc:dark_prismarine')
    m.box([4.5, 2, 4.5], [11.5, 9, 11.5], 'lamp', uv={**sides([0, 9, 7, 16]), 'up': [9, 0, 14, 5]}, skip=('down',),
          light=15, shade=False)
    m.box([3.5, 1.5, 3.5], [12.5, 10, 12.5], 'lamp', uv=sides([0, 0, 9, 8.5]), only=('north', 'south', 'east', 'west'))
    m.box([3, 10, 3], [13, 11.5, 13], 'mc:dark_prismarine')
    m.box([4.5, 11.5, 4.5], [11.5, 12.5, 11.5], 'mc:prismarine_bricks', skip=('down',))
    m.box([7, 12.5, 7], [9, 13.5, 9], 'mc:gold_block', skip=('down',))
    m.box([7.5, 13.5, 7.5], [8.5, 15, 8.5], 'mc:prismarine', skip=('down',))
    b.particle = 'mc:prismarine_bricks'
    b.display = {'gui': {'rotation': [30, 225, 0], 'translation': [0, 0, 0], 'scale': [0.85, 0.85, 0.85]}}
    return b


BLOCKS = [pearl_basin, kelp_rack, shell_bench, conch_shrine, prism_lathe, sponge_rack, tide_lamp]
