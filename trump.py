import subprocess
import os
import random
import time
import sys

def get_ansi_characters(string):
    nc = []
    on_ansi=False
    for c in string:
        nc.append(c)
        if c == "\033":
            on_ansi = True
        if on_ansi:
            if c == "m":
                on_ansi = False
            continue
        yield "".join(nc)
        nc = []

def copy_to_out(out,w,h,x,y,colors=False):
    mugshot = sys.path[0] + "/"
    if not colors:
        mugshot += "mugshot.jpg"
    else:
        ri = random.randint(0,5)
        mugshot += f"{ri}.jpg"
    args = ["chafa","--stretch",f"--size={w}x{h}","--symbols=block",mugshot]
    img = subprocess.run(args, stdout=subprocess.PIPE)
    img = img.stdout.decode("utf-8")
    ix = -1
    iy = 0
    for c in get_ansi_characters(img):
        if "\n" in c:
            out[iy+y][ix+x] += "\033[0m"
            ix = -1
            iy += 1
            continue
        ix += 1
        out[iy+y][ix+x] = c

def rec_blocks(out,w,h,x=1,y=1):
    wspace = 2
    hspace = 1
    if w <= wspace or h <= hspace:
        return

    #print(w,h,x,y)

    iw = random.randint(1,w-wspace)
    ih = random.randint(1,h-hspace)

    #print(iw,ih)

    copy_to_out(out,iw,ih,x,y) 
    
    rec_blocks(out, w-iw-wspace, ih+hspace, x+iw+wspace, y )
    rec_blocks(out, w, h-ih-hspace, x, y+ih+hspace )

def slice_area(areas,area_index,w,h,x,y,mode,wspace=2,hspace=1):
    area = areas[area_index]
    new_areas = []
    if mode == 1:
        new_areas.append( [area[0], y-area[3], area[2], area[3]] ) #top
        new_areas.append( [area[0], area[1]+area[3]-y-h, area[2], y+h] ) #bottom
        new_areas.append( [x-area[2], h, area[2], y] ) #left
        new_areas.append( [area[0]+area[2]-x-w, h, x+w, y] ) #right
    else:
        new_areas.append( [x-area[2], area[1], area[2], area[3]] ) #left
        new_areas.append( [area[0]+area[2]-x-w, area[1], x+w, area[3]] ) #right
        new_areas.append( [w, y-area[3], x, area[3]] ) #top
        new_areas.append( [w, area[1]+area[3]-y-h, x, y+h] ) #bottom
    areas.pop(area_index)
    for a in new_areas:
        if a[0] <= wspace or a[1] <= hspace:
            continue
        areas.append(a)

#areas = array of (w,h,x,y)
def rec_areas(out,areas,colors,wspace,hspace):

    while(len(areas) > 0):
        ri = random.randint(0,len(areas)-1)
        area = areas[ri]

        ix = area[2] + random.randint(0, area[0] // 2)
        iy = area[3] + random.randint(0, area[1] // 2)

        iw = min(random.randint(1,area[0]+area[2]-ix),30)
        ih = min(random.randint(1,area[1]+area[3]-iy),30)

        copy_to_out(out,iw,ih,ix,iy,colors)

        slice_area(areas,ri,iw,ih,ix,iy,random.randint(0,1),wspace,hspace)
    

def main(colors,ws,hs):
    ts = (213,47)
    if sys.stdout.isatty():
        ts = os.get_terminal_size()
    out = [ [ " " for j in range(ts[0]) ] for i in range(ts[1]) ]
    rec_areas(out, [ [ts[0]-2,ts[1]-2,1,1] ], colors, ws, hs )
    #rec_blocks(out, ts.columns-1, ts.lines-1)
    for s in out:
        print("".join(s))

def main_main():
    colors = False
    loops = 0
    infinite = True
    ws = 1
    hs = 1
    for i in range(1,len(sys.argv)):
        a = sys.argv[i]
        if a == "-h":
            print("why are you using this")
            return
        if a == "-c":
            colors = True
        if "-l" in a:
            infinite = False
            loops = int(a.split("=")[1])

        if "-w" in a:
            ws = int(a.split("=")[1])

        if "-h" in a:
            hs = int(a.split("=")[1])

                    
    while(infinite or loops > 0):
        main(colors,ws,hs)
        if not sys.stdout.isatty():
            break
        time.sleep(0.5)
        loops -= 1

if __name__ == "__main__":
    main_main()
