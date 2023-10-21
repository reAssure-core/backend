from utils import allowed_file
import os
import json
from flask import make_response, jsonify
from models import UnderWrittenPolicy, MarketplaceListing, TokenMetadata
from utils import add_to_embeddings, read_embeddings
from utils import msg_formatter, openai_autcomplete
import random
from datetime import datetime

already_embedded_files = []


def autocomplete_policy_specs(request, dbClient):
    # check if the post request has the file part
    if 'file' not in request.files:
        return {'error': 'No file part'}

    file = request.files['file']

    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return {'error': 'No selected file'}

    if not (file and allowed_file(file.filename)):
        return {'success': 'Autocomplete failed'}

    filename = os.path.join("/home/priyeshsriv/unfoldapis/", file.filename)
    file.save(filename)
    if filename not in already_embedded_files:
        already_embedded_files.append(add_to_embeddings(dbClient, filename))
    queries = [
        'who is the insuree in this policy?',
        'who is the insurer in this policy?',
        'what is the premium amount?',
        'when does the policy expire?',
        'what is the coverage amount? [Mention the maximum coverage amount of this policy (mentioned at the time of sales) along with maximum amount per claim, maximum amount for copay and so on.]',
        'Give some coverage details [Itemized details on coverage specifics with payment limit per billable item, disbursal conditions, payout schedules, dispute resolution and jurisdiction information.]'
    ]
    answers = []
    for i in range(len(queries)):
        context, chunks = read_embeddings(queries[i], dbClient)
        answers.append(
            list(json.loads(
                openai_autcomplete(msg_formatter(context, queries[i]))
            ).values())[0]
        )

    return make_response(jsonify({
        "insurer": {
            "name": answers[0],
            "logo": "https://i.ibb.co/hgr21ZC/ALV-DE-D.png",
            "site": "https://www.allianz.com/en.html"
        },
        "policy_doc_url": "https://www.allianz.com/policies/meta12345.pdf",
        "claim_processor": "holder_votes",
        "insuree": {
            "name": answers[1],
            "logo": "https://assets.stickpng.com/images/5847f9cbcef1014c0b5e48c8.png",
            "site": "https://about.google.com"
        },
        "policy_premium": answers[2],
        "policy_expiry": answers[3],
        "coverage_amt": answers[4],
        "coverage_details": answers[5]
    }), 200)


def underwrite_policy(data):
    try:
        policy = UnderWrittenPolicy(
            insurer=data['insurer'],
            policy_doc_url=data['policy_doc_url'],
            claim_processor=data['claim_processor'],
            insuree=data['insuree'],
            policy_premium=data['policy_premium'],
            policy_expiry=data['policy_expiry'],
            coverage_amt=data['coverage_amt'],
            underwriting_commission=data['underwriting_commission'],
            coverage_details=data['coverage_details'],
            risk_mitigation=data['risk_mitigation'],
            deepbook_liquidity=data['deepbook_liquidity']
        )
        policy.save()
        token_data = TokenMetadata(
            name=data["insuree"]["name"],
            logo=data["insuree"]["logo"],
            symbol=data["insuree"]["name"].replace(" ", "").upper()[:3]
        )
        market_place = MarketplaceListing(
            token_name=token_data,
            underwriter=data['insurer'],
            validity=data['policy_expiry'],
            apy=random.randint(1, 18)/100,
            liquidity=data['coverage_amt'],
            creation_date=datetime.now(),
            has_community_oracle=False
        )
        market_place.save()
        return make_response(
            jsonify({"message": "Policy Saved Successfully"}), 200
        )
    except Exception as e:
        print(e)
        return make_response(
            jsonify({"message": "Policy Save Failed"}), 400
        )
