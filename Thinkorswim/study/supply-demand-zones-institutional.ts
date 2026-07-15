# =====================================================================
# Supply & Demand Zones - Institution-Grade Rewrite
# Demand Index (Sibbet) core + invalidating zones, VWAP value-area
# context, and a measurable hold-rate stat.
# Version 5.1
#
# Honest scope note: thinkorswim has no order-book / dark-pool / true
# volume-profile feed, so real institutional liquidity can't be read here.
# The closest native "value area" proxy is a volume-weighted VWAP +/- sigma
# band, included below. Treat this as a DISCRETIONARY CONTEXT tool, validated
# by the on-chart hold-rate stat -- not a standalone signal.
#
# DISPLAY MODE (input ExtendRight):
#   - yes (default): show ONLY the latest demand + supply zone, each as one
#     clean ribbon extended to the right edge (the look in the reference chart).
#     NOTE: this latest-zone view is forward-looking and updates as new zones
#     form, so it is NOT backtestable as drawn -- it is a "current context" view.
#   - no: show every historical zone exactly where it was active (the
#     non-repainting, backtestable view). Use this mode to validate the edge.
#
# Other improvements vs the original:
#   - FIXED ANCHOR: a zone is pinned to its formation base and does NOT
#     trail to new highs/lows.
#   - INVALIDATION: a zone is marked broken once price closes through it;
#     the extended ribbon dims to gray when the latest zone is broken.
#   - PARAMETERIZED: all thresholds are inputs (no hardcoded -0.2 / 0.5).
#   - VALUE AREA: VWAP +/- sigma band as an institutional reference.
#   - MEASURABLE: zones formed / broken / hold-rate label to prove an edge.
# =====================================================================

# ============================
# USER INPUTS
# ============================
input n              = 5;     # Demand Index smoothing length
input CreateThresh   = 0.35;  # |DMI| crossover that CREATES a zone
input BaseBars       = 3;     # bars used to define a zone's base (anchor)
input UseAtrBuffer   = yes;   # require a close beyond zone by an ATR buffer to invalidate
input AtrBufferMult  = 0.10;  # ATR multiple added to the breach level (noise filter)
input AtrLength      = 14;
input VwapLength     = 100;   # rolling VWAP / value-area window
input VwapSigma      = 1.0;   # value-area band width in std devs (~1s ~ 68%)
input ResAtrMult     = 1.5;   # overhead-resistance band thickness (ATR)
input ShowVWAP       = yes;
input ShowResistance = yes;
input ShowLabels     = yes;
input ExtendRight    = yes;   # show ONLY the latest zone, extended to the right edge

# ============================
# CORE CALCULATIONS (Demand Index - unchanged math, parameterized)
# ============================
def h = high;
def l = low;
def c = close;
def v = volume;
def x = BarNumber();
def na = Double.NaN;

def atr = Average(TrueRange(h, c, l), AtrLength);
def buf = if UseAtrBuffer then AtrBufferMult * atr else 0;

# Weighted close & change rate
def wC  = (h + l + 2 * c) * 0.25;
def wCR = (wC - wC[1]) / Min(wC, wC[1]);
def cR  = 3 * wC / Average(Highest(h, 2) - Lowest(l, 2), n) * AbsValue(wCR);

# Volume ratio & volume-per-change
def vR    = v / Average(v, n);
def vPerC = vR / Exp(Min(88, cR));

# Buying / selling pressure
def buyP  = if wCR > 0 then vR else vPerC;
def sellP = if wCR > 0 then vPerC else vR;

def buyPres  = if IsNaN(buyPres[1])  then 0 else ((buyPres[1]  * (n - 1)) + buyP)  / n;
def sellPres = if IsNaN(sellPres[1]) then 0 else ((sellPres[1] * (n - 1)) + sellP) / n;

# Demand Index -> DMI in roughly [-1, +1]
def DI = if ((((sellPres[1] * (n - 1)) + sellP) / n - ((buyPres[1] * (n - 1)) + buyP) / n) > 0)
         then -(if sellPres != 0 then buyPres / sellPres else 1)
         else  (if buyPres  != 0 then sellPres / buyPres else 1);
def DMI = if IsNaN(c) then na else if DI < 0 then -1 - DI else 1 - DI;

# =====================================================================
# DEMAND ZONE - non-repainting state machine (form -> hold -> invalidate)
# =====================================================================
def dTrigger = DMI crosses below -CreateThresh;

