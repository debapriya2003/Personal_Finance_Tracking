import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import bcrypt
import plotly.express as px
import random
import string
from datetime import datetime, timedelta
import pymongo
import streamlit as st
# Fixed MongoDB URI and Database Name
MONGO_URI = "mongodb+srv://tintin:tintin@cluster0.qot4y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "pf"

# MongoDB Connection Setup
def initialize_mongodb():
    """Initialize MongoDB connection."""
    st.title("Personal Finance Manager")

    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        st.success("Connected to MongoDB successfully!")
        st.session_state.db = db
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")

# Send Password Reset Email
def send_reset_email(user_email, reset_token):
    """Send a password reset link to the user's email."""
    sender_email = ""
    receiver_email = user_email
    password = ""  # Use an environment variable or secret manager for sensitive info

    subject = "Password Reset Request"
    body = f"Click the following link to reset your password:\n\nhttp://your-app-url/reset_password?token={reset_token}"

    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Set up the SMTP server and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        st.success("Password reset email sent successfully.")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Generate Password Reset Token
def generate_reset_token():
    """Generate a unique token for password reset."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# Password Reset Logic
def reset_password(token, new_password):
    """Reset the password using the reset token."""
    users_collection = st.session_state.db["users"]
    user = users_collection.find_one({"reset_token": token})

    if user and datetime.now() < user["reset_token_expiry"]:
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"password": hashed_password, "reset_token": None, "reset_token_expiry": None}}
        )
        st.success("Password reset successfully. You can now log in with your new password.")
    else:
        st.error("Invalid or expired reset token.")

# Forgot Password Flow
def forgot_password():
    """Handle the forgot password flow."""
    st.subheader("Forgot Password?")
    email = st.text_input("Enter your email address:")

    if st.button("Send Reset Link"):
        if email:
            users_collection = st.session_state.db["users"]
            user = users_collection.find_one({"email": email})

            if user:
                reset_token = generate_reset_token()
                reset_token_expiry = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
                users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"reset_token": reset_token, "reset_token_expiry": reset_token_expiry}}
                )
                send_reset_email(user["email"], reset_token)
            else:
                st.error("Email address not found.")
        else:
            st.error("Please enter a valid email address.")

# Authentication (Login & Register)
def authenticate_user():
    """Authenticate a user."""
    st.subheader("Login")
    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")

    if st.button("Login"):
        users_collection = st.session_state.db["users"]
        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            st.success("Login successful!")
            st.session_state.user_id = user["_id"]
            st.session_state.username = username
            st.session_state.authenticated = True
        else:
            st.error("Invalid credentials.")
            st.markdown("[Forgot Password?](#)", unsafe_allow_html=True)

# Register User (for demo purposes)
def register_user():
    """Register a new user."""
    st.subheader("Register")
    username = st.text_input("Username")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if password == confirm_password:
        if st.button("Register"):
            users_collection = st.session_state.db["users"]
            existing_user = users_collection.find_one({"email": email})

            if existing_user:
                st.error("Email address already registered.")
            else:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                users_collection.insert_one({
                    "username": username,
                    "email": email,
                    "password": hashed_password,
                    "reset_token": None,
                    "reset_token_expiry": None
                })
                st.success("Registration successful! Please log in.")
        else:
            st.error("Passwords do not match.")
    else:
        st.error("Please enter a valid email address.")



# Generate Financial Reports
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO


def generate_report():
    """Generate a financial report and make it downloadable with readable charts."""
    st.subheader("Generate Report")
    period = st.radio("Report Period", ["Monthly", "Yearly"])
    year = st.text_input("Year (YYYY)")

    month = None
    if period == "Monthly":
        month = st.text_input("Month (MM)")

    if st.button("Generate Report"):
        if year and (period == "Yearly" or (period == "Monthly" and month)):
            transactions_collection = st.session_state.db["transactions"]
            date_filter = year if period == "Yearly" else f"{year}-{month.zfill(2)}"

            pipeline = [
                {"$match": {"user_id": st.session_state.user_id, "date": {"$regex": f"^{date_filter}"}}},
                {"$group": {"_id": "$type", "total": {"$sum": "$amount"}}}
            ]
            report = list(transactions_collection.aggregate(pipeline))

            # Calculate summary data
            total_income = sum(item["total"] for item in report if item["_id"] == "income")
            total_expenses = sum(item["total"] for item in report if item["_id"] == "expense")
            savings = total_income - total_expenses

            # Display summary
            st.write(f"**Total Income:** ₹{total_income:,.2f}")
            st.write(f"**Total Expenses:** ₹{total_expenses:,.2f}")
            st.write(f"**Savings:** ₹{savings:,.2f}")

            # Get all transactions for the selected period
            transactions = list(transactions_collection.find(
                {"user_id": st.session_state.user_id, "date": {"$regex": f"^{date_filter}"}}
            ))
            df = pd.DataFrame(transactions)
            if not df.empty:
                df = df[["date", "type", "category", "amount"]]  # Keep relevant columns
                st.table(df)

                # Create totals DataFrame for plotting
                totals = pd.Series(
                    {"Income": total_income, "Expenses": total_expenses},
                    name="Amount"
                )

                # Improved Bar Chart
                bar_fig, ax = plt.subplots()

                # Plot the bar chart using `ax.bar` for compatibility with `bar_label`
                bar_colors = ["#2b8cbe", "#de2d26"]
                bars = ax.bar(totals.index, totals.values, color=bar_colors)

                ax.set_title("Income vs Expenses", fontsize=14, fontweight="bold")
                ax.set_xlabel("Type", fontsize=12)
                ax.set_ylabel("Amount (₹)", fontsize=12)
                ax.tick_params(axis="x", labelsize=10)

                # Add bar labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        height,
                        f"₹{height:,.2f}",
                        ha="center",
                        va="bottom",
                        fontsize=10,
                    )

                st.pyplot(bar_fig)

                # Improved Pie Chart
                pie_fig, ax = plt.subplots()
                pie_totals = totals.reset_index()
                wedges, texts, autotexts = ax.pie(
                    pie_totals["Amount"],
                    labels=pie_totals["index"],
                    autopct="%.2f%%",
                    colors=["#2b8cbe", "#de2d26"],
                    textprops={"fontsize": 10},
                )
                ax.set_title("Income vs Expenses Distribution", fontsize=14, fontweight="bold")
                st.pyplot(pie_fig)

                # Allow CSV download
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="Download Transactions CSV",
                    data=csv_data,
                    file_name="transactions_report.csv",
                    mime="text/csv",
                )

                # Download graphs as images
                pie_buffer = BytesIO()
                bar_buffer = BytesIO()

                # Save the Pie chart to pie_buffer
                pie_fig.savefig(pie_buffer, format="png")
                pie_buffer.seek(0)

                # Save the Bar chart to bar_buffer
                bar_fig.savefig(bar_buffer, format="png")
                bar_buffer.seek(0)

                st.download_button(
                    label="Download Pie Chart",
                    data=pie_buffer.getvalue(),
                    file_name="pie_chart.png",
                    mime="image/png",
                )

                st.download_button(
                    label="Download Bar Chart",
                    data=bar_buffer.getvalue(),
                    file_name="bar_chart.png",
                    mime="image/png",
                )
            else:
                st.warning("No transactions found for the selected period.")
        else:
            st.error("Please provide the necessary details.")




# User Authentication
def authenticate_user():
    """Authenticate a user."""
    st.subheader("Login")
    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")

    if st.button("Login"):
        users_collection = st.session_state.db["users"]
        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            st.success("Login successful!")
            st.session_state.user_id = user["_id"]
            st.session_state.username = username
            st.session_state.authenticated = True
        else:
            st.error("Invalid credentials.")


# Add Income or Expense
def add_transaction():
    """Add a new income or expense transaction."""
    st.subheader("Add Transaction")

    # Transaction type selector
    t_type = st.selectbox("Transaction Type", ["Income", "Expense"])

    # Conditionally display the category field only for expenses
    category = None
    if t_type == "Expense":
        category = st.text_input("Category (e.g., Food, Rent, Entertainment)", placeholder="Enter a category")

    # Amount and date input
    amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
    date = st.date_input("Date", datetime.now())

    if st.button("Add Transaction"):
        if t_type == "Expense" and not category:
            st.error("Please provide a category for your expense.")
            return

        transactions_collection = st.session_state.db["transactions"]
        transactions_collection.insert_one({
            "user_id": st.session_state.user_id,
            "type": t_type.lower(),
            "category": category if t_type == "Expense" else None,
            "amount": amount,
            "date": date.strftime("%Y-%m-%d")
        })
        st.success(f"{t_type} transaction added successfully!")


# Home Page with Charts and Dashboard Summary
def home_page():
    """Display financial dashboard with cards, charts, and a table of transactions."""
    import datetime
    import pandas as pd
    import plotly.express as px
    import matplotlib.pyplot as plt

    st.write("Welcome to your personal finance dashboard!")

    # Fetch data for financial summary
    transactions_collection = st.session_state.db["transactions"]

    # Allow the user to choose between date-wise and year-wise data
    view_type = st.radio("Select View Type", ["Date-Wise", "Year-Wise"])

    if view_type == "Date-Wise":
        selected_date = st.date_input(
            "Select a Date",
            min_value=datetime.date(2020, 1, 1),
            max_value=datetime.date(2025, 12, 31),
            value=datetime.date.today()
        )
        date_filter = selected_date.strftime("%Y-%m-%d")
        pipeline = [{"$match": {"user_id": st.session_state.user_id, "date": {"$regex": f"^{date_filter}"}}}]
        year_filter = None  # Not applicable for Date-Wise view

    elif view_type == "Year-Wise":
        years = transactions_collection.distinct("date", {"user_id": st.session_state.user_id})
        years = sorted(set(date[:4] for date in years))  # Extract unique years
        if not years:
            st.warning("No transactions found to select a year.")
            return
        selected_year = st.selectbox("Select a Year", years, index=0)
        pipeline = [{"$match": {"user_id": st.session_state.user_id, "date": {"$regex": f"^{selected_year}"}}}]
        year_filter = selected_year  # For Year-Wise view

    # Aggregate data for income and expenses
    pipeline.append({"$group": {"_id": "$type", "total": {"$sum": "$amount"}}})
    report = list(transactions_collection.aggregate(pipeline))

    # Check if data is available
    if not report:
        st.write("No data available to show.")
        return

    total_income = sum(item["total"] for item in report if item["_id"] == "income")
    total_expenses = sum(item["total"] for item in report if item["_id"] == "expense")
    savings = total_income - total_expenses

    # Create and display summary cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="background-color:#4CAF50; padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h3>Total Income</h3>
            <h4>₹{total_income:,.2f}</h4>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background-color:#FF5733; padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h3>Total Expenses</h3>
            <h4>₹{total_expenses:,.2f}</h4>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background-color:#00BCD4; padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h3>Savings</h3>
            <h4>₹{savings:,.2f}</h4>
        </div>
        """, unsafe_allow_html=True)

    # Create Pie Chart
    pie_labels = ["Income", "Expenses"]
    pie_values = [total_income, total_expenses]
    pie_fig, pie_ax = plt.subplots(figsize=(6, 6))
    pie_ax.pie(pie_values, labels=pie_labels, autopct='%1.1f%%', startangle=140, colors=["#4CAF50", "#FF5733"])
    pie_ax.set_title("Income vs Expenses Distribution")

    # Create Bar Chart
    bar_categories = ["Income", "Expenses"]
    bar_values = [total_income, total_expenses]
    bar_df = pd.DataFrame({"Category": bar_categories, "Amount": bar_values})
    bar_fig = px.bar(bar_df, x="Category", y="Amount", title="Income vs Expenses", text="Amount",
                     color="Category", color_discrete_map={"Income": "#4CAF50", "Expenses": "#FF5733"})

    # Display Pie and Bar Charts side by side
    col4, col5 = st.columns(2)

    with col4:
        st.pyplot(pie_fig)

    with col5:
        st.plotly_chart(bar_fig, use_container_width=True)

    # Transaction Table
    transactions = list(transactions_collection.find(
        {"user_id": st.session_state.user_id, "date": {"$regex": f"^{year_filter if view_type == 'Year-Wise' else date_filter}"}}))

    if transactions:
        transaction_df = pd.DataFrame(transactions)
        transaction_df['Date'] = pd.to_datetime(transaction_df['date']).dt.strftime('%Y-%m-%d')
        transaction_df = transaction_df[['Date', 'type', 'category', 'amount']]  # Select necessary columns
        transaction_df.columns = ['Date', 'Transaction Type', 'Category', 'Amount']  # Rename columns for display
        st.dataframe(transaction_df)  # Display in a tabular format
    else:
        st.write("No transactions found for the selected period.")

        # Add delete buttons for removing expenses and user account
    col6, col7 = st.columns(2)

    with col6:
        if st.button("Delete My Expenses Data"):
            try:
                # Delete all expenses for the user
                transactions_collection.delete_many({"user_id": st.session_state.user_id})
                st.success("Your expenses data has been successfully deleted.")
            except Exception as e:
                st.error(f"An error occurred while deleting the expenses data: {e}")

    with col7:
        if st.button("Delete My Account"):
            try:
                # Delete user data from transactions and user collection
                transactions_collection.delete_many({"user_id": st.session_state.user_id})
                users_collection.delete_one({"_id": st.session_state.user_id})
                st.success("Your account has been successfully deleted.")
            except Exception as e:
                st.error(f"An error occurred while deleting your account: {e}")




