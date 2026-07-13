from flask import Flask, render_template, request, jsonify
import requests
import base64
import urllib.parse

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/update-passwords', methods=['POST'])
def update_passwords():
    data = request.json
    
    env_id = data.get('envId')
    api_path = data.get('apiPath', 'https://api.pingone.com/v1').rstrip('/')
    auth_path = data.get('authPath', 'https://auth.pingone.com').rstrip('/')
    client_id = data.get('clientId')
    client_secret = data.get('clientSecret')
    usernames_raw = data.get('usernames', '')
    new_password = data.get('newPassword')

    usernames = [u.strip() for u in usernames_raw.split('\n') if u.strip()]
    
    if not all([env_id, client_id, client_secret, usernames, new_password]):
        return jsonify({'error': 'Missing required fields'}), 400

    token_url = f"{auth_path}/{env_id}/as/token"
    auth_bytes = f"{client_id}:{client_secret}".encode('utf-8')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode(auth_bytes).decode('utf-8')
    }
    payload = {'grant_type': 'client_credentials'}
    
    try:
        token_res = requests.post(token_url, headers=headers, data=payload)
        token_res.raise_for_status()
        access_token = token_res.json().get('access_token')
    except Exception as e:
        error_msg = token_res.json() if 'token_res' in locals() else str(e)
        return jsonify({'error': 'Failed to authenticate with PingOne', 'details': error_msg}), 401

    auth_header = {
        'Authorization': f'Bearer {access_token}', 
        'Content-Type': 'application/json'
    }
    
    results = []

    for username in usernames:
        try:
            safe_username = urllib.parse.quote(username)
            search_url = f"{api_path}/environments/{env_id}/users?filter=username eq \"{safe_username}\""
            search_res = requests.get(search_url, headers=auth_header)
            search_res.raise_for_status()
            
            users_data = search_res.json().get('_embedded', {}).get('users', [])
            if not users_data:
                results.append({'username': username, 'status': 'Failed', 'message': 'User not found in PingOne'})
                continue
            
            user_id = users_data[0].get('id')
            update_url = f"{api_path}/environments/{env_id}/users/{user_id}/password"
            
            pwd_headers = {
                'Authorization': f'Bearer {access_token}', 
                'Content-Type': 'application/vnd.pingidentity.password.reset+json'
            }
            update_payload = {"newPassword": new_password}
            
            update_res = requests.put(update_url, headers=pwd_headers, json=update_payload)
            
            if update_res.status_code in (200, 204):
                results.append({'username': username, 'status': 'Success', 'message': f'Password updated. (ID: {user_id})'})
            else:
                if update_res.status_code in (415, 400):
                    pwd_headers['Content-Type'] = 'application/vnd.pingidentity.password.set+json'
                    fallback_payload = {"value": new_password, "forceChange": False}
                    update_res_fallback = requests.put(update_url, headers=pwd_headers, json=fallback_payload)
                    
                    if update_res_fallback.status_code in (200, 204):
                        results.append({'username': username, 'status': 'Success', 'message': f'Password updated via set+json. (ID: {user_id})'})
                        continue
                    else:
                        error_body = update_res_fallback.text
                else:
                    error_body = update_res.text
                        
                results.append({'username': username, 'status': 'Failed', 'message': str(error_body)})

        except Exception as e:
            results.append({'username': username, 'status': 'Failed', 'message': str(e)})

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
