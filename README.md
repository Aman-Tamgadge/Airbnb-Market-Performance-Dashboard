# Airbnb-Market-Performance-Dashboard
Airbnb Market Analysis Dashboard

📌 Project Overview

This project analyzes Airbnb open data from Kaggle to uncover market dynamics, host performance, pricing behavior, and availability trends.
The workflow starts with data cleaning and transformation in Python, storage in PostgreSQL, and Power BI dashboards for visualization and insights.
The dataset was downloaded manually from Kaggle.

⚙️ Tech Stack

Python (ETL): Data cleaning, feature engineering, transformations
PostgreSQL: Structured storage with fact/dimension schema
Power BI: Dashboard visualizations, DAX measures, calculated columns
Dataset: Kaggle Airbnb Open Data (https://www.kaggle.com/datasets/arianazmoudeh/airbnbopendata)
🏗️ Data Pipeline

Download Airbnb open dataset manually from Kaggle.
Transform with Python (handle missing values, clean text, standardize categories, filter invalid geolocation & price ranges, create engineered features such as: effective_nightly_price, minimum_booking, dpi, price_bucket, review_recency_days).
Load cleaned dataset into PostgreSQL with star-schema tables:
fact_listing
dim_location
dim_host
dim_listing
Visualize insights in Power BI (KPIs, charts, filters, executive summary).
📊 Dashboard Pages & Previews

Download Full Dashboard (PDF)

1. Executive Summary

High-level insights & recommendations for decision-makers.
Executive Summary

2. Market Overview

KPIs + distribution of listings by borough and room type.
Market Overview

3. Pricing & Profitability

Price ranges, average price dynamics, and premium segments.
Pricing & Profitability

4. Neighbourhood Insights

Top neighbourhoods by listings, pricing, and concentration.
Neighbourhood Insights

5. Host Performance

Top hosts, Superhost share, and review-driven engagement.
Host Performance

6. Availability & Liquidity

Booking availability distribution and calendar openness.
Availability & Liquidity

📈 Key Insights (Summary)

Market Concentration: Most listings are in Manhattan and Brooklyn.
Pricing Consistency: Nightly prices remain fairly stable across boroughs.
Neighbourhood Leaders: Bedford-Stuyvesant leads in listings, while New Dorp commands premium prices.
Host Dynamics: Few top hosts dominate reviews; Superhosts achieve higher ratings.
Liquidity Gaps: Many inactive listings inflate perceived supply.
✅ Recommendations

Focus growth on Manhattan & Brooklyn, while supporting emerging neighbourhoods.
Encourage accurate pricing & transparency to build guest trust.
Incentivize hosts to update calendars and reduce ghost listings.
Promote Superhost practices as benchmarks for new hosts.
Balance portfolio by supporting both Entire Homes and Private Rooms.
🚀 How to Run the Pipeline

Clone this repo.
Create a .env file with PostgreSQL credentials:
PG_USER=your_user
PG_PASS=your_password
Install dependencies
pip install -r requirements.txt
Run the pipeline:
 python airbnb.py
Open Power BI → connect to PostgreSQL → build visuals with provided schema.
