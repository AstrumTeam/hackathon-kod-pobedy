import { AfterViewInit, Component, OnInit } from '@angular/core';
import { Video } from '../main/main.component';
import * as Plyr from 'plyr';
import { TranslateService } from '@ngx-translate/core';
import { ActivatedRoute } from '@angular/router';
import { VideoService } from 'src/app/services/VideoService';
import { ServerUrlService } from 'src/app/services/ServerURLService';

@Component({
  selector: 'app-single-video',
  templateUrl: './single-video.component.html',
  styleUrls: ['./single-video.component.css']
})
export class SingleVideoComponent implements AfterViewInit, OnInit {
  videoId: string = "";

  url = "";

  video: Video = {
    id: "",
    letter: "",
    video_filename: "",
    preview_filename: "",
    author: "",
  }
//   video: Video = {
//     video: 'assets/videos/example.mp4',
//     poster: 'assets/photos/photo.jpeg',
//     id: '0',
//     letter: `Здравствуй, дорогая моя, любимая жена Рая! Крепко целую тебя. 
// Меня ранило 24 марта 45 г. с левой стороны в шею. Я лежу в госпитале. Сейчас мне стало полегче. Могу вставать и ходить вокруг койки. Действовал на 3 Украинск. 
// Рая, я получил одно твое письмо. Ты меня спрашивала, как я провожу время. В этом день вечером мы отбивали танковую атаку 13 шт. Вот как проводили время. До Вены осталось 150 км. На фронт выехал 15 января 45 г. Не обижайся, что так долго не писал. Шли все время с боями. Когда ранило меня, я стал терять сознание. Я думал, что пришел конец. Как не хотелось умирать на Венгерской земле. 
// Крепко целую тебя, моя милая женочка. 
// Твой муж Закурдаев А.И. 
// Адрес пока у меня не постоянный.`
//   };

  constructor(
    private translate: TranslateService,
    private route: ActivatedRoute,
    private videoService: VideoService,
    private serverUrl: ServerUrlService
  ) { 
    this.url = this.serverUrl.serverUrl;
  }

  ngOnInit(): void {
    this.videoId = this.route.snapshot.paramMap.get('id')!;
    console.log('Video ID:', this.videoId);
    this.getVideoInfo();
  }

  getVideoInfo(){
    this.videoService.getVideoInfo(this.videoId).subscribe(
      (data) => { 
        this.video = data;
        console.log(this.video);
      }
    );
  }

    ngAfterViewInit() {
    const player = new Plyr('#player');
  }
}
