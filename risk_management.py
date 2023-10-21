from models import Solvency, RiskOracle, ClaimProcessing
from models import RiskMitigationStrategy, Vote
from flask import make_response, jsonify
from bson import ObjectId


def token_solvency():
    solvencies = Solvency.objects.all()
    return make_response(jsonify(
        [i.to_mongo().to_dict() for i in solvencies]
    ), 200)


def get_oracles():
    oracles = RiskOracle.objects.all()
    return make_response(jsonify(
        [i.to_mongo().to_dict() for i in oracles]
    ), 200)


def get_claim_processing_list():
    claim_proc = ClaimProcessing.objects.all()
    return make_response(jsonify(
        [i.to_mongo().to_dict() for i in claim_proc]
    ), 200)


def get_risk_mitigation_strategies():
    mitigation_strategies = RiskMitigationStrategy.objects.all()
    return make_response(jsonify(
        [i.to_mongo().to_dict() for i in mitigation_strategies]
    ), 200)


def save_vote_mitigation_strategies(strategy_id, pubkey, weightage, vote_type):
    vote = Vote(pubkey=pubkey, weightage=weightage)
    if vote_type.lower() == 'for':
        RiskMitigationStrategy.objects(
            id=ObjectId(strategy_id)
        ).update(add_to_set__for_votes=vote)
    elif vote_type.lower() == 'against':
        RiskMitigationStrategy.objects(
            id=ObjectId(strategy_id)
        ).update(add_to_set__against_votes=vote)

    return make_response(
        jsonify({"message": "Vote updated successfully"}), 200
    )


def save_vote_claim_processing(claim_id, pubkey, weightage, vote_type):
    vote = Vote(pubkey=pubkey, weightage=weightage)
    if vote_type.lower() == 'for':
        ClaimProcessing.objects(
            id=ObjectId(claim_id)
        ).update(add_to_set__for_votes=vote)
    elif vote_type.lower() == 'against':
        ClaimProcessing.objects(
            id=ObjectId(claim_id)
        ).update(add_to_set__against_votes=vote)

    return make_response(
        jsonify({"message": "Vote updated successfully"}), 200
    )
