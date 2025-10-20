from fastapi import FastAPI, Form, Request, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import os

from database import engine, get_db
from models import Base, Item

# Cria as tabelas no banco
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "super-secret-key"))

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Função auxiliar para mensagens flash
def get_flashed_messages(request: Request):
    return request.session.pop("flashed_messages", [])

# 🔹 Página inicial + busca
@app.get("/")
def listar_itens(request: Request, q: str = "", db: Session = Depends(get_db)):
    messages = get_flashed_messages(request)
    if q:
        itens = db.query(Item).filter(Item.nome.ilike(f"%{q}%")).all()
    else:
        itens = db.query(Item).all()
    return templates.TemplateResponse("index.html", {"request": request, "itens": itens, "q": q, "messages": messages})

# 🔹 Formulário de criação
@app.get("/novo")
def form_criar_item(request: Request):
    messages = get_flashed_messages(request)
    return templates.TemplateResponse("create.html", {"request": request, "messages": messages})

# 🔹 Criar novo item
@app.post("/criar")
def criar_item(request: Request, nome: str = Form(...), descricao: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(Item).filter(Item.nome.ilike(nome)).first()
    if existing:
        request.session["flashed_messages"] = [{"type": "error", "message": f"Já existe um item com o nome '{nome}'"}]
        return RedirectResponse("/novo", status_code=status.HTTP_303_SEE_OTHER)

    novo_item = Item(nome=nome, descricao=descricao)
    db.add(novo_item)
    db.commit()
    db.refresh(novo_item)

    request.session["flashed_messages"] = [{"type": "success", "message": "Item criado com sucesso!"}]
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

# 🔹 Editar item
@app.get("/editar/{item_id}")
def editar_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        request.session["flashed_messages"] = [{"type": "error", "message": f"Item com ID {item_id} não encontrado."}]
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("edit.html", {"request": request, "item": item})

# 🔹 Atualizar item
@app.post("/atualizar/{item_id}")
def atualizar_item(request: Request, item_id: int, nome: str = Form(...), descricao: str = Form(...), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        request.session["flashed_messages"] = [{"type": "error", "message": f"Item com ID {item_id} não encontrado."}]
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    item.nome = nome
    item.descricao = descricao
    db.commit()

    request.session["flashed_messages"] = [{"type": "success", "message": "Item atualizado com sucesso!"}]
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

# 🔹 Deletar item
@app.get("/deletar/{item_id}")
def deletar_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        request.session["flashed_messages"] = [{"type": "error", "message": f"Item com ID {item_id} não encontrado."}]
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    db.delete(item)
    db.commit()

    request.session["flashed_messages"] = [{"type": "success", "message": "Item excluído com sucesso!"}]
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
