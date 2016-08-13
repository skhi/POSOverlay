from JMTTools import *
from JMTROOTTools import *
set_style(True)
ROOT.gStyle.SetOptStat(111111)

from write_other_hc_configs import doer, HC, module_sorter_by_portcard
disk = 1
daq_dir = '/home/fnaltest/SCurveInfo/disk1_runs-1227-1238'
modtests_dir = '/home/fnaltest/SCurveInfo/BmI_Configs_m20_SCurveInfo'
the_doer = doer(disk)

def convert_doug(fn):
    x = cPickle.load(open(fn, 'rb'))
    d = fn.replace('.p', '')
    try:
        os.mkdir(d)
    except OSError:
        pass
    for roc, v in x.iteritems():
        seen = set()
        newl = [0]*4160
        for i, (c,r, th,sg) in enumerate(v):
            assert 0 <= c <= 51
            assert 0 <= r <= 79
            assert 0 <= th
            assert 0 <= sg
            assert (c,r) not in seen
            seen.add((c,r))
            newl[c*80 + r] = (th,sg)
        newfn = os.path.join(d, roc)
        cPickle.dump(newl, open(newfn, 'wb'), -1)
        
def convert_trimdat(fn):
    d = fn.replace('.dat', '')
    try:
        os.mkdir(d)
    except OSError:
        pass
    newls = defaultdict(lambda: [0]*4160)
    seens = defaultdict(set)
    for iline, line in enumerate(open(fn)):
        if iline % 50000 == 0:
            print iline
        line = line.strip()
        if line:
            line = line.split()
            assert line[0] == '[PixelSCurveHistoManager::fit()]RocName='
            assert line[1].startswith('FPix_')
            roc = line[1]
            seen = seens[roc]
            newl = newls[roc]
            r, c = int(line[2]), int(line[3])
            assert 0 <= c <= 51
            assert 0 <= r <= 79
            assert (c,r) not in seen
            seen.add((c,r))
            sg, th = float(line[4]), float(line[5])
            assert 0 <= th
            assert 0 <= sg
            newl[c*80 + r] = (th, sg)

    for roc, newl in newls.iteritems(): 
        newfn = os.path.join(d, roc)
        cPickle.dump(newl, open(newfn, 'wb'), -1)

