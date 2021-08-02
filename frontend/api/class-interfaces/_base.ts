import { ApiRequestInstance } from "~/types/api";

export class BaseAPIClass {
    requests: ApiRequestInstance
    
    constructor(requests: ApiRequestInstance) {
        this.requests = requests;
    }
}

