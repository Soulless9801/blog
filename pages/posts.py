from pages.page import CollectionEditorPage

class PostsPage(CollectionEditorPage):

    def __init__(self, collection="posts"):

        fields = {
            'title': {
                'type': 'lineedit',
                'label': 'Title',
            },
            'body': {
                'type': 'textedit',
                'label': 'Body',
                'on_change': self.render_markdown,
            }
        }

        super().__init__(collection=collection, fields=fields, theme='dark', title="Posts")

    def gen_html(self):

        return r"""
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8" />
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css">
                    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.js"></script>
                    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/contrib/auto-render.min.js"></script>

                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            color: %s;
                            background-color: %s;
                            transition: background-color 0.3s, color 0.3s;
                        }
                        .textParserBlock {
                            display: block;
                            margin-bottom: 1em;
                        }
                        a {
                            color: %s;
                            text-decoration: none;
                            transition: background-color 0.3s, color 0.3s;
                        }
                        a:hover {
                            color: %s;
                        }
                    </style>
                </head>

                <body>
                    <div id="content"></div>

                    <script>

                        function parseNewlines(text) {
                            return text
                            .split('\n\n')
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

                        function renderContent(text) {
                            const container = document.getElementById("content");
                            container.innerHTML = parseMarkdown(text);

                            renderMathInElement(container, {
                                delimiters: [
                                    {left: "\\[", right: "\\]", display: true},
                                    {left: "\\(", right: "\\)", display: false}
                                ]
                            });
                        }
                    </script>
                </body>
            </html>
        """ % (
            '#252525' if self.theme == 'light' else '#ffffff',
            '#f9f5f1' if self.theme == 'light' else '#212529',
            '#252525' if self.theme == 'light' else '#ffffff',
            '#898989' if self.theme == 'light' else '#9b9b9b',
        )

    def render_markdown(self):
        latex_str = self.field_widgets['body'].toPlainText()
        js = f"renderContent({latex_str!r});"
        self.web.page().runJavaScript(js)

