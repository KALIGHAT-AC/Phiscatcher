import axios from "axios";

const API_URL = "http://localhost:8000";

const api = axios.create({
    baseURL: API_URL
});

export const getLatestFlows = async () => {

    const response = await api.get(
        "/api/flows"
    );

    return response.data;

};

export const getDashboardStats = async () => {

    const response = await api.get(
        "/api/dashboard/stats"
    );

    return response.data;

};

export default api;