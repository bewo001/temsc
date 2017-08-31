# -*- coding: utf-8 -*-
import cairo
import math
import os.path
import os
import subprocess
import sys
import time
import traceback

# W=595
# H=842
W = 842
H = 595


class TxtPlain:
    """
    Output module for plain text
    """
    def __init__(self, basnam=None, page=1):
        self.page = page
        if basnam is not None:
            self.set_outfile(basname, page)

    def set_outfile(self, basnam, combis=[], page=1):
        self.basnam = basnam
        self.fd = open((basnam + ".txt") % page, "w")

    def outitem(self, nr, text):
        self.fd.write("%d. %s\n" % (nr, text))

    def finish(self):
        self.fd.close()


class TxtLatex:
    """
    Output module for LaTeX article class
    """
    def __init__(self, basnam=None, page=1):
        self.page = page
        self.dryrun = True
        self.fd = None
        self.combis = []
        if basnam is not None:
            self.set_outfile(basname)
        self.fd = None
        self.first = True

    def set_outfile(self, basnam, combis=[], page=1):
        self.imgname = basnam
        if combis != []:
            self.combis = combis
        self.basnam = basnam
        if self.fd is None:
            self.fd = open((basnam + ".ltx") % page, "w")
            self.fd.write(
                "\\documentclass{article}\n\
\\usepackage[utf8]{inputenc}\n\
\\usepackage{float}\n\
\\usepackage{german}\n\
\\usepackage{graphicx}\n\
\\begin{document}\n")
            self.first = True
        self.dryrun = True

    def outitem(self, nr, text):
        if self.dryrun:
            return
        if nr == 1:
            if not self.first:
                self.fd.write("\\end{enumerate}\n\n")
            else:
                self.first = False

            self.fd.write(
                "\\section{")
            for i in self.combis:
                if i is not None:
                    self.fd.write("%s " % str(i)),
            self.fd.write("}\n")
            self.fd.write(
                "\\begin{figure}[H]\n\
\\includegraphics[width=\\textwidth]{%s}\n\
\\end{figure}\n\
\\begin{enumerate}\n" % (self.imgname + ".pdf") % self.page)

        self.fd.write("\item\n%s\n" % text)

    def finish(self):
        if not self.first:
            self.fd.write("\\end{enumerate}\n")
        self.fd.write("\\end{document}\n")
        self.fd.close()


class TxtBeamer:
    """
    Output module for LaTeX beamer class
    """
    def __init__(self, basnam=None, page=1):
        self.page = page
        self.dryrun = True
        self.fd = None
        self.combis = []
        if basnam is not None:
            self.set_outfile(basname)
        self.fd = None
        self.first = True

    def set_outfile(self, basnam, combis=[], page=1):
        self.imgname = basnam
        if combis != []:
            self.combis = combis
        self.basnam = basnam
        if self.fd is None:
            self.fd = open((basnam + ".ltx") % page, "w")
            self.fd.write(
                "\\documentclass{beamer}\n\
\\usepackage[utf8]{inputenc}\n\
\\usepackage{float}\n\
\\usepackage{german}\n\
\\usepackage{graphicx}\n\
\\begin{document}\n")
            self.first = True
        self.dryrun = True

    def outitem(self, nr, text):
        if self.dryrun:
            return
        if nr == 1:
            if not self.first:
                self.fd.write("\\end{enumerate}\n\end{frame}\n")
            else:
                self.first = False

            self.fd.write(
                "\\begin{frame}\n\
\\frametitle{")
            for i in self.combis:
                if i is not None:
                    self.fd.write("%s " % str(i)),
            self.fd.write("}\n")
            self.fd.write(
                "\\begin{figure}[H]\n\
\\includegraphics[width=\\textwidth]{%s}\n\
\\end{figure}\n\
\\end{frame}\n" % (self.imgname + ".pdf") % self.page)

            self.fd.write(
                "\\begin{frame}\n\
\\frametitle{")
            for i in self.combis:
                if i is not None:
                    self.fd.write("%s " % str(i)),
            self.fd.write("}\n")
            self.fd.write("\\begin{enumerate}\n")

        self.fd.write("\item %s\n" % text)

    def finish(self):
        if not self.first:
            self.fd.write("\\end{enumerate}\n\end{frame}\n")
        self.fd.write("\\end{document}\n")
        self.fd.close()

