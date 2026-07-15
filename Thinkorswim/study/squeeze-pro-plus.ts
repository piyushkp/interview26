# =====================================================================
# ST_SqueezePRO+  (enhanced)
# Based on Simpler Trading "Squeeze Pro" (c) 2019 Simpler Trading, LLC.
# Original methodology unchanged; this adds usability only.
#
# Improvements vs the original:
#   - REAL INPUTS: length / nBB / Keltner factors are now editable inputs
#     (were hardcoded def's), so you can tune per timeframe.
#   - SPLIT ALERTS: separate toggles for "entered squeeze" vs "squeeze fired"
#     (the tradeable release), with a tier selector (was one all-or-nothing
#     toggle). Entry alerts default off, fire alerts on.
#   - FIRE MARKERS: the squeeze RELEASE bar is now drawn (white dot on the
#     zero line) instead of only triggering a silent alert -- that release is
#     the actionable moment.
#   - DIRECTION REMINDER: the histogram shows momentum and the dots show
#     COMPRESSION; NEITHER shows breakout direction. Pair with a trend filter.
#
# Methodology preserved exactly:
#   Squeeze = Bollinger Band width inside Keltner Channel width.
#   Three tiers by Keltner factor: 1.0 high/orange, 1.5 mid/red, 2.0 low/black.
# =====================================================================

declare lower;

# ---------- INPUTS (were hardcoded def's) ----------
input length   = 20;     # BB / KC length
input nBB      = 2.0;    # Bollinger std-dev multiplier
input nK_High  = 1.0;    # tightest Keltner factor -> "high"/extreme squeeze (orange)
input nK_Mid   = 1.5;    # original TTM squeeze (red)
input nK_Low   = 2.0;    # widest Keltner factor -> loosest squeeze (black)

input enableEntryAlerts = no;          # alert when a squeeze STARTS
input enableFireAlerts  = yes;         # alert when a squeeze FIRES (releases)
input alertTier         = {default Mid, Low, High, Any};  # which tier alerts use
input showFireMarkers   = yes;         # draw the release bar on the zero line
input showHTF           = yes;         # show a higher-timeframe squeeze-state label
input htfAggregation    = AggregationPeriod.DAY;  # the higher timeframe to read

def price = close;

# ---------- MOMENTUM HISTOGRAM (unchanged) ----------
def momentum = TTM_Squeeze(price = price, length = length, nk = nK_Mid, nbb = nBB)."Histogram";
plot oscillator = momentum;
oscillator.DefineColor("Up", CreateColor(0, 255, 255));
oscillator.DefineColor("UpDecreasing", CreateColor(0, 0, 255));
oscillator.DefineColor("Down", CreateColor(255, 0, 0));
oscillator.DefineColor("DownDecreasing", CreateColor(255, 255, 0));
oscillator.AssignValueColor(
    if oscillator[1] < oscillator then
        if oscillator >= 0 then oscillator.Color("Up") else oscillator.Color("DownDecreasing")
    else
        if oscillator >= 0 then oscillator.Color("UpDecreasing") else oscillator.Color("Down"));
oscillator.SetPaintingStrategy(PaintingStrategy.HISTOGRAM);
oscillator.SetLineWeight(5);

# ---------- SQUEEZE TIERS: BB width vs KC width (unchanged math) ----------
def BolKelDelta_Mid  = reference BollingerBands("num_dev_up" = nBB, "length" = length)."upperband"
                     - KeltnerChannels("factor" = nK_Mid,  "length" = length)."Upper_Band";
def BolKelDelta_Low  = reference BollingerBands("num_dev_up" = nBB, "length" = length)."upperband"
                     - KeltnerChannels("factor" = nK_Low,  "length" = length)."Upper_Band";
def BolKelDelta_High = reference BollingerBands("num_dev_up" = nBB, "length" = length)."upperband"
                     - KeltnerChannels("factor" = nK_High, "length" = length)."Upper_Band";

# Squeeze dots on the zero line, colored by tightest active tier.
plot squeeze = if IsNaN(close) then Double.NaN else 0;
squeeze.DefineColor("NoSqueeze", Color.GREEN);
squeeze.DefineColor("SqueezeLow", Color.BLACK);
squeeze.DefineColor("SqueezeMid", Color.RED);
squeeze.DefineColor("SqueezeHigh", Color.ORANGE);
squeeze.AssignValueColor(
    if BolKelDelta_High <= 0 then squeeze.Color("SqueezeHigh")
    else if BolKelDelta_Mid <= 0 then squeeze.Color("SqueezeMid")
    else if BolKelDelta_Low <= 0 then squeeze.Color("SqueezeLow")
    else squeeze.Color("NoSqueeze"));
