import {NgModule} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';
import {AppRoutingModule} from './app-routing.module';

import {AppComponent} from './app.component';
import {HomeComponent} from './home/home.component';
import {DatasetViewerComponent} from "./dataset-viewer/dataset-viewer.component";
import {AccountComponent} from "./account/account.component";

import {HttpClientModule} from "@angular/common/http";
import {RestService} from "./rest.service";


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    DatasetViewerComponent,
    AccountComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule

  ],
  providers: [RestService],
  bootstrap: [AppComponent]
})
export class AppModule {
}
