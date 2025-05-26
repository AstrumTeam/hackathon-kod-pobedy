import { AfterViewInit, Component, OnInit } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import * as Plyr from 'plyr';
import { ActivatedRoute, Router } from '@angular/router';
import { ServerUrlService } from 'src/app/services/ServerURLService';
import { VideoService } from 'src/app/services/VideoService';

@Component({
  selector: 'app-result',
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.css']
})
export class ResultComponent implements AfterViewInit, OnInit {
  videoId: string | null = null;

  letter: string | null = null;

  autor: string = '';

  isReady = false;

  isPublished: boolean = false;
  isDownloaded: boolean = false;

  url = '';

  video = {
    url: 'assets/videos/example.mp4',
    poster: 'assets/photos/photo.jpeg',
    letter: `Здравствуй, дорогая моя, любимая жена Рая! Крепко целую тебя. 
Меня ранило 24 марта 45 г. с левой стороны в шею. Я лежу в госпитале. Сейчас мне стало полегче. Могу вставать и ходить вокруг койки. Действовал на 3 Украинск. 
Рая, я получил одно твое письмо. Ты меня спрашивала, как я провожу время. В этом день вечером мы отбивали танковую атаку 13 шт. Вот как проводили время. До Вены осталось 150 км. На фронт выехал 15 января 45 г. Не обижайся, что так долго не писал. Шли все время с боями. Когда ранило меня, я стал терять сознание. Я думал, что пришел конец. Как не хотелось умирать на Венгерской земле. 
Крепко целую тебя, моя милая женочка. 
Твой муж Закурдаев А.И. 
Адрес пока у меня не постоянный.`,
    promptsWithScenes: [
      { prompt: 'Закат над горами', video: 'assets/videos/example.mp4' },
      { prompt: 'Девочка играет с собакой', video: 'assets/videos/example.mp4' },
      { prompt: 'Город ночью с огнями', video: 'assets/videos/example.mp4' },
      { prompt: 'Закат над горами', video: 'assets/videos/example.mp4' },
      { prompt: 'Девочка играет с собакой', video: 'assets/videos/example.mp4' },
      { prompt: 'Город ночью с огнями', video: 'assets/videos/example.mp4' }
    ],
    options: {
      subtitles: true,
      backgroundSounds: false,
      backgroundMusic: true
    }
  };

  constructor(
    private translate: TranslateService,
    private route: ActivatedRoute,
    private serverUrl: ServerUrlService,
    private router: Router,
    private videoService: VideoService
  ) {
    this.url = this.serverUrl.serverUrl;
  }

  ngOnInit() {

    setTimeout(() => {
      this.isReady = true;
    }, 1500);

    this.route.queryParams.subscribe(params => {
      this.videoId = params['id'];
      this.letter = params['letter'];
      console.log('Video ID:', this.videoId);
      console.log('Letter:', this.letter);
    });
  }

  ngAfterViewInit(): void {
    new Plyr('#main-player');

    this.video.promptsWithScenes.forEach((_, i) => {
      const id = `#scene-player-${i}`;
      new Plyr(id);
    });
  }

  regenerate() {

  }

  download() {
    this.videoService.getVideo(this.videoId!).subscribe((blob: Blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `video_${this.videoId}.mp4`;
      a.click();
      window.URL.revokeObjectURL(url);
      console.log('Видео скачано');

      this.isDownloaded = true;

      setTimeout(() => this.isDownloaded = false, 3000);
    });
  }

  show() {
    this.isPublished = true;
    setTimeout(() => this.isPublished = false, 3000);
  }

  publish() {
    this.videoService.publishVideo({
      letter: this.letter!,
      author: this.autor,
      job_id: this.videoId!
    }).subscribe((response) => {
      console.log('Response:', response);
      this.isPublished = true;
      setTimeout(() => this.isPublished = false, 3000);
    })
  }

  generateMore() {
    this.router.navigate(['/create'])
  }
}
