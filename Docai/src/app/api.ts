import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom,Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class Api {

  private ai_url = "http://127.0.0.1:8000/"

  constructor(
    private httpClient:HttpClient
  ){}


  async post<T = any>(url:string,data:any): Promise <T>{
    return await firstValueFrom(this.httpClient.post<T>(this.ai_url+url,data));
  }
  
}
