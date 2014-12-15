from optparse import OptionParser


parser = OptionParser()



parser.add_option('--inputfile', metavar='F', type='string', action='store',
                  default='textfile_input.txt',
                  dest='inputfile',
                  help='Name of input file')

parser.add_option('--maxval0', metavar='F', type='int', action='store',
                  default=1.5,
                  dest='maxval0',
                  help='Maximum value of the XTY plots')

parser.add_option('--maxval1', metavar='F', type='int', action='store',
                  default=5,
                  dest='maxval1',
                  help='Maximum value of the RES plots')

parser.add_option('--batch', action='store_true',
                  default=False,
                  dest='batch',
                  help='Run ROOT in batch mode')

(options, args) = parser.parse_args()

argv = []


from ROOT import *
if options.batch == True :
    gROOT.SetBatch()

# Set Style issues
gROOT.Macro("rootlogon.C")
gStyle.SetOptStat(000000)
gStyle.SetTitleFont(43)
gStyle.SetTitleFont(43, "XYZ")
gStyle.SetTitleSize(30, "XYZ")
gStyle.SetTitleOffset(3.5, "X")
gStyle.SetLabelFont(43, "XYZ")
gStyle.SetLabelSize(16, "X")
gStyle.SetLabelSize(30, "YZ")


##############################################################################################
# Define the styles for each of the measurement
#         Name    Color           Title           Left(0) or right(1)
##############################################################################################
styles = {"T'":[TColor.kGreen+1, "Vector-like T'",      0],
          "Q'":[TColor.kOrange-2,   "Vector-like Q'",    0],
          "B'":[TColor.kGreen+3,     "Vector-like B'",      0],
          "DM":[TColor.kGray+3,  "Dark matter",         0],
          "Z'":[TColor.kAzure+1,    "t#bar{t} Resonances", 1],
          "W'":[TColor.kBlue+2, "tb Resonances",       1],
          "t*":[TColor.kViolet,  "Excited tops",        1],
          "LLt":[TColor.kMagenta+2, "Displaced tops",    1],
}

##############################################################################################
# Location of text boxes : change this by eye!
##############################################################################################
texts = {
    "Q'":[0.68, 0.95, 0.95, 0.99],
    "B'":[0.68, 0.5, 0.95, 0.58],
    "T'":[0.68, 0.8, 0.95, 0.88],
    "DM":[0.68, 0.2, 0.95, 0.28],
    "Z'":[0.65,0.7, 0.95, 0.78],
    "t*":[0.65, 0.24, 0.95, 0.32],
    "W'":[0.65, 0.355, 0.95, 0.435],
    "LLt":[0.65, 0.14, 0.95, 0.19]
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
    toks = line.split("\t")
    if not masters.has_key( toks[0] ) :
        masters[toks[0]] = []
    #    limit           COM            ana name  color               class of ana        left(0) or right(1)
    s = [float(toks[1]), float(toks[2]), toks[3], styles[toks[0]][0], styles[toks[0]][1], styles[toks[0]][2] ]
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
# Histograms are "left" and "right" with a big stack of mass limits
histstodraw = [
    TH1F('hists0', '', n0, 0, n0),
    TH1F('hists1', '', n1, 0, n1),
    ]

# Set the maximum to the user's desire
histstodraw[0].SetMaximum(options.maxval0)
histstodraw[1].SetMaximum(options.maxval1)
#  labels includes   [bin number,    value,    label]
labels = [ ]
plotbins = [ 0, 0 ]  # Current bin for each plot
canvs = []  # Canvases for the various categories
for key  in [ "DM", "B'", "T'", "Q'", "LLt", "t*", "W'", "Z'"] :
    value = masters[key]
    print 'key =  ' + str (key)
    print 'value = '
    print value
    if styles[ key ][2] == 1 :
        #print 'set to right plot'
        plot = 1
        nbins = n1
    else :
        #print 'set to left plot'        
        plot = 0    # 0 = left plot, 1 = right plot    
        nbins = n0  # Default to left.        

    # If we don't have a histogram for this category (Z', T', B', etc), make one
    if hists.has_key( key ) == False : 
        hist = TH1F( key, "", nbins, 0, nbins )
        hist.SetFillColor( styles[key][0]     )
        #hist.SetMaximum( maxval[] )
        hist.SetBarWidth(0.8)
        hist.SetBarOffset(0.1)
        hist.GetXaxis().SetNdivisions(0)
        #hist.GetYaxis().SetNdivisions(options.maxval + 2)
        hists[key] = [ styles[key][2], hist]

    # Now add the individual mass limits to each category
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

    # plot the individual histograms
    c = TCanvas('debug' + key, key)
    hists[key][1].Draw('hbar')
    canvs.append( c )



# Draw the histograms together
c_all = TCanvas('ca', 'ca',  int(1100*1.5), int(850*1.5))
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

# First draw to get the axes drawn correctly
# for the "left" and "right" sides
firstdrawn = [True,True]
for ihist in range(len(histstodraw)) :
    hist = histstodraw[ihist]
    c.cd(ihist + 1)
    gPad.SetTopMargin(0.)
    gPad.SetLeftMargin(0.3)
    gPad.SetRightMargin(0.05)
    gPad.SetGridx()
    hist.GetYaxis().SetTitle( 'Excluded Mass (TeV)')
    #hist.GetXaxis().SetNdivisions(0)
    #hist.GetYaxis().SetNdivisions(options.maxval + 2)
    hist.Draw('axis hbar')

# Now draw all of the different categories
for key in [ "DM", "B'", "T'", "Q'", "LLt", "t*", "W'", "Z'"]  :
    val = hists[key]
    side = val[0]
    hist = val[1]
    c.cd(side + 1)
    gPad.SetLeftMargin(0.3)
    gPad.SetRightMargin(0.05)
    gPad.SetGridx()
    hist.Draw('hbar same')
    #gPad.SetLogx()
    ihist += 1

# Finall draw the labels
paves = []
for key in [ "DM", "B'", "T'", "Q'", "LLt", "t*", "W'", "Z'"] :
    vals = texts[key]
    style = styles[key]
    c.cd(style[2] + 1)
    p = TPaveText(vals[0], vals[1], vals[2], vals[3], "NDC" )
    p.AddText( style[1] )
    p.SetFillColor( style[0] )
    p.SetTextColor(0)
    p.SetTextFont(43)
    p.SetTextSize(30)
    p.Draw()
    paves.append(p)

c_all.Update()
c_all.Print("b2g_summary_updated.pdf", "pdf")
c_all.Print("b2g_summary_updated.png", "png")