def comp(daq_dir, modtests_dir):
    summaries = []
    class summary:
        def __init__(self):
            pass

    for ifn, daq_fn in enumerate(sorted(glob(os.path.join(daq_dir, 'FPix*')))):
        #if ifn > 50: break
        roc = os.path.basename(daq_fn)
        print roc

        modtests_fn = os.path.join(modtests_dir, roc)
        assert os.path.isfile(modtests_fn)

        daq_l   = cPickle.load(open(daq_fn,   'rb'))
        modtests_l = cPickle.load(open(modtests_fn, 'rb'))

        h_th_daq   = ROOT.TH1F('h_th_daq',   roc + ';threshold (vcal low);pixels/0.3', 100, 20, 50)
        h_sg_daq   = ROOT.TH1F('h_sg_daq',   roc + ';width (vcal low);pixels/0.06',    100, 0, 6)
        h_th_modtests = ROOT.TH1F('h_th_modtests', roc + ';threshold (vcal low);pixels/0.3', 100, 20, 50)
        h_sg_modtests = ROOT.TH1F('h_sg_modtests', roc + ';width (vcal low);pixels/0.06',    100, 0, 6)
        for h in (h_th_modtests, h_sg_modtests, h_th_daq, h_sg_daq):
            h.SetLineWidth(2)
        for h in (h_th_modtests, h_sg_modtests):
            h.SetLineColor(2)
        h_th_daq_v_modtests = ROOT.TH2F('h_th_daq_v_modtests', roc + ';modtests threshold (vcal low);daq threshold (vcal low)', 100, 20, 50, 100, 20, 50)
        h_sg_daq_v_modtests = ROOT.TH2F('h_sg_daq_v_modtests', roc + ';modtests width (vcal low);daq width (vcal low)', 100, 0, 6, 100, 0, 6)
        h_th_daq_m_modtests = ROOT.TH1F('h_th_daq_m_modtests', roc + ';daq threshold - modtests threshold  (vcal low);pixels/0.3', 100, -15, 15)
        h_sg_daq_m_modtests = ROOT.TH1F('h_sg_daq_m_modtests', roc + ';daq width - modtests width (vcal low);pixels/0.06', 100, -3, 3)
        hists = [h_th_daq, h_sg_daq, h_th_modtests, h_sg_modtests, h_th_daq_v_modtests, h_sg_daq_v_modtests, h_th_daq_m_modtests, h_sg_daq_m_modtests]

        for i, (daq, modtests) in enumerate(izip(daq_l, modtests_l)):
            if type(daq) != tuple:
                daq = (0.,0.)
            assert type(modtests) == tuple

            col = i / 80
            row = i % 80

            daq_th, daq_sg = daq
            modtests_th, modtests_sg = modtests

            if daq_th != 0.:
                h_th_daq.Fill(daq_th)
            if daq_sg != 0.:
                h_sg_daq.Fill(daq_sg)

            if modtests_th != 0.:
                h_th_modtests.Fill(modtests_th)
            if modtests_sg != 0.:
                h_sg_modtests.Fill(modtests_sg)

            h_th_daq_v_modtests.Fill(modtests_th, daq_th)
            h_sg_daq_v_modtests.Fill(modtests_sg, daq_sg)

            if daq_th != 0. and modtests_th != 0.:
                h_th_daq_m_modtests.Fill(daq_th - modtests_th)
            if daq_sg != 0. and modtests_sg != 0.:
                h_sg_daq_m_modtests.Fill(daq_sg - modtests_sg)

        s = summary()
        s.roc = roc
        s.daq_th_entries = h_th_daq.GetEntries()
        s.daq_th_mean = h_th_daq.GetMean()
        s.daq_th_rms = h_th_daq.GetRMS()
        s.daq_sg_entries = h_sg_daq.GetEntries()
        s.daq_sg_mean = h_sg_daq.GetMean()
        s.daq_sg_rms = h_sg_daq.GetRMS()
        s.modtests_th_entries = h_th_modtests.GetEntries()
        s.modtests_th_mean = h_th_modtests.GetMean()
        s.modtests_th_rms = h_th_modtests.GetRMS()
        s.modtests_sg_entries = h_sg_modtests.GetEntries()
        s.modtests_sg_mean = h_sg_modtests.GetMean()
        s.modtests_sg_rms = h_sg_modtests.GetRMS()
        summaries.append(s)
        
        for h in (h_th_modtests, h_th_daq):
            h.GetYaxis().SetRangeUser(0.1, 800)
        for h in (h_sg_modtests, h_sg_daq):
            h.GetYaxis().SetRangeUser(0.1, 1100)
        h_th_daq_m_modtests.GetYaxis().SetRangeUser(0, 1000)
        h_sg_daq_m_modtests.GetYaxis().SetRangeUser(0, 350)

        c = ROOT.TCanvas('c', '', 1920, 1000)
        c.Divide(4,2)
        p = c.cd(1)
        h_th_modtests.Draw()
        h_th_daq.Draw('sames')
        p.Update()
        differentiate_stat_box(h_th_modtests, 0)
        differentiate_stat_box(h_th_daq, 1)
        p = c.cd(2)
        p.SetLogy()
        h_th_modtests.Draw()
        h_th_daq.Draw('sames')
        p.Update()
        differentiate_stat_box(h_th_modtests, 0)
        differentiate_stat_box(h_th_daq, 1)
        p = c.cd(3)
        h_sg_modtests.Draw()
        h_sg_daq.Draw('sames')
        p.Update()
        differentiate_stat_box(h_sg_modtests, 0)
        differentiate_stat_box(h_sg_daq, 1)
        p = c.cd(4)
        p.SetLogy()
        h_sg_modtests.Draw()
        h_sg_daq.Draw('sames')
        p.Update()
        differentiate_stat_box(h_sg_modtests, 0)
        differentiate_stat_box(h_sg_daq, 1)
        c.cd(5)
        h_th_daq_v_modtests.Draw('colz')
        c.cd(6)
        h_sg_daq_v_modtests.Draw('colz')
        c.cd(7)
        h_th_daq_m_modtests.Draw()
        c.cd(8)
        h_sg_daq_m_modtests.Draw()
        c.cd(0)
        c.SaveAs(roc + '.png')

        del c
        for h in hists:
            del h

    return summaries

