import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Expense Management System", layout="centered")
st.title("💰 Expense Management System")

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:

    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["admin", "manager", "employee"])

    if st.button("Login"):
        res = requests.post(f"{API}/login", json={
            "role": role,
            "email": email,
            "password": password
        })

        if res.status_code == 200:
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.password = password
            st.session_state.role = role
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

# ---------------- AFTER LOGIN ----------------
else:

    # 🔐 LOGOUT
    st.sidebar.success(f"Logged in as {st.session_state.role}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # ---------------- ADMIN PANEL ----------------
    if st.session_state.role == "admin":

        st.header("👨‍💼 Admin Panel")

        action = st.selectbox("Choose Action", ["Add Employee", "Add Manager"])

        # -------- ADD EMPLOYEE --------
        if action == "Add Employee":

            emp_email = st.text_input("Employee Email")
            emp_pass = st.text_input("Employee Password", type="password")

            if st.button("Create Employee"):
                res = requests.post(
                    f"{API}/employees",
                    params={
                        "email": st.session_state.email,
                        "password": st.session_state.password
                    },
                    json={
                        "email": emp_email,
                        "password": emp_pass
                    }
                )

                if res.status_code == 200:
                    st.success("Employee Added ✅")
                else:
                    st.error(res.text)

        # -------- ADD MANAGER --------
        else:

            mgr_email = st.text_input("Manager Email")
            mgr_pass = st.text_input("Manager Password", type="password")

            if st.button("Create Manager"):
                res = requests.post(
                    f"{API}/managers",
                    params={
                        "email": st.session_state.email,
                        "password": st.session_state.password
                    },
                    json={
                        "email": mgr_email,
                        "password": mgr_pass
                    }
                )

                if res.status_code == 200:
                    st.success("Manager Added ✅")
                else:
                    st.error(res.text)

    # ---------------- EMPLOYEE PANEL ----------------
    elif st.session_state.role == "employee":

        st.header("🧑‍💻 Employee Panel")

        emp_id = st.number_input("Your Employee ID", min_value=1)

        amount = st.number_input("Amount")
        desc = st.text_input("Description")

        # ✅ ADD EXPENSE
        if st.button("Submit Expense"):
            res = requests.post(f"{API}/expenses", json={
                "employee_id": emp_id,
                "amount": amount,
                "description": desc
            })

            if res.status_code == 200:
                st.success("Expense Submitted ✅")
            else:
                st.error(res.text)

        st.write("----")

        # ✅ VIEW EXPENSES
        if st.button("View My Expenses"):

            res = requests.get(f"{API}/expenses/employee/{emp_id}")

            if res.status_code == 200:

                for exp in res.json():

                    st.write(f"🆔 ID: {exp['id']}")
                    st.write(f"💰 Amount: {exp['amount']}")
                    st.write(f"📝 Desc: {exp['description']}")
                    st.write(f"📊 Status: {exp['status']}")

                    if exp["status"] == "approved":
                        st.success("Approved ✅")
                    elif exp["status"] == "rejected":
                        st.error("Rejected ❌")
                    else:
                        st.warning("Pending ⏳")

                    st.write("------")

            else:
                st.error("Failed to fetch expenses")

    # ---------------- MANAGER PANEL ----------------
    if st.session_state.role == "manager":

        st.header("👨‍💼 Manager Panel")

        if "expenses" not in st.session_state:
            st.session_state.expenses = []

        if st.button("Load Expenses"):
            res = requests.get(f"{API}/expenses")
            if res.status_code == 200:
                st.session_state.expenses = res.json()

    # 🔥 ALWAYS SHOW DATA FROM SESSION
        for exp in st.session_state.expenses:

            st.write(f"🆔 ID: {exp['id']}")
            st.write(f"👤 Employee: {exp['employee_id']}")
            st.write(f"💰 Amount: {exp['amount']}")
            st.write(f"📝 Desc: {exp['description']}")
            st.write(f"📊 Status: {exp['status']}")

            if exp["status"] == "pending":

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Approve {exp['id']}", key=f"a_{exp['id']}"):

                        res = requests.put(
                            f"{API}/expenses/{exp['id']}",
                            json={"status": "approved"}
                        )

                        st.write(res.status_code, res.text)

                        st.success("Approved ✅")
                        st.rerun()

                with col2:
                    if st.button(f"Reject {exp['id']}", key=f"r_{exp['id']}"):

                        res = requests.put(
                            f"{API}/expenses/{exp['id']}",
                            json={"status": "rejected"}
                        )

                        st.write(res.status_code, res.text)

                        st.error("Rejected ❌")
                        st.rerun()