squeeze.SetPaintingStrategy(PaintingStrategy.POINTS);
squeeze.SetLineWeight(3);

# ---------- ENTER / FIRE EVENTS (unchanged) ----------
def enteredHighSqueeze = BolKelDelta_High <= 0 and BolKelDelta_High[1] > 0;
def enteredMidSqueeze  = BolKelDelta_Mid  <= 0 and BolKelDelta_Mid[1]  > 0;
def enteredLowSqueeze  = BolKelDelta_Low  <= 0 and BolKelDelta_Low[1]  > 0;

def exitedHighSqueeze = BolKelDelta_High > 0 and BolKelDelta_High[1] <= 0;
def exitedMidSqueeze  = BolKelDelta_Mid  > 0 and BolKelDelta_Mid[1]  <= 0;
def exitedLowSqueeze  = BolKelDelta_Low  > 0 and BolKelDelta_Low[1]  <= 0;

# ---------- FIRE MARKER: draw the release bar (new) ----------
# The mid-tier release is the classic "squeeze fired" trigger.
plot Fire = if showFireMarkers and exitedMidSqueeze then 0 else Double.NaN;
Fire.SetPaintingStrategy(PaintingStrategy.POINTS);
Fire.SetDefaultColor(Color.WHITE);
Fire.SetLineWeight(5);
Fire.HideBubble();

# ---------- ALERTS: split entry vs fire, per chosen tier, with sound ----------
def entered =
    if alertTier == alertTier.High then enteredHighSqueeze
    else if alertTier == alertTier.Low then enteredLowSqueeze
    else if alertTier == alertTier.Any then (enteredHighSqueeze or enteredMidSqueeze or enteredLowSqueeze)
    else enteredMidSqueeze;

def fired =
    if alertTier == alertTier.High then exitedHighSqueeze
    else if alertTier == alertTier.Low then exitedLowSqueeze
    else if alertTier == alertTier.Any then (exitedHighSqueeze or exitedMidSqueeze or exitedLowSqueeze)
    else exitedMidSqueeze;

# Note: thinkScript requires a LITERAL Sound.* constant in Alert() -- it cannot
# be a variable -- so the sounds are fixed (Ding for entry, Bell for fire).
Alert(enableEntryAlerts and entered, "Squeeze entered (" + alertTier + ")", Alert.BAR, Sound.Ding);
Alert(enableFireAlerts and fired,    "Squeeze FIRED ("   + alertTier + ")", Alert.BAR, Sound.Bell);

# ---------- CONTEXT LABEL ----------
AddLabel(yes,
    "Squeeze: " +
    (if BolKelDelta_High <= 0 then "HIGH/extreme"
     else if BolKelDelta_Mid <= 0 then "MID"
     else if BolKelDelta_Low <= 0 then "LOW"
     else "none") +
    "   (dots=compression, histogram=momentum -- NOT direction)",
    if BolKelDelta_High <= 0 then Color.ORANGE
    else if BolKelDelta_Mid <= 0 then Color.RED
    else if BolKelDelta_Low <= 0 then Color.GRAY
    else Color.GREEN);

# ---------- HIGHER-TIMEFRAME SQUEEZE STATE (multi-timeframe confluence) ----------
# Read the same BB-vs-Keltner squeeze on a higher aggregation (default Daily).
# Squeeze setups that stack across timeframes are the strongest; this lets you
# see the HTF compression tier while trading a lower timeframe. Uses a secondary
# series, so it only updates on the lower chart's bars (a known TOS limitation).
def htfClose = close(period = htfAggregation);
# Compute BB/KC tiers on the HTF series (BB = SMA +/- nBB*StDev; KC = SMA + factor*ATR).
def htfBasis = Average(htfClose, length);
def htfRange = Average(TrueRange(high(period = htfAggregation), htfClose, low(period = htfAggregation)), length);
def htfBBupper = htfBasis + nBB * StDev(htfClose, length);
def htfHigh = htfBBupper - (htfBasis + nK_High * htfRange);
def htfMid  = htfBBupper - (htfBasis + nK_Mid  * htfRange);
def htfLow  = htfBBupper - (htfBasis + nK_Low  * htfRange);

AddLabel(showHTF,
    "HTF Squeeze: " +
    (if htfHigh <= 0 then "HIGH/extreme"
     else if htfMid <= 0 then "MID"
     else if htfLow <= 0 then "LOW"
     else "none"),
    if htfHigh <= 0 then Color.ORANGE
    else if htfMid <= 0 then Color.RED
    else if htfLow <= 0 then Color.LIGHT_GRAY
    else Color.GREEN);

# End Code
