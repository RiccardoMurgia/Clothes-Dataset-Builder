import {NgModule} from '@angular/core';
import {RouteReuseStrategy, RouterModule, Routes} from "@angular/router";

import {HomeComponent} from "./home/home.component";
import {AccountComponent} from "./account/account.component";
import {DatasetViewerComponent} from "./dataset-viewer/dataset-viewer.component";
import {CustomRouteReuseStrategy} from "./custom-route-reuse-strategy.service";

const routes: Routes = [
  {path: '', component: HomeComponent},
  {path: 'account', component: AccountComponent},
  {path: 'dataset_viewer', component:DatasetViewerComponent }
]

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
  providers: [{
    provide: RouteReuseStrategy,
    useClass: CustomRouteReuseStrategy,
  }],
})
export class AppRoutingModule {
}
