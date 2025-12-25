require('dotenv').config();

const TelegramBot = require('node-telegram-bot-api');
const ogs = require('open-graph-scraper');
const axios = require('axios');
const cheerio = require('cheerio');

const token = process.env.TELEGRAM_TOKEN;
const bot = new TelegramBot(token, { polling: true });

const SPOTIFY_REGEX = /https?:\/\/(open\.spotify\.com|spotify\.link)\/[^\s]+/gi;
const YANDEX_MUSIC_REGEX = /https?:\/\/music\.yandex\.ru\/[^\s]+/gi;
const MTS_MUSIC_REGEX = /https?:\/\/mts-music-spo\.onelink\.me\/[^\s]+/gi;

function escapeMarkdown(text) {
    if (!text) return 'N/A';
    return text.replace(/([*_`\[\]()~>#+-=|{}.!])/g, '\\$1');
}

const puppeteer = require('puppeteer');

async function parseYandexMusic(url) {
    try {
        const browser = await puppeteer.launch({ headless: true });
        const page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
        await page.goto(url, { waitUntil: 'networkidle2' });
        console.log(page);
        const title = await page.title();
        console.log('Yandex Music page title:', title);
        await browser.close();
        // Title format: "Artist — Track — Яндекс Музыка"
        const parts = title.split(' — ');
        console.log('Title parts:', parts);
        if (parts.length >= 3) {
            const artist = parts[0].trim();
            const track = parts[1].trim();
            return {
                title: track,
                artists: artist,
                url: url
            };
        }
        return { error: 'Could not parse Yandex Music page' };
    } catch (error) {
        console.error('Error parsing Yandex Music:', error);
        return { error: 'Failed to parse Yandex Music link' };
    }
}

async function parseLink(url) {
    try {
        if (SPOTIFY_REGEX.test(url)) {
            const { result } = await ogs({ url });
            const title = result.ogTitle || 'Unknown Title';
            const artists = result.ogDescription.split(title)[0] || 'Unknown Artist';
            return {
                title: title.trim(),
                artists: artists.replace(/(by|•)/gi, '').trim(),
                url: result.ogUrl || url,
            }
        }

        if (YANDEX_MUSIC_REGEX.test(url)) {
            console.log('Detected Yandex Music link');
            return await parseYandexMusic(url);
        }

        if (MTS_MUSIC_REGEX.test(url)) {
            console.log('Detected MTS Music link');
            const result = await parseYandexMusic(url);
            console.log(result);
        }

        return result;
    } catch (error) {
        console.error('Error parsing link:', error);
        return { error: 'Failed to parse link' };
    }
}

bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, 'Hello! Send me a music track link from Spotify, Yandex Music, or MTS Music, and I\'ll provide you with multi-links to the track on other services.');
});

bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text;

    const urlRegex = /^(https?:\/\/[^\s]+)/g;
    const match = text.match(urlRegex);

    if (match) {
        const parsingMsg = await bot.sendMessage(chatId, 'Parsing your link...');

        const ogData = await parseLink(match[0]);

        await bot.deleteMessage(chatId, parsingMsg.message_id);

        if (ogData.error) {
            bot.sendMessage(chatId, 'Error parsing the link.');
            return
        };

        let response = `*Title:* ${escapeMarkdown(ogData.title)}\n`;
        response += `*Artists:* ${escapeMarkdown(ogData.artists)}\n`;
        response += `*URL:* ${ogData.url}\n`;

        bot.sendMessage(chatId, response, { parse_mode: 'Markdown' });
    }
})