import { defineConfig, UserConfig } from 'vitepress'
import { withSidebar } from 'vitepress-sidebar';
import { VitePressSidebarOptions } from 'vitepress-sidebar/types';



const vitePressOptions: UserConfig = {
  // VitePress의 옵션
  title: "TIL",
  outDir: '../dist',
  base: '/til/',
  lastUpdated: true,
  markdown: {
	math: true
  },
  head: [
    ['link', {rel: 'icon', href: '/til/favicon.ico'}]
  ],
  themeConfig: {
    nav: [
      // { text: 'Home', link: '/' },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/opjt' }
    ],
    search: {
      provider: 'local'
    },
    outline:  {
      level: [1,3]
    },
  },
   
};

const vitePressSidebarConfig: VitePressSidebarOptions = {
	documentRootPath: 'docs',
	collapseDepth: 2,
	capitalizeFirst: true,
	underscoreToSpace: false,
  excludeFilesByFrontmatterFieldName: "hide", //hide 옵션이 켜져있는 파일 disable
	useTitleFromFileHeading: true, 
	useTitleFromFrontmatter: true,
  sortMenusByFrontmatterOrder: true, // order 값을 통해 순서 정렬
};

// https://vitepress.dev/reference/site-config
export default defineConfig(withSidebar(vitePressOptions, vitePressSidebarConfig))
