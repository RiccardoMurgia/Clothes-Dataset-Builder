import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';


@Injectable({
  providedIn: 'root'
})
export class RestService {

  url: string = "http://127.0.0.1:5000/dataset_viewer";

  constructor(private http: HttpClient) {
  }

  ngOnInit() {
  }

  read_the_folder_structure() {
    return this.http.get(this.url);
  }

}
