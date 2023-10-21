from models import MarketplaceListing
from flask import jsonify, make_response
import json


def fetch_listings(token_name, is_expired, has_community_oracle, order_by, start_with):

    query = MarketplaceListing.objects

    if token_name:
        query = query.filter(token_name__name__icontains=token_name)

    if is_expired is not None:
        query = query.filter(is_expired=is_expired)

    if has_community_oracle is not None:
        query = query.filter(has_community_oracle=has_community_oracle)

    if order_by:
        if order_by in ['hotness', 'apy', 'liquidity', 'creation_date']:
            query = query.order_by(f'-{order_by}')
        else:
            return {'error': 'Invalid order_by parameter'}, 400

    result = [json.loads(item.to_json()) for item in query]

    # Place the 'start_with' token at the beginning of the result list if exists
    if start_with:
        for item in result:
            if start_with.lower() == item["token_name"]["name"].lower():
                result.remove(item)
                result.insert(0, item)

    return make_response(jsonify(result), 200)
