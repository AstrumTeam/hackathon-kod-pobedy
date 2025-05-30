import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ServerUrlService } from './ServerURLService';

export interface GenerateVideo {
    letter: string;
    speaker: string;
    subtitles: boolean;
    music: boolean;
}

export interface Video {
    id: string;
    video: string;
    poster: string;
    letter: string;
}

export interface GenerateVideoResponse {
    job_id: string;
    message: string;
    queue_position: number;
}

export interface PublishVideo{
    letter: string;
    author: string;
    job_id: string;
}

@Injectable({
    providedIn: 'root'
})
export class VideoService {

    constructor(
        private http: HttpClient,
        private serverUrl: ServerUrlService
    ) { }

    private apiUrl = `${this.serverUrl.serverUrl}/api`;

    getVideoInfo(id: string): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/publicated_video_info/${id}/`);
    }

    getPublicatedVideos(): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/publicated_videos/`);
    }

    publishVideo(data: PublishVideo): Observable<any> {
        console.log(data);
        return this.http.post<any>(`${this.apiUrl}/publish_video/`, data);
    }

    getVideo(id: string): Observable<Blob> {
        return this.http.get(`${this.apiUrl}/get_video/${id}/`, {
            responseType: 'blob' as 'blob'
        });
    }

    getVideoStatus(jobId: string): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/video_status/${jobId}/`);
    }

    getVideos(): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}`);
    }

    generateVideo(data: GenerateVideo): Observable<GenerateVideoResponse> {
        console.log(data);
        return this.http.post<any>(`${this.apiUrl}/generate_video/`, data);
    }
}