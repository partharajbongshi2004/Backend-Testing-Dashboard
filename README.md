# 🧪 Clothing Store Backend Testing Dashboard

A production-ready **Automated QA & Backend Testing Dashboard** built with **Python**, **Pytest**, and **Streamlit**. 

This project showcases clean, modular backend business logic for a Clothing Store Management System paired with an interactive QA dashboard that executes automated unit and integration tests in real time, visualizes test coverage and latency, and displays full execution logs.

---

## ✨ Key Features

* **⚡ Real-Time Pytest Execution:** Run the entire automated test suite—or filter by specific test classes—directly from the browser with a single click.
* **📊 Live QA Metrics & Charts:** Tracks **Total Tests**, **Passed**, **Failed**, and **Execution Time (ms)** alongside visual breakdowns by test suite and execution latency.
* **🛡️ Defensive Backend Logic (`backend_app.py`):** Clean, type-hinted business functions with custom exception handling (`StoreValidationError`) for invalid inputs and edge cases.
* **🔬 Comprehensive Test Coverage (`test_backend.py`):** Covers happy paths, boundary conditions, parameterized inputs, and exception assertions across 4 core test suites.
* **☁️ Streamlit Cloud Ready:** Uses relative path resolution (`pathlib.Path`) and active interpreter execution (`sys.executable -m pytest`) for zero-configuration deployment on Streamlit Community Cloud.

---

## 🏗️ Repository Structure

```text
clothing-store-qa-dashboard/
├── app.py               # Interactive Streamlit QA Dashboard & subprocess test runner
├── backend_app.py       # Core Clothing Store business logic & custom validation errors
├── test_backend.py      # Automated Pytest unit & integration test suites
├── requirements.txt     # Python package dependencies
└── README.md            # Project documentation
```

---

## 🧩 Tested Backend Modules & Suites

| Test Suite | Backend Function | What It Validates |
| :--- | :--- | :--- |
| **`TestDiscountCalculation`** | `calculate_discount()` | Promo code tiers (`WELCOME10`, `VIP20`, `SEASONAL30`), case normalization, zero prices, negative prices, and invalid codes. |
| **`TestInventoryStatus`** | `check_inventory_status()` | `IN_STOCK`, `LOW_STOCK` boundary thresholds, `OUT_OF_STOCK` alerts, reorder flags, and negative/invalid SKUs. |
| **`TestUserCredentials`** | `validate_user_credentials()` | Email regex validation, password strength (8+ chars, uppercase, numeric digit), and role authorization (`admin`, `manager`, `cashier`, `customer`). |
| **`TestOrderTotalIntegration`** | `calculate_order_total()` | Multi-item cart subtotals, promo code stacking, regional tax calculation, rounding precision, and empty cart guards. |

---

## 🚀 Getting Started Locally

### 1. Clone the Repository
```bash
git clone https://github.com
cd clothing-store-qa-dashboard
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the QA Dashboard
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

### *(Optional)* Run Tests via CLI
You can also execute the test suite directly in your terminal:
```bash
pytest test_backend.py -v
```

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push all files (`app.py`, `backend_app.py`, `test_backend.py`, `requirements.txt`, and `README.md`) to a public or private **GitHub** repository.
2. Sign in to [Streamlit Community Cloud](https://streamlit.io) and click **New app**.
3. Select your repository, branch (`main`), and set **Main file path** to `app.py`.
4. Click **Deploy**.

---

## 🛠️ Tech Stack

* **Language:** Python 3.9+
* **Testing Framework:** [Pytest](https://pytest.org) & `pytest-json-report`
* **Dashboard UI:** [Streamlit](https://streamlit.io)
* **Data Processing:** [Pandas](https://pydata.org)

---

## 📄 License

This project is open-source and available under the [MIT License](https://opensource.org).
