"""Google Dork Engine - Template library and query builder"""

import webbrowser
import urllib.parse

DORK_TEMPLATES = {
    "🔐 Login Pages": [
        'inurl:"/admin/login"',
        'inurl:"/wp-login.php"',
        'intitle:"Login" inurl:admin',
        'inurl:login filetype:php',
        'intitle:"admin panel" inurl:admin',
        'inurl:user/login',
        'inurl:account/login',
        'inurl:signin',
        'inurl:"/administrator/"',
        'inurl:dashboard inurl:login',
    ],
    "📁 Exposed Files": [
        'filetype:log inurl:log',
        'filetype:sql "INSERT INTO"',
        'filetype:env "DB_PASSWORD"',
        'filetype:cfg "password"',
        'filetype:xlsx "confidential"',
        'filetype:csv "email" "password"',
        'filetype:bak inurl:backup',
        'ext:xml "username" "password"',
        'filetype:txt "api_key"',
        '"Index of /" +backup',
    ],
    "📷 IP Cameras": [
        'inurl:"/view/view.shtml" cam',
        'intitle:"Live View / - AXIS"',
        'inurl:axis-cgi/mjpg',
        'intitle:"webcamXP 5"',
        'inurl:"/webcam.html"',
        'intitle:"Network Camera"',
        'inurl:top.htm inurl:currenttime',
        'intitle:"MJPG Live Demo"',
    ],
    "💾 Database Exposure": [
        'inurl:phpMyAdmin',
        'intitle:"phpMyAdmin" "Welcome to phpMyAdmin"',
        'inurl:adminer.php',
        'filetype:sql "INSERT INTO" "VALUES"',
        'intitle:"MongoDB Server Information"',
        'inurl:elasticsearch',
        'intitle:"Apache CouchDB"',
        'intitle:"redis"',
    ],
    "🔑 Sensitive Info": [
        'filetype:env "AWS_ACCESS_KEY"',
        'filetype:cfg "api_key"',
        '"apikey" filetype:json',
        '"secret_key" filetype:py',
        'inurl:config filetype:php',
        '"password" filetype:log',
        'filetype:yaml "password"',
        '"token" filetype:json',
    ],
    "📋 Documents": [
        'filetype:pdf',
        'filetype:doc',
        'filetype:xls',
        'filetype:ppt',
        'filetype:docx "confidential"',
        'filetype:xlsx "salary"',
        'filetype:pptx "internal"',
        'filetype:odt "private"',
    ],
    "⚠️ Vulnerabilities": [
        'inurl:".php?id="',
        'inurl:"?page="',
        'inurl:"redirect="',
        'intitle:"Apache Status"',
        'inurl:wp-content/uploads',
        '"Index of /"',
        'inurl:"shell.php"',
        'inurl:"/phpinfo.php"',
    ],
    "📧 Email Harvest": [
        '"@gmail.com" "password" filetype:txt',
        '"@" filetype:csv "password"',
        'intext:"email" filetype:xls',
        'site:pastebin.com "email" "password"',
        '"contact" "email" filetype:txt',
    ],
    "🌐 Subdomains": [
        'site:*.target.com',
        'inurl:dev.',
        'inurl:staging.',
        'inurl:test.',
        'inurl:beta.',
        'inurl:admin.',
        'inurl:api.',
        'inurl:internal.',
    ],
    "🕵️ OSINT": [
        'site:pastebin.com',
        'site:github.com "password"',
        'site:linkedin.com intitle:"at"',
        'site:twitter.com',
        'site:instagram.com',
        'inurl:about "phone" "email"',
    ],
}


class DorkEngine:
    def get_categories(self):
        return list(DORK_TEMPLATES.keys())

    def get_templates(self, category):
        return DORK_TEMPLATES.get(category, [])

    def build_custom_dork(self, site="", inurl="", intitle="",
                          filetype="", intext="", ext="", custom=""):
        parts = []
        if site:
            parts.append(f'site:{site}')
        if inurl:
            parts.append(f'inurl:"{inurl}"')
        if intitle:
            parts.append(f'intitle:"{intitle}"')
        if filetype:
            parts.append(f'filetype:{filetype}')
        if ext:
            parts.append(f'ext:{ext}')
        if intext:
            parts.append(f'intext:"{intext}"')
        if custom:
            parts.append(custom)
        return ' '.join(parts)

    def apply_target(self, dork, target):
        return dork.replace('{target}', target)

    def open_google(self, query):
        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        webbrowser.open(url)

    def open_bing(self, query):
        url = "https://www.bing.com/search?q=" + urllib.parse.quote(query)
        webbrowser.open(url)

    def open_duckduckgo(self, query):
        url = "https://duckduckgo.com/?q=" + urllib.parse.quote(query)
        webbrowser.open(url)
