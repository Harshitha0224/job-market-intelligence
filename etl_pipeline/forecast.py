import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# 1. Connect to MySQL
db_connection_str = 'mysql+mysqlclient://root:pass@localhost/job_trends'
db_connection = create_engine(db_connection_str)

# 2. Load Data (Grouped by Date)
query = "SELECT posted_date as ds, COUNT(*) as y FROM master_job_list GROUP BY posted_date"
df = pd.read_sql(query, db_connection)

# 3. Train Model
m = Prophet()
m.fit(df)

# 4. Predict Next 30 Days
future = m.make_future_dataframe(periods=30)
forecast = m.predict(future)

# 5. Visualize & Save
fig1 = m.plot(forecast)
plt.title("30-Day Job Market Forecast")
plt.savefig("../sql_analytics/forecast_chart.png") # Save inside your analytics folder
print("Forecast generated and saved!")