class TxtHtml:
    def __init__(self, basnam=None, page=1):
        self.basnam = basnam
        self.page = page
        self.itms = 0
        self.fd = None
        if basnam is not None:
            self.set_outfile(basnam, page=page)
        print("basnam %s" % basnam)
    def set_outfile(self, basnam, combis=[], page=1):
        self.page = basnam % page
        self.fd = open(self.page + ".html", mode='w')
        txt = '<html><head><title>%s</title></head><body><h1>%s</h1><p><img src="%s"></img>' \
              % (combis, combis, os.path.basename(self.page + ".svg"))
        print(txt)
        self.fd.write(txt)
        self.dryrun = True
        self.itms = 0
    def outitem(self, nr, txt):
        if self.dryrun:
            return
        if self.itms == 0:
            buf = '<ol>'
        else:
            buf = ''
        buf += "<li>%s" % txt
        self.fd.write(buf)
        self.itms += 1
        print('outitem: %s' % txt)
    def finish(self):
        if self.fd is None:
            return
        if self.itms > 0:
            txt = '</ol>'
        else:
            txt = ''
        txt += '</body>'
        print(txt)
        self.fd.write(txt)
        self.fd.close()

class Config:
    """
    configuration data for msc output
    """

    def __init__(self,
                 # in em
                 outdir=".",
                 outfile=None,
                 format="pdf",
                 txtout=TxtPlain(),
                 tmargin=4,
                 bmargin=4,
                 lmargin=6,
                 rmargin=6,
                 # in pts
                 header_sz=10,
                 msg_sz=8,
                 box_sz=8,
                 linesp=None,
                 landscape=False,
                 inkscape="inkscape"):
        """
        outdir: path to output directory
        outfile: name of outputfile, must contain a %d which will be replaced with a page number
        format: one of "pdf", "svg", or "emf"
        txtout: output module instance, eg TxtPlain()

        The following size values are in typographical em units (characters):

        tmargin: top margin
        bmargin: bottom margin
        lmargin: left margin
        rmargin: right margin

        The following size values are in typographical points:

        header_sz: size of column header text
        msg_sz: size of message text
        box_sz: size of box text

        landscape: when True output is in landscape mode
        inkscape: set inkscape command with complete path
        """
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        self.outdir = outdir
        self.txtout = txtout
        if outfile is not None:
            self.set_outfile(outfile)
        self.format = format
        self.tmargin0 = tmargin
        self.bmargin0 = bmargin
        self.lmargin0 = lmargin
        self.rmargin0 = rmargin
        self.header_sz = header_sz
        self.msg_sz = msg_sz
        self.box_sz = box_sz
        self.linesp0 = linesp
        # din a 4
        self.W = 595
        self.H = 842
        self.inkscape = inkscape
        if landscape:
            t = self.W
            self.W = self.H
            self.H = t

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        print(exc_value)
        traceback.print_tb(tb)
        self.txtout.finish()

    def set_outfile(self, outfile, combis=[]):
        self.basnam = os.path.join(self.outdir, outfile)
        self.txtout.set_outfile(self.basnam, combis=combis)

    def textadjust(self, c):
        """
        re-calculate margin size using the Cairo context passed as <c>
        """
        self.c = c
        self.c.set_font_size(self.header_sz)
        _, _, w, h, _, _ = self.c.text_extents("M")
        self.header_emh = h
        self.header_emw = w
        self.tmargin = self.tmargin0 * self.header_emh
        self.bmargin = self.bmargin0 * self.header_emh
        self.lmargin = self.lmargin0 * self.header_emw
        self.rmargin = self.rmargin0 * self.header_emw

        self.c.set_font_size(self.msg_sz)
        _, _, w, h, _, _ = self.c.text_extents("M")
        self.msg_emh = h
        self.msg_emw = w
        self.c.set_font_size(self.box_sz)
        _, _, w, h, _, _ = self.c.text_extents("M")
        self.box_emh = h
        self.box_emw = w
        if self.linesp0 is None:
            self.linesp = 0.5 * self.msg_emh
        else:
            self.linesp = self.linesp0


