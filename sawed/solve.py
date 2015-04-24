s = "".join("""
ddddddwwwwwwaaaaaasssssssssssssseddddddddddddddddddewwawwawwawwawwawwawwaedddssssssd
dddssssssssewwdwwdwwdwwdwwddssdssdssdssdsswwdwwdwwdwwdwwdwwdwwdassassassassassassass
edddddddddddddddewwwwwwwwwwwwwwdssdssdssdssdssdssdsswwwwwwwwwwwwwwsssssssssssssseddd
ddddddddewwwwwwwwwwwwweddddddddddessssssssssssssedddddddewwwwwwwwwwwwwweaaaaaaaedssd
ssdssdssdssdssdssewdwdwdddwddwdwwddwddwddwddewawwawawaaasasassasssasssdsssdsddsddddw
dwwdwwwaaaessdddsddsddddsddddewdwdwdwdwdwdwdwawawawawawawaedddddddddddddddedddddddda
aaaaaaasssssssssssssswwwwwwwwdddddeddddddddeddddddwwwwwwaaaaaasssssssssssssseddddddd
ddddddwwesdsddsdddwddwdwwwawwawawaawaawawwdwwdwdddsddsdsedddwwwdddesssssssssesssssess
""".split())

direction = { 'd': (1, 0), 'a': (-1, 0), 'w': (0, -1), 's': (0, 1) }
points = []
x = y = 0
on = True
for c in s:
    if on:
        points.append((x,y))
    if c == 'e':
        on = not on
    else:
        x += direction[c][0]
        y += direction[c][1]

minx = min(p[0] for p in points)
maxx = max(p[0] for p in points)
miny = min(p[1] for p in points)
maxy = max(p[1] for p in points)
w = maxx - minx + 1
h = maxy - miny + 1
from PIL import Image
img = Image.new('RGB', (w, h), "white")
pixels = img.load()
for x, y in points:
    pixels[x - minx, y - miny] = (0,0,0)
img.show()
