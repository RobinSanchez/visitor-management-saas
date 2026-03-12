from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from datetime import datetime

import models
import schemas
from database import engine, get_db
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)

from ai_service import ask_ai
from routers.chat_router import router as chat_router



# =============================
# APP INIT
# =============================

app = FastAPI()


# Static files (widget)
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(chat_router)

# Templates
templates = Jinja2Templates(directory="templates")

# Create tables
models.Base.metadata.create_all(bind=engine)


# =============================
# ROLE VALIDATION
# =============================

def require_role(required_role: str):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="No tienes permisos suficientes")
        return current_user
    return role_checker


# =============================
# ROOT
# =============================

@app.get("/")
def root():
    return {"message": "Welcome to Visitor Management SaaS"}


# =============================
# REGISTER
# =============================

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    institution = db.query(models.Institution).filter(
        models.Institution.name == user.institution_name
    ).first()

    if not institution:
        institution = models.Institution(name=user.institution_name)
        db.add(institution)
        db.commit()
        db.refresh(institution)

    new_user = models.User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        institution_id=institution.id,
        role="admin"
    )

    db.add(new_user)
    db.commit()

    return {"message": "Usuario creado correctamente"}


# =============================
# LOGIN
# =============================

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    access_token = create_access_token(
        data={"sub": str(db_user.id)}
    )

    response = RedirectResponse(url="/admin", status_code=302)

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True
    )

    return response


@app.get("/login")
def login_form():
    return HTMLResponse("""
        <form action="/login" method="post">
            <input type="text" name="username" placeholder="Email"/>
            <input type="password" name="password" placeholder="Password"/>
            <button type="submit">Login</button>
        </form>
    """)


# =============================
# ADMIN INFO
# =============================

@app.get("/admin/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "institution_id": current_user.institution_id,
        "role": current_user.role
    }


# =============================
# ADMIN DASHBOARD
# =============================

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    institution_id = current_user.institution_id
    today = datetime.utcnow().date()

    total_visitors = db.query(models.Visitor).filter(
        models.Visitor.institution_id == institution_id
    ).count()

    visitors_today = db.query(models.Visitor).filter(
        models.Visitor.institution_id == institution_id,
        models.Visitor.created_at >= today
    ).count()

    total_users = db.query(models.User).filter(
        models.User.institution_id == institution_id
    ).count()

    total_operators = db.query(models.User).filter(
        models.User.institution_id == institution_id,
        models.User.role == "operator"
    ).count()

    recent_visitors = db.query(models.Visitor).filter(
        models.Visitor.institution_id == institution_id
    ).order_by(models.Visitor.created_at.desc()).limit(10).all()

    institution_name = current_user.institution.name

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "institution_name": institution_name,
        "total_visitors": total_visitors,
        "visitors_today": visitors_today,
        "total_users": total_users,
        "total_operators": total_operators,
        "recent_visitors": recent_visitors
    })


# =============================
# LOGOUT
# =============================

@app.get("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Sesión cerrada"}


# =============================
# CREATE VISITOR
# =============================

@app.post("/visitors")
def create_visitor(
    visitor: schemas.VisitorCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    new_visitor = models.Visitor(
        name=visitor.name,
        email=visitor.email,
        institution_id=current_user.institution_id
    )

    db.add(new_visitor)
    db.commit()
    db.refresh(new_visitor)

    return new_visitor


# =============================
# USERS ADMIN
# =============================

@app.get("/admin/users")
def get_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    return db.query(models.User).filter(
        models.User.institution_id == current_user.institution_id
    ).all()


@app.post("/admin/create-operator")
def create_operator(
    email: str,
    password: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):

    hashed_pw = get_password_hash(password)

    new_user = models.User(
        email=email,
        hashed_password=hashed_pw,
        role="operator",
        institution_id=current_user.institution_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Operador creado correctamente"}


# =============================
# CHAT AI
# =============================

@app.post("/chat")
def chat(
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    message = request.message

    response, department = ask_ai(message)

    conversation = models.Conversation(
        message=message,
        response=response,
        department=department,
        institution_id=current_user.institution_id
    )

    db.add(conversation)
    db.commit()

    return {
        "response": response,
        "department": department
    }

@app.post("/chat/public")
def public_chat(
    request: schemas.ChatRequest,
    api_key: str,
    db: Session = Depends(get_db)
):

    institution = db.query(models.Institution).filter(
        models.Institution.api_key == api_key
    ).first()

    if not institution:
        raise HTTPException(status_code=403, detail="API key inválida")

    message = request.message

    response, department = ask_ai(message)

    conversation = models.Conversation(
        message=message,
        response=response,
        department=department,
        institution_id=institution.id
    )

    db.add(conversation)
    db.commit()

    return {"response": response}