def dActive;
def dHigh;
def dLow;
def dAge;
def dTouch;
def dFormed;
def dBroken;

if dTrigger {
    # New demand zone: anchor to the base of the last BaseBars and FIX it.
    dActive = 1;
    dHigh   = Highest(h, BaseBars);
    dLow    = Lowest(l, BaseBars);
    dAge    = 0;
    dTouch  = 0;
    dFormed = (if IsNaN(dFormed[1]) then 0 else dFormed[1]) + 1;
    dBroken =  if IsNaN(dBroken[1]) then 0 else dBroken[1];
} else if dActive[1] == 1 and c < dLow[1] - buf {
    # Breach: close below the zone (minus ATR buffer) invalidates it.
    dActive = 0;
    dHigh   = na;
    dLow    = na;
    dAge    = dAge[1];
    dTouch  = dTouch[1];
    dFormed = dFormed[1];
    dBroken = dBroken[1] + 1;
} else if dActive[1] == 1 {
    # Still active: hold the fixed anchor, age it, count fresh re-entries.
    dActive = 1;
    dHigh   = dHigh[1];
    dLow    = dLow[1];
    dAge    = dAge[1] + 1;
    dTouch  = dTouch[1] + (if l <= dHigh[1] and l[1] > dHigh[1] then 1 else 0);
    dFormed = dFormed[1];
    dBroken = dBroken[1];
} else {
    dActive = 0;
    dHigh   = na;
    dLow    = na;
    dAge    = 0;
    dTouch  = 0;
    dFormed = if IsNaN(dFormed[1]) then 0 else dFormed[1];
    dBroken = if IsNaN(dBroken[1]) then 0 else dBroken[1];
}

# ---- LATEST demand zone only, extended to the right edge (matches image) ----
# Find the most recent demand formation bar, then broadcast that one zone's
# high/low to every bar so we can draw a single ribbon from it to the right.
def dFormX        = HighestAll(if dTrigger then x else na);
def latestDemandH = HighestAll(if x == dFormX then dHigh else na);
def latestDemandL = HighestAll(if x == dFormX then dLow  else na);
# Is that latest zone still active (unbroken) as of the current bar?
def dCurActive    = HighestAll(if IsNaN(c[-1]) then dActive else na);

plot DZHigh = if ExtendRight then (if x >= dFormX then latestDemandH else na) else dHigh;
plot DZLow  = if ExtendRight then (if x >= dFormX then latestDemandL else na) else dLow;
DZHigh.SetLineWeight(2);
DZLow.SetLineWeight(2);
# Active zone = bright cyan; already broken = dim gray.
DZHigh.AssignValueColor(if !ExtendRight then (if dTouch == 0 then Color.CYAN else Color.GRAY)
                        else if dCurActive == 1 then Color.CYAN else Color.GRAY);
DZLow.AssignValueColor(if !ExtendRight then (if dTouch == 0 then Color.CYAN else Color.GRAY)
                        else if dCurActive == 1 then Color.CYAN else Color.GRAY);
AddCloud(DZHigh, DZLow, Color.CYAN, Color.CYAN);

# =====================================================================
# SUPPLY ZONE - non-repainting state machine
# =====================================================================
def sTrigger = DMI crosses above CreateThresh;

def sActive;
def sHigh;
def sLow;
def sAge;
def sTouch;
def sFormed;
def sBroken;

if sTrigger {
    sActive = 1;
    sHigh   = Highest(h, BaseBars);
    sLow    = Lowest(l, BaseBars);
    sAge    = 0;
    sTouch  = 0;
    sFormed = (if IsNaN(sFormed[1]) then 0 else sFormed[1]) + 1;
    sBroken =  if IsNaN(sBroken[1]) then 0 else sBroken[1];
} else if sActive[1] == 1 and c > sHigh[1] + buf {
    # Breach: close above the supply zone invalidates it.
    sActive = 0;
    sHigh   = na;
    sLow    = na;
    sAge    = sAge[1];
    sTouch  = sTouch[1];
    sFormed = sFormed[1];
    sBroken = sBroken[1] + 1;
} else if sActive[1] == 1 {
    sActive = 1;
    sHigh   = sHigh[1];
    sLow    = sLow[1];
    sAge    = sAge[1] + 1;
    sTouch  = sTouch[1] + (if h >= sLow[1] and h[1] < sLow[1] then 1 else 0);
    sFormed = sFormed[1];
    sBroken = sBroken[1];
} else {
    sActive = 0;
    sHigh   = na;
    sLow    = na;
    sAge    = 0;
    sTouch  = 0;
    sFormed = if IsNaN(sFormed[1]) then 0 else sFormed[1];
    sBroken = if IsNaN(sBroken[1]) then 0 else sBroken[1];
}

