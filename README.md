![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)

# 💰 Smart Expense Tracker
# 💰 Smart Expense Tracker

A Python-based personal finance application built with **Streamlit, Pandas, and SQLite** to help users track expenses, monitor spending habits, manage budgets, and plan savings.

## ✨ Features

- 📊 **Expense Tracking** — Record and manage personal expenses.
- 📈 **Spending Analytics** — Visualize spending patterns and expense summaries.
- 🤖 **AI Insights** — Explore financial insights provided by the application.
- 🎯 **Savings Goal Planner** — Set monthly savings goals and track progress.
- 💡 **Budget Monitoring** — Review spending and stay aware of your budget.
- 🎨 **Theme Settings** — Customize the application theme.
- 💾 **Local Data Storage** — Store expense data using SQLite.
- 🧪 **Database Tests** — Test core database functionality.

## 📸 Screenshots

### 🏠 Dashboard
Track income, expenses, current balance, and recent transactions.

![Smart Expense Tracker Dashboard](screenshots/dashboard.png)

### 📊 Spending Analytics
Visualize category-wise expenses and monthly spending trends.

![Spending Analytics](screenshots/analytics.png)

### 🤖 Smart Expense Insights
View spending summaries, estimated month-end expenses, and rule-based recommendations.

![Smart Expense Insights](screenshots/ai-insights.png)

### 🎯 Savings Goal Planner
Set monthly spending-reduction targets and monitor progress.

![Savings Goal Planner](screenshots/savings-goal.png)

### ⚙️ Profile & Settings
Customize your display name and application theme.

![Profile and Settings](screenshots/profile-settings.png)

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| Pandas | Data processing and analysis |
| SQLite | Local database storage |
| Plotly | Interactive data visualizations |

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or a compatible version
- Git
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Rajukumar1202/smart-expense-tracker.git
cd smart-expense-tracker
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser. If it does not open automatically, follow the local URL displayed in the terminal.

## 🧪 Run Tests

Run the database tests with:

```bash
python -m pytest test_database.py -v
```

If pytest is not installed, install it first:

```bash
python -m pip install pytest
```

## 📁 Project Structure

```text
smart-expense-tracker/
├── app.py
├── database.py
├── requirements.txt
├── test_database.py
├── .gitignore
└── README.md
```

## 🔐 Data & Privacy

- The current application uses a local SQLite database.
- Local database files and personal profile settings should not be committed to GitHub.
- Never commit passwords, API keys, or other secrets.
- Cloud storage and deployment are not yet documented as available features.

## 🗺️ Roadmap

- [ ] Cloud database integration
- [ ] Secure user authentication
- [ ] Online deployment
- [ ] Additional financial reports and analytics
- [ ] Expanded automated test coverage

## 👨‍💻 Author

**Raju Kumar**

GitHub: [@Rajukumar1202](https://github.com/Rajukumar1202)

## 📄 License

No license has been specified yet. All rights are reserved by the copyright holder unless a license is added to this repository.

---

⭐ If you find this project useful, consider starring the repository!
