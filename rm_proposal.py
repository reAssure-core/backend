import datetime
from models import RiskMitigationStrategy, RiskOracle, Vote, Insuree
from models import ClaimProcessing, UnderWriter, Claim, TokenMetadata
from flask import make_response, jsonify


def create_claim_processing_tender(request_body):
    claim_data = request_body.get('claim')
    processing_fee = request_body.get('processing_fee')
    settlement_breakdown = request_body.get('settlement_breakdown')
    waived_liability = request_body.get('waived_liability')
    for_votes_data = request_body.get('for_votes')
    against_votes_data = request_body.get('against_votes')
    expiry = datetime.strptime(request_body.get('expiry'), "%Y-%m-%d %H:%M:%S")

    # Create EmbeddedDocuments from extracted data
    insuree = Insuree(**claim_data.get('insuree'))
    underwriter = UnderWriter(**claim_data.get('underwriter'))
    claim = Claim(
        insuree=insuree,
        underwriter=underwriter,
        claim_amount=claim_data.get('claim_amount'),
        claim_file_date=datetime.strptime(claim_data.get('claim_file_date'), "%Y-%m-%d %H:%M:%S"),
        claim_docs_url=claim_data.get('claim_docs_url')
    )

    for_votes = [Vote(**vote) for vote in for_votes_data]
    against_votes = [Vote(**vote) for vote in against_votes_data]

    # Create and save ClaimProcessing document
    claim_processing = ClaimProcessing(
        claim=claim,
        processing_fee=processing_fee,
        settlement_breakdown=settlement_breakdown,
        waived_liability=waived_liability,
        for_votes=for_votes,
        against_votes=against_votes,
        expiry=expiry
    )

    claim_processing.save()

    return make_response(
        jsonify({"message": "Claim Process Tender Created"}), 200
    )


def create_risk_mitigation_strategy(request_body):
    strategy = RiskMitigationStrategy(
        token=TokenMetadata(**request_body.get('token', {})),
        insuree=Insuree(**request_body.get('insuree', {})),
        underwriter=UnderWriter(**request_body.get('underwriter', {})),
        for_votes=[Vote(**vote_data) for vote_data in request_body.get('for_votes', [])],
        against_votes=[Vote(**vote_data) for vote_data in request_body.get('against_votes', [])],
        risk_amount=request_body.get('risk_amount'),
        risk_model=request_body.get('risk_model'),
        processing_fee=request_body.get('processing_fee'),
        monitoring_oracle_addr=request_body.get('monitoring_oracle_addr'),
        transparency_ipfs=request_body.get('transparency_ipfs'),
        expiry=request_body.get('expiry')
    )

    strategy.save()

    return make_response(
        jsonify({
            "message": "Risk Mitigation Strategy Created & Deployed"
        }), 200
    )


def create_risk_oracle(request_body):
    token_metadata = TokenMetadata(**request_body.get('token', {}))
    insuree = Insuree(**request_body.get('insuree', {}))
    underwriter = UnderWriter(**request_body.get('underwriter', {}))

    risk_oracle = RiskOracle(
        token=token_metadata,
        insuree=insuree,
        underwriter=underwriter,
        oracle_address=request_body['oracle_address'],
        refresh_frequency=request_body['refresh_frequency'],
        choose_visualization=request_body['choose_visualization']
    )

    risk_oracle.save()

    return make_response(
        jsonify({"message": "Risk Oracle Created"}), 200
    )
