import msc


def basic_call():
    sts = [("A", "UA A"),
           ("AP", "P-CSCF A"),
           ("AI", "I-CSCF A"),
           ("H", "HSS"),
           ("ASC", "S-CSCF A"),
           ("BP", "P-CSCF B"),
           ("B", "UA B")
           ]
    cfg = msc.Config(outdir="./basic_call", outfile="basic_call%d",
                     txtout=msc.TxtLatex(), format="pdf")
    sl = msc.StatList(cfg, sts)
    sl.msg_to("INVITE\nFrom: a\nTo: b", ["A", "AP", "AI"], "A makes a call")
    sl.msg_to("Cx", ["AI", "H"],
              "I-CSCF determines the S-CSCF that is serving user A")
    sl.msg_to("<s-cscf>", ["H", "AI"])
    sl.msg_to("INVITE", ["AI", "ASC"])
    sl.box("ASC", "The S-CSCF processes A\'s originating IFCs")
    sl.msg_to("Cx", ["ASC", "H"])
    sl.msg_to("<s-cscf>", ["H", "ASC"])
    sl.box("ASC",
           "The S-CSCF processes B\'s terminating IFCs")
    sl.msg_to("INVITE", ["ASC", "BP", "B"])
    sl.box("B", "B picks up the phone")
    sl.msg_to("180 Ringing", ["B", "BP", "ASC", "AP", "A"])
    sl.msg_to("200 OK", ["B", "BP", "ASC", "AP", "A"])
    sl.msg_to("ACK\nFrom: a\nTo: b", msc.rev(["B", "BP", "ASC", "AP", "A"]))
    sl.media("RTP/RTCP", ["B", "BP", "AP", "A"])
    sl.drop_to("BYE", "B", "BP")
    sl.close()

basic_call()
