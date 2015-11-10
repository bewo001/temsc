# -*- coding: utf-8 -*-
import msc

def f():
    aprec = msc.Var([("A precond.", False), ("A precond.", True)])
    bprec = msc.Var([("B precond.", False), ("B precond.", True)])
    with msc.Config(outdir="./tpcc", txtout=msc.TxtLatex(), format="pdf") as cfg:
        v = 0
        for i in msc.Combis([aprec, bprec]):
            sts = [("A", "User Agent A"),
                   ("AS", "Application Server"),
                   ("B", "User Agent B")]
            cfg.set_outfile("tpcc%d-%%d" % v, combis=i)
            v += 1
            print(i)
            sl = msc.StatList(cfg, sts)
            if aprec.value[1]:
                sl.msg_to("INVITE", ["AS", "A"],
                    "AS beginnt 3pcc ohne SDP")
                sl.msg_to("183 Progress\nofferA", ["A", "AS"])
                sl.msg_to("INVITE\nofferA", ["AS", "B"])
                if bprec.value[1]:
                    sl.msg_to("183 Progress\nanswerB", ["B", "AS"])
                    sl.msg_to("PRACK\nanswerB", ["AS", "A"])
                    sl.msg_to("200 OK(PRACK)", ["A", "AS"])
                    sl.msg_to("PRACK", ["AS", "B"])
                    sl.msg_to("200 OK(PRACK)", ["B", "AS"])
                    sl.msg_to("180 Ringing", ["B", "AS"])
                    sl.msg_to("200 OK", ["B", "AS"])
                else:
                    sl.msg_to("180 Ringing", ["B", "AS"])
                    sl.msg_to("200 OK\nanswerB", ["B", "AS"])
                    sl.msg_to("PRACK\nanswerB", ["AS", "A"])
                    sl.msg_to("200 OK(PRACK)", ["A", "AS"])
                sl.msg_to("ACK", ["AS", "A"])
                sl.msg_to("ACK", ["AS", "B"])
            else:
                sl.msg_to("INVITE\noffer no media", ["AS", "A"],
                    "AS beginnt 3pcc mit SDP on m-line")
                sl.msg_to("180 Ringing", ["A", "AS"])
                sl.msg_to("200 OK\nanswer no media", ["A", "AS"])
                sl.msg_to("ACK", ["AS", "A"])
                sl.msg_to("INVITE", ["AS", "B"],
                    "AS sendet INVITE ohne SDP")
                if bprec.value[1]:
                    sl.msg_to("183 Progress\nofferB", ["B", "AS"])
                    sl.msg_to("INVITE\nofferB", ["AS", "A"],
                        "AS verändert den dialog mit A mittels Re-INVITE")
                    sl.msg_to("200 OK\nanswerA", ["A", "AS"])
                    sl.msg_to("ACK", ["AS", "A"])
                    sl.msg_to("PRACK\nanswerA", ["AS", "B"])
                    sl.msg_to("200 OK(PRACK)", ["B", "AS"])
                    sl.msg_to("180 Ringing", ["B", "AS"])
                    sl.msg_to("200 OK", ["B", "AS"])
                    sl.msg_to("ACK", ["AS", "B"])
                else:
                    sl.msg_to("180 Ringing", ["B", "AS"])
                    sl.msg_to("200 OK\nofferB", ["B", "AS"])
                    sl.msg_to("INVITE\nofferB", ["AS", "B"],
                        "AS verändert den dialog mit A mittels Re-INVITE")
                    sl.msg_to("200 OK\nanswerA", ["A", "AS"])
                    sl.msg_to("ACK", ["AS", "A"])

            sl.close()

f()
