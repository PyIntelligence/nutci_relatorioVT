from flask import Blueprint, request, jsonify
from sqlalchemy import text
from ..extensions import db
from ..models.relatorio import RelatorioVisita
from ..services.relatorio_service import (
    ValidationError,
    criar_ou_sincronizar_relatorio,
    listar_relatorios,
)

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ok", "database": "neon_postgresql_connected"}), 200
    except Exception as exc:
        return jsonify({"status": "error", "detail": str(exc)}), 503


@api_bp.route("/relatorios", methods=["GET"])
def api_listar():
    busca = request.args.get("q", "")
    status = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)
    pag = listar_relatorios(busca=busca, status=status, page=page, per_page=20)
    return jsonify(
        {
            "items": [r.to_dict() for r in pag.items],
            "total": pag.total,
            "page": pag.page,
            "pages": pag.pages,
        }
    )


@api_bp.route("/relatorios", methods=["POST"])
def api_criar():
    dados = request.get_json(silent=True) or request.form.to_dict()
    try:
        relatorio, criado = criar_ou_sincronizar_relatorio(dados)
        return (
            jsonify(
                {
                    "ok": True,
                    "created": criado,
                    "relatorio": relatorio.to_dict(),
                    "redirect_url": f"/relatorio/{relatorio.id}",
                }
            ),
            201 if criado else 200,
        )
    except ValidationError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"ok": False, "error": f"Erro ao gravar no banco de dados: {exc}"}), 500


@api_bp.route("/relatorios/sync", methods=["POST"])
def api_sync_lote():
    payload = request.get_json(silent=True) or {}
    itens = payload.get("items", [])
    if not isinstance(itens, list):
        return jsonify({"ok": False, "error": "Formato inválido para sincronização."}), 400

    sincronizados = []
    erros = []

    for item in itens:
        try:
            relatorio, _ = criar_ou_sincronizar_relatorio(item)
            sincronizados.append(
                {
                    "client_uuid": item.get("client_uuid"),
                    "id": relatorio.id,
                    "protocolo": relatorio.protocolo,
                }
            )
        except Exception as exc:
            db.session.rollback()
            erros.append(
                {
                    "client_uuid": item.get("client_uuid"),
                    "error": str(exc),
                }
            )

    return jsonify({"ok": True, "synced": sincronizados, "errors": erros}), 200


@api_bp.route("/relatorios/<int:relatorio_id>", methods=["DELETE"])
def api_excluir(relatorio_id: int):
    relatorio = RelatorioVisita.query.get_or_404(relatorio_id)
    db.session.delete(relatorio)
    db.session.commit()
    return jsonify({"ok": True}), 200
