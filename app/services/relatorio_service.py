from datetime import date
from sqlalchemy import or_, desc
from ..extensions import db
from ..models.relatorio import RelatorioVisita


class ValidationError(Exception):
    pass


def gerar_proximo_protocolo(ano: int) -> str:
    prefixo = f"{ano}-"
    ultimo = (
        RelatorioVisita.query.filter(RelatorioVisita.protocolo.like(f"{prefixo}%"))
        .order_by(desc(RelatorioVisita.id))
        .first()
    )
    if not ultimo:
        return f"{ano}-0001"
    try:
        seq = int(ultimo.protocolo.split("-")[-1]) + 1
    except ValueError:
        seq = ultimo.id + 1
    return f"{ano}-{seq:04d}"


def _parse_bool(valor) -> bool:
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        v = valor.strip().lower()
        if v in ("true", "1", "sim", "s", "yes"):
            return True
        if v in ("false", "0", "nao", "não", "n", "no"):
            return False
    raise ValidationError("Selecione se o problema da instituição foi resolvido (SIM ou NÃO).")


def criar_ou_sincronizar_relatorio(dados: dict) -> tuple[RelatorioVisita, bool]:
    client_uuid = (dados.get("client_uuid") or "").strip() or None
    if client_uuid:
        existente = RelatorioVisita.query.filter_by(client_uuid=client_uuid).first()
        if existente:
            return existente, False

    escola_setor = (dados.get("escola_setor") or "").strip()
    endereco = (dados.get("endereco") or "").strip()
    motivo_chamado = (dados.get("motivo_chamado") or "").strip()
    tecnico = (dados.get("tecnico") or "").strip()
    matricula = (dados.get("matricula") or "").strip()
    descricao_atendimento = (dados.get("descricao_atendimento") or "").strip()
    cidade = (dados.get("cidade") or "Campina Grande - PB").strip() or "Campina Grande - PB"
    gestor_nome = (dados.get("gestor_nome") or "").strip() or None
    tipo_assinatura = (dados.get("tipo_assinatura") or "govbr").strip()
    if tipo_assinatura not in ("govbr", "impressa"):
        tipo_assinatura = "govbr"

    if not escola_setor:
        raise ValidationError("O campo 'Escola/Setor' é obrigatório.")
    if not endereco:
        raise ValidationError("O campo 'Endereço' é obrigatório.")
    if not motivo_chamado:
        raise ValidationError("O campo 'Motivo do chamado' é obrigatório.")
    if not tecnico:
        raise ValidationError("Selecione ou informe o 'Técnico'.")
    if not matricula:
        raise ValidationError("O campo 'Matrícula' é obrigatório.")
    if not descricao_atendimento:
        raise ValidationError("O campo 'Descrição do atendimento' é obrigatório.")

    data_str = (dados.get("data_visita") or "").strip()
    if not data_str:
        raise ValidationError("O campo 'Data da visita' é obrigatório.")
    try:
        data_visita = date.fromisoformat(data_str)
    except ValueError as exc:
        raise ValidationError("Formato de data inválido. Use AAAA-MM-DD.") from exc

    problema_resolvido = _parse_bool(dados.get("problema_resolvido"))
    protocolo = gerar_proximo_protocolo(data_visita.year)

    relatorio = RelatorioVisita(
        protocolo=protocolo,
        client_uuid=client_uuid,
        escola_setor=escola_setor,
        data_visita=data_visita,
        endereco=endereco,
        motivo_chamado=motivo_chamado,
        tecnico=tecnico,
        matricula=matricula,
        problema_resolvido=problema_resolvido,
        descricao_atendimento=descricao_atendimento,
        cidade=cidade,
        gestor_nome=gestor_nome,
        tipo_assinatura=tipo_assinatura,
    )

    db.session.add(relatorio)
    db.session.commit()
    return relatorio, True


def listar_relatorios(busca: str = "", status: str = "", page: int = 1, per_page: int = 15):
    query = RelatorioVisita.query

    if busca:
        termo = f"%{busca.strip()}%"
        query = query.filter(
            or_(
                RelatorioVisita.escola_setor.ilike(termo),
                RelatorioVisita.tecnico.ilike(termo),
                RelatorioVisita.matricula.ilike(termo),
                RelatorioVisita.protocolo.ilike(termo),
                RelatorioVisita.motivo_chamado.ilike(termo),
            )
        )

    if status == "sim":
        query = query.filter(RelatorioVisita.problema_resolvido.is_(True))
    elif status == "nao":
        query = query.filter(RelatorioVisita.problema_resolvido.is_(False))

    query = query.order_by(desc(RelatorioVisita.data_visita), desc(RelatorioVisita.id))
    return query.paginate(page=page, per_page=per_page, error_out=False)
