import json
import pandas as pd
import concurrent.futures
from preprocessAPI import data_preprocessing, prediction

data = ["Good", "No", "Low_spent_Small_value_payments", 23, 3, 4, 3, 4, 3, 7, 11.27, 5, 809.98, 1824.80, 186.26, 236.64, 49.50, 216]

columns = [
    "Credit_Mix", "Payment_of_Min_Amount", "Payment_Behaviour", "Age", "Num_Bank_Accounts", "Num_Credit_Card",
    "Interest_Rate", "Num_of_Loan", "Delay_from_due_date", "Num_of_Delayed_Payment", "Changed_Credit_Limit",
    "Num_Credit_Inquiries", "Outstanding_Debt", "Monthly_Inhand_Salary", "Monthly_Balance",
    "Amount_invested_monthly", "Total_EMI_per_month", "Credit_History_Age"
]
df = pd.DataFrame([data], columns=columns)
new_data = data_preprocessing(data=df)

# Konversi DataFrame ke format JSON yang diinginkan
json_output = {
    "dataframe_split": {
        "columns": new_data.columns.tolist(),
        "data": new_data.values.tolist()
    }
}
data_testing = json.dumps(json_output)

def test_prediction():
    """Fungsi untuk menjalankan prediction secara concurrent."""
    return prediction(data_testing)

# Menjalankan concurrent testing
NUM_THREADS = 100  # Sesuaikan dengan jumlah thread yang diinginkan

with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [executor.submit(test_prediction) for _ in range(NUM_THREADS)]
    
    # Mengambil hasil eksekusi
    results = [future.result() for future in concurrent.futures.as_completed(futures)]

# Menampilkan hasil
for i, result in enumerate(results):
    print(f"Result {i+1}: {result}")
