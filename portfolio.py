from models import Portfolio
from flask import jsonify, make_response, Response


def portfolio_performance(pub_key):
    portfolio = Portfolio.objects(user_pubkey=pub_key).exclude(
        'my_holdings', 'my_txns'
    ).first()
    return make_response(jsonify(portfolio.to_mongo().to_dict()), 200)


def portfolio_txns(pub_key, token_name=None, export_csv=False):
    filter_args = {
        "user_pubkey": pub_key
    }

    if token_name:
        filter_args["my_txns__token__name__icontains"] = token_name

    portfolio = Portfolio.objects(**filter_args).only("my_txns").first()

    if not portfolio:
        return make_response(
            jsonify(
                {'error': 'No transactions found for the given user or token name'}
            ),
            404
        )

    transactions = portfolio.my_txns[:10]

    if export_csv:
        # Check if transactions have token names, include only those that have
        csv_data = "txn_type,token_name,txn_date,txn_time_in_mod,gas\n"  # Header
        csv_data += "\n".join([
            f'{txn.txn_type},{txn.token.name if txn.token and txn.token.name else "N/A"},{txn.txn_date},{txn.txn_time_in_mod},{txn.gas}'
            for txn in transactions
        ])

        return Response(
            csv_data,
            headers={
                'Content-Disposition': 'attachment; filename=transactions.csv',
                'Content-Type': 'text/csv'
            },
            status=200
        )

    return make_response(jsonify(transactions), 200)


def condensed_holdings(pub_key):
    portfolio = Portfolio.objects(
        user_pubkey=pub_key
    ).only("my_holdings").first()

    underwriter_aggregate = {}
    insuree_aggregate = {}
    total_current_val = 0

    for holding in portfolio.my_holdings:
        underwriter_name = holding.underwriter.name
        insuree_name = holding.insuree.name
        current_val = holding.current_val

        total_current_val += current_val

        if underwriter_name in underwriter_aggregate:
            underwriter_aggregate[underwriter_name] += current_val
        else:
            underwriter_aggregate[underwriter_name] = current_val

        if insuree_name in insuree_aggregate:
            insuree_aggregate[insuree_name] += current_val
        else:
            insuree_aggregate[insuree_name] = current_val

    wallet = portfolio.balance - total_current_val
    policy_tokens = total_current_val
    claims = policy_tokens * 0.1

    response = {
        "underwriter_aggregate": underwriter_aggregate,
        "insuree_aggregate": insuree_aggregate,
        "wallet": wallet,
        "policy_tokens": policy_tokens,
        "claims": claims
    }

    return jsonify(response)
