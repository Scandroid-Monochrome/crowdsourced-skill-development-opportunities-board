import { Component, inject, signal, linkedSignal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FormField, form, required } from '@angular/forms/signals';
import { OpportunityService } from './opportunity-service';
import { RouterOutlet } from '@angular/router';
import { httpResource } from '@angular/common/http';
import { Opportunity } from '../dataDefs';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  // Display Opportunities
  oppService = inject(OpportunityService)
  opportunityResource = this.oppService.getOpps()
  oppList = this.opportunityResource.value

  // Get Professions
  profResource = this.oppService.getProfs()
  profList = this.profResource.value

  // Post Opportunity
  create_opp = signal<boolean>(false)
  // new_opp = signal<Opportunity>({
  //   ID: 0,
  //   name: "",
  //   description: "",
  //   link: "",
  //   location: [],
  //   professions: [],
  //   repeatable: false,
  //   user: "",
  // })

  // Testing 
  new_opp = signal<Opportunity>({
    ID: 0,
    name: "New Opportunity",
    description: "A short description of the opportunity",
    link: "Not a real link",
    location: [],
    professions: [],
    repeatable: false,
    user: "",
  })

  submitOpp() {
    // console.log(this.new_opp())
    this.oppService.postOpp(this.new_opp())
    this.opportunityResource.reload()
  }

  toggleProfession(profession: string, isChecked: boolean) {
    if (isChecked) {
      this.new_opp().professions.push(profession);
    } else {
      const index = this.new_opp().professions.indexOf(profession);
      if (index !== -1) {
        this.new_opp().professions.splice(index, 1);
      }
    }
    console.log(this.new_opp().professions)
  }
}

