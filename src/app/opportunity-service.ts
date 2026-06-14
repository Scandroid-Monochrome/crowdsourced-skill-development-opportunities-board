import { Injectable } from '@angular/core';
import { httpResource } from '@angular/common/http';
import { Opportunity } from '../dataDefs';

const API_URL = "http://localhost:8000"

@Injectable({
  providedIn: 'root',
})
export class OpportunityService {
  // Function to generate new essay for specific college
  getOpps() {
    return httpResource<Opportunity[]>(() => `${API_URL}/opportunities`);
  }

  // Send a data modification request to the API/Back End Database
  postOpp(opp: Opportunity) {
    // Set our send/receive message format to JSON
    const headers: Headers = new Headers()
    headers.set('Content-Type', 'application/json')
    headers.set('Accept', 'application/json')

    // To prevent modification type errors
    opp.ID = Number(opp.ID);
    opp.name = String(opp.name)
    opp.description = String(opp.description);
    opp.link = String(opp.link);
    opp.repeatable = Boolean(opp.repeatable);
    opp.user = String(opp.user);
    // Create request body:
    var body: RequestInit | undefined = { method: 'POST', headers: headers, body: JSON.stringify(opp) }

    var currentUrl = API_URL + '/opportunities/';

    // Send the request and print the response
    console.log(currentUrl, body)
    return fetch(new Request(currentUrl, body));
  }

  getProfs() {
    return httpResource<string[]>(() => `${API_URL}/professions`);
  }
}
