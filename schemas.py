from pydantic import BaseModel

class LoginSchema(BaseModel):
    role: str
    email: str
    password: str

class EmployeeCreate(BaseModel):
    email: str
    password: str

class ManagerCreate(BaseModel):
    email: str
    password: str

class ExpenseCreate(BaseModel):
    employee_id: int
    amount: float
    description: str

class ExpenseCreate(BaseModel):
    employee_id: int
    amount: float
    description: str

class ExpenseUpdate(BaseModel):
    status: str   # approved / rejected
    
