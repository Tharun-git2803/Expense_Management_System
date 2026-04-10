from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
import crud
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: schemas.LoginSchema, db: Session = Depends(get_db)):
    if data.role == "admin":
        user = db.query(models.Admin).filter_by(email=data.email, password=data.password).first()
    elif data.role == "manager":
        user = db.query(models.Manager).filter_by(email=data.email, password=data.password).first()
    else:
        user = db.query(models.Employee).filter_by(email=data.email, password=data.password).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"status": "success"}

# ---------------- ADD EMPLOYEE ----------------
@app.post("/employees")
def add_employee(
    emp: schemas.EmployeeCreate,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    admin = db.query(models.Admin).filter_by(email=email, password=password).first()

    if not admin:
        raise HTTPException(status_code=401, detail="Admin not valid")

    existing = db.query(models.Employee).filter_by(email=emp.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee exists")

    new_emp = models.Employee(email=emp.email, password=emp.password)
    db.add(new_emp)
    db.commit()

    return {"message": "Employee added"}

# ---------------- ADD MANAGER ----------------
@app.post("/managers")
def add_manager(
    mgr: schemas.ManagerCreate,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    admin = db.query(models.Admin).filter_by(email=email, password=password).first()

    if not admin:
        raise HTTPException(status_code=401, detail="Admin not valid")

    existing = db.query(models.Manager).filter_by(email=mgr.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Manager exists")

    new_mgr = models.Manager(email=mgr.email, password=mgr.password)
    db.add(new_mgr)
    db.commit()

    return {"message": "Manager added"}

# ---------------- ADD EXPENSE ----------------
@app.post("/expenses")
def add_expense(exp: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    new_exp = models.Expense(
        employee_id=exp.employee_id,
        amount=exp.amount,
        description=exp.description,
        status="pending"
    )

    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)

    return {"message": "Expense submitted"}

# ---------------- VIEW EXPENSES ----------------
@app.get("/expenses")
def get_expenses(db: Session = Depends(get_db)):
    return db.query(models.Expense).all()

# @app.put("/expenses/{expense_id}")
# def update_expense(
#     expense_id: int,
#     data: schemas.ExpenseUpdate,
#     db: Session = Depends(get_db)
# ):
#     exp = db.query(models.Expense).filter_by(id=expense_id).first()

#     if not exp:
#         raise HTTPException(status_code=404, detail="Expense not found")

#     exp.status = data.status

#     db.commit()
#     db.refresh(exp)   # 🔥 IMPORTANT

    return {"message": f"Expense {data.status}", "status": exp.status}
@app.get("/expenses/employee/{emp_id}")
def get_employee_expenses(emp_id: int, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).filter_by(employee_id=emp_id).all()
    return expenses
# @app.put("/expenses/{expense_id}")
# def update_expense(expense_id: int, data: schemas.ExpenseUpdate, db: Session = Depends(get_db)):

#     print("🔥 API HIT:", expense_id, data.status)

#     exp = db.query(models.Expense).filter_by(id=expense_id).first()

#     if not exp:
#         raise HTTPException(status_code=404, detail="Expense not found")

#     print("Before:", exp.status)

#     exp.status = data.status

#     db.commit()
#     db.refresh(exp)

#     print("After:", exp.status)

#     return {"message": "Updated", "status": exp.status}



@app.put("/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    data: schemas.ExpenseUpdate,
    db: Session = Depends(get_db)
):
    updated = crud.update_expense_status(db, expense_id, data.status)

    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")

    return {"message": "Updated", "status": updated.status}