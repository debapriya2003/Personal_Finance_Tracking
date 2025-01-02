
# Personal Finance Dashboard 🏠💰

Welcome to the **Personal Finance Dashboard**! This repository contains the code for building a powerful, user-friendly personal finance application. It helps users track their income, expenses, savings, and manage their financial data effectively. Below, you'll find detailed explanations of the technologies used, how the application works, and future features that can be added.

---

## 🚀 Key Features

- **User Authentication** 🔒: Secure login and sign-up with user-specific data.
- **Expense Tracking** 📊: Track and categorize daily expenses.
- **Income Overview** 💸: See the total income, expenses, and savings for the month.
- **Visual Analytics** 📉: Generate pie and bar charts for income vs expenses and category-wise expenses.
- **Delete Data** 🗑️: Options to delete all expenses data or even delete the entire user account.

---

## 🧑‍💻 Technologies Used

Here is a table summarizing the key technologies and libraries used in the project:

| Technology/Library      | Purpose                                          | Link/Docs |
|--------------------------|--------------------------------------------------|-----------|
| **Streamlit**            | Framework for building interactive web apps      | [Streamlit Docs](https://docs.streamlit.io/) |
| **MongoDB**              | Database for storing user data and transactions  | [MongoDB](https://www.mongodb.com/) |
| **Matplotlib**           | Used for generating static pie charts            | [Matplotlib Docs](https://matplotlib.org/) |
| **Plotly**               | Used for generating interactive bar charts       | [Plotly Docs](https://plotly.com/python/) |
| **Pandas**               | Data manipulation for transaction data           | [Pandas Docs](https://pandas.pydata.org/) |
| **Python 3.x**           | Programming language                             | [Python](https://www.python.org/) |
| **Heroku (Optional)**    | For deploying the app to the cloud               | [Heroku](https://www.heroku.com/) |
| **bcrypt**               | Password hashing and authentication             | [bcrypt Docs](https://pypi.org/project/bcrypt/) |

---

## 🌱 How It Works

### 1. **User Authentication**

When users sign up or log in, their details are securely stored using hashed passwords in a **MongoDB** database. The authentication process uses the **bcrypt** library for password encryption.

- **Sign-Up:** Users provide their username, email, and password. Passwords are hashed before storing.
- **Login:** Users can log in with their credentials, which are verified against the stored hash.

### 2. **Expense and Income Tracking**

Users can add their transactions, marking them as either **income** or **expense**, and categorize them (e.g., **Food**, **Entertainment**, **Utilities**). The data is stored in MongoDB and can be viewed through interactive charts.

- **Income vs Expenses Pie Chart:** A pie chart showing the breakdown of income and expenses.
- **Category-wise Expenses Bar Chart:** A bar chart showing the total expenses for each category.

### 3. **Deleting Data**

- Users have the option to **delete all expense data** or **delete their account** entirely from the database. 

### 4. **Future Enhancements**

- **Budgeting Feature**: Allow users to set monthly or yearly budgets and track progress.
- **Expense Alerts**: Notify users if they exceed a certain budget or category limit.
- **Recurring Expenses**: Implement functionality to manage recurring expenses automatically.
- **Financial Insights**: Provide personalized reports and insights based on user data.
- **Mobile App** 📱: Develop a mobile version using **Flutter** or **React Native**.
- **Multi-Currency Support** 💱: Allow users to track expenses in different currencies.

---

## 📊 Visual Analytics

The app generates the following visualizations to help users understand their financial data:

### 1. **Income vs Expenses Pie Chart** 🎂

This pie chart shows the proportion of income versus expenses, helping users easily understand their financial status for the current month.

Example:
![Pie Chart](Personal_finance_tracking_system/pie_chart.png)

### 2. **Category-wise Expenses Bar Chart** 📊

This bar chart helps users see which categories are consuming the most of their income, providing a clear breakdown.

Example:
![Bar Chart](Personal_finance_tracking_system/bar_chart.png)

---

## 🛠️ Installation Guide

To run this app on your local machine:

### Prerequisites
- Python 3.x
- MongoDB (Local or Cloud-based)
- Streamlit for the web interface

### Step 1: Clone the Repo
```bash
git clone https://github.com/yourusername/personal-finance-dashboard.git
```

### Step 2: Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the App
```bash
streamlit run app.py
```

---

## 🚧 Future Updates

We plan to add more features to enhance the functionality and improve the user experience. Here are some ideas for the future:

1. **User Customization** 🖌️: Allow users to customize the theme and appearance of the dashboard.
2. **Data Export** 💾: Provide an option to export transaction data to CSV or PDF.
3. **Cloud Sync** ☁️: Sync data across multiple devices by integrating with cloud storage providers.
4. **Financial Recommendations** 📈: Use machine learning to give users personalized financial advice based on their spending habits.

---

## 📝 Contribution

We welcome contributions! If you'd like to improve the app or add new features, feel free to fork the repository and submit a pull request.

- Fork the repository
- Create a new branch (`git checkout -b feature/your-feature`)
- Commit your changes (`git commit -am 'Add new feature'`)
- Push to the branch (`git push origin feature/your-feature`)
- Open a pull request

---

## 📱 Contact & Support

For support or feedback, you can reach out through the following channels:

- **GitHub Issues**: [Submit an issue](https://github.com/yourusername/personal-finance-dashboard/issues)
- **Email**: your-email@example.com
- **Twitter**: [@yourusername](https://twitter.com/yourusername)

---

Thank you for checking out the **Personal Finance Dashboard**! Feel free to explore, fork, and contribute. Let’s make financial tracking easy and fun! 🚀💰

---

