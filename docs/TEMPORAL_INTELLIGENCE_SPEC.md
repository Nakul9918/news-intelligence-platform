# Temporal Intelligence Product & Architecture Specification

## 1. Business & Analytic Purpose
The **Trend & Temporal Intelligence** module provides real-time and historical news volume dynamics, trend direction, statistical anomaly detection (spikes), emerging keyword/entity tracking, and cross-source topic correlation. It transforms unstructured real-time news data into explainable, verifiable intelligence signals.

## 2. Core Business Questions Answered
1. **What is happening?** (Top trending topics & multi-publisher events)
2. **When did it happen?** (Time-series volume distribution & bucketed timelines)
3. **Is it increasing or decreasing?** (Deterministic trend direction: `RISING`, `STABLE`, `DECLINING`, or `INSUFFICIENT BASELINE`)
4. **Is the change unusual?** (Statistical spike detection using rolling mean $\mu$ and standard deviation $\sigma$: $\text{Threshold} = \mu + 2\sigma$)
5. **Which source / category / topic caused the change?** (Source share breakdowns, category distributions)
6. **Which articles are responsible?** (Full evidence drill-down lineage: `TREND` $\rightarrow$ `EXPLANATION` $\rightarrow$ `EVIDENCE` $\rightarrow$ `ARTICLE`)
7. **Can the user verify the insight?** (Transparent mathematical formulas & data quality metrics)

---

## 3. Data Contract & Canonical Timestamp
- **PRIMARY TIME FIELD**: `published_date`
- **FALLBACK TIME FIELD**: `created_at` $\rightarrow$ `updated_at` $\rightarrow$ `fetched_at`
- **TIMEZONE**: `UTC`
- **DATE PARSING RULES**:
  - BSON `datetime.datetime` objects are normalized to UTC `tz-aware` (`dt.replace(tzinfo=timezone.utc)` if naive).
  - String timestamps are parsed via ISO-8601 or fallback `dateutil.parser`.
- **DATA QUALITY TRACEABILITY**:
  - Exposes `processed_count`, `valid_date_count`, `fallback_date_count`, `invalid_date_count`, and `valid_date_pct`.
  - Emits a visual data-quality notice if `valid_date_pct < 90%`.

---

## 4. Time Window & Granularity Matrix

| Time Window Preset | Window Duration | Recommended Bucket Granularity |
| :--- | :--- | :--- |
| **Last 24 Hours / Today** | 24 Hours | `1h` (Hourly - 24 buckets) |
| **Last 7 Days** | 7 Days | `1d` (Daily - 7 buckets) |
| **Last 30 Days / This Month** | 30 Days | `1d` (Daily - 30 buckets) |
| **Last 3 Months** | 90 Days | `1w` (Weekly - ~13 buckets) |
| **This Year / 12 Months** | 365 Days | `1m` (Monthly - 12 buckets) |
| **Custom Range** | User Defined | User Selectable (`1h`, `1d`, `1w`, `1m`) |

---

## 5. Mathematical Algorithms & Formulas

### 5.1 Deterministic Trend Direction
$$\text{Growth \%} = \frac{\text{Current Period Volume} - \text{Previous Period Volume}}{\max(\text{Previous Period Volume}, 1)} \times 100$$

- **`RISING`**: $\text{Growth \%} \ge +10.0\%$ (requires Previous Volume $\ge 3$)
- **`DECLINING`**: $\text{Growth \%} \le -10.0\%$ (requires Previous Volume $\ge 3$)
- **`STABLE`**: $-10.0\% < \text{Growth \%} < +10.0\%$
- **`INSUFFICIENT BASELINE`**: Previous Volume $< 3$ articles.

### 5.2 Statistical Spike Intelligence ($\mu + 2\sigma$)
$$\mu = \frac{1}{N}\sum_{i=1}^{N} x_i, \quad \sigma = \sqrt{\frac{1}{N}\sum_{i=1}^{N}(x_i - \mu)^2}$$
$$\text{Spike Threshold} = \max(\mu + 2\sigma, \, 1.5 \times \mu)$$

- **`UNUSUAL_ACTIVITY`**: Current Volume $\ge \text{Spike Threshold}$ (and Current Volume $\ge 5$).
- **`NORMAL`**: Current Volume $< \text{Spike Threshold}$.
- **`INSUFFICIENT BASELINE`**: Total historical buckets $N < 5$.

### 5.3 Emerging Keyword & Entity Growth
$$\text{Keyword Growth \%} = \frac{\text{Recent Mentions} - \text{Baseline Mentions}}{\max(\text{Baseline Mentions}, 1)} \times 100$$
- If Total Mentions $< 4$, tagged with `LOW CONFIDENCE`.

---

## 6. API Endpoints Contract

1. `GET /api/analytics/volume?window=24h&bucket=1h`
2. `GET /api/analytics/source-trends?window=24h&bucket=1h`
3. `GET /api/analytics/category-trends?window=24h&bucket=1h`
4. `GET /api/analytics/sentiment-trends?window=24h&bucket=1h`
5. `GET /api/analytics/spikes?window=24h`
6. `GET /api/analytics/keywords?window=24h`
7. `GET /api/analytics/entities?window=24h`
8. `GET /api/analytics/cross-source?window=24h`
9. `GET /api/analytics/trend-explanation?item_type=overall&item_name=all`

---

## 7. Evidence & Drill-Down Lineage
Every visual alert or trend metric in **06. TRENDS & TEMPORAL** links directly to an explanation drawer:
- **Mathematical Formula & Parameters**
- **Historical Baseline Stats** ($\mu, \sigma, N$)
- **Top Responsible Sources**
- **Top Responsible NLP Categories**
- **Top Responsible Keywords & Entities**
- **Full Article Evidence List** (Headlines, Published Dates, Summaries, Links)
