import { Component } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  mobileMenuOpen = false;
  dropdownOpen = false;

  title = 'PobedaLetters';

  currentLang = 'ru';

  languages = [
    { code: 'ru', label: 'Русский' },
    { code: 'en', label: 'English' },
    { code: 'es', label: 'Español' },
    { code: 'de', label: 'Deutsch' },
    { code: 'fr', label: 'Français' },
    { code: 'zh', label: '中文' },          // Chinese
    { code: 'ar', label: 'العربية' },       // Arabic
    { code: 'hi', label: 'हिन्दी' },        // Hindi
    { code: 'pt', label: 'Português' },
    { code: 'ja', label: '日本語' },         // Japanese
    { code: 'it', label: 'Italiano' }
  ];

  constructor(private translate: TranslateService) {
    this.translate.setDefaultLang('ru');
    this.translate.use('ru'); // или 'en'
  }

  get currentLangLabel() {
    return this.languages.find(lang => lang.code === this.currentLang)?.label || this.currentLang;
  }

  toggleMobileMenu() {
    this.mobileMenuOpen = !this.mobileMenuOpen;
  }

  closeMobileMenu() {
    this.mobileMenuOpen = false;
  }

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  closeDropdown() {
    this.dropdownOpen = false;
  }

  switchLang(lang: string) {
    this.currentLang = lang;
    this.translate.use(lang);
    this.dropdownOpen = false;
  }

  switchLangFromEvent(event: Event) {
    const target = event.target as HTMLSelectElement;
    const value = target.value;
    this.switchLang(value);
  }

  goHome() {
    window.location.href = '/';
  }

  redirectToTelegramBot() {
    window.open('https://t.me/pobedaletters_supportbot', '_blank');
  }
}
