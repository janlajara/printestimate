import {useToast} from 'vue-toastification'
import {reference} from '@/utils/format.js'

const toast = useToast();
const showToast = (type='default', message=null)=> {
    if (message != null)
        return toast(message, {type});
}
const toastResponse = (response, success, error)=> {
    if (response.status >= 200 && response.status <= 299) {
        if (success) showToast("success", success);
    } else {
        if (error) showToast("error", error);
        console.error(response);
    }
};

const _axios = require('axios')
const API_HOSTNAME = 'http://localhost:8000'
const AXIOS =  {
    execute: async (method, uri, success, error, data, params)=> {
        const methods = ["post", "put", "get", "delete", "options"];
        const url = API_HOSTNAME + uri;
        const config = {
            url: url,
            method: methods[method],
            data, params
        }; 
        let response; 

        try {
            response = await _axios.request(config);
            if (success != null || error != null)
                toastResponse(response, success, error);
        } catch (err) {
            showToast('error', 'An error occurred in the server. Please try again.')
            let error = err.response.data;
            if (err.response.data.properties) {
                const errArr = [];
                Object.entries(err.response.data.properties).forEach(entry => {
                    errArr.push(`${entry[0]} : ${entry[1]}`)
                })
                error = errArr.join(', ');
            }
            return {
                error
            };
        }
        return response;
    },
    POST: 0,
    PUT: 1,
    GET: 2,
    DELETE: 3,
    OPTIONS: 4,
}


export {AXIOS, showToast, toastResponse, reference};