# =====================================================================
# Self-Normalized Relative Strength vs Benchmark (IBD-style approximation)
# Version 2.0
#
# HONEST NAMING: This is NOT the real IBD RS Rating. True IBD RS is a
# CROSS-SECTIONAL percentile vs the ENTIRE market universe (RS 90 =
# outperformed 90% of all stocks). A single TOS study cannot see the whole
# universe, so this normalizes each stock against ITS OWN trailing range.
# => The number is comparable to this symbol's own history, NOT between
#    different tickers. For a true universe percentile, use a watchlist
#    scan/custom column or external data.
#
# Fixes vs the original "IBD-Style RS Rating":
#   - INTRADAY GATING: intraday charts no longer borrow the 252-bar daily
#     lookback (which was only ~3 days of 5-min bars). Intraday shows N/A.
#   - AGGREGATION FALL-THROUGH: non day/week/month charts no longer silently
#     use the monthly (12) lookback. They are treated as unsupported (N/A).
#   - DUAL-ENDPOINT BENCHMARK CHECK: validate the benchmark NOW and at the
#     lookback bar, so a stale/NaN historical value can't produce garbage.
#   - NAN-AWARE WARM-UP: the score only shows once enough history exists for
#     BOTH the return window and the normalization window.
#   - WEIGHTED RETURN (optional): IBD-style quarter-weighted performance
#     (recent quarter double-weighted) instead of one endpoint-sensitive
#     point-to-point return.
# =====================================================================

declare lower;

input benchmark        = "SPX";   # Benchmark symbol
input lookbackDaily    = 252;     # 12 months (252 trading days)
input lookbackWeekly   = 52;      # 12 months (52 weeks)
input lookbackMonthly  = 12;      # 12 months
input normWindowMult   = 3;       # normalization window = this * lookback
input useWeightedReturn = yes;    # IBD-style quarter-weighted return (daily only)
input strongLevel      = 80;      # IBD "leader" threshold (green)
input weakLevel        = 30;      # underperformer threshold (red)

# ---------------------------------------------------------------------
# Chart-type detection (explicit, no silent fall-through)
# ---------------------------------------------------------------------
def agg        = GetAggregationPeriod();
def isIntraday = agg < AggregationPeriod.DAY;
def isDaily    = agg == AggregationPeriod.DAY;
def isWeekly   = agg == AggregationPeriod.WEEK;
def isMonthly  = agg == AggregationPeriod.MONTH;
def isSupported = isDaily or isWeekly or isMonthly;   # day/week/month only

def lookback =
    if isDaily   then lookbackDaily
    else if isWeekly  then lookbackWeekly
    else if isMonthly then lookbackMonthly
    else Double.NaN;                                   # unsupported -> NaN

# ---------------------------------------------------------------------
# Prices (stock + benchmark on the same aggregation)
# ---------------------------------------------------------------------
def stockClose = close;
def benchClose = close(symbol = benchmark);

# Benchmark must be valid NOW *and* at the lookback bar (fixes the
# single-bar-only validity check in the original).
def benchOk = isSupported
          and !IsNaN(benchClose)
          and !IsNaN(GetValue(benchClose, lookback));

# ---------------------------------------------------------------------
# Relative return: stock return minus benchmark return over the lookback
# ---------------------------------------------------------------------
# Point-to-point (used for weekly/monthly, or when weighting is off).
def haveReturnHist = isSupported and BarNumber() > lookback;
def stockRetSimple = if haveReturnHist then stockClose / stockClose[lookback] - 1 else Double.NaN;
def benchRetSimple = if haveReturnHist and benchOk then benchClose / benchClose[lookback] - 1 else Double.NaN;

