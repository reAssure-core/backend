from mongoengine import Document, StringField, IntField, DateTimeField
from mongoengine import URLField, EmbeddedDocumentListField, EmbeddedDocumentField
from mongoengine import EmbeddedDocument, DateField, BooleanField, FloatField
from random import randint


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


class UnderWrittenPolicy(Document):
    insurer = EmbeddedDocumentField(UnderWriter)
    policy_doc_url = URLField(required=True)
    claim_processor = StringField(
        required=True, choices=["self_proc", "open_bid", "holder_votes"]
    )
    insuree = EmbeddedDocumentField(Insuree)
    policy_premium = IntField()
    policy_expiry = DateField()
    coverage_amt = StringField()
    underwriting_commission = FloatField()
    coverage_details = StringField()
    risk_mitigation = BooleanField(required=True, default=False)
    deepbook_liquidity = BooleanField(required=True, default=False)
    is_expired = BooleanField()


class MarketplaceListing(Document):
    token_name = EmbeddedDocumentField(TokenMetadata)
    underwriter = EmbeddedDocumentField(UnderWriter)
    validity = DateField()
    apy = FloatField()
    liquidity = FloatField()
    creation_date = DateTimeField()
    hotness = IntField(default=randint(1, 100))
    has_community_oracle = BooleanField()


class Holdings(EmbeddedDocument):
    token = EmbeddedDocumentField(TokenMetadata)
    underwriter = EmbeddedDocumentField(UnderWriter)
    insuree = EmbeddedDocumentField(Insuree)
    current_val = FloatField()


class Transactions(EmbeddedDocument):
    txn_type = StringField(choices=["buy", "sell"])
    token = EmbeddedDocumentField(TokenMetadata)
    txn_date = DateTimeField()
    txn_time_in_mod = IntField()
    gas = FloatField()


class Portfolio(Document):
    user_pubkey = StringField()
    balance = FloatField()
    monthly_chart = URLField()
    weekly_chart = URLField()
    yearly_chart = URLField()
    best_performer = EmbeddedDocumentField(TokenMetadata)
    best_underwriter = EmbeddedDocumentField(UnderWriter)
    my_holdings = EmbeddedDocumentListField(Holdings)
    my_txns = EmbeddedDocumentListField(Transactions)


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


class RiskOracle(Document):
    token = EmbeddedDocumentField(TokenMetadata)
    insuree = EmbeddedDocumentField(Insuree)
    underwriter = EmbeddedDocumentField(UnderWriter)
    oracle_address = StringField()
    refresh_frequency = IntField()
    choose_visualization = StringField(choices=["bar", "line"])


class Solvency(Document):
    token = EmbeddedDocumentField(TokenMetadata)
    treasury_value = URLField()
