from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from underwrite_connector import autocomplete_policy_specs, underwrite_policy
from marketplace import fetch_listings
from portfolio import portfolio_performance, portfolio_txns, condensed_holdings
from risk_management import token_solvency, get_oracles, get_risk_mitigation_strategies
from risk_management import get_claim_processing_list, save_vote_mitigation_strategies
from risk_management import save_vote_claim_processing
from rm_proposal import create_risk_oracle, create_risk_mitigation_strategy
from rm_proposal import create_claim_processing_tender
from marketplace_details import get_marketplace_value
from flask_cors import CORS
import mongoengine
import weaviate
from project_secrets import weaviateURI, mongouri

mitigationOn = False
app = Flask(__name__)
api = Api(app)
cors = CORS(app)
mongoengine.connect(
    host=mongouri
)
weviateClient = weaviate.Client(
    url=weaviateURI
)
className = "AutofillTest"
try:
    class_obj = {
        "class": className,
        "vectorizer": "none",
    }
    weviateClient.schema.create_class(class_obj)
except Exception:
    pass


class AutoCompletePolicyDetails(Resource):
    def post(self):
        return autocomplete_policy_specs(request, weviateClient)


class UnderwritePolicy(Resource):
    def post(self):
        # This is just to save the policy metadata and upload files to IPNS/IPFS
        data = request.get_json()
        return underwrite_policy(data)

    def put(self):
        # This is mainly post token creation to update the token address and other metadata
        pass


class PortfolioHoldings(Resource):
    def get(self):
        pubkey = request.args.get("pub_key")
        return portfolio_performance(pubkey)


class PortfolioHistory(Resource):
    def get(self):
        pubkey = request.args.get("pub_key")
        token_name = request.args.get("token_name", None)
        export_csv = request.args.get("to_export", False, type=bool)
        return portfolio_txns(pubkey, token_name, export_csv)


class PortfolioPerformance(Resource):
    def get(self):
        pubkey = request.args.get("pub_key")
        return condensed_holdings(pubkey)


class MarketPlaceListings(Resource):
    def get(self):
        token_name = request.args.get('token_name')
        start_with = request.args.get('start_with')
        is_expired = request.args.get('is_expired', type=bool)
        has_community_oracle = request.args.get('has_community_oracle', type=bool)
        order_by = request.args.get('order_by')
        return fetch_listings(
            token_name, is_expired, has_community_oracle,
            order_by, start_with
        )


class MarketPlaceItems(Resource):
    def get(self):
        return get_marketplace_value(mitigationOn)

    def put(self):
        pass


class RiskMitigationStrategy(Resource):
    def get(self):
        return get_risk_mitigation_strategies()

    def put(self):
        strategy_id = request.args.get("strategy_id")
        pubkey = request.args.get('pubkey')
        weightage = request.args.get('weightage')
        vote_type = request.args.get('vote_type', 'for')
        return save_vote_mitigation_strategies(
            strategy_id, pubkey, weightage, vote_type
        )

    def post(self):
        strategy_data = request.get_json()
        mitigationOn = True
        return create_risk_mitigation_strategy(strategy_data)


class ClaimProcessorSelection(Resource):
    def get(self):
        return get_claim_processing_list()

    def put(self):
        claim_id = request.args.get("strategy_id")
        pubkey = request.args.get('pubkey')
        weightage = request.args.get('weightage')
        vote_type = request.args.get('vote_type', 'for')
        return save_vote_claim_processing(
            claim_id, pubkey, weightage, vote_type
        )

    def post(self):
        claim_proc_data = request.get_json()
        return create_claim_processing_tender(claim_proc_data)


class RiskOracles(Resource):
    def get(self):
        return get_oracles()

    def post(self):
        risk_oracle_data = request.get_json()
        return create_risk_oracle(risk_oracle_data)


class Solvency(Resource):
    def get(self):
        return token_solvency()

    def put(self):
        pass


class Ping(Resource):
    def get(self):
        return make_response(jsonify({"status": "API is Up"}), 200)


api.add_resource(AutoCompletePolicyDetails, '/underwrite/autocomplete')
api.add_resource(UnderwritePolicy, "/underwrite/save")
api.add_resource(PortfolioHistory, "/portfolio/history")
api.add_resource(PortfolioHoldings, "/portfolio/holdings")
api.add_resource(PortfolioPerformance, "/portfolio/performance")
api.add_resource(MarketPlaceListings, "/marketplace/list")
api.add_resource(MarketPlaceItems, "/marketplace/details")
api.add_resource(RiskMitigationStrategy, "/risk/mitigations")
api.add_resource(RiskOracles, "/risk/oracles")
api.add_resource(ClaimProcessorSelection, "/risk/claims")
api.add_resource(Solvency, "/risk/solvency")
api.add_resource(Ping, "/ping")


if __name__ == '__main__':
    app.run(debug=True)