# IBD-style quarter-weighted return (daily only; quarters of 63 trading days).
# 0.4*Q1 + 0.2*Q2 + 0.2*Q3 + 0.2*Q4, recent quarter double-weighted.
def canWeight   = useWeightedReturn and isDaily and BarNumber() > 252;
def stockRetW = if canWeight then
        0.4 * (stockClose / stockClose[63]  - 1)
      + 0.2 * (stockClose / stockClose[126] - 1)
      + 0.2 * (stockClose / stockClose[189] - 1)
      + 0.2 * (stockClose / stockClose[252] - 1)
    else Double.NaN;
def benchRetW = if canWeight and benchOk then
        0.4 * (benchClose / benchClose[63]  - 1)
      + 0.2 * (benchClose / benchClose[126] - 1)
      + 0.2 * (benchClose / benchClose[189] - 1)
      + 0.2 * (benchClose / benchClose[252] - 1)
    else Double.NaN;

def stockReturn = if canWeight then stockRetW else stockRetSimple;
def benchReturn = if canWeight then benchRetW else benchRetSimple;
def relReturn   = stockReturn - benchReturn;

# ---------------------------------------------------------------------
# Normalize to 1..99 over a rolling window, but ONLY across bars that
# actually have a value (NaN-aware), so warm-up NaNs don't poison min/max.
# ---------------------------------------------------------------------
def normWindow = normWindowMult * lookback;
def hasRel     = !IsNaN(relReturn);

# Only start scoring once the normalization window is fully populated with
# real (non-NaN) relative returns.
def filledBars = if hasRel then (if IsNaN(filledBars[1]) then 1 else filledBars[1] + 1) else 0;
def windowReady = filledBars >= normWindow;

def minReturn = if hasRel then Lowest(relReturn, normWindow) else Double.NaN;
def maxReturn = if hasRel then Highest(relReturn, normWindow) else Double.NaN;

def RS_Score =
    if !windowReady or !benchOk then Double.NaN
    else if maxReturn == minReturn then 50
    else Round(99 * (relReturn - minReturn) / (maxReturn - minReturn), 0);

def boundedRS = if IsNaN(RS_Score) then Double.NaN else Max(1, Min(99, RS_Score));

# ---------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------
plot RS_Rating = boundedRS;
RS_Rating.SetPaintingStrategy(PaintingStrategy.LINE);
RS_Rating.SetLineWeight(3);
RS_Rating.AssignValueColor(
    if boundedRS >= strongLevel then Color.GREEN
    else if boundedRS <= weakLevel then Color.RED
    else Color.YELLOW
);

# Reference levels
plot StrongRef = if isSupported then strongLevel else Double.NaN;
plot WeakRef   = if isSupported then weakLevel   else Double.NaN;
StrongRef.SetDefaultColor(Color.DARK_GREEN);
WeakRef.SetDefaultColor(Color.DARK_RED);
StrongRef.SetStyle(Curve.SHORT_DASH);
WeakRef.SetStyle(Curve.SHORT_DASH);
StrongRef.HideBubble();
WeakRef.HideBubble();

# ---------------------------------------------------------------------
# Status label (honest about state)
# ---------------------------------------------------------------------
AddLabel(yes,
    if !isSupported then
        "RS: N/A (use Day/Week/Month chart)"
    else if !benchOk then
        "RS: N/A (benchmark " + benchmark + " data missing)"
    else if !windowReady then
        "RS: warming up (" + Round(filledBars, 0) + "/" + Round(normWindow, 0) + " bars)"
    else
        "RS vs " + benchmark + ": " + Round(boundedRS, 0) +
        (if useWeightedReturn and isDaily then "  [weighted]" else "  [12mo]"),
    if !isSupported or !benchOk or !windowReady then Color.GRAY
    else if boundedRS >= strongLevel then Color.GREEN
    else if boundedRS <= weakLevel then Color.RED
    else Color.YELLOW
);

# Reminder that this is self-normalized, not a market-wide percentile.
AddLabel(yes, "self-normalized (not cross-ticker)", Color.GRAY);

# End Code
