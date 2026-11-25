from datetime import date
from flask import Blueprint, render_template, request
from ..models.relatorio import RelatorioVisita, TECNICOS_NUTCI
from ..services.relatorio_service import listar_relatorios

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    hoje = date.today().isoformat()
    return render_template("index.html", hoje=hoje, tecnicos=TECNICOS_NUTCI)


@web_bp.route("/historico")
def historico():
    busca = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)

    paginacao = listar_relatorios(busca=busca, status=status, page=page, per_page=15)
    return render_template(
        "historico.html",
        paginacao=paginacao,
        busca=busca,
        status=status,
    )


@web_bp.route("/relatorio/<int:relatorio_id>")
def visualizar(relatorio_id: int):
    relatorio = RelatorioVisita.query.get_or_404(relatorio_id)
    return render_template("visualizar.html", relatorio=relatorio, em_branco=False)


@web_bp.route("/relatorio/em-branco")
def visualizar_em_branco():
    return render_template("visualizar.html", relatorio=None, em_branco=True)


@web_bp.route("/integracao-portal")
def integracao_portal():
    """Página auxiliar com botão/ícone pronto para embutir no portal see3gre."""
    return render_template("integracao_portal.html")


@web_bp.route("/offline")
def offline():
    return render_template("offline.html")
