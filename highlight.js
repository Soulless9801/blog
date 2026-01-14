import { codeToHtml } from "shiki";

const html = await codeToHtml(
    process.argv[2],
    { theme: "github-dark", lang: process.argv[3] }
)

console.log(html);