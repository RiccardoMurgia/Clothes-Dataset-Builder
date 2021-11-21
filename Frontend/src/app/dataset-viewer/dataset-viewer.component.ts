import { Component, OnInit } from '@angular/core';
import {RestService} from "../rest.service";

declare function build_dataset_viewer(response: any):any

@Component({
  selector: 'app-dataset-viewer',
  templateUrl: './dataset-viewer.component.html',
  styleUrls: ['./dataset-viewer.component.css']
})
export class DatasetViewerComponent implements OnInit {

  constructor(private rs: RestService) {
  }

  ngOnInit() {
    this.rs.read_the_folder_structure()
      .subscribe
      (
        (response) => {
          //console.log(response)
          build_dataset_viewer(response)
        },
        (error) => {
          console.log("No Data Found" + error);
        }
      )
  }
}
