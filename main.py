from fastapi import FastAPI, Form, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

app = FastAPI()
# Use uma chave secreta forte em produção! Você pode gerar uma com: os.urandom(32).hex()
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "super-secret-key"))

# Configuração de templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Banco de dados em memória
itens = []
contador = 1

# Função auxiliar para obter mensagens flash da sessão
def get_flashed_messages(request: Request):
    messages = request.session.pop("flashed_messages", [])
    return messages

# Rota para exibir o formulário de criação de item
@app.get("/novo")
def form_criar_item(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

# Rota para criar um novo item
@app.post("/criar")
def criar_item(request: Request, nome: str = Form(...), descricao: str = Form(...)):
    # Verifica se já existe um item com o mesmo nome (ignorando maiúsculas/minúsculas)
    for existing_item in itens:
        if existing_item["nome"].lower() == nome.lower():
            request.session["flashed_messages"] = [{"type": "error", "message": f"Já existe um item com o nome \'{nome}\'."}]
            return RedirectResponse("/novo", status_code=status.HTTP_303_SEE_OTHER)

    global contador
    item = {"id": contador, "nome": nome, "descricao": descricao}
    itens.append(item)
    contador += 1
    request.session["flashed_messages"] = [{"type": "success", "message": "Item criado com sucesso!"}]
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

# Rota para exibir o formulário de edição de um item
@app.get("/editar/{item_id}")
def editar_item(request: Request, item_id: int):
    for item in itens:
        if item["id"] == item_id:
            return templates.TemplateResponse("edit.html", {"request": request, "item": item})
    request.session["flashed_messages"] = [{"type": "error", "message": f"Item com ID {item_id} não encontrado para edição."}]
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

# Rota para atualizar um item existente
@app.post("/atualizar/{item_id}")
def atualizar_item(request: Request, item_id: int, nome: str = Form(...), descricao: str = Form(...)):
    for item in itens:
        if item["id"] == item_id:
            item["nome"] = nome
            item["descricao"] = descricao
            request.session["flashed_messages"] = [{"type": "success", "message": "Item atualizado com sucesso!"}]
            return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    request.session["flashed_messages"] = [{"type": "error", "message": f"Item com ID {item_id} não encontrado para atualização."}]
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

# Rota para deletar um item
@app.get("/deletar/{item_id}")
def deletar_item(request: Request, item_id: int):
    for item in itens:
        if item["id"] == item_id:
            itens.remove(item)
            request.session["flashed_messages"] = [{"type": "success", "message": "Item excluído com sucesso!"}]
            return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    request.session["flashed_messages"] = [{"type": "error", "message": f"Item com ID {item_id} não encontrado para exclusão."}]
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

# Rota principal e de busca de itens
@app.get("/")
def listar_itens(request: Request, q: str = ""):
    messages = get_flashed_messages(request)
    if q:
        itens_filtrados = [item for item in itens if q.lower() in item["nome"].lower()]
    else:
        itens_filtrados = itens

    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "itens": itens_filtrados, "q": q, "messages": messages}
    )