def arrow(c, x1, y1, x2, y2, alen=4, angle=35):
    """
    draw an arrow using Cairo context <c> from (x1,y1) to (x2,x2),
    point at (x2, y2).
    <alen> is the length of the arrow lines
    <angle> is the angle between the line and the arrow lines
    """
    c.move_to(x1, y1)
    c.line_to(x2, y2)
    dx = x1 - x2
    dy = y1 - y2
    # line angle
    theta = math.atan2(dy, dx)

    rad = angle / 180. * math.pi
    phi = -(angle / 180. * math.pi)
    ax1 = x2 + alen * math.cos(theta + rad)
    ay1 = y2 + alen * math.sin(theta + rad)

    ax2 = x2 + alen * math.cos(theta + phi)
    ay2 = y2 + alen * math.sin(theta + phi)

    w = c.get_line_width()
    c.set_line_width(1)
    c.move_to(ax1, ay1)
    c.line_to(x2, y2)
    c.line_to(ax2, ay2)
    c.stroke()
    c.set_line_width(w)


def xarrow(c, x1, y1, x2, y2, alen=4, angle=35):
    """
    draw an line using Cairo context <c> from (x1,y1) to (x2,x2),
    ending with a cross at (x2, y2).
    <alen> is the length of the cross lines
    <angle> is the angle between the line and the cross lines
    """
    c.move_to(x1, y1)
    c.line_to(x2, y2)
    dx = x1 - x2
    dy = y1 - y2
    # line angle
    theta = math.atan2(dy, dx)

    rad = angle / 180. * math.pi
    phi = -(angle / 180. * math.pi)
    ax1 = alen * math.cos(theta + rad)
    ay1 = alen * math.sin(theta + rad)

    ax2 = alen * math.cos(theta + phi)
    ay2 = alen * math.sin(theta + phi)

    w = c.get_line_width()
    c.set_line_width(1)
    c.move_to(ax1 + x2, ay1 + y2)
    c.line_to(x2 - ax1, y2 - ay1)
    c.move_to(ax2 + x2, ay2 + y2)
    c.line_to(x2 - ax2, y2 - ay2)
    c.stroke()
    c.set_line_width(w)


def marrow(c, x1, y1, x2, y2, alen=10, angle=35):
    """
    draw a double arrow using Cairo context <c> from (x1,y1) to (x2,x2),
    pointing at (x1, y1) and (x2, y2).
    <alen> is the length of the arrow lines
    <angle> is the angle between the line and the arrow lines
    """
    w = c.get_line_width()
    c.set_line_width(w * 2)
    arrow(c, x1, y1, x2, y2, alen, angle)
    arrow(c, x2, y2, x1, y1, alen, angle)
    c.set_line_width(w)


def file_age_cmp(a, b):
    """
    compare the age of the two files <a> and <b>;
    returns
    -1: if <a> is older than <b>
     0: if <a> and <b> have the same age
     1: if <a> is newer than <b>
    """
    return os.path.getmtime(a) - os.path.getmtime(b)


def sign(x):
    if x == 0:
        return 0
    elif x < 0:
        return -1
    else:
        return 1


class Defer:
    fs = []

    def __init__(self, f, args, kwargs):
        self.f = f
        self.args = args
        self.kwargs = kwargs

    def force(self):
        return self.f(*self.args, **self.kwargs)


def defer(f):
    def newf(*args, **kwargs):
        return Defer.fs.append(Defer(f, args, kwargs))

    return newf


class Station:

    def __init__(self, cfg, id, label):
        self.cfg = cfg
        self.id = id
        self.label = label
        if "c" in cfg.__dict__:
            self.set_cairo(cfg.c)

    def set_cairo(self, c):
        self.c = c
        self.c.select_font_face("Sans")
        self.c.set_font_size(self.cfg.header_sz)
        self.extents = self.c.text_extents(self.label)

    def __repr__(self):
        return self.id

    def __str__(self):
        return label

    def out(self, x, row_y):
        self.c.set_line_width(1)
        xb, yb, w, h, xa, ya = self.extents
        self.c.move_to(x - w / 2, self.cfg.tmargin + self.cfg.header_emh)
        self.c.set_source_rgb(0, 0, 0)
        self.c.show_text(self.label)
        self.c.move_to(x, self.cfg.tmargin +
                       self.cfg.header_emh + self.cfg.header_emh / 2)
        self.c.line_to(x, row_y)
        self.c.stroke()


