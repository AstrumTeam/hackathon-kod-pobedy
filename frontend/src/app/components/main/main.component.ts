import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ServerUrlService } from 'src/app/services/ServerURLService';
import { VideoService } from 'src/app/services/VideoService';

export interface Video {
  id: string;
  letter: string;
  video_filename: string;
  preview_filename: string;
  author: string;
}

@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.css']
})
export class MainComponent implements OnInit {
  videos: Video[] = [];
  error: string = '';

  show_ai = false;

  url = '';

  videosColumn1: Video[] = [];
  videosColumn2: Video[] = [];
  videosColumn3: Video[] = [];

  constructor(
    private router: Router,
    private videoService: VideoService,
    private urlService: ServerUrlService
  ) {
    this.url = this.urlService.serverUrl;
  }

  onImageLoad(event: Event) {
    const img = event.target as HTMLImageElement;
    img.classList.add('loaded');
  }

  goToVideo(id: string) {
    this.router.navigate([`/video/${id}`]);
  }

  getPublicatedVideos() {
    this.videoService.getPublicatedVideos().subscribe((data: any) => {
      this.videos = data.reverse();
      console.log('Videos:', this.videos);
      this.makeVideoRaw();
    }, (error) => {
      console.error('Error fetching videos:', error);
      this.error = error;
    });
  }

  ngOnInit() {
    this.getPublicatedVideos();
    setTimeout(() => this.show_ai = true, 3000);
  }

  makeVideoRaw() {
    this.videos.forEach((v, i) => {
      if (i % 3 === 0) this.videosColumn1.push(v);
      else if (i % 3 === 1) this.videosColumn2.push(v);
      else this.videosColumn3.push(v);
    });
  }

  goToCreate() {
    this.router.navigate([`/create`]);
  }
}
