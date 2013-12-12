from optparse import OptionParser


parser = OptionParser()



parser.add_option('--inputfile', metavar='F', type='string', action='store',
                  default='textfile_input.txt',
                  dest='inputfile',
                  help='Name of input file')

parser.add_option('--maxval', metavar='F', type='int', action='store',
                  default=5,
                  dest='maxval',
                  help='Maximum value of the plots')


(options, args) = parser.parse_args()

argv = []


from ROOT import *
gROOT.Macro("rootlogon.C")

gStyle.SetOptStat(000000)

gStyle.SetTitleFont(43)
#gStyle.SetTitleFontSize(0.05)
gStyle.SetTitleFont(43, "XYZ")
gStyle.SetTitleSize(30, "XYZ")
gStyle.SetTitleOffset(3.5, "X")
gStyle.SetLabelFont(43, "XYZ")
gStyle.SetLabelSize(16, "XYZ")



# Define the styles for each of the measurement
#         Name    Color           Title           Left(0) or right(1)
styles = {"T'":[TColor.kMagenta, "Vector-like T'",      0],
          "B'":[TColor.kRed,     "Vector-like B'",      0],
          "DM":[TColor.kViolet,  "Dark matter",         0],
          "Z'":[TColor.kBlue,    "t#bar{t} Resonances", 1],
          "W'":[8,  "tb Resonances",       1],
          "t*":[TColor.kViolet,  "Excited tops",        1]
}

texts = {
    "B'":[0.5, 0.2, 0.95, 0.3],
    "T'":[0.5, 0.8, 0.95, 0.9],
    "DM":[0,   0,   0,   0],
    "Z'":[0.65,0.8, 0.95, 0.9],
    "t*":[0.65, 0.15, 0.95, 0.25],
    "W'":[0.65, 0.3, 0.95, 0.4],
    }



# Open the text file, get the lines, and store them in a dictionary
infile = open( options.inputfile, 'r')
lines = infile.readlines()
n0 = 0   # Number of bins in the "left" histogram
n1 = 0   # Number of bins in the "right" histogram
masters = dict()
for line in lines :
    if line[0] == '#' :
        continue
    toks = line.split()
    if not masters.has_key( toks[0] ) :
        masters[toks[0]] = []
    #    limit           COM            ana name  color               class of ana        left(0) or right(1)
    s = [float(toks[1]), float(toks[2]), toks[3], styles[toks[0]][0], styles[toks[0]][1], styles[toks[0]][2] ]
    ## print 'Adding to ' + toks[0]
    ## for si in s :
    ##     print si,
    ## print ''
    masters[toks[0]].append( s )
    if styles[ toks[0] ][2] == 0 :
        #print 'Added to left plot'
        n0 += 1
    elif styles[ toks[0] ][2] == 1 :
        #print 'Added to right plot'
        n1 += 1
    else :
        print 'Invalid input, skipping'


# Get info to fill histos
hists = dict()
histstodraw = [
    TH1F('hists0', '', n0, 0, n0),
    TH1F('hists1', '', n1, 0, n1),
    ]
histstodraw[0].SetMaximum(options.maxval)
histstodraw[1].SetMaximum(options.maxval)
#         bin number    value    label
labels = [ ]
plotbins = [ 0, 0 ]  # Current bin for each plot
binlabels = [ [], [] ]
canvs = []
for key  in [  "B'", "T'", "t*", "W'", "Z'"] :
    value = masters[key]
    print 'key =  ' + str (key)
    print 'value = '
    print value
    if styles[ key ][2] == 1 :
        plot = 1
        nbins = n1
        #print 'set to right plot'
    else :
        plot = 0    # 0 = left plot, 1 = right plot    
        nbins = n0  # Default to left.        
        #print 'set to left plot'

    if hists.has_key( key ) == False : 
        hist = TH1F( key, "", nbins, 0, nbins )
        hist.SetFillColor( styles[key][0]     )
        hist.SetMaximum( options.maxval )
        hist.SetBarWidth(0.8)
        hist.SetBarOffset(0.1)
        hist.GetXaxis().SetNdivisions(0)
        hist.GetYaxis().SetNdivisions(options.maxval + 2)
        hists[key] = [ styles[key][2], hist]
        
    for ival in range(len(value)) :
        plotbin = plotbins[plot]
        limit = value[ival][0]
        label = value[ival][2]
        ileftright = value[ival][3]
        labels.append( [plot, plotbin, label] )
        hists[key][1].SetBinContent( plotbin+1, limit )
        hists[key][1].GetXaxis().SetBinLabel( plotbin+1, label )
        histstodraw[plot].GetXaxis().SetBinLabel( plotbin+1, label )
        histstodraw[plot].SetBinContent( plotbin+1, limit )
        plotbins[plot] += 1
    c = TCanvas('debug' + key, key)
    hists[key][1].Draw('hbar')
    canvs.append( c )



# Draw the histograms
c_all = TCanvas('ca', 'ca',  1100, 850)
ctitle = TPad("ctitle", "ctitle", 0.0, 0.90, 1.0, 1.0)
ctitle.Draw()
ctitle.cd()
title = TPaveText( 0.05, 0.05, 0.95, 0.95)
title.SetFillColor(0)
title.SetBorderSize(0)
title.AddText("CMS Searches for New Physics Beyond Two Generations (B2G)")
title.AddText("95% CL Exclusions (TeV)")
title.SetTextFont(63)
title.SetTextSize(30)
#title.SetTextColor(ROOT.kBlue)
title.Draw()
c_all.cd()
c = TPad('c', 'c', 0.0, 0.0, 1.0, 0.90)
c.Divide(2,1)
c.Draw()
iplot = 0

firstdrawn = [True,True]
for ihist in range(len(histstodraw)) :
    hist = histstodraw[ihist]
    c.cd(ihist + 1)
    gPad.SetTopMargin(0.)
    gPad.SetLeftMargin(0.3)
    gPad.SetRightMargin(0.05)
    gPad.SetGridx()
    hist.Draw('axis hbar')


for key in [  "B'", "T'", "t*", "W'", "Z'"]  :
    val = hists[key]
    side = val[0]
    hist = val[1]
    c.cd(side + 1)
    gPad.SetLeftMargin(0.3)
    gPad.SetRightMargin(0.05)
    gPad.SetGridx()
    hist.Draw('hbar same')
    ihist += 1

paves = []
for key in [  "B'", "T'", "t*", "W'", "Z'"] :
    vals = texts[key]
    style = styles[key]
    c.cd(style[2] + 1)
    p = TPaveText(vals[0], vals[1], vals[2], vals[3], "NDC" )
    p.AddText( style[1] )
    p.SetFillColor( style[0] )
    p.SetTextColor(0)
    p.Draw()
    paves.append(p)

c_all.Update()
c_all.Print("b2g_summary_updated.pdf", "pdf")
c_all.Print("b2g_summary_updated.png", "png")
