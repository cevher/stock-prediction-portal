import axios from "axios";

const BASE_URL = import.meta.env.VITE_BACKEND_BASE_API

const axiosInstance = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    }

})

// Request interceptors
axiosInstance.interceptors.request.use(
    function (config){
        const accessToken = localStorage.getItem("accessToken");

        if(accessToken){
            config.headers['Authorization'] = `Bearer ${accessToken}`;
        }

        return config;
    },
    function(error) {
        return Promise.reject(error);
    }
);

axiosInstance.interceptors.response.use(
    function(response) {
        return response;
    },
   async function(error){
        const originalRequest = error.config;
        if(error.response.status == 401 && !originalRequest.retry){
            originalRequest.retry = true;
            const refreshToken = localStorage.getItem("refreshToken");
            
            try {
                const response = await axiosInstance.post('/token/refresh/', {refresh: refreshToken});     
                localStorage.setItem('accessToken', response.data.access);
                originalRequest.headers['Authorization'] = `Bearer ${response.data.access}`;
                return axiosInstance(originalRequest);
            } catch (error) {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                window.location.href= '/login';
            }
        }
    }
);

export default axiosInstance;