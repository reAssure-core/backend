from mongoengine import Document, StringField, IntField, DateTimeField
from mongoengine import URLField, EmbeddedDocumentListField, FloatField
from mongoengine import EmbeddedDocument, BooleanField, EmbeddedDocumentField


class Insuree(EmbeddedDocument):
    name = StringField()
    logo = URLField()
    site = URLField()


class UnderWriter(EmbeddedDocument):
    name = StringField()
    logo = URLField()
    site = URLField()
    pub_key = StringField()


class TokenMetadata(EmbeddedDocument):
    name = StringField()
    logo = URLField()
    symbol = StringField()


class Vote(EmbeddedDocument):
    pubkey = StringField()
    weightage = IntField()


class RiskMitigationStrategy(Document):
    token = EmbeddedDocumentField(TokenMetadata)
    insuree = EmbeddedDocumentField(Insuree)
    underwriter = EmbeddedDocumentField(UnderWriter)
    for_votes = EmbeddedDocumentListField(Vote)
    against_votes = EmbeddedDocumentListField(Vote)
    risk_amount = FloatField()
    risk_model = StringField()
    processing_fee = IntField()
    monitoring_oracle_addr = StringField()
    transparency_ipfs = URLField()
    expiry = DateTimeField()


class Claim(EmbeddedDocument):
    insuree = EmbeddedDocumentField(Insuree)
    underwriter = EmbeddedDocumentField(UnderWriter)
    claim_amount = FloatField()
    claim_file_date = DateTimeField()
    claim_docs_url = URLField()


class ClaimProcessing(Document):
    claim = EmbeddedDocumentField(Claim)
    processing_fee = FloatField()
    settlement_breakdown = StringField()
    waived_liability = BooleanField()
    for_votes = EmbeddedDocumentListField(Vote)
    against_votes = EmbeddedDocumentListField(Vote)
    expiry = DateTimeField()