class NetAbbrev:

    def __init__(self, cfg, id, label):
        self.cfg = cfg
        self.id = id
        self.label = label
        if "c" in cfg.__dict__:
            self.set_cairo(cfg.c)

    def set_cairo(self, c):
        self.c = c
        self.c.select_font_face("Sans")
        self.c.set_font_size(self.cfg.header_sz)
        self.extents = self.c.text_extents(self.label)

    def __repr__(self):
        return self.id

    def __str__(self):
        return self.label

    def out(self, x, row_y):
        self.c.set_line_width(1)
        xb, yb, w, h, xa, ya = self.extents
        self.c.move_to(x - w / 2, self.cfg.tmargin + self.cfg.header_emh)
        self.c.set_source_rgb(0, 0, 0)
        self.c.show_text(self.label)
        self.c.set_source_rgb(0.8, 0.8, 0.8)
        self.c.rectangle(x - 2 * self.cfg.header_emw,
                         self.cfg.tmargin + self.cfg.header_emh + self.cfg.header_emh / 2,
                         4 * self.cfg.header_emw,
                         row_y - (self.cfg.tmargin + self.cfg.header_emh + self.cfg.header_emh / 2))
        #self.c.line_to(x, self.cfg.H - self.cfg.bmargin)
        self.c.fill()
        self.c.stroke()