def draw_summaries(summaries):
    hs = defaultdict(dict)
    def _h(s, name, title, *binning):
        mod = the_doer.modules_by_name[s.roc.split('_ROC')[0]]
        pc = mod.portcard.replace('FPix_', '')
        hn = name + '_' + pc
        ht = pc + title
        if not hs[pc].has_key(name):
            assert len(binning) in (3,6)
            H = ROOT.TH1F if len(binning) == 3 else ROOT.TH2F
            h = H(hn, ht, *binning)
            if H == ROOT.TH2F:
                h.SetStats(0)
            if 'modtests' in hn:
                h.SetLineColor(2)
            h.SetLineWidth(2)
            hs[pc][name] = h
        return hs[pc][name]

    for s in summaries:
        nback = 10
        _h(s, 'h_entries_daq_v_modtests_th', ';modtests threshold entries;daq threshold entries', nback, 4161-nback, 4161, nback, 4161-nback, 4161).Fill(s.modtests_th_entries, s.daq_th_entries)
        _h(s, 'h_entries_daq_v_modtests_sg', ';modtests width entries;daq width entries',         nback, 4161-nback, 4161, nback, 4161-nback, 4161).Fill(s.modtests_sg_entries, s.daq_sg_entries)
        _h(s, 'h_mean_daq_th',      ';threshold mean;rocs', 80, 10, 60).Fill(s.daq_th_mean)
        _h(s, 'h_mean_modtests_th', ';threshold mean;rocs', 80, 10, 60).Fill(s.modtests_th_mean)
        _h(s, 'h_mean_daq_sg',      ';width mean;rocs', 80, 0, 10).Fill(s.daq_sg_mean)
        _h(s, 'h_mean_modtests_sg', ';width mean;rocs', 80, 0, 10).Fill(s.modtests_sg_mean)
        _h(s, 'h_rms_daq_th',      ';threshold rms;rocs', 80, 0, 3).Fill(s.daq_th_rms)
        _h(s, 'h_rms_modtests_th', ';threshold rms;rocs', 80, 0, 3).Fill(s.modtests_th_rms)
        _h(s, 'h_rms_daq_sg',      ';width rms;rocs', 80, 0, 3).Fill(s.daq_sg_rms)
        _h(s, 'h_rms_modtests_sg', ';width rms;rocs', 80, 0, 3).Fill(s.modtests_sg_rms)

    #hs = dict(hs)
    #return hs

    for pc, hpc in sorted(hs.items()):
        c = ROOT.TCanvas('c', '', 1920, 1000)
        c.Divide(3,2)

        c.cd(1)
        hpc['h_entries_daq_v_modtests_th'].Draw('colz text00')
        c.cd(4)
        hpc['h_entries_daq_v_modtests_sg'].Draw('colz text00')

        for i,x in enumerate(['mean', 'rms']):
            for j,y in enumerate(['th', 'sg']):
                p = c.cd(3*j+2+i)
                hpc['h_%s_modtests_%s' % (x,y)].Draw()
                hpc['h_%s_daq_%s' % (x,y)].Draw('sames')
                p.Update()
                differentiate_stat_box(hpc['h_%s_daq_%s' % (x,y)], 0)
                differentiate_stat_box(hpc['h_%s_modtests_%s' % (x,y)], 1)

        c.cd(0)
        c.SaveAs('summary_' + pc + '.png')
        del c

def to_pdf():
    summary_cmd = []
    for pcnum in xrange(1,4+1):
        print pcnum
        l = [m.name for m in sorted(the_doer.modules, key=module_sorter_by_portcard) if the_doer.moduleOK(m) and m.portcardnum == pcnum]
        these = [x + '_ROC%i.png' % roc for roc in xrange(16) for x in l]
        these2 = [x for x in these if os.path.isfile(x)]
        print 'missing'
        pprint(sorted(set(these) - set(these2)))
        cmd = 'convert ' + ' '.join(these2) + ' %s_D%s_PRT%i.pdf' % (HC, disk, pcnum)
        #print cmd
        os.system(cmd)
        summary_cmd.append('summary_%s_D%s_PRT%i.png' % (HC, disk, pcnum))

    os.system('convert ' + ' '.join(summary_cmd) + ' summary_%s_D%i.pdf' % (HC, disk))

#convert_trimdat('disk1_runs-1227-1238.dat')
#draw_summaries(comp(daq_dir, modtests_dir))
to_pdf()