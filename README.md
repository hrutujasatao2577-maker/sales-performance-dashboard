# Sales Performance Project

This project simulates the workflow of analyzing a 50,000+ row dataset and deploying an interactive dashboard, as highlighted in data analyst resumes.

## Features
- **Data Generation**: Generates 50,000+ rows of mock transactional data with realistic distributions and outliers.
- **Data Analysis**: Pandas scripts to clean the data, impute missing values, and calculate key performance metrics (profit margin, total cost, net sales).
- **Dashboard**: A sleek, interactive UI built with Streamlit and Plotly to showcase the insights.

## How to use

1. **Install Requirements**
```bash
pip install -r requirements.txt
```

2. **Generate the Data**
```bash
python data_generator.py
```
*(Produces `raw_sales_data.csv`)*

3. **Clean and Analyze**
```bash
python analyze_data.py
```
*(Produces `cleaned_sales_data.csv` and outputs terminal insights)*

4. **Run the Dashboard**
```bash
streamlit run app.py
```

### Note for Tableau / Power BI users:
You can take the `cleaned_sales_data.csv` and directly import it into Tableau or Power BI to build your own dashboard!
