# =====================================================================
# Relative Strength vs Benchmark - WATCHLIST CUSTOM COLUMN
# Version 3.0  (fixes the "shows NaN" problem)
#
# WHY v2 SHOWED NaN:
#   v2 normalized to 1..99 over a 3*252 = 756-bar (~3 year) rolling window.
#   Watchlist columns DO NOT load that much history (and the secondary SPX
#   series loads even less), so Lowest/Highest over 756 bars were NaN ->
#   the whole score was NaN. Self-normalizing to 1..99 cannot work in a
#   column; it needs deep per-symbol history a column does not have.
#
# v3 APPROACH (column-correct):
#   Output the RAW relative return (stock 12-mo return minus benchmark
#   12-mo return), in %. This needs only lookback+1 bars. Then SORT the
#   column: the RANK across rows IS the cross-sectional ranking (the closest
#   thing to IBD's universe percentile inside thinkorswim). Sort descending
#   -> leaders on top. Positive = outperforming the benchmark.
#
# HOW TO USE:
#   Watchlist -> gear -> Customize -> Add study filter -> Custom -> paste.
#   Set the column aggregation to Daily (D). Sort by this column descending.
#
# IF A CELL IS STILL BLANK:
#   that symbol lacks `lookback` daily bars (recent IPO, or the column did
#   not load enough history) -> correctly left blank instead of guessing.
#   Lower `lookback` to use a shorter window if you need a value.
# =====================================================================

input benchmark         = "SPX";  # Benchmark symbol
input lookback          = 252;    # 12 months of DAILY bars (set column tf = Day)
input useWeightedReturn = no;     # IBD-style quarter-weighted return (needs 252 bars)
input displayScale      = 100;    # output as a percentage

def stockClose = close;
def benchClose = close(symbol = benchmark);

# Historical anchors (constant offsets are the most reliable on a secondary symbol).
def stockPast = stockClose[lookback];
def benchPast = benchClose[lookback];

# Valid only if BOTH endpoints exist and are non-zero (no div-by-zero / stale data).
def ok = !IsNaN(stockPast) and !IsNaN(benchPast) and stockPast != 0 and benchPast != 0;

# --- simple 12-month relative return ---
def stockRetSimple = stockClose / stockPast - 1;
def benchRetSimple = benchClose / benchPast - 1;

# --- optional IBD-style quarter-weighted return (recent quarter 2x) ---
def s63  = stockClose[63];   def b63  = benchClose[63];
def s126 = stockClose[126];  def b126 = benchClose[126];
def s189 = stockClose[189];  def b189 = benchClose[189];
def weightOk = useWeightedReturn
           and !IsNaN(s63)  and s63  != 0
           and !IsNaN(s126) and s126 != 0
           and !IsNaN(s189) and s189 != 0
           and !IsNaN(stockPast) and stockPast != 0
           and !IsNaN(b63)  and b63  != 0
           and !IsNaN(b126) and b126 != 0
           and !IsNaN(b189) and b189 != 0
           and !IsNaN(benchPast) and benchPast != 0;

def stockRetW = 0.4 * (stockClose / s63  - 1)
              + 0.2 * (stockClose / s126 - 1)
              + 0.2 * (stockClose / s189 - 1)
              + 0.2 * (stockClose / stockPast - 1);
def benchRetW = 0.4 * (benchClose / b63  - 1)
              + 0.2 * (benchClose / b126 - 1)
              + 0.2 * (benchClose / b189 - 1)
              + 0.2 * (benchClose / benchPast - 1);

def relReturn =
    if weightOk then stockRetW - benchRetW
    else if ok  then stockRetSimple - benchRetSimple
    else Double.NaN;

# Single sortable value: relative outperformance vs the benchmark, in %.
# Positive = outperforming over the window; sort descending for leaders.
plot RS = if IsNaN(relReturn) then Double.NaN else Round(relReturn * displayScale, 1);

# Cell color: green = outperforming, red = lagging, yellow ~ in line.
RS.AssignValueColor(
    if IsNaN(RS) then Color.GRAY
    else if RS >= 10 then Color.GREEN
    else if RS <= -10 then Color.RED
    else Color.YELLOW
);

# End Code
