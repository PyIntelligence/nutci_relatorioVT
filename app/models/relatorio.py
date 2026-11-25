from datetime import datetime, timezone
from ..extensions import db

# Equipe técnica fixa do NUTCI - 3ª GRE (pode preencher a matrícula padrão se desejar)
TECNICOS_NUTCI = [
    {"nome": "Guega", "matricula": ""},
    {"nome": "Jairo", "matricula": ""},
    {"nome": "João Paulo", "matricula": ""},
    {"nome": "Valdênio", "matricula": ""},
    {"nome": "Isaque", "matricula": ""},
]

MESES_PT = {
    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
}


class RelatorioVisita(db.Model):
    __tablename__ = "relatorios_visita"

    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    client_uuid = db.Column(db.String(36), unique=True, nullable=True, index=True)

    # Campos oficiais do Relatório de Visita Técnica (NUTCI - 3ª GRE)
    escola_setor = db.Column(db.String(200), nullable=False, index=True)
    data_visita = db.Column(db.Date, nullable=False, index=True)
    endereco = db.Column(db.String(255), nullable=False)
    motivo_chamado = db.Column(db.String(255), nullable=False)
    tecnico = db.Column(db.String(150), nullable=False, index=True)
    matricula = db.Column(db.String(50), nullable=False)
    problema_resolvido = db.Column(db.Boolean, nullable=False, default=True)
    descricao_atendimento = db.Column(db.Text, nullable=False)

    # Local, Gestor e Modalidade de Assinatura (Gov.br ou Impressa)
    cidade = db.Column(db.String(100), nullable=False, default="Campina Grande - PB")
    gestor_nome = db.Column(db.String(150), nullable=True)
    tipo_assinatura = db.Column(db.String(20), nullable=False, default="govbr")  # 'govbr' ou 'impressa'

    criado_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    atualizado_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def data_visita_br(self) -> str:
        return self.data_visita.strftime("%d/%m/%Y") if self.data_visita else ""

    @property
    def data_extenso_documento(self) -> str:
        if not self.data_visita:
            return f"{self.cidade}, ______ de ___________________ de _______."
        mes = MESES_PT.get(self.data_visita.month, "")
        return f"{self.cidade}, {self.data_visita.day:02d} de {mes} de {self.data_visita.year}."

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "protocolo": self.protocolo,
            "client_uuid": self.client_uuid,
            "escola_setor": self.escola_setor,
            "data_visita": self.data_visita.isoformat() if self.data_visita else None,
            "data_visita_br": self.data_visita_br,
            "endereco": self.endereco,
            "motivo_chamado": self.motivo_chamado,
            "tecnico": self.tecnico,
            "matricula": self.matricula,
            "problema_resolvido": self.problema_resolvido,
            "descricao_atendimento": self.descricao_atendimento,
            "cidade": self.cidade,
            "gestor_nome": self.gestor_nome,
            "tipo_assinatura": self.tipo_assinatura,
            "data_extenso_documento": self.data_extenso_documento,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