class StatList:

    def station_init(self, s):
        if type(s) is tuple:
            return Station(self.cfg, s[0], s[1])
        else:
            s.set_cairo(self.c)
            return s

    def is_defined(self, s):
        if s is None:
            return False
        elif type(s) is tuple:
            return s[1] is not None
        else:
            return s.label is not None

    def begin(self):
        self.pages = 1
        if self.format == "pdf":
            self.fnam = (self.cfg.basnam + ".pdf") % self.pages
            self.sfc = cairo.PDFSurface(self.fnam,
                                        self.cfg.W, self.cfg.H)
        elif self.format == "svg" or self.format == "emf":
            self.fnam = (self.cfg.basnam + ".svg") % self.pages
            if self.pages < self.last_page:
                self.sfc = cairo.SVGSurface(self.fnam,
                                            self.extent_w, self.cfg.H)
            else:
                self.sfc = cairo.SVGSurface(self.fnam,
                                            self.extent_w, self.extent_h)
        self.c = cairo.Context(self.sfc)
        self.cfg.textadjust(self.c)
        self.stations = [self.station_init(
            s) for s in self.stations0 if self.is_defined(s)]

        self.c.set_source_rgb(1.0, 1.0, 1.0)
        self.c.rectangle(0, 0, self.extent_w, self.extent_h)
        self.c.fill()
        self.c.set_source_rgb(0, 0, 0)

        lmargin = self.cfg.lmargin
        rmargin = self.cfg.rmargin

        self.mno = 1
        fk = (self.extent_w - (lmargin + rmargin)) / len(self.stations)
        self.col_w = fk
        self.st = {}
        self.st_xi = [max(lmargin, fk / 2) + fk * i
                      for i in range(0, len(self.stations))]
        self.st_x = {}
        self.row_y = self.cfg.tmargin + self.cfg.header_emh \
            + 2 * self.cfg.msg_emh
        self.c.select_font_face("Sans")
        self.c.set_font_size(self.cfg.msg_sz)
        for i in range(len(self.stations)):
            self.stations[i].c = self.c
            self.st[self.stations[i].id] = i
            self.st_x[self.stations[i].id] = self.st_xi[i]
        if self.pages < self.last_page:
            self.timelines(self.cfg.H - self.cfg.bmargin)
        else:
            self.timelines(self.extent_h - self.cfg.msg_emh)

    def __init__(self, cfg, stations, format="pdf"):
        Defer.fs = []
        self.cfg = cfg
        self.format = cfg.format
        self.extent_w = cfg.W
        self.extent_h = self.cfg.H
        self.stations0 = stations
        self.last_page = 0

    def timelines(self, row_y):
        for i in range(len(self.stations)):
            self.stations[i].out(self.st_x[self.stations[i].id],
                                 row_y)

    def export_emf(self):
        subprocess.call([self.cfg.inkscape, "-M",
                         (self.cfg.basnam + ".emf") % self.pages,
                         self.fnam])

    def page(self, row_y=None):
        if row_y is None:
            row_y = self.row_y
        if row_y < self.cfg.H - (self.cfg.bmargin + len(self.stations) * self.cfg.linesp) :
            return
        self.pages += 1
        if self.format == "pdf":
            self.sfc.show_page()
        elif self.format == "svg" or self.format == "emf":
            self.sfc.flush()
            self.sfc.finish()
            if self.format == "emf":
                self.export_emf()
            self.fnam = (self.cfg.basnam + ".svg") % self.pages
            self.sfc = cairo.SVGSurface(self.fnam, self.cfg.W, self.cfg.H)
            self.c = cairo.Context(self.sfc)
            self.cfg.textadjust(self.c)
            self.c.set_source_rgb(1.0, 1.0, 1.0)
            self.c.select_font_face("Sans")
            self.c.set_font_size(self.cfg.msg_sz)
            self.c.rectangle(0, 0, self.cfg.W, self.cfg.H)
            self.c.fill()
            [i.set_cairo(self.c) for i in self.stations]

        if self.pages < self.last_page:
            self.timelines(self.cfg.H - self.cfg.bmargin)
        else:
            self.timelines(self.extent_h - self.cfg.msg_emh)
        self.row_y = self.cfg.tmargin + self.cfg.header_emh \
            + 2 * self.cfg.msg_emh

    @defer
    def msg_to(self, msg, stations, descr=None):
        """
        draw message <msg> between all stations mentioned in <stations>
        msg: text, a '\n' character results in  a line break
        stations: list of station IDs
        """
        self.page()
        self.c.set_line_width(2.0)
        self.c.set_font_size(self.cfg.msg_sz)
        for i in stations:
            if not (i in self.st):
                return
        f = self.st_x[stations[0]]
        i = 1
        num_out = False
        y = self.row_y
        dx0 = None
        max_hbt = 0
        while i < len(stations):
            idx = self.st[stations[i]]
            if num_out or descr is None:
                msg1 = msg
            else:
                msg1 = "%d. %s" % (self.mno, msg)
                # self.c.show_text("%d. %s" % (self.mno, msg))
                num_out = True
                self.cfg.txtout.outitem(self.mno, descr)
                self.mno += 1
            wbt, hbt, rws = self.lefttxt_extents(msg1)
            max_hbt = max(hbt, max_hbt)
            t = self.st_x[stations[i]]
            dx = sign(t - f)
            if dx0 is not None and dx != dx0:
                y += hbt + self.cfg.linesp
            self.c.set_source_rgb(1., 1., 1.)
            x0 = f + (t - f) / 2 - wbt / 2
            y0 = y - self.cfg.msg_emh - self.cfg.linesp - 2
            rw = wbt
            rh = hbt + 2
            self.c.rectangle(x0, y0, rw, rh)
            self.c.fill()
            self.c.set_source_rgb(0., 0., 0.)
            ry = y - self.cfg.linesp
            self.c.move_to(f + (t - f) / 2 - wbt / 2, ry)
            lsp = 2 * self.cfg.linesp
            for (lw, r) in rws:
                self.c.show_text(r)
                ry += self.cfg.msg_emh + lsp
                lsp = self.cfg.linesp
                self.c.move_to(f + (t - f) / 2 - wbt / 2, ry)
            arrow(self.c, f, y, t, y)
            i += 1
            y += self.cfg.linesp
            dx0 = dx
            f = t
        self.row_y = y + max_hbt - self.cfg.msg_emh + self.cfg.linesp

    @defer
    def drop_to(self, msg, a, b, descr=None):
        self.page()
        self.c.set_font_size(self.cfg.msg_sz)
        f = self.st_x[a]
        t = self.st_x[b]
        y = self.row_y
        _, _, w, h, _, _ = self.c.text_extents(msg)
        self.c.move_to(f + (t - f) / 2 - w / 2, y - 2)
        if descr is None:
            self.c.show_text(msg)
        else:
            self.c.show_text("%d. %s" % (self.mno, msg))
            self.cfg.txtout.outitem(self.mno, descr)
            self.mno += 1
        xarrow(self.c, f, y, f + (t - f) * 0.75, y)
        self.row_y = y + self.cfg.msg_emh + self.cfg.linesp

    @defer
    def media(self, msg, stations, descr=None):
        """
        draw double ended media arrow with text <msg> between all stations mentioned in <stations>
        msg: text, a '\n' character results in  a line break
        stations: list of station IDs
        """
        self.page()
        wl = self.c.get_line_width()
        self.c.set_line_width(2)
        self.c.set_font_size(self.cfg.msg_sz)
        f = self.st_x[stations[0]]
        i = 1
        num_out = False
        y = self.row_y
        while i < len(stations):
            idx = self.st[stations[i]]
            _, _, w, h, _, _ = self.c.text_extents(msg)
            t = self.st_x[stations[i]]
            self.c.set_source_rgb(1., 1., 1.)
            x0 = f + (t - f) / 2 - w / 2
            y0 = y - h - 2
            rw = w
            rh = h + 2
            self.c.rectangle(x0, y0, rw, rh)
            self.c.fill()
            self.c.set_source_rgb(0., 0., 0.)
            self.c.move_to(f + (t - f) / 2 - w / 2, y - 2)
            if num_out or descr is None:
                self.c.show_text(msg)
            else:
                self.c.show_text("%d. %s" % (self.mno, msg))
                num_out = True
                self.cfg.txtout.outitem(self.mno, descr)
                self.mno += 1
            marrow(self.c, f, y, t, y)
            i += 1
            f = t
        self.row_y = y + self.cfg.msg_emh + 2 * self.cfg.linesp

    def lefttxt_extents(self, txt):
        lins = txt.split('\n')
        wbt = 0
        hbt = 0
        rv = []
        lsp = 2 * self.cfg.linesp
        for lin in lins:
            _, _, w, h, _, _ = self.c.text_extents(lin)
            wbt = max(w, wbt)
            hbt += (h + lsp)
            lsp = self.cfg.linesp
            rv.append((w, lin))
        return (wbt, hbt, rv)

    def textwrap(self, txt, halfwidth=False):
        _, _, w, h, _, _ = self.c.text_extents(txt)
        if halfwidth:
            wb = self.col_w - 2 * self.cfg.box_emw
        else:
            wb = 3 * self.col_w / 2 - 2 * self.cfg.box_emw
        if w > wb:
            wds = txt.split()
            hb = h
            tx = " "
            rws = []
            for wrd in wds:
                tx0 = tx
                w0 = w
                tx = "%s%s " % (tx, wrd)
                _, _, w, h, _, _ = self.c.text_extents(tx)
                if w >= wb:
                    rws.append((w0, tx0))
                    hb += h + self.cfg.linesp
                    tx = wrd + " "
                    _, _, w, h, _, _ = self.c.text_extents(tx)
            if w < wb:
                rws.append((w, tx))
        else:
            hb = h
            wb = w
            rws = [(wb, txt)]
        return (wb, hb, rws)

    @defer
    def box(self, station_id, txtm, descr=None, halfwidth=False):
        """
        draw a box with text <txtm> at station <station_id>
        station_id: ID of the station column where this box should be drawn
        txtm: text, the text will be centered, line breaks will be inserted automatically when needed
        """
        idx = self.st[station_id]
        halfwidth = halfwidth or idx == 0 or idx == (len(self.st) - 1)
        self.c.set_font_size(self.cfg.box_sz)
        txt = "%d. %s" % (self.mno, txtm)
        wbt, hbt, rws = self.textwrap(txt, halfwidth)
        x = self.st_x[station_id]
        y = self.row_y
        mgw = self.cfg.box_emw
        mgh = self.cfg.box_emh
        bw = wbt + mgw
        bh = hbt + mgh
        self.page(bh)
        x0 = x - bw / 2
        y0 = y
        self.c.set_source_rgb(0.9, 0.9, 0.9)
        self.c.rectangle(x0, y0, bw, bh)
        self.c.fill()
        self.c.set_source_rgb(0, 0, 0)
        h = mgh / 2 + self.cfg.box_emh + self.cfg.linesp / 2
        for (lw, r) in rws:
            self.c.move_to(x - lw / 2, y + h)
            self.c.show_text(r)
            h += self.cfg.box_emh + self.cfg.linesp
        self.c.stroke()
        if descr is None:
            self.cfg.txtout.outitem(self.mno, txtm)
        else:
            self.cfg.txtout.outitem(self.mno, descr)
        self.mno += 1
        self.row_y = y + h + mgh + self.cfg.linesp + self.cfg.box_emh

    def close(self):
        self.begin()
        for f in Defer.fs:
            f.force()
        self.last_page = self.pages
        self.extent_h = min(self.row_y + self.cfg.bmargin / 2, self.cfg.H)
        self.cfg.txtout.dryrun = False
        self.begin()
        for f in Defer.fs:
            f.force()

        self.sfc.flush()
        self.sfc.finish()
        if self.format == "emf":
            self.export_emf()


