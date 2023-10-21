from flask import make_response, jsonify
from models import MarketplaceListing, UnderWrittenPolicy
import json
from datetime import datetime, timedelta
import random


def get_marketplace_value(mitigationValue=False):
    listing = json.loads(MarketplaceListing.objects.first().to_json())
    underwritten = UnderWrittenPolicy.objects.first()
    listing["description"] = f"Premium: {underwritten.policy_premium}\nCoverage Amount:\n{underwritten.coverage_amt}\nCoverage Details:\n{underwritten.coverage_details}"
    listing["insuree"] = json.loads(underwritten.insuree.to_json())
    listing["exipry"] = underwritten["policy_expiry"]
    listing["insuree"] = {
        "name": "Alphabet Inc.",
        "logo": "https://assets.stickpng.com/images/5847f9cbcef1014c0b5e48c8.png",
        "site": "https://about.google.com"
    }
    listing["oracles"] = {
        "Pool Solvency": {"value": "100%", "updated": datetime.now()-timedelta(minutes=random.randint(1,5))},
        "Dependency Risk": {"value": ["0.45" if not mitigationValue else "0.23"][0], "updated": datetime.now()-timedelta(minutes=random.randint(1,5))},
        "Core Language Risk": {"value": "Golang (in-house)", "updated": datetime.now()-timedelta(minutes=random.randint(1,5))},
        "Terraform Script Risk": {"value": "None", "updated": datetime.now()-timedelta(minutes=random.randint(1,5))},
        "Secrets Leak Risk": {"value": "0.001%", "updated": datetime.now()-timedelta(minutes=random.randint(1,5))}
    }
    return make_response(jsonify(listing), 200)
