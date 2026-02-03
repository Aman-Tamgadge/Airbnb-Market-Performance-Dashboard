# Airbnb Market Analysis Dashboard  

## 📌 Project Overview
This project analyzes Airbnb open data from Kaggle to uncover **market dynamics, host performance, pricing behavior, and availability trends**.  
The workflow starts with **data cleaning and transformation in Python**, storage in **PostgreSQL**, and **Power BI dashboards** for visualization and insights.  
The dataset was downloaded manually from Kaggle.

---

## ⚙️ Tech Stack
- **Python (ETL):** Data cleaning, feature engineering, transformations  
- **PostgreSQL:** Structured storage with fact/dimension schema  
- **Power BI:** Dashboard visualizations, DAX measures, calculated columns  
- **Dataset:** [Kaggle Airbnb Open Data](https://www.kaggle.com/datasets/arianazmoudeh/airbnbopendata)  

---

## 🏗️ Data Pipeline
1. **Download** Airbnb open dataset manually from Kaggle.  
2. **Transform** with Python (handle missing values, clean text, standardize categories, filter invalid geolocation & price ranges, create engineered features such as: `effective_nightly_price`, `minimum_booking`, `dpi`, `price_bucket`, `review_recency_days`).  
3. **Load** cleaned dataset into PostgreSQL with star-schema tables:  
   - `fact_listing`  
   - `dim_location`  
   - `dim_host`  
   - `dim_listing`  
4. **Visualize** insights in Power BI (KPIs, charts, filters, executive summary).  

---

## 📊 Dashboard Pages & Previews  

[Download Full Dashboard (PDF)](docs/airbnb_dashboard.pdf)

### 1. Executive Summary  
High-level insights & recommendations for decision-makers.  
![Executive Summary](docs/screenshots/summary.png)  

### 2. Market Overview  
KPIs + distribution of listings by borough and room type.  
![Market Overview](docs/screenshots/market.png)  

### 3. Pricing & Profitability  
Price ranges, average price dynamics, and premium segments.  
![Pricing & Profitability](docs/screenshots/pricing.png)  

### 4. Neighbourhood Insights  
Top neighbourhoods by listings, pricing, and concentration.  
![Neighbourhood Insights](docs/screenshots/neighbourhood.png)  

### 5. Host Performance  
Top hosts, Superhost share, and review-driven engagement.  
![Host Performance](docs/screenshots/host.png)  

### 6. Availability & Liquidity  
Booking availability distribution and calendar openness.  
![Availability & Liquidity](docs/screenshots/availability.png)  

---

## 📈 Key Insights (Summary)
- **Market Concentration:** Most listings are in Manhattan and Brooklyn.  
- **Pricing Consistency:** Nightly prices remain fairly stable across boroughs.  
- **Neighbourhood Leaders:** Bedford-Stuyvesant leads in listings, while New Dorp commands premium prices.  
- **Host Dynamics:** Few top hosts dominate reviews; Superhosts achieve higher ratings.  
- **Liquidity Gaps:** Many inactive listings inflate perceived supply.  

---

## ✅ Recommendations
1. Focus growth on Manhattan & Brooklyn, while supporting emerging neighbourhoods.  
2. Encourage accurate pricing & transparency to build guest trust.  
3. Incentivize hosts to update calendars and reduce ghost listings.  
4. Promote Superhost practices as benchmarks for new hosts.  
5. Balance portfolio by supporting both Entire Homes and Private Rooms.  

---

## 🚀 How to Run the Pipeline
1. Clone this repo.  
2. Create a `.env` file with PostgreSQL credentials:  
   ```ini
   PG_USER=your_user
   PG_PASS=your_password
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Run the pipeline:
  ```bash
   python airbnb.py
   ```
5. Open Power BI → connect to PostgreSQL → build visuals with provided schema.

---