# ---- LATEST supply zone only, extended to the right edge (matches image) ----
def sFormX        = HighestAll(if sTrigger then x else na);
def latestSupplyH = HighestAll(if x == sFormX then sHigh else na);
def latestSupplyL = HighestAll(if x == sFormX then sLow  else na);
def sCurActive    = HighestAll(if IsNaN(c[-1]) then sActive else na);

plot SZHigh = if ExtendRight then (if x >= sFormX then latestSupplyH else na) else sHigh;
plot SZLow  = if ExtendRight then (if x >= sFormX then latestSupplyL else na) else sLow;
SZHigh.SetLineWeight(2);
SZLow.SetLineWeight(2);
SZHigh.AssignValueColor(if !ExtendRight then (if sTouch == 0 then Color.PINK else Color.GRAY)
                        else if sCurActive == 1 then Color.PINK else Color.GRAY);
SZLow.AssignValueColor(if !ExtendRight then (if sTouch == 0 then Color.PINK else Color.GRAY)
                        else if sCurActive == 1 then Color.PINK else Color.GRAY);
AddCloud(SZHigh, SZLow, Color.PINK, Color.PINK);

# =====================================================================
# OVERHEAD RESISTANCE - anchored to the LATEST supply zone, extended right
# =====================================================================
def resBand = ResAtrMult * atr;
plot ResLow  = if ShowResistance and x >= sFormX then latestSupplyH + buf           else na;
plot ResHigh = if ShowResistance and x >= sFormX then latestSupplyH + buf + resBand else na;
ResLow.SetDefaultColor(Color.ORANGE);
ResHigh.SetDefaultColor(Color.ORANGE);
ResLow.SetLineWeight(1);
ResHigh.SetLineWeight(1);
AddCloud(ResHigh, ResLow, Color.LIGHT_ORANGE, Color.LIGHT_ORANGE);

# =====================================================================
# VALUE-AREA PROXY - rolling volume-weighted VspyWAP +/- sigma band
# (closest native stand-in for an institutional value area)
# =====================================================================
def tp     = (h + l + c) / 3;
def vwap   = Sum(tp * v, VwapLength) / Sum(v, VwapLength);
def vwapSD = StDev(tp, VwapLength);

plot VWAPmid = if ShowVWAP then vwap else na;
plot VWAPup  = if ShowVWAP then vwap + VwapSigma * vwapSD else na;
plot VWAPdn  = if ShowVWAP then vwap - VwapSigma * vwapSD else na;
VWAPmid.SetDefaultColor(Color.YELLOW);
VWAPup.SetDefaultColor(Color.DARK_GRAY);
VWAPdn.SetDefaultColor(Color.DARK_GRAY);
VWAPmid.SetStyle(Curve.SHORT_DASH);
VWAPup.SetStyle(Curve.SHORT_DASH);
VWAPdn.SetStyle(Curve.SHORT_DASH);

# =====================================================================
# MEASURABLE STATS - prove (or disprove) an edge instead of trusting visuals
# =====================================================================
def dHold = if dFormed > 0 then (dFormed - dBroken) / dFormed * 100 else 0;
def sHold = if sFormed > 0 then (sFormed - sBroken) / sFormed * 100 else 0;

AddLabel(ShowLabels,
    "Demand: " + Round(latestDemandL, 2) + " - " + Round(latestDemandH, 2) +
    "  (" + (if dCurActive == 1 then "active" else "broken") + ")",
    Color.CYAN);

AddLabel(ShowLabels,
    "Supply: " + Round(latestSupplyL, 2) + " - " + Round(latestSupplyH, 2) +
    "  (" + (if sCurActive == 1 then "active" else "broken") + ")",
    Color.PINK);

AddLabel(ShowLabels,
    "Demand zones formed:" + Round(dFormed, 0) + " broken:" + Round(dBroken, 0) +
    " hold:" + Round(dHold, 0) + "%   |   " +
    "Supply formed:" + Round(sFormed, 0) + " broken:" + Round(sBroken, 0) +
    " hold:" + Round(sHold, 0) + "%",
    Color.LIGHT_GRAY);

# End Code
