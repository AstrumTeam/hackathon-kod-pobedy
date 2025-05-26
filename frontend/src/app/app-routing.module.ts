import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MainComponent } from './components/main/main.component';
import { CreateComponent } from './components/create/create.component';
import { ResultComponent } from './components/result/result.component';
import { SingleVideoComponent } from './components/single-video/single-video.component';

const routes: Routes = [
  {path: '', component: MainComponent},
  {path:'create', component: CreateComponent},
  {path: 'result', component: ResultComponent},
  {path: 'video/:id', component: SingleVideoComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