#Main Streamlit Application

#Add Demo Data
def add_demo_data():
    """Add 100 demo transactions to the database."""
    st.subheader("Add Demo Data")
    if st.button("Generate Demo Data"):
        transactions_collection = st.session_state.db["transactions"]

        for _ in range(100):
            # Randomly decide transaction type
            t_type = random.choice(["income", "expense"])

            # For expenses, assign a category
            category = None
            if t_type == "expense":
                category = random.choice(["Food", "Rent", "Entertainment", "Travel", "Shopping"])

            # Generate random amounts and dates
            amount = round(random.uniform(10, 1000), 2)
            date = datetime.strptime(f"2025-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}", "%Y-%m-%d")

            # Insert transaction
            transactions_collection.insert_one({
                "user_id": st.session_state.user_id,
                "type": t_type,
                "category": category,
                "amount": amount,
                "date": date.strftime("%Y-%m-%d")
            })

        st.success("100 demo transactions added successfully!")


# Budget Management
def budget_management():
    """Manage budgets and view category-wise expenses."""
    st.subheader("Budget Management")

    # MongoDB collection for budgets
    budgets_collection = st.session_state.db["budgets"]
    transactions_collection = st.session_state.db["transactions"]

    # Fetch existing budgets
    existing_budgets = list(budgets_collection.find({"user_id": st.session_state.user_id}))

    # Display current budgets
    if existing_budgets:
        st.write("### Your Current Budgets")
        for budget in existing_budgets:
            st.write(f"Category: **{budget['category']}**, Budget: ₹{budget['budget']:,.2f}")

    # Set a new budget
    st.write("### Set a New Budget")
    category = st.text_input("Category")
    budget_amount = st.number_input("Budget Amount", min_value=0.01)
    if st.button("Set Budget"):
        if category and budget_amount > 0:
            budgets_collection.update_one(
                {"user_id": st.session_state.user_id, "category": category},
                {"$set": {"budget": budget_amount}},
                upsert=True
            )
            st.success(f"Budget set for {category}: ₹{budget_amount:,.2f}")
        else:
            st.error("Please enter a valid category and budget amount.")

    # Category-wise expenses
    st.write("### Category-wise Expenses")
    pipeline = [
        {"$match": {"user_id": st.session_state.user_id, "type": "expense"}},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}
    ]
    category_expenses = list(transactions_collection.aggregate(pipeline))

    if category_expenses:
        categories = [item["_id"] for item in category_expenses]
        expenses = [item["total"] for item in category_expenses]

        df = pd.DataFrame({"Category": categories, "Expense": expenses})
        st.bar_chart(df.set_index("Category"))

        # Check for budget alerts
        st.write("### Budget Alerts")
        for expense in category_expenses:
            budget = next((b["budget"] for b in existing_budgets if b["category"] == expense["_id"]), None)
            if budget and expense["total"] > budget:
                st.warning(f"Alert! Expenses for **{expense['_id']}** exceed the budget of ₹{budget:,.2f}!")
    else:
        st.write("No expenses recorded yet.")
# Main Streamlit Application
# Add to Main Navigation
def main():
    if "db" not in st.session_state:
        initialize_mongodb()

    if "db" in st.session_state:
        if "authenticated" not in st.session_state or not st.session_state.authenticated:
            # Show Login/Registration options if not authenticated
            menu = st.selectbox("Menu", ["Login", "Register", "Forgot Password"])

            if menu == "Login":
                authenticate_user()
            elif menu == "Register":
                register_user()
            elif menu == "Forgot Password":
                forgot_password()
        else:
            st.header(f"Welcome, {st.session_state.username}!")
            menu = st.sidebar.selectbox(
                "Navigation",
                ["Home", "Add Transaction", "Generate Report", "Budget Management", "Add Demo Data", "Logout"],
                index=0
            )

            if menu == "Home":
                home_page()
            elif menu == "Add Transaction":
                add_transaction()
            elif menu == "Generate Report":
                generate_report()
            elif menu == "Budget Management":
                budget_management()
            elif menu == "Add Demo Data":
                add_demo_data()
            elif menu == "Logout":
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.username = None
                st.success("Logged out successfully.")


if __name__ == "__main__":
    main()

# mongodb+srv://tintin:tintin@cluster0.qot4y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

