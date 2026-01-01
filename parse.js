function parseNewlines(text) {
    return text
    .split('\\n')
    .map(p => `<p class="textParserBlock">${p}</p>`)
    .join("");
}

function parseBlockMath(html) {
    return html.replace(
        /\$\$([\s\S]+?)\$\$/g,
        (_, expr) => `<div>\\[${expr.trim()}\\]</div>`
    );
}

function parseInlineMath(html) {
    return html.replace(
        /\$(.+?)\$/g,
        (_, expr) => `\\(${expr}\\)`
    );
}

function parseTextDecorations(html) {
    return html
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/__(.+?)__/g, "<u>$1</u>");
}

function parseLinks(html) {
    return html.replace(
        /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g,
        '<a href="$2" target="_blank">$1</a>'
    );
}

function parseMarkdown(text) {
    let html = text;
    html = parseNewlines(html);
    html = parseBlockMath(html);
    html = parseInlineMath(html);
    html = parseTextDecorations(html);
    html = parseLinks(html);
    return html;
}