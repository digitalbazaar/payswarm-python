"""PaySwarm context and frame constants."""

__all__ = [
  'CONTEXT_V1_URL',
  'CONTEXT_URL',
  'CONTEXTS',
  'CONTEXT',
  'FRAMES',
]

# Versioned PaySwarm JSON-LD context URLs.
CONTEXT_V1_URL = "https://w3id.org/payswarm/v1"

# Default PaySwarm JSON-LD context URL.
CONTEXT_URL = CONTEXT_V1_URL

# Supported PaySwarm JSON-LD contexts.
CONTEXTS = {}

# V1 PaySwarm JSON-LD context.
CONTEXTS[CONTEXT_V1_URL] = {
  # aliases
  'id': '@id',
  'type': '@type',

  # prefixes
  'ccard': 'https://w3id.org/commerce/creditcard#',
  'com': 'https://w3id.org/commerce#',
  'dc': 'http://purl.org/dc/terms/',
  'foaf': 'http://xmlns.com/foaf/0.1/',
  'gr': 'http://purl.org/goodrelations/v1#',
  'pto': 'http://www.productontology.org/id/',
  'ps': 'https://w3id.org/payswarm#',
  'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
  'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
  'sec': 'https://w3id.org/security#',
  'vcard': 'http://www.w3.org/2006/vcard/ns#',
  'xsd': 'http://www.w3.org/2001/XMLSchema#',

  # general
  'address': {'@id': 'vcard:adr', '@type': '@id'},
  'comment': 'rdfs:comment',
  'countryName': 'vcard:country-name',
  'created': {'@id': 'dc:created', '@type': 'xsd:dateTime'},
  'creator': {'@id': 'dc:creator', '@type': '@id'},
  'depiction': {'@id': 'foaf:depiction', '@type': '@id'},
  'description': 'dc:description',
  'email': 'foaf:mbox',
  'fullName': 'vcard:fn',
  'label': 'rdfs:label',
  'locality': 'vcard:locality',
  'postalCode': 'vcard:postal-code',
  'region': 'vcard:region',
  'streetAddress': 'vcard:street-address',
  'title': 'dc:title',
  'website': {'@id': 'foaf:homepage', '@type': '@id'},
  'Address': 'vcard:Address',

  # bank
  'bankAccount': 'bank:account',
  'bankAccountType': {'@id': 'bank:accountType', '@type': '@vocab'},
  'bankRoutingNumber': 'bank:routing',
  'BankAccount': 'bank:BankAccount',
  'Checking': 'bank:Checking',
  'Savings': 'bank:Savings',

  # credit card
  'cardBrand': {'@id': 'ccard:brand', '@type': '@vocab'},
  'cardCvm': 'ccard:cvm',
  'cardExpMonth': {'@id': 'ccard:expMonth', '@type': 'xsd:integer'},
  'cardExpYear': {'@id': 'ccard:expYear', '@type': 'xsd:integer'},
  'cardNumber': 'ccard:number',
  'AmericanExpress': 'ccard:AmericanExpress',
  'ChinaUnionPay': 'ccard:ChinaUnionPay',
  'CreditCard': 'ccard:CreditCard',
  'Discover': 'ccard:Discover',
  'Visa': 'ccard:Visa',
  'MasterCard': 'ccard:MasterCard',

  # commerce
  'account': {'@id': 'com:account', '@type': '@id'},
  'amount': 'com:amount',
  'authorized': {'@id': 'com:authorized', '@type': 'xsd:dateTime'},
  'balance': 'com:balance',
  'currency': {'@id': 'com:currency', '@type': '@vocab'},
  'destination': {'@id': 'com:destination', '@type': '@id'},
  'maximumAmount': 'com:maximumAmount',
  'maximumPayeeRate': 'com:maximumPayeeRate',
  'minimumPayeeRate': 'com:minimumPayeeRate',
  'minimumAmount': 'com:minimumAmount',
  'payee': {'@id': 'com:payee', '@type': '@id', '@container': '@set'},
  'payeeApplyAfter': {'@id': 'com:payeeApplyAfter', '@container': '@set'},
  'payeeApplyGroup': {'@id': 'com:payeeApplyGroup', '@container': '@set'},
  'payeeApplyType': {'@id': 'com:payeeApplyType', '@type': '@vocab'},
  'payeeGroup': {'@id': 'com:payeeGroup', '@container': '@set'},
  'payeeGroupPrefix': {'@id': 'com:payeeGroupPrefix', '@container': '@set'},
  'payeeExemptGroup': {'@id': 'com:payeeExemptGroup', '@container': '@set'},
  'payeeLimitation': {'@id': 'com:payeeLimitation', '@type': '@vocab'},
  'payeeRate': 'com:payeeRate',
  'payeeRateType': {'@id': 'com:payeeRateType', '@type': '@vocab'},
  'payeeRule': {'@id': 'com:payeeRule', '@type': '@id', '@container': '@set'},
  'paymentGateway': 'com:paymentGateway',
  'paymentMethod': {'@id': 'com:paymentMethod', '@type': '@vocab'},
  'paymentToken': 'com:paymentToken',
  'referenceId': 'com:referenceId',
  'settled': {'@id': 'com:settled', '@type': 'xsd:dateTime'},
  'source': {'@id': 'com:source', '@type': '@id'},
  'transfer': {'@id': 'com:transfer', '@type': '@id', '@container': '@set'},
  'vendor': {'@id': 'com:vendor', '@type': '@id'},
  'voided': {'@id': 'com:voided', '@type': 'xsd:dateTime'},
  'ApplyExclusively': 'com:ApplyExclusively',
  'ApplyInclusively': 'com:ApplyInclusively',
  'FinancialAccount': 'com:Account',
  'FlatAmount': 'com:FlatAmount',
  'Deposit': 'com:Deposit',
  'NoAdditionalPayeesLimitation': 'com:NoAdditionalPayeesLimitation',
  'Payee': 'com:Payee',
  'PayeeRule': 'com:PayeeRule',
  'PayeeScheme': 'com:PayeeScheme',
  'PaymentToken': 'com:PaymentToken',
  'Percentage': 'com:Percentage',
  'Transaction': 'com:Transaction',
  'Transfer': 'com:Transfer',
  'Withdrawal': 'com:Withdrawal',

  # currencies
  'USD': 'https://w3id.org/currencies/USD',

  # error
  # FIXME: add error terms
  # 'errorMessage': 'err:message'

  # payswarm
  'asset': {'@id': 'ps:asset', '@type': '@id'},
  'assetAcquirer': {'@id': 'ps:assetAcquirer', '@type': '@id'},
  # FIXME: support inline content
  'assetContent': {'@id': 'ps:assetContent', '@type': '@id'},
  'assetHash': 'ps:assetHash',
  'assetProvider': {'@id': 'ps:assetProvider', '@type': '@id'},
  'authority': {'@id': 'ps:authority', '@type': '@id'},
  'contract': {'@id': 'ps:contract', '@type': '@id'},
  'identityHash': 'ps:identityHash',
  # FIXME: move?
  'ipv4Address': 'ps:ipv4Address',
  'license': {'@id': 'ps:license', '@type': '@id'},
  'licenseHash': 'ps:licenseHash',
  'licenseTemplate': 'ps:licenseTemplate',
  'licenseTerms': {'@id': 'ps:licenseTerms', '@type': '@id'},
  'listing': {'@id': 'ps:listing', '@type': '@id'},
  'listingHash': 'ps:listingHash',
  'listingRestrictions': {'@id': 'ps:listingRestrictions', '@type': '@id'},
  'preferences': {'@id': 'ps:preferences', '@type': '@vocab'},
  'validFrom': {'@id': 'ps:validFrom', '@type': 'xsd:dateTime'},
  'validUntil': {'@id': 'ps:validUntil', '@type': 'xsd:dateTime'},
  'Asset': 'ps:Asset',
  'Budget': 'ps:Budget',
  'Contract': 'ps:Contract',
  'License': 'ps:License',
  'Listing': 'ps:Listing',
  'PersonalIdentity': 'ps:PersonalIdentity',
  'IdentityPreferences': 'ps:IdentityPreferences',
  'Profile': 'ps:Profile',
  'PurchaseRequest': 'ps:PurchaseRequest',
  'PreAuthorization': 'ps:PreAuthorization',
  'Receipt': 'ps:Receipt',
  'VendorIdentity': 'ps:VendorIdentity',

  # security
  'cipherAlgorithm': 'sec:cipherAlgorithm',
  'cipherData': 'sec:cipherData',
  'cipherKey': 'sec:cipherKey',
  'digestAlgorithm': 'sec:digestAlgorithm',
  'digestValue': 'sec:digestValue',
  'expiration': {'@id': 'sec:expiration', '@type': 'xsd:dateTime'},
  'initializationVector': 'sec:initializationVector',
  'nonce': 'sec:nonce',
  'normalizationAlgorithm': 'sec:normalizationAlgorithm',
  'owner': {'@id': 'sec:owner', '@type': '@id'},
  'password': 'sec:password',
  'privateKey': {'@id': 'sec:privateKey', '@type': '@id'},
  'privateKeyPem': 'sec:privateKeyPem',
  'publicKey': {'@id': 'sec:publicKey', '@type': '@id'},
  'publicKeyPem': 'sec:publicKeyPem',
  'publicKeyService': {'@id': 'sec:publicKeyService', '@type': '@id'},
  'revoked': {'@id': 'sec:revoked', '@type': 'xsd:dateTime'},
  'signature': 'sec:signature',
  'signatureAlgorithm': 'sec:signatureAlgorithm',
  'signatureValue': 'sec:signatureValue',
  'EncryptedMessage': 'sec:EncryptedMessage',
  'CryptographicKey': 'sec:Key',
  'GraphSignature2012': 'sec:GraphSignature2012'
}

# Default PaySwarm JSON-LD context.
CONTEXT = CONTEXTS[CONTEXT_URL]

# PaySwarm JSON-LD frames.
FRAMES = {}

# PaySwarm JSON-LD frame for an Asset.
FRAMES['Asset'] = {
  '@context': CONTEXT_URL,
  'type': 'Asset',
  'creator': {},
  'signature': {'@embed': True},
  'assetProvider': {'@embed': False}
}

# PaySwarm JSON-LD frame for a License.
FRAMES['License'] = {
  '@context': CONTEXT_URL,
  'type': 'License'
}

# PaySwarm JSON-LD frame for a Listing.
FRAMES['Listing'] = {
  '@context': CONTEXT_URL,
  'type': 'Listing',
  'asset': {'@embed': False},
  'license': {'@embed': False},
  'vendor': {'@embed': False},
  'signature': {'@embed': True}
}