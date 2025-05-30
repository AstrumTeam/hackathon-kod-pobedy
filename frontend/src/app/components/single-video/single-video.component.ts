import { AfterViewInit, Component, OnInit } from '@angular/core';
import { Video } from '../main/main.component';
import * as Plyr from 'plyr';
import { TranslateService } from '@ngx-translate/core';
import { ActivatedRoute, Router } from '@angular/router';
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

  error = "";

  video: Video = {
    id: "",
    letter: "",
    video_filename: "",
    preview_filename: "",
    author: "",
  }

  constructor(
    private translate: TranslateService,
    private route: ActivatedRoute,
    private videoService: VideoService,
    private serverUrl: ServerUrlService,
    private router: Router
  ) {
    this.url = this.serverUrl.serverUrl;
  }

  ngOnInit(): void {
    this.videoId = this.route.snapshot.paramMap.get('id')!;
    console.log('Video ID:', this.videoId);
    this.getVideoInfo();
  }


  getVideoInfo() {
    this.videoService.getVideoInfo(this.videoId).subscribe({
      next: (data) => {
        this.video = data;
        this.error = '';
        console.log(this.video);
      },
      error: (err) => {
        console.error('Ошибка при получении видео:', err);

        if (err.status === 404 && err.error?.message) {
          this.error = err.error.message;
        } else {
          this.error = `Ошибка: ${err.status || 'неизвестна'}`;
        }
      }
    });
  }

  toMain() {
    this.router.navigate([`/`]);
  }

  ngAfterViewInit() {
    const player = new Plyr('#player');
  }
}
