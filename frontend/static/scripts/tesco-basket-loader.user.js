// ==UserScript==
// @name         Mealie Tesco Loader
// @namespace    http://tampermonkey.net/
// @version      4.1
// @description  Loads items from Mealie into Tesco basket
// @author       Mealie
// @match        https://www.tesco.com/groceries/en-GB/basket*
// @match        https://www.tesco.com/groceries/en-GB/trolley*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function () {
    'use strict';

    // 1. Check for Mealie Items
    const hash = window.location.hash;
    if (!hash || !hash.includes('mealie_items=')) return;

    const params = new URLSearchParams(hash.substring(1));
    const itemsStr = params.get('mealie_items');
    const productIds = itemsStr ? itemsStr.split(',').filter(id => id) : [];

    if (productIds.length === 0) return;

    console.log('[Mealie] Initialized with items', productIds);

    // 2. State & Persistence
    const STORAGE_KEYS = {
        AUTH: 'mealie_tesco_auth',
        BASKET: 'mealie_tesco_basket',
        XSRF: 'mealie_tesco_xsrf',
        APIKEY: 'mealie_tesco_apikey'
    };

    let state = {
        authToken: localStorage.getItem(STORAGE_KEYS.AUTH),
        basketId: localStorage.getItem(STORAGE_KEYS.BASKET),
        xsrfToken: localStorage.getItem(STORAGE_KEYS.XSRF),
        apiKey: localStorage.getItem(STORAGE_KEYS.APIKEY),
        processed: false
    };

    // 3. Minimal UI Helper (Toast)
    function showToast(msg, type = 'info') {
        let toast = document.getElementById('mealie-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'mealie-toast';
            toast.style = "position: fixed; top: 20px; right: 20px; z-index: 99999; padding: 12px 20px; border-radius: 4px; font-family: sans-serif; font-size: 14px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: opacity 0.3s ease;";
            if (document.body) document.body.appendChild(toast);
            else window.addEventListener('DOMContentLoaded', () => document.body.appendChild(toast));
        }

        switch (type) {
            case 'success': toast.style.backgroundColor = '#008800'; break; // Green
            case 'error': toast.style.backgroundColor = '#d32f2f'; break; // Red
            default: toast.style.backgroundColor = '#00539f'; break; // Tesco Blue
        }

        toast.textContent = msg;
        toast.style.opacity = '1';

        if (type !== 'info') {
            setTimeout(() => { toast.style.opacity = '0'; }, 3000);
        }
    }

    showToast("Mealie: Initializing...");

    // 4. Helper: Recursive Search
    const findKey = (obj, targetKey) => {
        if (!obj || typeof obj !== 'object') return null;
        if (obj[targetKey]) return obj[targetKey];
        for (const key in obj) {
            if (Object.prototype.hasOwnProperty.call(obj, key)) {
                const result = findKey(obj[key], targetKey);
                if (result) return result;
            }
        }
        return null;
    };

    const processHeaders = (headers) => {
        let headerMap = {};

        if (headers instanceof Headers) {
            headers.forEach((v, k) => headerMap[k.toLowerCase()] = v);
        } else if (typeof headers === 'object') {
            Object.keys(headers).forEach(k => headerMap[k.toLowerCase()] = headers[k]);
        } else if (typeof headers === 'string') {
            headers.split(/[\r\n]+/).forEach(line => {
                const parts = line.split(': ');
                if (parts.length >= 2) {
                    headerMap[parts[0].toLowerCase()] = parts.slice(1).join(': ');
                }
            });
        }

        const auth = headerMap['authorization'];
        if (auth && auth !== state.authToken) {
            state.authToken = auth;
            localStorage.setItem(STORAGE_KEYS.AUTH, auth);
            checkAndExecute();
        }

        const apikey = headerMap['x-apikey'];
        if (apikey && apikey !== state.apiKey) {
            state.apiKey = apikey;
            localStorage.setItem(STORAGE_KEYS.APIKEY, apikey);
            checkAndExecute();
        }

        // Optional XSRF capture
        Object.keys(headerMap).forEach(key => {
            if (key.includes('xsrf') || key.includes('csrf') || (key.includes('token') && !key.includes('auth'))) {
                const val = headerMap[key];
                if (val && val !== state.xsrfToken) {
                    state.xsrfToken = val;
                    localStorage.setItem(STORAGE_KEYS.XSRF, val);
                }
            }
        });
    };

    const processBody = (body) => {
        if (!body) return;
        try {
            if (typeof body === 'string') body = JSON.parse(body);
            const id = findKey(body, 'orderId') || findKey(body, 'basketId');
            if (id && typeof id === 'string' && id.startsWith('trn:tesco') && id !== state.basketId) {
                state.basketId = id;
                localStorage.setItem(STORAGE_KEYS.BASKET, id);
                checkAndExecute();
            }
        } catch (e) { }
    };

    // 5. FETCH Interceptor
    const originalFetch = window.fetch;
    window.fetch = async function (...args) {
        const [resource, config] = args;
        const url = resource ? resource.toString() : '';

        if (url.includes('tesco.com') || url.includes('graphql')) {
            if (config) {
                if (config.headers) processHeaders(config.headers);
                if (config.body) processBody(config.body);
            }
        }

        const response = await originalFetch.apply(this, args);

        if (url.includes('tesco.com') || url.includes('graphql')) {
            try {
                const clone = response.clone();
                clone.json().then(data => processBody(data)).catch(() => { });
            } catch (e) { }
        }
        return response;
    };

    // 6. XHR Interceptor
    const originalOpen = XMLHttpRequest.prototype.open;
    const originalSend = XMLHttpRequest.prototype.send;
    const originalSetRequestHeader = XMLHttpRequest.prototype.setRequestHeader;

    XMLHttpRequest.prototype.open = function (...args) {
        this._url = args[1];
        this._requestHeaders = {};
        return originalOpen.apply(this, args);
    };

    XMLHttpRequest.prototype.setRequestHeader = function (header, value) {
        this._requestHeaders[header.toLowerCase()] = value;
        return originalSetRequestHeader.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function (body) {
        if (this._url && (this._url.includes('tesco.com') || this._url.includes('graphql'))) {
            processHeaders(this._requestHeaders);
            processBody(body);
        }

        this.addEventListener('load', function () {
            if (this._url && (this._url.includes('tesco.com') || this._url.includes('graphql'))) {
                try {
                    const data = JSON.parse(this.responseText);
                    processBody(data);
                } catch (e) { }
            }
        });

        return originalSend.apply(this, arguments);
    };

    // 7. Execution Logic
    function checkAndExecute() {
        if (state.authToken && state.basketId && state.apiKey && !state.processed && productIds.length > 0) {
            state.processed = true;
            addItemsToBasket();
        }
    }

    function addItemsToBasket() {
        showToast("Mealie: Adding items to basket...");

        // Aggregate quantities
        const quantityMap = {};
        productIds.forEach(id => {
            quantityMap[id] = (quantityMap[id] || 0) + 1;
        });

        const items = Object.keys(quantityMap).map(id => ({
            adjustment: false,
            id: id,
            newUnitChoice: "pcs",
            newValue: quantityMap[id],
            substitutionOption: "DoNotSubstitute"
        }));

        const payload = {
            operationName: "UpdateBasket",
            query: "mutation UpdateBasket($items: [BasketLineItemInputType], $orderId: ID) { basket(items: $items, orderId: $orderId) { id } }",
            variables: {
                orderId: state.basketId,
                items: items
            }
        };

        const headers = {
            'Content-Type': 'application/json',
            'Authorization': state.authToken,
            'x-apikey': state.apiKey
        };

        // Only send XSRF if we DON'T have an API key (fallback), though we prioritize API key now.
        if (state.xsrfToken && !state.apiKey) {
            headers['x-xsrf-token'] = state.xsrfToken;
        }

        originalFetch('https://xapi.tesco.com/v1/graphql', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload)
        })
            .then(res => res.json())
            .then(data => {
                if (data.errors) {
                    console.error('[Mealie] GraphQL Errors', data.errors);
                    showToast(`Mealie Error: ${data.errors[0].message}`, 'error');
                    state.processed = false;
                } else {
                    showToast("Mealie: Success! Reloading...", 'success');
                    setTimeout(() => {
                        window.location.hash = '';
                        window.location.reload();
                    }, 1500);
                }
            })
            .catch(err => {
                console.error('[Mealie] Network Error', err);
                showToast("Mealie: Network Error", 'error');
                state.processed = false;
            });
    }

    // Initial check
    checkAndExecute();

})();