class Combis:
    """
    iterator over all combinations of values
    """

    def __init__(self, allvars):
        """
        allvars: a list of msc.Var instances
        """
        self.allvars = allvars

    def add(self, var):
        """
        add <var> to list of variables that will be used in the iterator
        """
        self.allvars.append(var)

    def __iter__(self):
        self.vstate = []
        self.vdigit = []
        c = 0
        for i in self.allvars:
            self.vstate.append(i.values)
            self.vdigit.append(0)
            c += 1
        self.vc = c
        rv = []
        p = 0
        for i in range(len(self.vdigit)):
            rv.append(self.vstate[i][self.vdigit[i]])
            p += 1
        return self

    def __next__(self):
        rv = []
        for i in range(len(self.vdigit)):
            if self.vdigit[i] == len(self.vstate[i]):
                raise StopIteration()
            rv.append(self.vstate[i][self.vdigit[i]])
            self.allvars[i].value = self.vstate[i][self.vdigit[i]]
        p = self.vc - 1
        self.vdigit[p] += 1
        while p > 0 and self.vdigit[p] == len(self.vstate[p]):
            self.vdigit[p] = 0
            p -= 1
            self.vdigit[p] += 1
        if p >= 0:
            return rv
        else:
            raise StopIteration()
    def next(self):
        # python2 compatibility
        return self.__next__()


