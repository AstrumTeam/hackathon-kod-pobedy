import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { GenerateVideo, VideoService } from 'src/app/services/VideoService';

export interface Speaker {
  key: string;
  name: string;
  photo: string;
  description: string;
}

@Component({
  selector: 'app-create',
  templateUrl: './create.component.html',
  styleUrls: ['./create.component.css']
})
export class CreateComponent {
  queue: number = 0;
  message: string = '';

  error: string = '';

  video: GenerateVideo = {
    letter: "",
    speaker: "",
    subtitles: true,
    music: true
  }

  page: string = 'letter'; // 'letter', 'speakerSex', 'speaker', 'checkboxes', 'process', 'error'

  speakers: Speaker[] = [];

  speakersSex: Speaker[] = [
    {
      key: "man",
      name: 'SPEAKER_MALE',
      photo: 'assets/speakers/levitan_2.jpg',
      description: 'SPEAKER_MALE_DESC'
    },
    {
      key: "woman",
      name: 'SPEAKER_FEMALE',
      photo: 'assets/speakers/shatilova.jpg',
      description: 'SPEAKER_FEMALE_DESC'
    }
  ];

  speakersMen: Speaker[] = [
    {
      key: "levitan",
      name: 'LEVITAN_NAME',
      photo: 'assets/speakers/levitan.jpg',
      description: 'LEVITAN_DESC'
    },
    {
      key: "hmara",
      name: 'KHMARA_NAME',
      photo: 'assets/speakers/khmara.jpg',
      description: 'KHMARA_DESC'
    },
  ];

  speakersWomen: Speaker[] = [
    {
      key: "bergholz",
      name: 'BERGGOLTS_NAME',
      photo: 'assets/speakers/berggolts.jpg',
      description: 'BERGGOLTS_DESC'
    },
    {
      key: "vysotskaya",
      name: 'VYSOTSKAYA_NAME',
      photo: 'assets/speakers/vysotskaya.webp',
      description: 'VYSOTSKAYA_DESC'
    },
  ];

  options = {
    subtitles: true,
    backgroundSounds: true,
    backgroundMusic: true,
  };

  constructor(
    private router: Router,
    private translate: TranslateService,
    private videoService: VideoService
  ) {

  }

  goToLetter() {
    this.page = 'letter';
  }

  goToSpeackerSex() {
    const text = this.video?.letter || '';
    const length = text.trim().length;

    if (length < 100) {
      return;
    }

    if (length > 2000) {
      return;
    }

    this.page = 'speakerSex';
  }

  goToSpeaker(name: string) {
    if (name === 'SPEAKER_MALE') {
      this.speakers = this.speakersMen;
    } else if (name === 'SPEAKER_FEMALE') {
      this.speakers = this.speakersWomen;
    }
    this.page = 'speaker';
  }

  goToProcess() {
    const existingJobId = localStorage.getItem('job_id');

    if (existingJobId) {
      this.checkVideoStatus(existingJobId);
      return;
    }

    this.videoService.generateVideo(this.video).subscribe({
      next: (response) => {
        console.log('Response:', response);
        this.message = response.message;

        const jobId = response.job_id;

        if (response.message === 'Видео поставлено в очередь на генерацию') {
          localStorage.setItem('job_id', jobId);
          this.page = 'process';
          this.queue = response.queue_position;

          this.checkVideoStatus(jobId);
        } else if (response.message === 'Неверный формат данных') {
          localStorage.removeItem('job_id');
          this.error = response.message;
          this.page = 'error';
        } else {
          this.error = response.message;
          this.page = 'error';
        }
      },
      error: (err) => {
        console.error('Error:', err);

        if (err.error?.message) {
          this.error = err.error.message;
        } else if (err.status) {
          this.error = `Ошибка ${err.status}`;
        } else {
          this.error = 'Произошла ошибка при отправке запроса';
        }

        this.page = 'error';
      }
    });
  }

  checkVideoStatus(jobId: string) {
    const intervalId = setInterval(() => {
      this.videoService.getVideoStatus(jobId).subscribe({
        next: (statusResponse) => {
          console.log('Status Response:', statusResponse);

          this.queue = statusResponse.queue_position;

          if (statusResponse.status === 'processing') {
            this.page = 'process';
            this.message = 'Обработка...';
          }

          if (statusResponse.status === 'completed') {
            clearInterval(intervalId);
            localStorage.removeItem('job_id');
            this.router.navigate(['/result'], {
              queryParams: {
                id: jobId,
                letter: this.video.letter
              }
            });
          }

          if (statusResponse.status === 'failed' && statusResponse.error === 'Письмо не прошло фильтрацию') {
            clearInterval(intervalId);
            localStorage.removeItem('job_id');
            this.error = statusResponse.error || 'Письмо не прошло фильтрацию на корректность. Повторите попытку.';
            this.page = 'error';
          }
          if (statusResponse.status === 'failed' && statusResponse.error === 'division by zero') {
            clearInterval(intervalId);
            localStorage.removeItem('job_id');
            this.error = 'Ошибка генерации. Повторите попытку.';
            this.page = 'error';
          }
        },
        error: (err) => {
          console.error('Status Error:', err);

          if (err.error?.message) {
            this.error = err.error.message;
          } else {
            this.error = `Ошибка: ${err.status || 'неизвестна'}`;
          }

          this.page = 'error';
          clearInterval(intervalId);
          localStorage.removeItem('job_id');
        }
      });
    }, 5000);
  }

  goToCheckboxes(key: string) {
    this.video.speaker = key;
    this.page = 'checkboxes';
  }
}
