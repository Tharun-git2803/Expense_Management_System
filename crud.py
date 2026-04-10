import models

def login(db, data):
    role_map = {
        "admin": models.Admin,
        "manager": models.Manager,
        "employee": models.Employee
    }

    model = role_map.get(data.role)

    if not model:
        return None

    return db.query(model).filter(
        model.email == data.email,
        model.password == data.password
    ).first()


def create_employee(db, user):
    emp = models.Employee(email=user.email, password=user.password)
    db.add(emp)
    db.commit()
    db.refresh(emp)   # ✅ ADD THIS
    return emp


def create_manager(db, user):
    mgr = models.Manager(email=user.email, password=user.password)
    db.add(mgr)
    db.commit()
    db.refresh(mgr)   # ✅ ADD THIS
    return mgr


def create_expense(db, exp):
    expense = models.Expense(**exp.dict())
    db.add(expense)
    db.commit()
    db.refresh(expense)   # ✅ ADD THIS
    return expense


def get_expenses(db):
    return db.query(models.Expense).all()
def update_expense_status(db, expense_id, status):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()

    if not expense:
        return None

    print("Before:", expense.status)  # DEBUG

    expense.status = status

    db.commit()
    db.refresh(expense)

    print("After:", expense.status)  # DEBUG

    return expense