class Var:

    def __init__(self, values=[]):
        """
        <values> is a list of values this msc.variable can have
        """
        self.values = values
        self.value = values[0]


def rev(v):
    rv = list(v)
    rv.reverse()
    return rv


def example0(fname):
    sts = [("A", "UA A"),
           ("AP", "P-CSCF A"),
           ("AI", "I-CSCF A"),
           ("H", "HSS"),
           ("ASC", "S-CSCF A"),
           ("BP", "P-CSCF B"),
           ("B", "UA B")
           ]
    cfg = Config()
    sl = StatList(cfg, fname, sts)
    sl.msg_to("INVITE", ["A", "AP", "AI"], "A makes a call")
    sl.msg_to("Cx", ["AI", "H"],
              "I-CSCF determines the S-CSCF that is serving user A")
    sl.msg_to("<s-cscf>", ["H", "AI"])
    sl.msg_to("INVITE", ["AI", "ASC"])
    sl.box("ASC", "process A\'s originating IFCs")
    sl.msg_to("Cx", ["ASC", "H"])
    sl.msg_to("<s-cscf>", ["H", "ASC"])
    sl.box("ASC", "process B\'s terminating IFCs")
    sl.msg_to("INVITE", ["ASC", "BP", "B"])
    sl.box("B", "B picks up the phone")
    sl.msg_to("180 Ringing", ["B", "BP", "ASC", "AP", "A"])
    sl.msg_to("200 OK", ["B", "BP", "ASC", "AP", "A"])
    sl.msg_to("ACK", rev(["B", "BP", "ASC", "AP", "A"]))
    sl.drop_to("BYE", "B", "BP")
    sl.explan_fd.close()
    sl.sfc.write_to_png("t.png")

# setup("basic_call")
